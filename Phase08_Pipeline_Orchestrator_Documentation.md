# Phase 08: Pipeline Orchestrator — Detailed Documentation

## Overview

Phase 08 wires every individual service (Phases 04–07) into a single, chainable pipeline that takes a project from **"files uploaded"** to **"CMA generated"** with one API call. It adds background processing, real-time progress tracking, error recovery with retry, and audit/notification hooks.

---

## 1. Core Orchestrator Service (Task 8.1)

**File:** `backend/app/services/pipeline/orchestrator.py`

### Pipeline Steps

| # | Step | Progress | Status Transitions |
|---|------|----------|--------------------|
| 1 | `extract` | 0 – 25 % | `extracting` → `extracted` |
| 2 | `classify` | 25 – 50 % | `classifying` → `classified` |
| 3 | `review` | 50 – 60 % | `reviewing` (pauses) or skips |
| 4 | `validate` | 60 – 80 % | `validating` → `validated` |
| 5 | `generate` | 80 – 100 % | `generating` → `completed` |

### Key Functions

- **`run_pipeline(project_id, firm_id, options)`** — Executes all steps sequentially, returning a `PipelineResult` that indicates `completed`, `awaiting_review`, or an error reason.
- **`resume_pipeline(project_id, firm_id)`** — Resumes from "validate" after CA reviews are done.
- **`should_run(step, status, options)`** — Decides if a step needs execution based on current DB status and `PipelineOptions` (force_reprocess, start_from).

### Pipeline Options

| Option | Default | Effect |
|--------|---------|--------|
| `start_from` | `None` | Resume from a specific step |
| `skip_review` | `False` | Auto-approve all review items |
| `skip_validation` | `False` | Generate even if validation errors exist |
| `force_reprocess` | `False` | Re-run already-completed steps |
| `auto_approve_above` | `0.70` | Auto-approve review items above this confidence |
| `notify_on_review` | `True` | Send email when review is needed |

---

## 2. Background Task Processing (Task 8.2)

**File:** `backend/app/services/pipeline/background.py`

- Uses **FastAPI `BackgroundTasks`** — no Celery/Redis needed for V1.
- `run_pipeline_background()` wraps `run_pipeline()` in a try/except, so unhandled errors are caught and the project is marked as `status="error"`.
- `is_project_processing()` checks the `is_processing` flag for concurrency protection.

---

## 3. Progress Tracking Endpoint (Task 8.3)

**Endpoint:** `GET /api/v1/projects/{id}/progress`

Returns real-time pipeline state including:
- Current step (`extract`, `classify`, etc.)
- Per-step status timestamps (`started_at`, `completed_at`, `duration_ms`)
- Overall `pipeline_progress` percentage
- `is_processing` flag (frontend polls while `true`)
- `estimated_remaining_seconds` based on step-time averages

Progress data is stored in the `pipeline_steps` JSONB column on `cma_projects`.

---

## 4. Error Recovery & Retry (Task 8.4)

**File:** `backend/app/services/pipeline/error_handler.py`

### Error Categories

| Category | Examples | Action |
|----------|----------|--------|
| **Transient** | 429 rate limit, timeout, connection error | Auto-retry up to 3× with exponential back-off |
| **Permanent** | Invalid file, no data, template missing | Stop and report |
| **Partial** | Some files fail, some items unclassified | Continue with partial results |

### Retry Endpoint

`POST /api/v1/projects/{id}/retry` — Resumes the pipeline from the failed step (auto-detected from `pipeline_steps` metadata). Preserves all partial results from completed steps.

---

## 5. One-Click Process Endpoint (Task 8.5)

**Endpoint:** `POST /api/v1/projects/{id}/process`

- Validates project has uploaded files (400 if empty)
- Checks concurrency (409 if already processing)
- Starts background pipeline
- Returns immediately with estimated duration

### Resume After Review

`POST /api/v1/projects/{id}/resume` — Called after CA finishes reviewing. Applies review decisions and continues from validation → generation.

---

## 6. Pipeline Hooks — Notifications & Audit (Task 8.6)

**File:** `backend/app/services/pipeline/hooks.py`

Every step fires audit log entries:
```
pipeline_extract_start → pipeline_extract_complete
pipeline_classify_start → pipeline_classify_complete
pipeline_review_needed
pipeline_validate_start → pipeline_validate_complete
pipeline_generate_start → pipeline_generate_complete
pipeline_complete (with duration + cost)
```

Email notifications fire on:
- **Review needed** → `send_review_notification()` to all CAs/owners
- **Pipeline complete** → `send_ready_notification()` with download link

All hooks are fire-and-forget; failures are logged but never crash the pipeline.

---

## 7. Integration Tests (Task 8.7)

**File:** `backend/tests/test_pipeline_integration.py`

| Test | What It Proves |
|------|----------------|
| `TestShouldRun` | `should_run()` correctly handles `force_reprocess`, `start_from`, and default flow |
| `TestHappyPath` | Full pipeline runs extract → classify → validate → generate → `completed` |
| `TestReviewPause` | Pipeline pauses at "reviewing" when items need attention |
| `TestExtractionFailure` | Extraction failure stops pipeline cleanly with error report |
| `TestRetryLogic` | Transient errors retry 3× with back-off; permanent errors raise immediately |

**All 9 tests pass** (8 pipeline + 1 existing E2E golden).

---

## Complete Project Lifecycle

```
draft  →  (upload files)  →  draft
       →  POST /process   →  extracting → extracted
       →  classifying → classified
       →  reviewing  ←  CA reviews  →  validated
       →  validating → validated
       →  generating → completed

       →  error  (at any step)  →  POST /retry  →  resumes from failed step
```

---

## Files Created / Modified

| File | Task |
|------|------|
| `backend/app/services/pipeline/__init__.py` | Package |
| `backend/app/services/pipeline/orchestrator.py` | 8.1 |
| `backend/app/services/pipeline/background.py` | 8.2 |
| `backend/app/services/pipeline/error_handler.py` | 8.4 |
| `backend/app/services/pipeline/hooks.py` | 8.6 |
| `backend/app/api/v1/endpoints/pipeline.py` | 8.3 / 8.5 |
| `backend/app/api/v1/router.py` | Updated |
| `backend/tests/test_pipeline_integration.py` | 8.7 |
