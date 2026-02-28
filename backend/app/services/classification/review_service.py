import logging
from typing import List, Dict, Any
from app.db.supabase_client import get_supabase
from app.services.classification.classifier import ClassifiedItem
from app.services.classification.rule_matcher import filter_rules, match_item_to_rules

logger = logging.getLogger(__name__)


def get_alternatives(item_name: str, entity_type: str, document_type: str) -> List[Dict[str, Any]]:
    filtered_rules = filter_rules(entity_type, document_type)
    matches = match_item_to_rules(item_name, filtered_rules)

    alts = []
    for match in matches[:3]:
        alts.append({
            "row": match.rule.target_row,
            "sheet": match.rule.target_sheet,
            "label": match.rule.target_label,
            "score": match.score,
        })
    return alts


def populate_review_queue(project_id: str, firm_id: str, classified_items: List[ClassifiedItem], entity_type: str) -> int:
    db = get_supabase()

    count = 0
    for item in classified_items:
        if item.needs_review:
            try:
                existing = (
                    db.table("review_queue")
                    .select("id")
                    .eq("cma_project_id", project_id)
                    .eq("firm_id", firm_id)
                    .eq("source_item_name", item.item_name)
                    .execute()
                )

                alts = get_alternatives(item.item_name, entity_type, "")

                payload = {
                    "firm_id": firm_id,
                    "cma_project_id": project_id,
                    "source_item_name": item.item_name,
                    "source_item_amount": item.item_amount,
                    "suggested_row": item.target_row,
                    "suggested_sheet": item.target_sheet,
                    "suggested_label": item.target_label,
                    "confidence": item.confidence,
                    "reasoning": item.reasoning,
                    "status": "pending",
                    "source": item.source,
                    "alternative_suggestions": alts,
                }

                if existing.data:
                    db.table("review_queue").update(payload).eq("id", existing.data[0]["id"]).eq("firm_id", firm_id).execute()
                else:
                    db.table("review_queue").insert(payload).execute()

                count += 1
            except Exception as e:
                logger.error("Failed to populate review queue for item '%s': %s", item.item_name, e)

    return count


def get_review_summary(project_id: str, firm_id: str) -> Dict[str, Any]:
    """Get review queue summary, scoped by firm_id for multi-tenant safety."""
    db = get_supabase()
    res = (
        db.table("review_queue")
        .select("status, confidence")
        .eq("cma_project_id", project_id)
        .eq("firm_id", firm_id)
        .execute()
    )

    pending = 0
    resolved = 0
    skipped = 0
    conf_sum = 0.0

    buckets = {
        "0.50-0.69": 0,
        "0.30-0.49": 0,
        "<0.30": 0,
    }

    for row in res.data:
        status = row["status"]
        if status == "pending":
            pending += 1
            conf = row["confidence"] or 0.0
            conf_sum += conf

            if conf >= 0.50:
                buckets["0.50-0.69"] += 1
            elif conf >= 0.30:
                buckets["0.30-0.49"] += 1
            else:
                buckets["<0.30"] += 1
        elif status == "resolved":
            resolved += 1
        else:
            skipped += 1

    avg_conf = (conf_sum / pending) if pending > 0 else 0.0

    return {
        "total_pending": pending,
        "total_resolved": resolved,
        "total_skipped": skipped,
        "avg_confidence": avg_conf,
        "items_by_confidence": buckets,
    }
