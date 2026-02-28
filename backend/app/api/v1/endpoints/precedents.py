from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.core.auth import get_current_user
from app.models.user import CurrentUser
from app.models.response import StandardResponse
from app.db.supabase_client import get_supabase
from datetime import datetime

router = APIRouter(prefix="/precedents")

class PrecedentUpdate(BaseModel):
    target_row: Optional[int] = None
    target_sheet: Optional[str] = None
    notes: Optional[str] = None

class PromotePrecedent(BaseModel):
    precedent_id: str
    scope: str = "global"

@router.get("", response_model=StandardResponse[dict])
def list_precedents(
    entity_type: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    current_user: CurrentUser = Depends(get_current_user)
):
    db = get_supabase()
    
    query = db.table("classification_precedents").select("*", count="exact").eq("firm_id", str(current_user.firm_id)).eq("is_active", True)
    
    if entity_type:
        query = query.eq("entity_type", entity_type)
        
    if search:
        query = query.ilike("source_term", f"%{search}%")
        
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page - 1
    
    query = query.order("created_at", desc=True)
    res = query.range(start_idx, end_idx).execute()
    
    items = res.data
    total = res.count if res.count is not None else len(items)
    
    return StandardResponse(data={
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page
    })

@router.get("/{prec_id}", response_model=StandardResponse[dict])
def get_precedent(prec_id: str, current_user: CurrentUser = Depends(get_current_user)):
    db = get_supabase()
    
    res = db.table("classification_precedents").select("*").eq("id", prec_id).eq("firm_id", str(current_user.firm_id)).eq("is_active", True).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Precedent not found")
        
    # We could simulate usage_history by grabbing reviews resolved via this, but standard schema hasn't tracked direct FK usage.
    # Safe fallback
    prec = res.data[0]
    prec["usage_history"] = []
    
    return StandardResponse(data=prec)
    
@router.put("/{prec_id}", response_model=StandardResponse[dict])
def update_precedent(prec_id: str, payload: PrecedentUpdate, current_user: CurrentUser = Depends(get_current_user)):
    db = get_supabase()
    
    res = db.table("classification_precedents").select("id").eq("id", prec_id).eq("firm_id", str(current_user.firm_id)).eq("is_active", True).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Precedent not found")
        
    update_data = {}
    if payload.target_row is not None: update_data["target_row"] = payload.target_row
    if payload.target_sheet is not None: update_data["target_sheet"] = payload.target_sheet
    
    if not update_data:
        raise HTTPException(status_code=400, detail="Nothing to update")
        
    up_res = db.table("classification_precedents").update(update_data).eq("id", prec_id).execute()
    
    # Audit log simulation
    # db.table("audit_log").insert({"action": "update_precedent", "user_id": ..., "details": ...}).execute()
    
    val = up_res.data[0] if up_res.data else update_data
    return StandardResponse(data=val)

@router.delete("/{prec_id}", response_model=StandardResponse[dict])
def delete_precedent(prec_id: str, current_user: CurrentUser = Depends(get_current_user)):
    db = get_supabase()
    
    res = db.table("classification_precedents").select("id").eq("id", prec_id).eq("firm_id", str(current_user.firm_id)).eq("is_active", True).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Precedent not found")
        
    # Soft delete if column exists, hard delete otherwise. We'll try soft delete.
    try:
        db.table("classification_precedents").update({"is_active": False}).eq("id", prec_id).execute()
    except Exception:
        # DB schema might not have is_active, hard delete
        db.table("classification_precedents").delete().eq("id", prec_id).execute()
    
    return StandardResponse(data={"deleted": True, "id": prec_id})

@router.post("/promote", response_model=StandardResponse[dict])
def promote_precedent(payload: PromotePrecedent, current_user: CurrentUser = Depends(get_current_user)):
    if current_user.role != "owner":
        raise HTTPException(status_code=403, detail="Only owners can promote precedents to global scope")
        
    db = get_supabase()
    res = db.table("classification_precedents").select("id").eq("id", payload.precedent_id).eq("firm_id", str(current_user.firm_id)).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Precedent not found")
        
    up_res = db.table("classification_precedents").update({"scope": "global", "firm_id": None}).eq("id", payload.precedent_id).execute()
    
    return StandardResponse(data={"promoted": True, "id": payload.precedent_id})
