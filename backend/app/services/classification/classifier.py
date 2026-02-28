import json
import logging
import os
from typing import List, Optional
from pydantic import BaseModel
from app.services.classification.precedent_matcher import get_best_precedent
from app.services.classification.rule_matcher import classify_by_rules, filter_rules
from app.services.classification.prompts import CLASSIFICATION_SYSTEM_PROMPT, CLASSIFICATION_USER_PROMPT
from app.services.gemini_client import GeminiClient, log_llm_usage

logger = logging.getLogger(__name__)


class ClassifiedItem(BaseModel):
    item_name: str
    item_amount: float
    target_row: Optional[int] = None
    target_sheet: Optional[str] = None
    target_label: Optional[str] = None
    confidence: float
    source: str
    matched_rule_id: Optional[int] = None
    matched_precedent_id: Optional[str] = None
    reasoning: str
    needs_review: bool


class ClassificationResult(BaseModel):
    total_items: int
    classified_by_precedent: int
    classified_by_rule: int
    classified_by_ai: int
    unclassified: int
    needs_review: int
    auto_classified: int
    average_confidence: float
    items: List[ClassifiedItem]
    llm_cost_usd: float
    llm_tokens_used: int


def get_db_extracted_data(project_id: str, firm_id: str):
    from app.db.supabase_client import get_supabase
    db = get_supabase()
    res = db.table("cma_projects").select("extracted_data").eq("id", project_id).eq("firm_id", firm_id).execute()
    if not res.data or not res.data[0].get("extracted_data"):
        return {}
    return res.data[0]["extracted_data"]


def clean_json(text: str) -> str:
    text = text.strip()
    if text.startswith("```json"):
        text = text[len("```json"):]
    if text.startswith("```"):
        text = text[len("```"):]
    if text.endswith("```"):
        text = text[:-len("```")]
    return text.strip()


def classify_project(project_id: str, firm_id: str, entity_type: str) -> ClassificationResult:
    data = get_db_extracted_data(project_id, firm_id)

    all_raw_items = []

    for doc in ["profit_and_loss", "balance_sheet", "trial_balance"]:
        if data.get(doc) and data[doc].get("line_items"):
            for itm in data[doc]["line_items"]:
                if not itm.get("is_total") and itm.get("name"):
                    all_raw_items.append({
                        "item_name": itm["name"],
                        "item_amount": itm.get("amount", 0.0),
                        "document_type": doc,
                    })

    results: List[ClassifiedItem] = []
    to_ai = []

    # Tier 1 & 2
    for item in all_raw_items:
        name = item["item_name"]
        amt = item["item_amount"]
        doc_type = item["document_type"]

        # Tier 1: Precedent matching
        try:
            prec = get_best_precedent(firm_id, name, entity_type)
        except Exception as e:
            logger.warning("Precedent lookup failed for '%s': %s", name, e)
            prec = None

        if prec and prec.confidence >= 0.80:
            results.append(ClassifiedItem(
                item_name=name,
                item_amount=amt,
                target_row=prec.target_row,
                target_sheet=prec.target_sheet,
                target_label="Precedent matched",
                confidence=prec.confidence,
                source="precedent",
                matched_precedent_id=prec.precedent_id,
                reasoning=f"Matched CA precedent ({prec.match_type})",
                needs_review=False,
            ))
            continue

        # Tier 2: Rule matching
        rule_match = classify_by_rules(name, entity_type, doc_type)
        if rule_match and rule_match.score >= 0.85:
            results.append(ClassifiedItem(
                item_name=name,
                item_amount=amt,
                target_row=rule_match.rule.target_row,
                target_sheet=rule_match.rule.target_sheet,
                target_label=rule_match.rule.target_label,
                confidence=rule_match.score,
                source="rule",
                matched_rule_id=rule_match.rule.id,
                reasoning=f"Matched Rule ID {rule_match.rule.id} via {rule_match.match_type}",
                needs_review=False,
            ))
            continue

        # Tier 3: Queue for AI
        to_ai.append(item)

    ai_cost = 0.0
    ai_tokens = 0

    # Tier 3: AI classification
    if to_ai:
        try:
            client = GeminiClient()
        except ValueError as e:
            logger.error("GeminiClient init failed: %s", e)
            # Mark all AI items as unclassified
            for bi in to_ai:
                results.append(ClassifiedItem(
                    item_name=bi["item_name"],
                    item_amount=bi["item_amount"],
                    confidence=0.0,
                    source="unclassified",
                    reasoning=f"AI unavailable: {e}",
                    needs_review=True,
                ))
        else:
            model_name = os.getenv("LLM_CLASSIFICATION_MODEL", "gemini-2.0-flash")

            batch_size = 20
            total_batches = (len(to_ai) + batch_size - 1) // batch_size

            filtered_rules = filter_rules(entity_type, "")
            rules_compact = [{"id": r.id, "terms": r.source_terms, "row": r.target_row, "sheet": r.target_sheet} for r in filtered_rules]
            rules_str = json.dumps(rules_compact)
            precedents_str = "[]"

            for b in range(total_batches):
                batch_items = to_ai[b * batch_size:(b + 1) * batch_size]
                prompt = CLASSIFICATION_USER_PROMPT.format(
                    entity_type=entity_type,
                    batch_note=f"This is batch {b + 1} of {total_batches}.",
                    rules_json=rules_str,
                    precedents_json=precedents_str,
                    items_json=json.dumps(batch_items),
                )

                try:
                    resp = client.generate(
                        model=model_name,
                        prompt=prompt,
                        system_instruction=CLASSIFICATION_SYSTEM_PROMPT,
                        temperature=0.1,
                        response_format="json",
                    )

                    ai_cost += resp.cost_usd
                    ai_tokens += resp.input_tokens + resp.output_tokens

                    log_llm_usage(firm_id, project_id, model_name, "classification", resp, bool(resp.text))

                    if resp.text:
                        parsed = json.loads(clean_json(resp.text))
                        for p in parsed:
                            conf = p.get("confidence", 0.0)
                            results.append(ClassifiedItem(
                                item_name=p.get("item_name", "Unknown"),
                                item_amount=p.get("item_amount", 0.0),
                                target_row=p.get("target_row"),
                                target_sheet=p.get("target_sheet"),
                                target_label=p.get("target_label"),
                                confidence=conf,
                                source="ai",
                                matched_rule_id=p.get("matched_rule_id"),
                                reasoning=p.get("reasoning", ""),
                                needs_review=(conf < 0.70),
                            ))
                    else:
                        raise Exception("Empty generation")

                except Exception as e:
                    logger.error("AI batch %d/%d failed: %s", b + 1, total_batches, e)
                    for bi in batch_items:
                        results.append(ClassifiedItem(
                            item_name=bi["item_name"],
                            item_amount=bi["item_amount"],
                            confidence=0.0,
                            source="unclassified",
                            reasoning=f"AI failure: {e}",
                            needs_review=True,
                        ))

    # Summarize
    avg_conf = sum(r.confidence for r in results) / len(results) if results else 0.0

    return ClassificationResult(
        total_items=len(results),
        classified_by_precedent=sum(1 for r in results if r.source == "precedent"),
        classified_by_rule=sum(1 for r in results if r.source == "rule"),
        classified_by_ai=sum(1 for r in results if r.source == "ai"),
        unclassified=sum(1 for r in results if r.source == "unclassified"),
        needs_review=sum(1 for r in results if r.needs_review),
        auto_classified=sum(1 for r in results if not r.needs_review),
        average_confidence=avg_conf,
        items=results,
        llm_cost_usd=ai_cost,
        llm_tokens_used=ai_tokens,
    )
