from fastapi import APIRouter, Depends, HTTPException
from app.core.auth import get_current_user
from app.models.user import CurrentUser
from app.models.response import StandardResponse
from app.db.supabase_client import get_supabase
from datetime import datetime

router = APIRouter()

@router.get("/stats", response_model=StandardResponse[dict])
def get_dashboard_stats(current_user: CurrentUser = Depends(get_current_user)):
    db = get_supabase()
    firm_id = str(current_user.firm_id)
    
    # 1. total_clients & active_clients
    clients_res = db.table("clients").select("is_active").eq("firm_id", firm_id).execute()
    total_clients = len(clients_res.data) if clients_res.data else 0
    active_clients = sum(1 for c in clients_res.data if c.get("is_active")) if clients_res.data else 0
    
    # 2. total_projects & projects_by_status
    projects_res = db.table("cma_projects").select("id, status, created_at, updated_at").eq("firm_id", firm_id).execute()
    total_projects = len(projects_res.data) if projects_res.data else 0
    
    projects_by_status = {
        "draft": 0, "extracting": 0, "classifying": 0, "reviewing": 0,
        "validating": 0, "generating": 0, "completed": 0, "error": 0
    }
    
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    this_month_created = 0
    this_month_completed = 0
    
    if projects_res.data:
        for p in projects_res.data:
            s = p.get("status")
            if s in projects_by_status:
                projects_by_status[s] += 1
                
            # 'created_at' and 'updated_at' processing
            # Dates from supabase come as ISO-8601 strings (e.g. "2026-02-25T15:30:00Z")
            created_str = p.get("created_at")
            if created_str:
                try:
                     # basic parsing considering it might end in Z or +00:00
                     dt = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
                     if dt.month == current_month and dt.year == current_year:
                         this_month_created += 1
                except Exception:
                     pass
                     
            if s == "completed":
                updated_str = p.get("updated_at")
                if updated_str:
                    try:
                         dt = datetime.fromisoformat(updated_str.replace("Z", "+00:00"))
                         if dt.month == current_month and dt.year == current_year:
                             this_month_completed += 1
                    except Exception:
                         pass
    
    # 5. pending_reviews
    reviews_res = db.table("review_queue").select("id").eq("firm_id", firm_id).eq("status", "pending").execute()
    pending_reviews = len(reviews_res.data) if reviews_res.data else 0
    
    # 7. llm_usage
    llm_res = db.table("llm_usage_log").select("cost_usd, input_tokens, output_tokens, created_at").eq("firm_id", firm_id).execute()
    total_cost = 0.0
    total_tokens = 0
    this_month_cost = 0.0
    
    if llm_res.data:
        for log in llm_res.data:
             c = float(log.get("cost_usd", 0))
             t = int(log.get("input_tokens", 0)) + int(log.get("output_tokens", 0))
             total_cost += c
             total_tokens += t
             
             created_str = log.get("created_at")
             if created_str:
                 try:
                      dt = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
                      if dt.month == current_month and dt.year == current_year:
                          this_month_cost += c
                 except Exception:
                      pass
                      
    # 8. recent_projects
    recent_projects_res = db.table("cma_projects").select(
        "id, financial_year, status, updated_at, clients(name)"
    ).eq("firm_id", firm_id).order("updated_at", desc=True).limit(5).execute()
    
    recent_projects = []
    if recent_projects_res.data:
        for p in recent_projects_res.data:
             c = p.pop("clients", {})
             if isinstance(c, list) and len(c) > 0: c = c[0]
             client_name = c.get("name", "Unknown") if isinstance(c, dict) else "Unknown"
             recent_projects.append({
                 "id": p["id"],
                 "client_name": client_name,
                 "financial_year": p["financial_year"],
                 "status": p["status"],
                 "updated_at": p["updated_at"]
             })
             
    stats_data = {
        "total_clients": total_clients,
        "active_clients": active_clients,
        "total_projects": total_projects,
        "projects_by_status": projects_by_status,
        "pending_reviews": pending_reviews,
        "this_month": {
            "projects_created": this_month_created,
            "projects_completed": this_month_completed
        },
        "llm_usage": {
            "total_cost_usd": round(total_cost, 4),
            "total_tokens": total_tokens,
            "this_month_cost_usd": round(this_month_cost, 4)
        },
        "recent_projects": recent_projects
    }
    
    return StandardResponse(data=stats_data)
