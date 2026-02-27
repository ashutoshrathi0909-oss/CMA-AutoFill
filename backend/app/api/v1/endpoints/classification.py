from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.core.auth import get_current_user
from app.models.user import CurrentUser
from app.models.response import StandardResponse
from app.db.supabase_client import get_supabase
from datetime import datetime
from app.services.classification.classifier import classify_project, ClassificationResult
from app.services.classification.review_service import populate_review_queue, get_review_summary
import time

router = APIRouter()

class ClassifyRequest(BaseModel):
    force_reclassify: bool = False

@router.post("/{project_id}/classify", response_model=StandardResponse[dict])
def classify_cma_project(project_id: str, payload: Optional[ClassifyRequest] = None, current_user: CurrentUser = Depends(get_current_user)):
    db = get_supabase()
    start_time = time.time()
    
    # 1. Validate project
    proj_resp = db.table("cma_projects").select("id, status, client_id").eq("id", project_id).eq("firm_id", str(current_user.firm_id)).execute()
    if not proj_resp.data:
        raise HTTPException(status_code=404, detail="Project not found")
        
    project = proj_resp.data[0]
    
    if project["status"] != "extracted" and not (payload and payload.force_reclassify):
        raise HTTPException(status_code=409, detail="Extraction must complete before classification")
        
    # get client entity_type
    client_resp = db.table("clients").select("entity_type").eq("id", project["client_id"]).execute()
    entity_type = client_resp.data[0]["entity_type"] if client_resp.data else "trading"
        
    # 3. Update status
    db.table("cma_projects").update({
        "status": "classifying",
        "pipeline_progress": 30
    }).eq("id", project_id).execute()
    
    # 4. Classify
    try:
        class_res = classify_project(project_id, str(current_user.firm_id), entity_type)
    except Exception as e:
        db.table("cma_projects").update({"status": "error", "error_message": str(e)}).eq("id", project_id).execute()
        raise HTTPException(status_code=500, detail=str(e))
        
    # 5. Save results
    classification_data = {
        "classified_at": datetime.now().isoformat() + "Z",
        "total_items": class_res.total_items,
        "items": [item.model_dump() for item in class_res.items],
        "summary": {
            "by_precedent": class_res.classified_by_precedent,
            "by_rule": class_res.classified_by_rule,
            "by_ai": class_res.classified_by_ai,
            "uncertain": class_res.unclassified
        }
    }
    
    db.table("cma_projects").update({"classification_data": classification_data}).eq("id", project_id).execute()
    
    # 6. Populate review queue
    items_to_review = populate_review_queue(project_id, str(current_user.firm_id), class_res.items, entity_type)
    
    # 7. Update status
    if items_to_review == 0:
        db.table("cma_projects").update({
            "status": "validated",  # skipping review
            "pipeline_progress": 60
        }).eq("id", project_id).execute()
        final_status = "validated"
    else:
        db.table("cma_projects").update({
            "status": "reviewing",
            "pipeline_progress": 50
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
            "uncertain": class_res.unclassified
        },
        "review_queue_items": items_to_review,
        "llm_cost_usd": class_res.llm_cost_usd,
        "llm_tokens_used": class_res.llm_tokens_used,
        "duration_ms": duration_ms,
        "project_status": final_status
    })

@router.get("/{project_id}/classification", response_model=StandardResponse[dict])
def get_project_classification(project_id: str, current_user: CurrentUser = Depends(get_current_user)):
    db = get_supabase()
    res = db.table("cma_projects").select("classification_data").eq("id", project_id).eq("firm_id", str(current_user.firm_id)).execute()
    
    if not res.data:
        raise HTTPException(status_code=404, detail="Project not found")
        
    class_data = res.data[0].get("classification_data", {})
    
    summary = get_review_summary(project_id)
    class_data["review_queue_summary"] = summary
    
    return StandardResponse(data=class_data)
