# Task 8.7: Pipeline Integration Tests

> **Phase:** 08 - Pipeline Orchestrator
> **Depends on:** All Phase 08 tasks complete
> **Time estimate:** 20 minutes

---

## Objective

Write comprehensive integration tests that prove the entire backend pipeline works end-to-end. These are the tests that must pass before starting frontend work.

---

## What to Do

### Create File
`backend/tests/test_pipeline_integration.py`

### Test 1: Happy Path (No Review Needed)

```
Setup: Create project with Mehta Computers files + skip_review=True
Run: POST /projects/{id}/process
Assert:
  - Pipeline runs to completion
  - Status transitions: draft → extracting → classifying → validating → generating → completed
  - CMA Excel file generated and downloadable
  - LLM usage logged
  - Audit trail complete
```

### Test 2: Happy Path (With Review)

```
Setup: Create project with files that have ambiguous items
Run: POST /projects/{id}/process
Assert:
  - Pipeline pauses at 'reviewing'
  - Review queue has items
  - Email notification sent (mock Resend, verify called)
Resolve: POST /review-queue/bulk-resolve (approve all)
Apply: POST /projects/{id}/apply-reviews
Resume: POST /projects/{id}/process (resumes from validate)
Assert:
  - Pipeline completes
  - CMA generated
  - Precedents created from reviews
```

### Test 3: Error Recovery

```
Setup: Project with files
Mock: Gemini API to fail on first call, succeed on retry
Run: POST /projects/{id}/process
Assert:
  - First classify attempt fails
  - Auto-retry succeeds
  - Pipeline completes normally
```

### Test 4: Full Failure + Manual Retry

```
Setup: Project with files
Mock: Gemini API to always fail
Run: POST /projects/{id}/process
Assert:
  - Pipeline stops at 'error'
  - Error message is user-friendly
Unmock: Gemini API
Run: POST /projects/{id}/retry
Assert:
  - Resumes from failed step (doesn't re-extract)
  - Completes successfully
```

### Test 5: Concurrent Safety

```
Setup: Two different projects
Run: POST /projects/{a}/process AND POST /projects/{b}/process simultaneously
Assert:
  - Both complete without interference
  - Data isolation maintained
Run: POST /projects/{a}/process while already processing
Assert:
  - 409 Conflict
```

### Test 6: Progress Tracking

```
Run: POST /projects/{id}/process
During: Poll GET /projects/{id}/progress every second
Assert:
  - progress_percent increases over time
  - current_step changes as pipeline progresses
  - is_processing = true during, false after
```

### Test 7: Golden Test (Upgraded)

Extend the Phase 06 golden test to run through the full orchestrator:
```
Input: Mehta Computers files (upload via API)
Run: Full pipeline through orchestrator
Assert:
  - Cell-by-cell accuracy >= 85%
  - Total cost < $0.02
  - Total time < 60 seconds
```

### Test Configuration

Create: `backend/tests/conftest.py` with:
- Test database setup (use Supabase test project or mock)
- Test user and firm fixtures
- Gemini API mock (for tests that shouldn't make real API calls)
- File upload fixtures (Mehta Computers files)
- Cleanup after each test

---

## What NOT to Do

- Don't skip the concurrent safety test — it catches real bugs
- Don't use real Gemini API for all tests (expensive) — mock for most, real for golden test
- Don't test UI (that's Phase 09-10)
- Don't leave test data in production database

---

## Verification

- [ ] All 7 tests pass
- [ ] Tests run in < 2 minutes total (with mocks)
- [ ] Golden test passes with real Gemini API
- [ ] No test data left in database after tests complete
- [ ] Tests can run in CI/CD (GitHub Actions)
- [ ] `pytest backend/tests/test_pipeline_integration.py -v` → all green

---

## Phase 08 Complete! 🎉

All 7 tasks done. You now have:
- ✅ Pipeline orchestrator chaining all steps
- ✅ Background processing (API returns immediately)
- ✅ Real-time progress tracking via polling
- ✅ Error recovery with retry and resume
- ✅ One-click process + upload-and-process endpoints
- ✅ Pipeline hooks for notifications and audit logging
- ✅ Comprehensive integration tests

**THE ENTIRE BACKEND IS COMPLETE.**

Pipeline: Upload → Extract → Classify → Review → Validate → Generate CMA

**Next → Phase 09: Frontend Shell (the UI begins!)**
