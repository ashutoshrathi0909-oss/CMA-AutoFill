import logging
import time
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.core.auth import get_current_user
from app.models.user import CurrentUser
from app.models.response import StandardResponse
from app.db.supabase_client import get_supabase
from app.services.classification.classifier import classify_project, ClassificationResult
from app.services.classification.review_service import populate_review_queue, get_review_summary
from app.services.classification.review_applier import apply_review_decisions

logger = logging.getLogger(__name__)

router = APIRouter()


class ClassifyRequest(BaseModel):
    force_reclassify: bool = False


@router.post("/{project_id}/apply-reviews", response_model=StandardResponse[dict])
async def apply_project_reviews(
    project_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    try:
        res = apply_review_decisions(project_id, str(current_user.firm_id))
    except Exception as e:
        logger.error("Failed to apply reviews for project %s: %s", project_id, e)
        raise HTTPException(status_code=500, detail="Failed to apply reviews. Please try again.")

    return StandardResponse(data=res.model_dump())


@router.post("/{project_id}/classify", response_model=StandardResponse[dict])
async def classify_cma_project(
    project_id: str,
    payload: Optional[ClassifyRequest] = None,
    current_user: CurrentUser = Depends(get_current_user),
):
    db = get_supabase()
    start_time = time.time()

    # 1. Validate project (with soft-delete filter)
    proj_resp = (
        db.table("cma_projects")
        .select("id, status, client_id")
        .eq("id", project_id)
        .eq("firm_id", str(current_user.firm_id))
        .neq("status", "error")
        .execute()
    )
    if not proj_resp.data:
        raise HTTPException(status_code=404, detail="Project not found")

    project = proj_resp.data[0]

    if project["status"] != "extracted" and not (payload and payload.force_reclassify):
        raise HTTPException(status_code=409, detail="Extraction must complete before classification")

    # Get client entity_type
    client_resp = db.table("clients").select("entity_type").eq("id", project["client_id"]).execute()
    if not client_resp.data:
        raise HTTPException(status_code=404, detail="Client not found for this project")
    entity_type = client_resp.data[0]["entity_type"]

    # 2. Update status
    db.table("cma_projects").update({
        "status": "classifying",
        "pipeline_progress": 30,
    }).eq("id", project_id).execute()

    # Audit log: classification triggered
    try:
        db.table("audit_log").insert({
            "firm_id": str(current_user.firm_id),
            "action": "trigger_classification",
            "entity_type": "cma_project",
            "entity_id": project_id,
            "metadata": {"user_id": str(current_user.id)},
        }).execute()
    except Exception:
        logger.warning("Failed to write audit log for classification trigger")

    # 3. Classify
    try:
        class_res = classify_project(project_id, str(current_user.firm_id), entity_type)
    except Exception as e:
        logger.error("Classification failed for project %s: %s", project_id, e)
        db.table("cma_projects").update({
            "status": "error",
            "error_message": str(e),
        }).eq("id", project_id).execute()
        raise HTTPException(status_code=500, detail="Classification failed. Please try again.")

    # 4. Save results
    classification_data = {
        "classified_at": datetime.now().isoformat() + "Z",
        "total_items": class_res.total_items,
        "items": [item.model_dump() for item in class_res.items],
        "summary": {
            "by_precedent": class_res.classified_by_precedent,
            "by_rule": class_res.classified_by_rule,
            "by_ai": class_res.classified_by_ai,
            "uncertain": class_res.unclassified,
        },
    }

    db.table("cma_projects").update({"classification_data": classification_data}).eq("id", project_id).execute()

    # 5. Populate review queue
    items_to_review = populate_review_queue(project_id, str(current_user.firm_id), class_res.items, entity_type)

    # 6. Update status
    if items_to_review == 0:
        db.table("cma_projects").update({
            "status": "validated",
            "pipeline_progress": 60,
        }).eq("id", project_id).execute()
        final_status = "validated"
    else:
        db.table("cma_projects").update({
            "status": "reviewing",
            "pipeline_progress": 50,
        }).eq("id", project_id).execute()
        final_status = "reviewing"

    duration_ms = int((time.time() - start_time) * 1000)
    acc_est = class_res.auto_classified / class_res.total_items if class_res.total_items > 0 else 0.0

    return StandardResponse(data={
        "project_id": project_id,
        "total_items": class_res.total_items,
        "auto_classified": class_res.auto_classified,
        "needs_review": class_res.needs_review,
        "unclassified": class_res.unclassified,
        "accuracy_estimate": acc_est,
        "classification_breakdown": {
            "by_precedent": class_res.classified_by_precedent,
            "by_rule": class_res.classified_by_rule,
            "by_ai": class_res.classified_by_ai,
            "uncertain": class_res.unclassified,
        },
        "review_queue_items": items_to_review,
        "llm_cost_usd": class_res.llm_cost_usd,
        "llm_tokens_used": class_res.llm_tokens_used,
        "duration_ms": duration_ms,
        "project_status": final_status,
    })


@router.get("/{project_id}/classification", response_model=StandardResponse[dict])
async def get_project_classification(
    project_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    db = get_supabase()
    res = (
        db.table("cma_projects")
        .select("classification_data")
        .eq("id", project_id)
        .eq("firm_id", str(current_user.firm_id))
        .neq("status", "error")
        .execute()
    )

    if not res.data:
        raise HTTPException(status_code=404, detail="Project not found")

    class_data = res.data[0].get("classification_data", {})

    summary = get_review_summary(project_id, str(current_user.firm_id))
    class_data["review_queue_summary"] = summary

    return StandardResponse(data=class_data)
