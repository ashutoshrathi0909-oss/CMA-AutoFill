"""
Task 8.3 / 8.5: Pipeline API endpoints.

• GET  /projects/{id}/progress     — real-time progress polling
• POST /projects/{id}/process      — one-click pipeline start
• POST /projects/{id}/retry        — resume from failed step
• POST /projects/{id}/resume       — resume after CA review
"""

import logging
from typing import Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from pydantic import BaseModel

from app.core.auth import get_current_user
from app.core.security import limiter
from app.db.supabase_client import get_supabase
from app.models.response import StandardResponse
from app.models.user import CurrentUser
from app.services.pipeline.background import is_project_processing, run_pipeline_background
from app.services.pipeline.orchestrator import PipelineOptions

logger = logging.getLogger(__name__)
router = APIRouter()

# Rough per-step time estimates (seconds) for progress UI
_STEP_ESTIMATES = {"extract": 5, "classify": 8, "review": 1, "validate": 1, "generate": 2}


# ── Request / Response models ─────────────────────────────────────────────
class ProcessRequest(BaseModel):
    skip_review: bool = False
    skip_validation: bool = False
    auto_approve_above: float = 0.70
    notify_on_review: bool = True
    force_reprocess: bool = False


class RetryRequest(BaseModel):
    from_step: Optional[str] = None


# ── GET progress ──────────────────────────────────────────────────────────
@router.get("/{project_id}/progress", response_model=StandardResponse[dict])
def get_pipeline_progress(project_id: str, current_user: CurrentUser = Depends(get_current_user)):
    db = get_supabase()
    res = (
        db.table("cma_projects")
        .select("status, pipeline_progress, pipeline_steps, is_processing, error_message")
        .eq("id", project_id)
        .eq("firm_id", str(current_user.firm_id))
        .execute()
    )
    if not res.data:
        raise HTTPException(status_code=404, detail="Project not found")

    project = res.data[0]
    steps_meta: dict = project.get("pipeline_steps") or {}

    # Build steps array for the frontend
    steps_list: List[Dict] = []
    for s_name in ["extract", "classify", "review", "validate", "generate"]:
        entry = steps_meta.get(s_name, {})
        steps_list.append({
            "name": s_name,
            "status": entry.get("status", "pending"),
            "started_at": entry.get("started_at"),
            "completed_at": entry.get("completed_at"),
            "duration_ms": entry.get("duration_ms"),
            "error": entry.get("error"),
        })

    # Current step = the first one still 'running'
    current_step = None
    for s in steps_list:
        if s["status"] == "running":
            current_step = s["name"]
            break

    # Estimate remaining time
    remaining = 0
    for s in steps_list:
        if s["status"] in ("pending", "running"):
            remaining += _STEP_ESTIMATES.get(s["name"], 2)

    return StandardResponse(data={
        "project_id": project_id,
        "status": project.get("status"),
        "pipeline_progress": project.get("pipeline_progress", 0),
        "current_step": current_step,
        "steps": steps_list,
        "is_processing": bool(project.get("is_processing")),
        "error": project.get("error_message"),
        "estimated_remaining_seconds": remaining,
    })


# ── POST process (one-click) ─────────────────────────────────────────────
@router.post("/{project_id}/process", response_model=StandardResponse[dict])
@limiter.limit("10/hour")
def start_pipeline(
    request: Request,
    project_id: str,
    payload: Optional[ProcessRequest] = None,
    background_tasks: BackgroundTasks = None,
    current_user: CurrentUser = Depends(get_current_user),
):
    db = get_supabase()

    # 1. Validate project exists and belongs to firm
    proj = (
        db.table("cma_projects")
        .select("id, status, is_processing")
        .eq("id", project_id)
        .eq("firm_id", str(current_user.firm_id))
        .execute()
    )
    if not proj.data:
        raise HTTPException(status_code=404, detail="Project not found")

    project = proj.data[0]

    # 2. Concurrency guard
    if project.get("is_processing"):
        raise HTTPException(status_code=409, detail="Pipeline already running for this project")

    # 3. Check there are uploaded files
    files_res = (
        db.table("uploaded_files")
        .select("id", count="exact")
        .eq("cma_project_id", project_id)
        .execute()
    )
    file_count = files_res.count if files_res.count is not None else len(files_res.data)
    if file_count == 0:
        raise HTTPException(status_code=400, detail="No files uploaded — please upload financial documents first")

    # 4. Build pipeline options
    opts = PipelineOptions(
        skip_review=payload.skip_review if payload else False,
        skip_validation=payload.skip_validation if payload else False,
        auto_approve_above=payload.auto_approve_above if payload else 0.70,
        notify_on_review=payload.notify_on_review if payload else True,
        force_reprocess=payload.force_reprocess if payload else False,
    )

    # 5. Mark as processing & kick off background task
    db.table("cma_projects").update({"is_processing": True, "error_message": None}).eq("id", project_id).execute()

    if background_tasks is not None:
        background_tasks.add_task(run_pipeline_background, project_id, str(current_user.firm_id), opts)
    else:
        # Fallback: synchronous (useful for tests)
        run_pipeline_background(project_id, str(current_user.firm_id), opts)

    estimated_seconds = sum(_STEP_ESTIMATES.values())

    return StandardResponse(data={
        "project_id": project_id,
        "status": "processing",
        "message": f"Pipeline started. Track progress at /projects/{project_id}/progress",
        "estimated_duration_seconds": estimated_seconds,
        "files_to_process": file_count,
    })


# ── POST retry (error recovery) ──────────────────────────────────────────
@router.post("/{project_id}/retry", response_model=StandardResponse[dict])
@limiter.limit("10/hour")
def retry_pipeline(
    request: Request,
    project_id: str,
    payload: Optional[RetryRequest] = None,
    background_tasks: BackgroundTasks = None,
    current_user: CurrentUser = Depends(get_current_user),
):
    db = get_supabase()

    proj = (
        db.table("cma_projects")
        .select("id, status, pipeline_steps, is_processing")
        .eq("id", project_id)
        .eq("firm_id", str(current_user.firm_id))
        .execute()
    )
    if not proj.data:
        raise HTTPException(status_code=404, detail="Project not found")

    project = proj.data[0]

    if project.get("status") != "error":
        raise HTTPException(status_code=409, detail="Project is not in an error state — use /process instead")

    if project.get("is_processing"):
        raise HTTPException(status_code=409, detail="Pipeline is already running")

    # Find the failed step if caller didn't specify
    from_step = payload.from_step if (payload and payload.from_step) else None
    if not from_step:
        steps_meta = project.get("pipeline_steps") or {}
        for sn in ["extract", "classify", "review", "validate", "generate"]:
            if steps_meta.get(sn, {}).get("status") == "failed":
                from_step = sn
                break
        if not from_step:
            from_step = "extract"  # fallback

    opts = PipelineOptions(start_from=from_step)

    db.table("cma_projects").update({"is_processing": True, "error_message": None}).eq("id", project_id).execute()

    if background_tasks is not None:
        background_tasks.add_task(run_pipeline_background, project_id, str(current_user.firm_id), opts)
    else:
        run_pipeline_background(project_id, str(current_user.firm_id), opts)

    return StandardResponse(data={
        "project_id": project_id,
        "status": "retrying",
        "from_step": from_step,
        "message": f"Pipeline resuming from '{from_step}'. Track at /projects/{project_id}/progress",
    })


# ── POST resume (after CA review) ────────────────────────────────────────
@router.post("/{project_id}/resume", response_model=StandardResponse[dict])
@limiter.limit("10/hour")
def resume_after_review(
    request: Request,
    project_id: str,
    background_tasks: BackgroundTasks = None,
    current_user: CurrentUser = Depends(get_current_user),
):
    db = get_supabase()

    proj = (
        db.table("cma_projects")
        .select("id, status, is_processing")
        .eq("id", project_id)
        .eq("firm_id", str(current_user.firm_id))
        .execute()
    )
    if not proj.data:
        raise HTTPException(status_code=404, detail="Project not found")

    project = proj.data[0]

    if project["status"] not in ("reviewing", "validated"):
        raise HTTPException(status_code=409, detail="Project is not awaiting review or validated")

    if project.get("is_processing"):
        raise HTTPException(status_code=409, detail="Pipeline is already running")

    opts = PipelineOptions(start_from="validate")

    db.table("cma_projects").update({"is_processing": True, "error_message": None}).eq("id", project_id).execute()

    if background_tasks is not None:
        background_tasks.add_task(run_pipeline_background, project_id, str(current_user.firm_id), opts)
    else:
        run_pipeline_background(project_id, str(current_user.firm_id), opts)

    return StandardResponse(data={
        "project_id": project_id,
        "status": "resuming",
        "message": f"Pipeline resuming from validation. Track at /projects/{project_id}/progress",
    })
