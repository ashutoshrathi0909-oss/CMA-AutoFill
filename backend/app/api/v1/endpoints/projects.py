from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional
from app.core.auth import get_current_user
from app.models.user import CurrentUser
from app.models.project import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse
from app.models.response import StandardResponse
from app.db.supabase_client import get_supabase
import uuid

router = APIRouter()

@router.post("", response_model=StandardResponse[ProjectResponse], status_code=201)
def create_project(project_in: ProjectCreate, current_user: CurrentUser = Depends(get_current_user)):
    db = get_supabase()
    
    # 1. validate client belongs to firm
    client_resp = db.table("clients").select("id, name, entity_type").eq("id", str(project_in.client_id)).eq("firm_id", str(current_user.firm_id)).execute()
    if not client_resp.data:
        raise HTTPException(status_code=404, detail="Client not found or does not belong to your firm")
        
    client_data = client_resp.data[0]
        
    # 2. check unique constraint
    exist_resp = db.table("cma_projects").select("id").eq("client_id", str(project_in.client_id)).eq("financial_year", project_in.financial_year).execute()
    if exist_resp.data:
        raise HTTPException(status_code=409, detail="A CMA project for this client and financial year already exists")
        
    proj_data = project_in.model_dump(exclude_unset=True)
    proj_data["firm_id"] = str(current_user.firm_id)
    proj_data["created_by"] = str(current_user.id)
    proj_data["client_id"] = str(proj_data["client_id"])
    
    response = db.table("cma_projects").insert(proj_data).execute()
    if not response.data:
        raise HTTPException(status_code=500, detail="Failed to create project")
        
    created_project = response.data[0]
    created_project["client_name"] = client_data["name"]
    created_project["client_entity_type"] = client_data["entity_type"]
    created_project["uploaded_file_count"] = 0
    created_project["review_pending_count"] = 0
    
    # audit
    db.table("audit_log").insert({
        "firm_id": str(current_user.firm_id),
        "user_id": str(current_user.id),
        "action": "create_project",
        "entity_type": "cma_project",
        "entity_id": created_project["id"],
        "metadata": {"client_name": client_data["name"], "financial_year": project_in.financial_year}
    }).execute()
    
    return StandardResponse(data=ProjectResponse(**created_project))

@router.get("", response_model=StandardResponse[ProjectListResponse])
def list_projects(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    client_id: Optional[str] = None,
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    current_user: CurrentUser = Depends(get_current_user)
):
    db = get_supabase()
    query = db.table("cma_projects").select("*, clients!inner(name, entity_type)", count="exact").eq("firm_id", str(current_user.firm_id))
    
    if status:
        query = query.eq("status", status)
    if client_id:
        query = query.eq("client_id", client_id)
        
    start = (page - 1) * per_page
    end = start + per_page - 1
    
    query = query.order(sort_by, desc=(sort_order == "desc"))
    response = query.range(start, end).execute()
    
    total_count = response.count if response.count is not None else 0
    projects = response.data
    
    for p in projects:
        c = p.pop("clients", {})
        if isinstance(c, list) and len(c) > 0: c = c[0]
        p["client_name"] = c.get("name", "Unknown") if isinstance(c, dict) else "Unknown"
        p["client_entity_type"] = c.get("entity_type", "Unknown") if isinstance(c, dict) else "Unknown"
        p["uploaded_file_count"] = 0 # optimize later if needed
        p["review_pending_count"] = 0 # optimize later if needed
        
    return StandardResponse(data=ProjectListResponse(
        items=[ProjectResponse(**p) for p in projects],
        total=total_count,
        page=page,
        per_page=per_page
    ))

@router.get("/{project_id}", response_model=StandardResponse[ProjectResponse])
def get_project(project_id: str, current_user: CurrentUser = Depends(get_current_user)):
    db = get_supabase()
    response = db.table("cma_projects").select("*, clients(name, entity_type)").eq("id", project_id).eq("firm_id", str(current_user.firm_id)).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Project not found")
        
    p = response.data[0]
    c = p.pop("clients", {})
    if isinstance(c, list) and len(c) > 0: c = c[0]
    p["client_name"] = c.get("name", "Unknown") if isinstance(c, dict) else "Unknown"
    p["client_entity_type"] = c.get("entity_type", "Unknown") if isinstance(c, dict) else "Unknown"
    
    # counts
    files_resp = db.table("uploaded_files").select("id", count="exact").eq("cma_project_id", project_id).execute()
    p["uploaded_file_count"] = files_resp.count if files_resp.count is not None else 0
    
    review_resp = db.table("review_queue").select("id", count="exact").eq("cma_project_id", project_id).eq("status", "pending").execute()
    p["review_pending_count"] = review_resp.count if review_resp.count is not None else 0
    
    return StandardResponse(data=ProjectResponse(**p))

@router.put("/{project_id}", response_model=StandardResponse[ProjectResponse])
def update_project(project_id: str, project_in: ProjectUpdate, current_user: CurrentUser = Depends(get_current_user)):
    db = get_supabase()
    check_resp = db.table("cma_projects").select("id, status").eq("id", project_id).eq("firm_id", str(current_user.firm_id)).execute()
    if not check_resp.data:
        raise HTTPException(status_code=404, detail="Project not found")
        
    if check_resp.data[0]["status"] != "draft":
        raise HTTPException(status_code=409, detail=f"Cannot modify project in '{check_resp.data[0]['status']}' status")
        
    update_data = project_in.model_dump(exclude_unset=True)
    if not update_data:
        return get_project(project_id, current_user)
        
    db.table("cma_projects").update(update_data).eq("id", project_id).eq("firm_id", str(current_user.firm_id)).execute()
    
    db.table("audit_log").insert({
        "firm_id": str(current_user.firm_id),
        "user_id": str(current_user.id),
        "action": "update_project",
        "entity_type": "cma_project",
        "entity_id": project_id,
        "metadata": {"updated_fields": list(update_data.keys())}
    }).execute()
    
    return get_project(project_id, current_user)

@router.delete("/{project_id}", response_model=StandardResponse[dict])
def delete_project(project_id: str, current_user: CurrentUser = Depends(get_current_user)):
    db = get_supabase()
    check_resp = db.table("cma_projects").select("id, status").eq("id", project_id).eq("firm_id", str(current_user.firm_id)).execute()
    if not check_resp.data:
        raise HTTPException(status_code=404, detail="Project not found")
        
    if check_resp.data[0]["status"] != "draft":
        raise HTTPException(status_code=409, detail=f"Cannot delete project in '{check_resp.data[0]['status']}' status")
        
    db.table("cma_projects").delete().eq("id", project_id).eq("firm_id", str(current_user.firm_id)).execute()
    
    db.table("audit_log").insert({
        "firm_id": str(current_user.firm_id),
        "user_id": str(current_user.id),
        "action": "delete_project",
        "entity_type": "cma_project",
        "entity_id": project_id,
        "metadata": {}
    }).execute()
    
    return StandardResponse(data={"success": True, "message": "Project deleted successfully"})
