# Task 8.1: Core Pipeline Orchestrator Service

> **Phase:** 08 - Pipeline Orchestrator
> **Depends on:** Phases 04-07 (all pipeline steps exist as individual services)
> **Agent reads:** CLAUDE.md → Pipeline Architecture
> **Time estimate:** 20 minutes

---

## Objective

Create the orchestrator that chains all pipeline steps together. One function call takes a project from "files uploaded" to "CMA generated" (or "awaiting review" if items need CA attention).

---

## What to Do

### Create File
`backend/app/services/pipeline/orchestrator.py`

### Pipeline Definition

```python
PIPELINE_STEPS = [
    {"name": "extract",    "progress": (0, 25),   "service": "extraction"},
    {"name": "classify",   "progress": (25, 50),  "service": "classification"},
    {"name": "review",     "progress": (50, 60),  "service": "review_check"},
    {"name": "validate",   "progress": (60, 80),  "service": "validation"},
    {"name": "generate",   "progress": (80, 100), "service": "generation"},
]
```

### Main Function

`run_pipeline(project_id: UUID, firm_id: UUID, options: PipelineOptions) → PipelineResult`

```python
class PipelineOptions:
    start_from: str = "extract"       # resume from a specific step
    skip_review: bool = False          # auto-approve all review items
    skip_validation: bool = False      # generate even with errors
    force_reprocess: bool = False      # redo completed steps

class PipelineResult:
    project_id: UUID
    completed_steps: list[str]
    current_step: str | None
    stopped_reason: str | None         # "awaiting_review", "validation_errors", "completed"
    duration_ms: int
    llm_cost_usd: float
    errors: list[dict]
```

### Pipeline Logic

```python
async def run_pipeline(project_id, firm_id, options):
    project = load_project(project_id)
    
    # Step 1: Extract
    if should_run("extract", project, options):
        update_status(project, "extracting", progress=5)
        result = await extraction_service.extract(project_id)
        if result.failed:
            return PipelineResult(stopped_reason="extraction_failed")
        update_status(project, "extracted", progress=25)
    
    # Step 2: Classify
    if should_run("classify", project, options):
        update_status(project, "classifying", progress=30)
        result = await classification_service.classify(project_id, firm_id)
        update_status(project, "classified", progress=50)
    
    # Step 3: Review Check
    if result.needs_review and not options.skip_review:
        update_status(project, "reviewing", progress=50)
        send_review_notification(firm_id, project_id, result.review_items)
        return PipelineResult(stopped_reason="awaiting_review")
        # Pipeline pauses here — CA reviews, then resumes
    
    # Step 4: Validate
    if should_run("validate", project, options):
        update_status(project, "validating", progress=65)
        validation = await validation_service.validate(project_id)
        if validation.errors > 0 and not options.skip_validation:
            update_status(project, "validation_failed", progress=65)
            return PipelineResult(stopped_reason="validation_errors")
    
    # Step 5: Generate
    update_status(project, "generating", progress=85)
    gen_result = await generation_service.generate(project_id, firm_id)
    update_status(project, "completed", progress=100)
    send_ready_notification(firm_id, project_id)
    
    return PipelineResult(stopped_reason="completed")
```

### Resume After Review

`resume_pipeline(project_id: UUID, firm_id: UUID) → PipelineResult`

Called after CA finishes reviewing:
1. Apply review decisions (task 7.4)
2. Resume from "validate" step
3. Continue to "generate"

### Helper: should_run()

Determines if a step needs to run based on current project status and options:
- If project is already "extracted" and start_from isn't "extract" → skip extraction
- If force_reprocess → run everything regardless

---

## What NOT to Do

- Don't duplicate logic from individual services — call them, don't copy code
- Don't make the orchestrator synchronous (next task adds background processing)
- Don't handle file upload here (that's a separate endpoint before pipeline starts)
- Don't auto-skip review (unless explicitly requested)

---

## Verification

- [ ] run_pipeline on fresh project → runs extract → classify → stops at review
- [ ] run_pipeline with skip_review=True → runs all steps to completion
- [ ] resume_pipeline after review → validate → generate → completed
- [ ] Pipeline progress updates at each step
- [ ] Extraction failure → pipeline stops cleanly, error reported
- [ ] force_reprocess → re-runs completed steps
- [ ] start_from="classify" → skips extraction

---

## Done → Move to task-8.2-background-tasks.md
