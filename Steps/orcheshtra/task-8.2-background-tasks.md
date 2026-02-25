# Task 8.2: Background Task Processing

> **Phase:** 08 - Pipeline Orchestrator
> **Depends on:** Task 8.1 (orchestrator service)
> **Time estimate:** 15 minutes

---

## Objective

Run the pipeline as a background task so the API returns immediately and the user sees progress in real-time instead of waiting for a timeout.

---

## What to Do

### Approach: FastAPI BackgroundTasks

For V1, use FastAPI's built-in `BackgroundTasks` — simple, no extra infrastructure (no Celery, no Redis).

### Create File
`backend/app/services/pipeline/background.py`

### How It Works

```python
from fastapi import BackgroundTasks

@router.post("/projects/{project_id}/process")
async def start_processing(
    project_id: UUID,
    background_tasks: BackgroundTasks,
    current_user: CurrentUser = Depends(get_current_user)
):
    # Validate project
    project = await get_project(project_id, current_user.firm_id)
    
    # Start background task
    background_tasks.add_task(
        run_pipeline_background,
        project_id=project_id,
        firm_id=current_user.firm_id,
        options=PipelineOptions()
    )
    
    # Return immediately
    return {"data": {"message": "Processing started", "project_id": project_id}}
```

### Background Pipeline Wrapper

```python
async def run_pipeline_background(project_id, firm_id, options):
    try:
        result = await run_pipeline(project_id, firm_id, options)
        # Pipeline completed or paused for review
    except Exception as e:
        # Update project status to 'error'
        await update_project_status(project_id, "error", error_message=str(e))
        # Log the error
        logger.error(f"Pipeline failed for {project_id}: {e}")
```

### Concurrency Protection

- Check if project is already being processed → 409 "Pipeline already running"
- Use a simple flag: `cma_projects.is_processing = True` while pipeline runs
- Reset flag on completion or error

### Limitations of BackgroundTasks (V1 acceptable)

- Tasks are tied to the server process — if server restarts, task is lost
- No retry across server restarts
- No task queue or priority system
- Fine for V1 with ~5 CMAs/month. Upgrade to Celery+Redis when scaling.

---

## What NOT to Do

- Don't use Celery or Redis for V1 (overkill for 5 CMAs/month)
- Don't make the process endpoint synchronous (will timeout on large files)
- Don't allow concurrent pipelines on the same project
- Don't lose error information — always update project status on failure

---

## Verification

- [ ] POST /process → returns immediately (< 1 second)
- [ ] Project status updates as pipeline progresses (poll to check)
- [ ] Pipeline completes in background → status = 'completed' or 'reviewing'
- [ ] Pipeline error → status = 'error' with error message
- [ ] Second call while processing → 409 conflict
- [ ] Server handles multiple projects processing simultaneously (different projects)

---

## Done → Move to task-8.3-progress-tracking.md
