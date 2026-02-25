# Task 8.3: Progress Tracking Endpoint

> **Phase:** 08 - Pipeline Orchestrator
> **Depends on:** Task 8.2 (background tasks running)
> **Time estimate:** 10 minutes

---

## Objective

Create a polling endpoint the frontend uses to show real-time pipeline progress.

---

## What to Do

### Endpoint

**`GET /api/v1/projects/{project_id}/progress`**

Response:
```json
{
  "data": {
    "project_id": "uuid",
    "status": "classifying",
    "pipeline_progress": 35,
    "current_step": "classify",
    "steps": [
      {"name": "extract", "status": "completed", "duration_ms": 2500},
      {"name": "classify", "status": "running", "started_at": "2026-02-25T10:30:15Z"},
      {"name": "review", "status": "pending"},
      {"name": "validate", "status": "pending"},
      {"name": "generate", "status": "pending"}
    ],
    "is_processing": true,
    "error": null,
    "estimated_remaining_seconds": 15,
    "llm_cost_so_far_usd": 0.003
  }
}
```

### Step Status Tracking

Add a `pipeline_steps` JSONB column to `cma_projects` (or use the existing metadata column):

Each step records:
- status: 'pending' | 'running' | 'completed' | 'failed' | 'skipped'
- started_at, completed_at
- duration_ms
- error (if failed)

The orchestrator updates this as it progresses through steps.

### Time Estimation

Simple estimation based on averages:
- Extraction: ~5s per file
- Classification: ~3s per 20 items
- Validation: ~1s
- Generation: ~2s

`estimated_remaining = sum of estimated times for pending steps`

### Frontend Polling Pattern

Frontend polls this endpoint every 2 seconds while `is_processing = true`. When `is_processing = false`, stop polling.

---

## What NOT to Do

- Don't use WebSockets for V1 (polling is simpler and sufficient for 5 CMAs/month)
- Don't compute progress on every poll — just read from database
- Don't expose internal error details to the user

---

## Verification

- [ ] Start pipeline → poll progress → see steps completing in sequence
- [ ] Progress percentage increases from 0 to 100
- [ ] Each step shows correct status (pending → running → completed)
- [ ] Pipeline error → error field has user-friendly message
- [ ] Pipeline complete → is_processing = false
- [ ] Polling is fast (< 50ms response time)

---

## Done → Move to task-8.4-error-recovery.md
