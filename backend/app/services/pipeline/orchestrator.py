"""
Task 8.1: Core Pipeline Orchestrator Service.

Chains:  extract → classify → review-check → validate → generate
into a single callable function with resume support.
"""

import logging
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional

from pydantic import BaseModel

from app.db.supabase_client import get_supabase
from app.services.pipeline.error_handler import (
    with_retry,
    TransientError,
    classify_transient_error,
    build_error_report,
)

logger = logging.getLogger(__name__)

# ── Pipeline step definitions ─────────────────────────────────────────────
PIPELINE_STEPS = [
    {"name": "extract", "progress": (0, 25), "service": "extraction"},
    {"name": "classify", "progress": (25, 50), "service": "classification"},
    {"name": "review", "progress": (50, 60), "service": "review_check"},
    {"name": "validate", "progress": (60, 80), "service": "validation"},
    {"name": "generate", "progress": (80, 100), "service": "generation"},
]

STEP_NAMES = [s["name"] for s in PIPELINE_STEPS]

# Maps a project status string → the next logical pipeline step.
STATUS_TO_NEXT_STEP: Dict[str, str] = {
    "draft": "extract",
    "uploaded": "extract",
    "extracting": "extract",
    "extracted": "classify",
    "classifying": "classify",
    "classified": "review",
    "reviewing": "review",
    "validated": "validate",
    "validating": "validate",
    "generating": "generate",
    "completed": "generate",  # force_reprocess case
    "error": "extract",       # default; actual step comes from metadata
}


# ── Models ────────────────────────────────────────────────────────────────
class PipelineOptions(BaseModel):
    start_from: Optional[str] = None   # resume from a specific step
    skip_review: bool = False           # auto-approve all review items
    skip_validation: bool = False       # generate even with validation errors
    force_reprocess: bool = False       # redo already-completed steps
    auto_approve_above: float = 0.70    # auto-approve review items ≥ this confidence
    notify_on_review: bool = True


class PipelineResult(BaseModel):
    project_id: str
    completed_steps: List[str] = []
    current_step: Optional[str] = None
    stopped_reason: Optional[str] = None  # awaiting_review | validation_errors | completed | error
    duration_ms: int = 0
    llm_cost_usd: float = 0.0
    errors: List[Dict] = []


class StepResult(BaseModel):
    success: bool
    needs_review: bool = False
    review_count: int = 0
    error: Optional[str] = None
    duration_ms: int = 0
    llm_cost_usd: float = 0.0


# ── Helpers ───────────────────────────────────────────────────────────────
def _step_index(name: str) -> int:
    return STEP_NAMES.index(name)


def _update_project(project_id: str, status: str, progress: int, **extra):
    db = get_supabase()
    payload = {"status": status, "pipeline_progress": progress, **extra}
    db.table("cma_projects").update(payload).eq("id", project_id).execute()


def _init_pipeline_steps(project_id: str):
    """Write initial pipeline_steps JSONB into project metadata."""
    steps_meta = {
        s["name"]: {"status": "pending", "started_at": None, "completed_at": None, "duration_ms": None, "error": None}
        for s in PIPELINE_STEPS
    }
    db = get_supabase()
    db.table("cma_projects").update({"pipeline_steps": steps_meta, "is_processing": True}).eq("id", project_id).execute()
    return steps_meta


def _mark_step(project_id: str, step: str, status: str, duration_ms: int = 0, error: str = None):
    db = get_supabase()
    proj = db.table("cma_projects").select("pipeline_steps").eq("id", project_id).execute()
    steps_meta = proj.data[0].get("pipeline_steps", {}) if proj.data else {}
    now_iso = datetime.now(timezone.utc).isoformat()

    entry = steps_meta.get(step, {})
    entry["status"] = status
    if status == "running":
        entry["started_at"] = now_iso
    elif status in ("completed", "failed", "skipped"):
        entry["completed_at"] = now_iso
        entry["duration_ms"] = duration_ms
    if error:
        entry["error"] = error

    steps_meta[step] = entry
    db.table("cma_projects").update({"pipeline_steps": steps_meta}).eq("id", project_id).execute()


def should_run(step_name: str, project_status: str, options: PipelineOptions) -> bool:
    """Decide whether *step_name* should execute given current state & options."""
    if options.force_reprocess:
        return True

    if options.start_from:
        return _step_index(step_name) >= _step_index(options.start_from)

    next_step = STATUS_TO_NEXT_STEP.get(project_status, "extract")
    return _step_index(step_name) >= _step_index(next_step)


# ── Hook helpers (fire-and-forget) ────────────────────────────────────────
def _hook_step_start(project_id: str, firm_id: str, step: str):
    try:
        from app.services.pipeline.hooks import on_step_start
        on_step_start(project_id, firm_id, step)
    except Exception:
        logger.debug("Hook on_step_start failed for %s", step, exc_info=True)


def _hook_step_complete(project_id: str, firm_id: str, step: str, duration_ms: int):
    try:
        from app.services.pipeline.hooks import on_step_complete
        on_step_complete(project_id, firm_id, step, duration_ms)
    except Exception:
        logger.debug("Hook on_step_complete failed for %s", step, exc_info=True)


def _hook_step_fail(project_id: str, firm_id: str, step: str, error: str):
    try:
        from app.services.pipeline.hooks import on_step_fail
        on_step_fail(project_id, firm_id, step, error)
    except Exception:
        logger.debug("Hook on_step_fail failed for %s", step, exc_info=True)


def _hook_pipeline_complete(project_id: str, firm_id: str, duration_ms: int, cost: float):
    try:
        from app.services.pipeline.hooks import on_pipeline_complete
        on_pipeline_complete(project_id, firm_id, duration_ms, cost)
    except Exception:
        logger.debug("Hook on_pipeline_complete failed", exc_info=True)


def _hook_review_needed(project_id: str, firm_id: str, count: int):
    try:
        from app.services.pipeline.hooks import on_review_needed
        on_review_needed(project_id, firm_id, count)
    except Exception:
        logger.debug("Hook on_review_needed failed", exc_info=True)


# ── Individual step runners ───────────────────────────────────────────────
def _run_extract(project_id: str, firm_id: str) -> StepResult:
    """Run the extraction service for all uploaded files."""
    from app.services.extraction.extractor import extract_project

    t0 = time.time()
    try:
        def _do_extract():
            try:
                return extract_project(project_id, firm_id)
            except Exception as exc:
                if classify_transient_error(exc):
                    raise TransientError(str(exc)) from exc
                raise

        result = with_retry(_do_extract, max_retries=2, base_delay=2.0)
        return StepResult(success=True, duration_ms=int((time.time() - t0) * 1000))
    except Exception as e:
        logger.error("Extraction failed: %s", e)
        return StepResult(success=False, error=str(e), duration_ms=int((time.time() - t0) * 1000))


def _run_classify(project_id: str, firm_id: str, entity_type: str) -> StepResult:
    """Run classification and populate review queue."""
    from app.services.classification.classifier import classify_project
    from app.services.classification.review_service import populate_review_queue

    t0 = time.time()
    try:
        def _do_classify():
            try:
                return classify_project(project_id, firm_id, entity_type)
            except Exception as exc:
                if classify_transient_error(exc):
                    raise TransientError(str(exc)) from exc
                raise

        class_res = with_retry(_do_classify, max_retries=3, base_delay=3.0)

        # Persist classification_data
        db = get_supabase()
        classification_data = {
            "classified_at": datetime.now(timezone.utc).isoformat(),
            "total_items": class_res.total_items,
            "items": [item.model_dump() for item in class_res.items],
            "summary": {
                "by_precedent": class_res.classified_by_precedent,
                "by_rule": class_res.classified_by_rule,
                "by_ai": class_res.classified_by_ai,
                "uncertain": class_res.unclassified,
            },
        }
        db.table("cma_projects").update({"classification_data": classification_data}).eq("id", project_id).execute()

        # Review queue
        review_count = populate_review_queue(project_id, firm_id, class_res.items, entity_type)
        needs_review = review_count > 0

        return StepResult(
            success=True,
            needs_review=needs_review,
            review_count=review_count,
            duration_ms=int((time.time() - t0) * 1000),
            llm_cost_usd=class_res.llm_cost_usd,
        )
    except Exception as e:
        logger.error("Classification failed: %s", e)
        return StepResult(success=False, error=str(e), duration_ms=int((time.time() - t0) * 1000))


def _run_review_check(project_id: str, firm_id: str, options: PipelineOptions) -> StepResult:
    """Check if review items remain; auto-approve high confidence if configured."""
    from app.services.classification.review_applier import apply_review_decisions

    t0 = time.time()
    try:
        db = get_supabase()

        if options.skip_review:
            # Approve everything
            pending = (
                db.table("review_queue")
                .select("id, suggested_row, suggested_sheet")
                .eq("cma_project_id", project_id)
                .eq("firm_id", firm_id)
                .eq("status", "pending")
                .execute()
            )
            for row in pending.data:
                db.table("review_queue").update({
                    "status": "resolved",
                    "resolved_row": row["suggested_row"],
                    "resolved_sheet": row["suggested_sheet"],
                    "resolved_at": datetime.now(timezone.utc).isoformat(),
                }).eq("id", row["id"]).eq("firm_id", firm_id).execute()

            apply_review_decisions(project_id, firm_id)
            return StepResult(success=True, needs_review=False, duration_ms=int((time.time() - t0) * 1000))

        if options.auto_approve_above and options.auto_approve_above < 1.0:
            # Auto-approve items above threshold
            high_conf = (
                db.table("review_queue")
                .select("id, suggested_row, suggested_sheet")
                .eq("cma_project_id", project_id)
                .eq("firm_id", firm_id)
                .eq("status", "pending")
                .gte("confidence", options.auto_approve_above)
                .execute()
            )
            for row in high_conf.data:
                db.table("review_queue").update({
                    "status": "resolved",
                    "resolved_row": row["suggested_row"],
                    "resolved_sheet": row["suggested_sheet"],
                    "resolved_at": datetime.now(timezone.utc).isoformat(),
                }).eq("id", row["id"]).eq("firm_id", firm_id).execute()

        # Check remaining pending
        remaining = (
            db.table("review_queue")
            .select("id", count="exact")
            .eq("cma_project_id", project_id)
            .eq("firm_id", firm_id)
            .eq("status", "pending")
            .execute()
        )
        still_pending = remaining.count if remaining.count else 0

        if still_pending > 0:
            return StepResult(success=True, needs_review=True, review_count=still_pending, duration_ms=int((time.time() - t0) * 1000))

        # All done — apply
        apply_review_decisions(project_id, firm_id)
        return StepResult(success=True, needs_review=False, duration_ms=int((time.time() - t0) * 1000))

    except Exception as e:
        logger.error("Review check failed: %s", e)
        return StepResult(success=False, error=str(e), duration_ms=int((time.time() - t0) * 1000))


def _run_validate(project_id: str, firm_id: str, entity_type: str, skip: bool = False) -> StepResult:
    from app.services.validation.validator import validate_project as run_validation

    t0 = time.time()
    try:
        db = get_supabase()

        proj = (
            db.table("cma_projects")
            .select("classification_data")
            .eq("id", project_id)
            .eq("firm_id", firm_id)
            .execute()
        )
        classification_data = proj.data[0].get("classification_data", {}) if proj.data else {}

        val = run_validation(project_id, classification_data, entity_type)

        if val.errors > 0 and not skip:
            return StepResult(
                success=False,
                error=f"{val.errors} validation error(s): {val.summary}",
                duration_ms=int((time.time() - t0) * 1000),
            )

        return StepResult(success=True, duration_ms=int((time.time() - t0) * 1000))
    except Exception as e:
        logger.error("Validation failed: %s", e)
        return StepResult(success=False, error=str(e), duration_ms=int((time.time() - t0) * 1000))


def _run_generate(project_id: str, firm_id: str, skip_validation: bool = False) -> StepResult:
    from app.services.excel.generator import generate_cma

    t0 = time.time()
    try:
        gen = generate_cma(project_id, firm_id, skip_validation=skip_validation)
        if not gen.success:
            return StepResult(success=False, error="Generation failed — validation errors remain", duration_ms=int((time.time() - t0) * 1000))
        return StepResult(success=True, duration_ms=int((time.time() - t0) * 1000))
    except Exception as e:
        logger.error("Excel generation failed: %s", e)
        return StepResult(success=False, error=str(e), duration_ms=int((time.time() - t0) * 1000))


# ── Main orchestrator ─────────────────────────────────────────────────────
def run_pipeline(project_id: str, firm_id: str, options: PipelineOptions | None = None) -> PipelineResult:
    """Execute the full CMA pipeline, returning when done or paused."""
    if options is None:
        options = PipelineOptions()

    start = time.time()
    completed_steps: List[str] = []
    errors: List[Dict] = []
    total_cost = 0.0

    db = get_supabase()
    proj = db.table("cma_projects").select("status, client_id").eq("id", project_id).eq("firm_id", firm_id).execute()
    if not proj.data:
        return PipelineResult(project_id=project_id, stopped_reason="project_not_found", duration_ms=0)

    project_status = proj.data[0]["status"]
    client_id = proj.data[0]["client_id"]

    # Resolve entity_type
    client_resp = db.table("clients").select("entity_type").eq("id", client_id).execute()
    entity_type = client_resp.data[0]["entity_type"] if client_resp.data else "trading"

    _init_pipeline_steps(project_id)

    # ── Step 1: EXTRACT ──────────────────────────────────────────────────
    if should_run("extract", project_status, options):
        _mark_step(project_id, "extract", "running")
        _hook_step_start(project_id, firm_id, "extract")
        _update_project(project_id, "extracting", 5)

        res = _run_extract(project_id, firm_id)
        if not res.success:
            _mark_step(project_id, "extract", "failed", res.duration_ms, res.error)
            _hook_step_fail(project_id, firm_id, "extract", res.error or "")
            _update_project(project_id, "error", 5, error_message=res.error, is_processing=False)
            return PipelineResult(
                project_id=project_id, stopped_reason="extraction_failed",
                completed_steps=completed_steps,
                errors=[build_error_report("extract", res.error or "Unknown error")],
                duration_ms=int((time.time() - start) * 1000),
            )

        _mark_step(project_id, "extract", "completed", res.duration_ms)
        _hook_step_complete(project_id, firm_id, "extract", res.duration_ms)
        _update_project(project_id, "extracted", 25)
        completed_steps.append("extract")
    else:
        _mark_step(project_id, "extract", "skipped")

    # ── Step 2: CLASSIFY ─────────────────────────────────────────────────
    if should_run("classify", project_status, options):
        _mark_step(project_id, "classify", "running")
        _hook_step_start(project_id, firm_id, "classify")
        _update_project(project_id, "classifying", 30)

        res = _run_classify(project_id, firm_id, entity_type)
        total_cost += res.llm_cost_usd

        if not res.success:
            _mark_step(project_id, "classify", "failed", res.duration_ms, res.error)
            _hook_step_fail(project_id, firm_id, "classify", res.error or "")
            _update_project(project_id, "error", 30, error_message=res.error, is_processing=False)
            return PipelineResult(
                project_id=project_id, stopped_reason="classification_failed",
                completed_steps=completed_steps,
                errors=[build_error_report("classify", res.error or "Unknown error")],
                duration_ms=int((time.time() - start) * 1000), llm_cost_usd=total_cost,
            )

        _mark_step(project_id, "classify", "completed", res.duration_ms)
        _hook_step_complete(project_id, firm_id, "classify", res.duration_ms)
        _update_project(project_id, "classified", 50)
        completed_steps.append("classify")
    else:
        _mark_step(project_id, "classify", "skipped")

    # ── Step 3: REVIEW CHECK ─────────────────────────────────────────────
    if should_run("review", project_status, options):
        _mark_step(project_id, "review", "running")
        _hook_step_start(project_id, firm_id, "review")
        review_res = _run_review_check(project_id, firm_id, options)

        if not review_res.success:
            _mark_step(project_id, "review", "failed", review_res.duration_ms, review_res.error)
            _hook_step_fail(project_id, firm_id, "review", review_res.error or "")
            _update_project(project_id, "error", 50, error_message=review_res.error, is_processing=False)
            return PipelineResult(
                project_id=project_id, stopped_reason="review_check_failed",
                completed_steps=completed_steps,
                errors=[{"step": "review", "message": review_res.error}],
                duration_ms=int((time.time() - start) * 1000), llm_cost_usd=total_cost,
            )

        if review_res.needs_review:
            _mark_step(project_id, "review", "completed", review_res.duration_ms)
            _hook_step_complete(project_id, firm_id, "review", review_res.duration_ms)
            _hook_review_needed(project_id, firm_id, review_res.review_count)
            _update_project(project_id, "reviewing", 50, is_processing=False)
            completed_steps.append("review")
            return PipelineResult(
                project_id=project_id, stopped_reason="awaiting_review",
                current_step="review", completed_steps=completed_steps,
                duration_ms=int((time.time() - start) * 1000), llm_cost_usd=total_cost,
            )

        _mark_step(project_id, "review", "completed", review_res.duration_ms)
        _hook_step_complete(project_id, firm_id, "review", review_res.duration_ms)
        _update_project(project_id, "validated", 60)
        completed_steps.append("review")
    else:
        _mark_step(project_id, "review", "skipped")

    # ── Step 4: VALIDATE ─────────────────────────────────────────────────
    if should_run("validate", project_status, options):
        _mark_step(project_id, "validate", "running")
        _hook_step_start(project_id, firm_id, "validate")
        _update_project(project_id, "validating", 65)

        val_res = _run_validate(project_id, firm_id, entity_type, skip=options.skip_validation)
        if not val_res.success and not options.skip_validation:
            _mark_step(project_id, "validate", "failed", val_res.duration_ms, val_res.error)
            _hook_step_fail(project_id, firm_id, "validate", val_res.error or "")
            _update_project(project_id, "validation_failed", 65, is_processing=False, error_message=val_res.error)
            return PipelineResult(
                project_id=project_id, stopped_reason="validation_errors",
                completed_steps=completed_steps,
                errors=[build_error_report("validate", val_res.error or "Validation errors")],
                duration_ms=int((time.time() - start) * 1000), llm_cost_usd=total_cost,
            )

        _mark_step(project_id, "validate", "completed", val_res.duration_ms)
        _hook_step_complete(project_id, firm_id, "validate", val_res.duration_ms)
        _update_project(project_id, "validated", 80)
        completed_steps.append("validate")
    else:
        _mark_step(project_id, "validate", "skipped")

    # ── Step 5: GENERATE ─────────────────────────────────────────────────
    _mark_step(project_id, "generate", "running")
    _hook_step_start(project_id, firm_id, "generate")
    _update_project(project_id, "generating", 85)

    gen_res = _run_generate(project_id, firm_id, skip_validation=True)  # already validated
    if not gen_res.success:
        _mark_step(project_id, "generate", "failed", gen_res.duration_ms, gen_res.error)
        _hook_step_fail(project_id, firm_id, "generate", gen_res.error or "")
        _update_project(project_id, "error", 85, error_message=gen_res.error, is_processing=False)
        return PipelineResult(
            project_id=project_id, stopped_reason="generation_failed",
            completed_steps=completed_steps,
            errors=[build_error_report("generate", gen_res.error or "Generation error")],
            duration_ms=int((time.time() - start) * 1000), llm_cost_usd=total_cost,
        )

    _mark_step(project_id, "generate", "completed", gen_res.duration_ms)
    _hook_step_complete(project_id, firm_id, "generate", gen_res.duration_ms)
    _update_project(project_id, "completed", 100, is_processing=False)
    completed_steps.append("generate")

    total_duration = int((time.time() - start) * 1000)
    _hook_pipeline_complete(project_id, firm_id, total_duration, total_cost)

    return PipelineResult(
        project_id=project_id,
        completed_steps=completed_steps,
        stopped_reason="completed",
        duration_ms=total_duration,
        llm_cost_usd=total_cost,
    )


def resume_pipeline(project_id: str, firm_id: str) -> PipelineResult:
    """Resume the pipeline after CA reviews have been completed."""
    return run_pipeline(project_id, firm_id, PipelineOptions(start_from="validate"))
