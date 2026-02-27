from fastapi import APIRouter, Depends
from app.core.auth import get_current_user
from app.models.user import CurrentUser
from app.models.response import StandardResponse
from app.db.supabase_client import get_supabase
from datetime import datetime

router = APIRouter()

ALL_STATUSES = ["draft", "extracting", "classifying", "reviewing", "validating", "generating", "completed", "error"]


@router.get("/stats", response_model=StandardResponse[dict])
def get_dashboard_stats(current_user: CurrentUser = Depends(get_current_user)):
    db = get_supabase()
    firm_id = str(current_user.firm_id)

    now = datetime.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()

    # 1. Client counts — use DB-level count instead of fetching all rows
    total_clients_res = db.table("clients").select("id", count="exact").eq("firm_id", firm_id).execute()
    total_clients = total_clients_res.count or 0

    active_clients_res = db.table("clients").select("id", count="exact").eq("firm_id", firm_id).eq("is_active", True).execute()
    active_clients = active_clients_res.count or 0

    # 2. Total projects — DB-level count
    total_projects_res = db.table("cma_projects").select("id", count="exact").eq("firm_id", firm_id).execute()
    total_projects = total_projects_res.count or 0

    # 3. Projects by status — one count query per status
    projects_by_status: dict[str, int] = {}
    for status_val in ALL_STATUSES:
        res = db.table("cma_projects").select("id", count="exact").eq("firm_id", firm_id).eq("status", status_val).execute()
        projects_by_status[status_val] = res.count or 0

    # 4. Pending reviews — DB-level count
    reviews_res = db.table("review_queue").select("id", count="exact").eq("firm_id", firm_id).eq("status", "pending").execute()
    pending_reviews = reviews_res.count or 0

    # 5. This month stats — DB-level count with date filter
    this_month_created_res = db.table("cma_projects").select("id", count="exact").eq("firm_id", firm_id).gte("created_at", month_start).execute()
    this_month_created = this_month_created_res.count or 0

    this_month_completed_res = (
        db.table("cma_projects")
        .select("id", count="exact")
        .eq("firm_id", firm_id)
        .eq("status", "completed")
        .gte("updated_at", month_start)
        .execute()
    )
    this_month_completed = this_month_completed_res.count or 0

    # 6. LLM usage — fetch only aggregation-needed columns, use DB count for month filter
    # For totals we still need to sum, but select only the minimal columns
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
                    if dt.month == now.month and dt.year == now.year:
                        this_month_cost += c
                except Exception:
                    pass

    # 7. Recent projects — limited to 5 at DB level
    recent_projects_res = db.table("cma_projects").select(
        "id, financial_year, status, updated_at, clients(name)"
    ).eq("firm_id", firm_id).order("updated_at", desc=True).limit(5).execute()

    recent_projects = []
    if recent_projects_res.data:
        for p in recent_projects_res.data:
            c = p.pop("clients", {})
            if isinstance(c, list) and len(c) > 0:
                c = c[0]
            client_name = c.get("name", "Unknown") if isinstance(c, dict) else "Unknown"
            recent_projects.append({
                "id": p["id"],
                "client_name": client_name,
                "financial_year": p["financial_year"],
                "status": p["status"],
                "updated_at": p["updated_at"],
            })

    stats_data = {
        "total_clients": total_clients,
        "active_clients": active_clients,
        "total_projects": total_projects,
        "projects_by_status": projects_by_status,
        "pending_reviews": pending_reviews,
        "this_month": {
            "projects_created": this_month_created,
            "projects_completed": this_month_completed,
        },
        "llm_usage": {
            "total_cost_usd": round(total_cost, 4),
            "total_tokens": total_tokens,
            "this_month_cost_usd": round(this_month_cost, 4),
        },
        "recent_projects": recent_projects,
    }

    return StandardResponse(data=stats_data)
