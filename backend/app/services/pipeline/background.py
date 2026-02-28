"""
Task 8.2: Background task wrapper for the pipeline orchestrator.

Uses FastAPI's built-in BackgroundTasks (V1 — no Celery/Redis needed).
"""

import logging
from datetime import datetime, timezone

from app.db.supabase_client import get_supabase
from app.services.pipeline.orchestrator import run_pipeline, PipelineOptions, PipelineResult

logger = logging.getLogger(__name__)


def run_pipeline_background(project_id: str, firm_id: str, options: PipelineOptions) -> None:
    """Entry-point called inside a BackgroundTask.  Never raises."""
    try:
        result = run_pipeline(project_id, firm_id, options)
        logger.info(
            "Pipeline %s for project %s (reason=%s, %d ms)",
            "completed" if result.stopped_reason == "completed" else "paused",
            project_id,
            result.stopped_reason,
            result.duration_ms,
        )
    except Exception as exc:
        logger.exception("Unhandled pipeline error for project %s", project_id)
        _mark_project_error(project_id, str(exc))


def _mark_project_error(project_id: str, error_msg: str) -> None:
    try:
        db = get_supabase()
        db.table("cma_projects").update({
            "status": "error",
            "is_processing": False,
            "error_message": error_msg,
        }).eq("id", project_id).execute()
    except Exception:
        logger.exception("Failed to mark project %s as error", project_id)


def is_project_processing(project_id: str) -> bool:
    """Quick check if the project has a pipeline currently running."""
    db = get_supabase()
    res = db.table("cma_projects").select("is_processing").eq("id", project_id).execute()
    if res.data:
        return bool(res.data[0].get("is_processing", False))
    return False
