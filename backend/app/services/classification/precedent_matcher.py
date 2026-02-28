import logging
from pydantic import BaseModel
from typing import List, Optional
from app.db.supabase_client import get_supabase
from app.services.classification.rule_matcher import normalize_indian_term, fuzzy_score

logger = logging.getLogger(__name__)


class Precedent(BaseModel):
    id: str
    firm_id: Optional[str] = None
    source_term: str
    target_row: int
    target_sheet: str
    entity_type: str
    scope: str
    created_at: str


class PrecedentMatch(BaseModel):
    precedent_id: str
    target_row: int
    target_sheet: str
    confidence: float
    source_term: str
    scope: str
    match_type: str


def find_precedents(firm_id: str, source_term: str, entity_type: str) -> List[PrecedentMatch]:
    try:
        db = get_supabase()
        # Query firm-specific + global precedents using safe PostgREST filter
        res = (
            db.table("classification_precedents")
            .select("*")
            .or_(f"firm_id.eq.{firm_id},scope.eq.global")
            .execute()
        )
    except Exception as e:
        logger.warning("Failed to query precedents: %s", e)
        return []

    precedents: List[Precedent] = [Precedent(**row) for row in res.data]

    matches = []
    norm_term = normalize_indian_term(source_term)

    for p in precedents:
        p_norm = normalize_indian_term(p.source_term)
        score = 0.0
        match_type = ""

        is_exact_term = (p_norm == norm_term)
        is_exact_firm = (str(p.firm_id) == str(firm_id) if p.firm_id else False)
        is_exact_entity = (p.entity_type == entity_type)
        is_global = (p.scope == "global")

        if is_exact_firm and is_exact_term and is_exact_entity:
            score = 1.0
            match_type = "exact_firm_term_entity"
        elif is_exact_firm and is_exact_term:
            score = 0.95
            match_type = "exact_firm_term"
        elif is_global and is_exact_term and is_exact_entity:
            score = 0.90
            match_type = "global_exact"
        else:
            f_score = fuzzy_score(norm_term, p_norm)
            if f_score > 0.70:
                if is_exact_firm and is_exact_entity:
                    score = 0.80
                    match_type = "fuzzy_firm_entity"
                elif is_global:
                    score = 0.70
                    match_type = "fuzzy_global"

        if score > 0.0:
            matches.append(PrecedentMatch(
                precedent_id=p.id,
                target_row=p.target_row,
                target_sheet=p.target_sheet,
                confidence=score,
                source_term=p.source_term,
                scope=p.scope,
                match_type=match_type,
            ))

    matches.sort(key=lambda x: x.confidence, reverse=True)
    return matches


def get_best_precedent(firm_id: str, source_term: str, entity_type: str) -> Optional[PrecedentMatch]:
    matches = find_precedents(firm_id, source_term, entity_type)
    if matches:
        return matches[0]
    return None


def create_precedent(
    firm_id: str,
    source_term: str,
    target_row: int,
    target_sheet: str,
    entity_type: str,
    scope: str,
    project_id: str,
    user_id: str,
):
    db = get_supabase()

    existing = (
        db.table("classification_precedents")
        .select("id")
        .eq("firm_id", firm_id)
        .eq("source_term", source_term)
        .eq("entity_type", entity_type)
        .execute()
    )

    payload = {
        "firm_id": firm_id,
        "source_term": source_term,
        "target_row": target_row,
        "target_sheet": target_sheet,
        "entity_type": entity_type,
        "scope": scope,
        "created_by": user_id,
        "cma_project_id": project_id,
    }

    if existing.data:
        res = (
            db.table("classification_precedents")
            .update(payload)
            .eq("id", existing.data[0]["id"])
            .eq("firm_id", firm_id)
            .execute()
        )
        return res.data[0] if res.data else payload
    else:
        res = db.table("classification_precedents").insert(payload).execute()
        return res.data[0] if res.data else payload
