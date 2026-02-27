from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional
from app.core.auth import get_current_user
from app.models.user import CurrentUser
from app.models.client import ClientCreate, ClientUpdate, ClientResponse, ClientListResponse
from app.models.response import StandardResponse
from app.db.supabase_client import get_supabase

router = APIRouter()

@router.post("", response_model=StandardResponse[ClientResponse], status_code=201)
def create_client(client_in: ClientCreate, current_user: CurrentUser = Depends(get_current_user)):
    db = get_supabase()
    client_data = client_in.model_dump(exclude_unset=True)
    client_data["firm_id"] = str(current_user.firm_id)
    
    response = db.table("clients").insert(client_data).execute()
    if not response.data:
        raise HTTPException(status_code=500, detail="Failed to create client")
    
    created_client = response.data[0]
    created_client["cma_count"] = 0
    
    # Audit log
    db.table("audit_log").insert({
        "firm_id": str(current_user.firm_id),
        "user_id": str(current_user.id),
        "action": "create_client",
        "entity_type": "client",
        "entity_id": created_client["id"],
        "metadata": {"client_name": created_client["name"]}
    }).execute()
    
    return StandardResponse(data=ClientResponse(**created_client))

@router.get("", response_model=StandardResponse[ClientListResponse])
def list_clients(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    entity_type: Optional[str] = None,
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    include_inactive: bool = Query(False),
    current_user: CurrentUser = Depends(get_current_user)
):
    db = get_supabase()
    query = db.table("clients").select("*", count="exact").eq("firm_id", str(current_user.firm_id))
    
    if search:
        safe_search = search.replace("%", "\\%").replace("_", "\\_")
        query = query.ilike("name", f"%{safe_search}%")
    if entity_type:
        query = query.eq("entity_type", entity_type)
    if not include_inactive:
        query = query.eq("is_active", True)
        
    start = (page - 1) * per_page
    end = start + per_page - 1
    
    query = query.order(sort_by, desc=(sort_order == "desc"))
    response = query.range(start, end).execute()
    
    total_count = response.count if response.count is not None else 0
    clients = response.data
    
    client_ids = [c["id"] for c in clients]
    cma_counts_map = {cid: 0 for cid in client_ids}
    
    if client_ids:
        cma_resp = db.table("cma_projects").select("client_id").in_("client_id", client_ids).execute()
        for p in cma_resp.data:
            cma_counts_map[p["client_id"]] = cma_counts_map.get(p["client_id"], 0) + 1
            
    for c in clients:
        c["cma_count"] = cma_counts_map.get(c["id"], 0)
        
    return StandardResponse(data=ClientListResponse(
        items=[ClientResponse(**c) for c in clients],
        total=total_count,
        page=page,
        per_page=per_page
    ))

@router.get("/{client_id}", response_model=StandardResponse[ClientResponse])
def get_client(client_id: str, current_user: CurrentUser = Depends(get_current_user)):
    db = get_supabase()
    response = db.table("clients").select("*").eq("id", client_id).eq("firm_id", str(current_user.firm_id)).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Client not found")
        
    client_data = response.data[0]
    cma_resp = db.table("cma_projects").select("*", count="exact").eq("client_id", client_id).execute()
    client_data["cma_count"] = cma_resp.count if cma_resp.count is not None else 0
    
    return StandardResponse(data=ClientResponse(**client_data))

@router.put("/{client_id}", response_model=StandardResponse[ClientResponse])
def update_client(client_id: str, client_in: ClientUpdate, current_user: CurrentUser = Depends(get_current_user)):
    db = get_supabase()
    check_resp = db.table("clients").select("id, name").eq("id", client_id).eq("firm_id", str(current_user.firm_id)).execute()
    if not check_resp.data:
        raise HTTPException(status_code=404, detail="Client not found")
        
    update_data = client_in.model_dump(exclude_unset=True)
    if not update_data:
        return get_client(client_id, current_user)
        
    response = db.table("clients").update(update_data).eq("id", client_id).eq("firm_id", str(current_user.firm_id)).execute()
    if not response.data:
        raise HTTPException(status_code=500, detail="Failed to update client")
        
    db.table("audit_log").insert({
        "firm_id": str(current_user.firm_id),
        "user_id": str(current_user.id),
        "action": "update_client",
        "entity_type": "client",
        "entity_id": client_id,
        "metadata": {"client_name": check_resp.data[0]["name"]}
    }).execute()
        
    return get_client(client_id, current_user)

@router.delete("/{client_id}", response_model=StandardResponse[dict])
def delete_client(client_id: str, current_user: CurrentUser = Depends(get_current_user)):
    db = get_supabase()
    check_resp = db.table("clients").select("id, name").eq("id", client_id).eq("firm_id", str(current_user.firm_id)).execute()
    if not check_resp.data:
        raise HTTPException(status_code=404, detail="Client not found")
        
    db.table("clients").update({"is_active": False}).eq("id", client_id).eq("firm_id", str(current_user.firm_id)).execute()
    
    db.table("audit_log").insert({
        "firm_id": str(current_user.firm_id),
        "user_id": str(current_user.id),
        "action": "delete_client",
        "entity_type": "client",
        "entity_id": client_id,
        "metadata": {"client_name": check_resp.data[0]["name"]}
    }).execute()
        
    return StandardResponse(data={"success": True, "message": "Client deleted successfully"})
