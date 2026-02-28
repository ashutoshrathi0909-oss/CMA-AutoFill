import logging
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from app.core.auth import get_current_user
from app.models.user import CurrentUser
from app.models.response import StandardResponse
from app.db.supabase_client import get_supabase
from app.services.classification.rules_loader import get_all_rules
from app.services.classification.precedent_matcher import create_precedent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/review-queue")


class ResolveAction(BaseModel):
    action: str
    target_row: Optional[int] = None
    target_sheet: Optional[str] = None
    notes: Optional[str] = None


class ResolveItem(ResolveAction):
    id: str


class BulkResolveAction(BaseModel):
    resolutions: List[ResolveItem]


class ApproveAllRequest(BaseModel):
    project_id: str
    min_confidence: float = 0.50


@router.get("", response_model=StandardResponse[dict])
async def list_review_queue(
    status: str = Query("pending", description="pending, resolved, skipped, or all"),
    project_id: Optional[str] = None,
    sort_by: str = Query("confidence", description="confidence or created_at"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: CurrentUser = Depends(get_current_user),
):
    db = get_supabase()

    query = (
        db.table("review_queue")
        .select("*, cma_projects!inner(client_id)", count="exact")
        .eq("firm_id", str(current_user.firm_id))
    )

    if status != "all":
        query = query.eq("status", status)
    if project_id:
        query = query.eq("cma_project_id", project_id)

    if sort_by == "confidence":
        query = query.order("confidence", desc=False)
    else:
        query = query.order("created_at", desc=True)

    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page - 1

    res = query.range(start_idx, end_idx).execute()

    items = res.data
    total = res.count if res.count is not None else len(items)

    # Compute summary
    summary_query = (
        db.table("review_queue")
        .select("status", count="exact")
        .eq("firm_id", str(current_user.firm_id))
    )
    if project_id:
        summary_query = summary_query.eq("cma_project_id", project_id)

    all_res = summary_query.execute()

    summary = {"pending": 0, "resolved": 0, "skipped": 0}
    for row in all_res.data:
        s = row.get("status")
        if s in summary:
            summary[s] += 1

    # Resolve project/client names
    proj_ids = list(set([item["cma_project_id"] for item in items]))
    projects_info = {}
    if proj_ids:
        p_res = db.table("cma_projects").select("id, client_id, clients(name)").in_("id", proj_ids).execute()
        for p in p_res.data:
            projects_info[p["id"]] = {
                "client_name": p.get("clients", {}).get("name", "Unknown") if p.get("clients") else "Unknown",
            }

    for item in items:
        item["project_name"] = "Project Data"
        item["client_name"] = projects_info.get(item["cma_project_id"], {}).get("client_name", "Unknown")

    return StandardResponse(data={
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "summary": summary,
    })


@router.get("/{item_id}", response_model=StandardResponse[dict])
async def get_review_item(
    item_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    db = get_supabase()
    res = (
        db.table("review_queue")
        .select("*")
        .eq("id", item_id)
        .eq("firm_id", str(current_user.firm_id))
        .execute()
    )

    if not res.data:
        raise HTTPException(status_code=404, detail="Review item not found")

    item = res.data[0]

    p_res = db.table("cma_projects").select("client_id, clients(name, entity_type)").eq("id", item["cma_project_id"]).execute()
    if p_res.data:
        item["client_name"] = p_res.data[0].get("clients", {}).get("name", "Unknown") if p_res.data[0].get("clients") else "Unknown"
        item["entity_type"] = p_res.data[0].get("clients", {}).get("entity_type", "trading") if p_res.data[0].get("clients") else "trading"
    else:
        item["client_name"] = "Unknown"
        item["entity_type"] = "trading"

    return StandardResponse(data=item)


@router.post("/{item_id}/resolve", response_model=StandardResponse[dict])
async def resolve_review_item(
    item_id: str,
    payload: ResolveAction,
    current_user: CurrentUser = Depends(get_current_user),
):
    db = get_supabase()
    res = (
        db.table("review_queue")
        .select("*, cma_projects!inner(client_id)")
        .eq("id", item_id)
        .eq("firm_id", str(current_user.firm_id))
        .execute()
    )

    if not res.data:
        raise HTTPException(status_code=404, detail="Review item not found")

    item = res.data[0]

    if item["status"] != "pending":
        raise HTTPException(status_code=409, detail="Item is already resolved or skipped")

    if payload.action in ["approve", "correct"] and (payload.target_row is None or payload.target_sheet is None):
        if payload.action == "approve":
            payload.target_row = item["suggested_row"]
            payload.target_sheet = item["suggested_sheet"]
        else:
            raise HTTPException(status_code=422, detail="target_row and target_sheet are required for correct")

    # Get client entity_type
    client_res = db.table("clients").select("entity_type").eq("id", item["cma_projects"]["client_id"]).execute()
    entity_type = client_res.data[0]["entity_type"] if client_res.data else "trading"

    resolved_row = payload.target_row if payload.action == "correct" else item["suggested_row"]
    resolved_sheet = payload.target_sheet if payload.action == "correct" else item["suggested_sheet"]

    if payload.action == "approve":
        resolved_row = item["suggested_row"]
        resolved_sheet = item["suggested_sheet"]

    prec_id = None
    prec_created = False

    if payload.action in ["approve", "correct"]:
        try:
            prec = create_precedent(
                firm_id=str(current_user.firm_id),
                source_term=item["source_item_name"],
                target_row=resolved_row,
                target_sheet=resolved_sheet,
                entity_type=entity_type,
                scope="firm",
                project_id=item["cma_project_id"],
                user_id=str(current_user.id),
            )
            prec_id = prec["id"] if isinstance(prec, dict) and "id" in prec else getattr(prec, "id", None)
            prec_created = True
        except Exception as e:
            logger.error("Failed to create precedent for item %s: %s", item_id, e)

    status_val = "resolved" if payload.action in ["approve", "correct"] else "skipped"

    update_payload = {
        "status": status_val,
        "resolved_by": str(current_user.id),
        "resolved_at": datetime.now().isoformat() + "Z",
    }

    if payload.action in ["approve", "correct"]:
        update_payload["resolved_row"] = resolved_row
        update_payload["resolved_sheet"] = resolved_sheet

    db.table("review_queue").update(update_payload).eq("id", item_id).eq("firm_id", str(current_user.firm_id)).execute()

    remaining = (
        db.table("review_queue")
        .select("id", count="exact")
        .eq("cma_project_id", item["cma_project_id"])
        .eq("firm_id", str(current_user.firm_id))
        .eq("status", "pending")
        .execute()
    )

    return StandardResponse(data={
        "review_item_id": item_id,
        "status": status_val,
        "resolved_row": resolved_row if payload.action != "skip" else None,
        "resolved_sheet": resolved_sheet if payload.action != "skip" else None,
        "precedent_created": prec_created,
        "precedent_id": prec_id,
        "remaining_pending": remaining.count if remaining.count is not None else 0,
    })


@router.post("/bulk-resolve", response_model=StandardResponse[dict])
async def bulk_resolve(
    payload: BulkResolveAction,
    current_user: CurrentUser = Depends(get_current_user),
):
    resolved = 0
    skipped = 0
    prec_created = 0
    errors = []

    for r in payload.resolutions:
        try:
            res = await resolve_review_item(
                r.id,
                ResolveAction(action=r.action, target_row=r.target_row, target_sheet=r.target_sheet, notes=r.notes),
                current_user,
            )
            if res.data["status"] == "resolved":
                resolved += 1
                if res.data["precedent_created"]:
                    prec_created += 1
            else:
                skipped += 1
        except Exception as e:
            errors.append({"id": r.id, "error": str(e)})

    return StandardResponse(data={
        "total": len(payload.resolutions),
        "resolved": resolved,
        "skipped": skipped,
        "precedents_created": prec_created,
        "errors": errors,
    })


@router.post("/approve-all", response_model=StandardResponse[dict])
async def approve_all(
    payload: ApproveAllRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    db = get_supabase()
    res = (
        db.table("review_queue")
        .select("id, suggested_row, suggested_sheet")
        .eq("cma_project_id", payload.project_id)
        .eq("firm_id", str(current_user.firm_id))
        .eq("status", "pending")
        .gte("confidence", payload.min_confidence)
        .execute()
    )

    resolutions = []
    for row in res.data:
        resolutions.append(ResolveItem(
            id=row["id"],
            action="approve",
            target_row=row["suggested_row"],
            target_sheet=row["suggested_sheet"],
        ))

    bulk_res = await bulk_resolve(BulkResolveAction(resolutions=resolutions), current_user)
    return bulk_res


@router.get("/config/cma-rows", response_model=StandardResponse[dict])
async def get_cma_rows(
    entity_type: Optional[str] = None,
    current_user: CurrentUser = Depends(get_current_user),
):
    rules = get_all_rules()

    grouped = {}
    for r in rules:
        if entity_type and entity_type not in r.entity_types and r.entity_types:
            continue

        sheet = r.target_sheet
        if sheet not in grouped:
            grouped[sheet] = []

        existing = [x for x in grouped[sheet] if x["row"] == r.target_row]
        if not existing:
            grouped[sheet].append({
                "row": r.target_row,
                "label": r.target_label,
            })

    for sheet in grouped:
        grouped[sheet].sort(key=lambda x: x["row"])

    return StandardResponse(data=grouped)
