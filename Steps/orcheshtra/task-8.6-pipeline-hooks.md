# Task 8.6: Pipeline Hooks (Notifications & Logging)

> **Phase:** 08 - Pipeline Orchestrator
> **Depends on:** Tasks 8.1-8.5, Phase 07 Task 7.7 (email service)
> **Time estimate:** 10 minutes

---

## Objective

Add pre/post hooks to each pipeline step for consistent notification and audit logging.

---

## What to Do

### Create File
`backend/app/services/pipeline/hooks.py`

### Hook System

```python
async def on_step_start(project_id, step_name, metadata):
    """Called before each pipeline step."""
    await update_pipeline_step(project_id, step_name, status="running")
    await create_audit_log(action=f"pipeline_{step_name}_start", entity_id=project_id)

async def on_step_complete(project_id, step_name, result, metadata):
    """Called after each pipeline step succeeds."""
    await update_pipeline_step(project_id, step_name, status="completed", duration=result.duration_ms)
    await create_audit_log(action=f"pipeline_{step_name}_complete", entity_id=project_id)

async def on_step_fail(project_id, step_name, error, metadata):
    """Called when a pipeline step fails."""
    await update_pipeline_step(project_id, step_name, status="failed", error=str(error))
    await create_audit_log(action=f"pipeline_{step_name}_failed", entity_id=project_id)

async def on_pipeline_complete(project_id, firm_id, result):
    """Called when entire pipeline finishes."""
    await send_ready_notification(firm_id, project_id)
    await create_audit_log(action="pipeline_complete", entity_id=project_id, 
                          metadata={"duration_ms": result.duration_ms, "cost_usd": result.llm_cost_usd})

async def on_review_needed(project_id, firm_id, review_items):
    """Called when pipeline pauses for review."""
    await send_review_notification(firm_id, project_id, review_items)
```

### Integrate into Orchestrator

Update `orchestrator.py` to call hooks at each step:
```python
await on_step_start(project_id, "extract", {})
result = await extraction_service.extract(project_id)
await on_step_complete(project_id, "extract", result, {})
```

### Comprehensive Audit Trail

After hooks, the `audit_log` table captures the complete pipeline journey:
- pipeline_extract_start → pipeline_extract_complete
- pipeline_classify_start → pipeline_classify_complete
- pipeline_review_needed (with item count)
- pipeline_validate_start → pipeline_validate_complete
- pipeline_generate_start → pipeline_generate_complete
- pipeline_complete (with total duration and cost)

---

## What NOT to Do

- Don't let hook failures crash the pipeline (wrap in try/catch)
- Don't send emails from every hook (only review_needed and complete)
- Don't log sensitive financial data in audit trail

---

## Verification

- [ ] Run full pipeline → audit_log has entries for every step
- [ ] Step failure → on_step_fail called, error logged
- [ ] Pipeline complete → notification email sent
- [ ] Review needed → review notification email sent
- [ ] Hook failure → logged but pipeline continues

---

## Done → Move to task-8.7-pipeline-tests.md
