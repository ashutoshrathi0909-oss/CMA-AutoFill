from typing import Dict, Any, List
from app.db.supabase_client import get_supabase
from pydantic import BaseModel

class ApplyResult(BaseModel):
    items_updated: int
    items_still_pending: int
    project_status: str
    ready_to_generate: bool
    message: str

def apply_review_decisions(project_id: str, firm_id: str) -> ApplyResult:
    db = get_supabase()
    
    # 1. Load project classification data
    proj_res = db.table("cma_projects").select("classification_data").eq("id", project_id).eq("firm_id", firm_id).execute()
    if not proj_res.data:
        raise ValueError("Project not found")
        
    class_data = proj_res.data[0].get("classification_data") or {"items": []}
    items: List[Dict[str, Any]] = class_data.get("items", [])
    
    # 2. Get resolved reviews
    reviews_res = db.table("review_queue").select("source_item_name, source_item_amount, resolved_row, resolved_sheet").eq("cma_project_id", project_id).eq("status", "resolved").execute()
    resolved_reviews = reviews_res.data
    
    # Map them for quick lookup
    resolved_map = {}
    for r in resolved_reviews:
        # composite key: name + amount
        key = f"{r['source_item_name']}_{r['source_item_amount']}"
        resolved_map[key] = {
            "row": r["resolved_row"],
            "sheet": r["resolved_sheet"]
        }
        
    # 3. Apply to items
    updated_count = 0
    for itm in items:
        # Match using same logic
        key = f"{itm.get('item_name')}_{itm.get('item_amount', 0.0)}"
        if key in resolved_map:
            # Update target
            change = resolved_map[key]
            itm["target_row"] = change["row"]
            itm["target_sheet"] = change["sheet"]
            itm["confidence"] = 1.0
            itm["source"] = "ca_reviewed"
            itm["needs_review"] = False
            updated_count += 1
            
    # Save back
    db.table("cma_projects").update({"classification_data": class_data}).eq("id", project_id).execute()
    
    # 5. Check pending remaining
    pending_res = db.table("review_queue").select("id", count="exact").eq("cma_project_id", project_id).eq("status", "pending").execute()
    pending_count = pending_res.count if pending_res.count is not None else 0
    
    status = "validated" if pending_count == 0 else "reviewing"
    progress = 60 if pending_count == 0 else 50
    
    db.table("cma_projects").update({
        "status": status,
        "pipeline_progress": progress
    }).eq("id", project_id).execute()
    
    return ApplyResult(
        items_updated=updated_count,
        items_still_pending=pending_count,
        project_status=status,
        ready_to_generate=(pending_count == 0),
        message=f"{updated_count} items updated. {pending_count} items still need review."
    )
