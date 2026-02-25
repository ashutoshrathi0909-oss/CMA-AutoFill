# Task 11.4: Error Monitoring & Structured Logging

> **Phase:** 11 - Testing & Production Deploy
> **Depends on:** All backend code complete
> **Time estimate:** 15 minutes

---

## Objective

Set up structured logging and error monitoring so you know when things break in production.

---

## What to Do

### Step 1: Structured Logging

File: `backend/app/core/logging.py`

Use Python's `structlog` or standard logging with JSON format:

```python
import structlog

logger = structlog.get_logger()

# Usage in code:
logger.info("pipeline_started", project_id=str(project_id), firm_id=str(firm_id))
logger.error("extraction_failed", project_id=str(project_id), error=str(e), file_name="mehta_pl.xlsx")
```

Log format (JSON for machine parsing):
```json
{
  "timestamp": "2026-02-25T10:30:00Z",
  "level": "error",
  "event": "extraction_failed",
  "project_id": "uuid",
  "error": "Invalid file format",
  "file_name": "mehta_pl.xlsx"
}
```

### Step 2: What to Log

**Always log (INFO):**
- Pipeline step start/complete with duration
- LLM API calls with model, tokens, cost
- User actions: login, create project, process, download
- File uploads with size and type

**Log on warning (WARN):**
- Slow API responses (>500ms)
- LLM retry attempts
- Validation warnings
- Rate limit approaches

**Log on error (ERROR):**
- Pipeline failures with full context
- LLM API errors with response details
- Unhandled exceptions
- Auth failures (potential security issues)

**Never log:**
- Full financial data or amounts
- JWT tokens or credentials
- File contents
- Personal email addresses (use user ID instead)

### Step 3: Error Alerting (Simple)

For V1, use a simple email alert for critical errors:

```python
async def alert_critical_error(error_details: dict):
    """Send email to admin when something critical fails."""
    await send_email(
        to=os.getenv("ADMIN_EMAIL"),
        subject=f"CMA AutoFill Error: {error_details['event']}",
        body=json.dumps(error_details, indent=2)
    )
```

Trigger on:
- Pipeline failure (all retries exhausted)
- Authentication security events (multiple failed attempts)
- Database connection failures

### Step 4: Health Dashboard

Enhance `GET /health` to include system status:

```json
{
  "status": "ok",
  "version": "1.0.0",
  "uptime_seconds": 86400,
  "database": "connected",
  "gemini_api": "available",
  "storage": "connected",
  "last_error": null,
  "active_pipelines": 0
}
```

---

## What NOT to Do

- Don't use paid error tracking services for V1 (Sentry etc. — add later when scaling)
- Don't log sensitive data
- Don't create complex dashboards (check Railway/Vercel logs directly)
- Don't suppress errors — always log them

---

## Verification

- [ ] All pipeline steps produce structured log entries
- [ ] Logs are JSON formatted (parseable)
- [ ] Error email sent on pipeline failure (test with mock failure)
- [ ] No sensitive data in logs (audit manually)
- [ ] Health endpoint shows system status
- [ ] Logs visible in Railway dashboard

---

## Done → Move to task-11.5-env-production.md
