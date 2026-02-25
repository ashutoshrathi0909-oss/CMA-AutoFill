# Task 8.4: Error Recovery & Retry Logic

> **Phase:** 08 - Pipeline Orchestrator
> **Depends on:** Tasks 8.1-8.3
> **Time estimate:** 15 minutes

---

## Objective

Handle pipeline failures gracefully — retry transient errors, allow resuming from the failed step, and preserve all partial results.

---

## What to Do

### Create File
`backend/app/services/pipeline/error_handler.py`

### Error Categories

**Transient (auto-retry):**
- Gemini API rate limit (429) → wait 5s, retry up to 3 times
- Gemini API timeout → retry once
- Supabase connection error → retry once after 2s
- Network errors → retry once

**Permanent (stop and report):**
- Invalid file format → stop extraction for that file, continue others
- No extractable data → stop pipeline, ask user to check files
- All files failed extraction → stop pipeline
- Validation hard errors → stop before generation (user must fix)

**Partial (continue with what works):**
- Some files extract, some fail → continue with successful ones
- Some items classify, AI fails → mark unclassified, continue to review
- Review queue has items → pause pipeline (not an error)

### Retry Logic

```python
async def with_retry(func, max_retries=3, delay=2):
    for attempt in range(max_retries):
        try:
            return await func()
        except TransientError as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(delay * (attempt + 1))  # exponential backoff
                continue
            raise PipelineError(step=current_step, error=str(e), retriable=False)
```

### Resume Endpoint

**`POST /api/v1/projects/{project_id}/retry`**

Request body:
```json
{
  "from_step": "classify"    // optional — default: resume from failed step
}
```

Logic:
1. Check project status is 'error'
2. Identify the failed step from pipeline_steps metadata
3. Resume pipeline from that step (preserving results from completed steps)
4. Return immediately (runs in background)

### Error Reporting

When pipeline fails, save to project:
```json
{
  "error": {
    "step": "classify",
    "message": "Gemini API rate limit exceeded after 3 retries",
    "timestamp": "2026-02-25T10:35:00Z",
    "retriable": true,
    "suggestion": "Wait a few minutes and try again, or reduce the number of items per batch"
  }
}
```

---

## What NOT to Do

- Don't retry permanent errors (waste of time and API calls)
- Don't lose partial results on retry (extraction results should persist)
- Don't retry indefinitely — max 3 attempts then stop
- Don't hide errors from the user — always report what happened

---

## Verification

- [ ] Simulated API timeout → auto-retry → succeeds on second try
- [ ] Simulated permanent error → pipeline stops, error reported clearly
- [ ] Retry endpoint → resumes from failed step, not from scratch
- [ ] Partial extraction (2/3 files succeed) → pipeline continues with 2 files
- [ ] Error message includes suggestion for user

---

## Done → Move to task-8.5-one-click-endpoint.md
