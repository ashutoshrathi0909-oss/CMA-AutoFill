"""
Task 8.6: Pre/post hooks for pipeline steps — notifications + audit logging.

All hooks are fire-and-forget: failures are logged but never crash the pipeline.
"""

import logging
from datetime import datetime, timezone

from app.db.supabase_client import get_supabase

logger = logging.getLogger(__name__)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_audit(firm_id: str, action: str, entity_id: str, metadata: dict | None = None):
    """Insert an audit_log row; silently swallow errors."""
    try:
        db = get_supabase()
        db.table("audit_log").insert({
            "firm_id": firm_id,
            "action": action,
            "entity_type": "cma_project",
            "entity_id": entity_id,
            "metadata": metadata or {},
        }).execute()
    except Exception as exc:
        logger.warning("Audit log write failed (%s): %s", action, exc)


# ── Step-level hooks ──────────────────────────────────────────────────────
def on_step_start(project_id: str, firm_id: str, step_name: str):
    _safe_audit(firm_id, f"pipeline_{step_name}_start", project_id)
    logger.info("Pipeline [%s] step '%s' STARTED", project_id[:8], step_name)


def on_step_complete(project_id: str, firm_id: str, step_name: str, duration_ms: int = 0):
    _safe_audit(firm_id, f"pipeline_{step_name}_complete", project_id, {"duration_ms": duration_ms})
    logger.info("Pipeline [%s] step '%s' COMPLETED (%d ms)", project_id[:8], step_name, duration_ms)


def on_step_fail(project_id: str, firm_id: str, step_name: str, error: str):
    _safe_audit(firm_id, f"pipeline_{step_name}_failed", project_id, {"error": error})
    logger.error("Pipeline [%s] step '%s' FAILED: %s", project_id[:8], step_name, error)


# ── Pipeline-level hooks ─────────────────────────────────────────────────
def on_pipeline_complete(project_id: str, firm_id: str, duration_ms: int, llm_cost_usd: float):
    _safe_audit(firm_id, "pipeline_complete", project_id, {"duration_ms": duration_ms, "cost_usd": llm_cost_usd})
    logger.info("Pipeline [%s] COMPLETED (total %d ms, $%.4f)", project_id[:8], duration_ms, llm_cost_usd)

    # Send 'ready to generate' email (best-effort)
    try:
        from app.services.notifications.email_service import send_ready_notification
        db = get_supabase()
        proj = db.table("cma_projects").select("client_id, clients(name)").eq("id", project_id).execute()
        client_name = "Unknown"
        if proj.data and proj.data[0].get("clients"):
            client_name = proj.data[0]["clients"].get("name", "Unknown")
        send_ready_notification(firm_id, project_id, client_name, f"{client_name} CMA")
    except Exception as exc:
        logger.warning("Ready notification failed: %s", exc)


def on_review_needed(project_id: str, firm_id: str, review_count: int):
    _safe_audit(firm_id, "pipeline_review_needed", project_id, {"review_items": review_count})
    logger.info("Pipeline [%s] paused — %d items need review", project_id[:8], review_count)

    # Send review-needed email (best-effort)
    try:
        from app.services.notifications.email_service import send_review_notification
        db = get_supabase()
        proj = db.table("cma_projects").select("client_id, clients(name)").eq("id", project_id).execute()
        client_name = "Unknown"
        if proj.data and proj.data[0].get("clients"):
            client_name = proj.data[0]["clients"].get("name", "Unknown")

        items_stub = []  # lightweight — full items not needed for email
        send_review_notification(firm_id, project_id, client_name, f"{client_name} CMA", items_stub)
    except Exception as exc:
        logger.warning("Review notification failed: %s", exc)
