# Task 11.1: End-to-End Tests (Playwright)

> **Phase:** 11 - Testing & Production Deploy
> **Depends on:** Phases 09-10 (all frontend pages built)
> **MCP:** Playwright MCP
> **Time estimate:** 25 minutes

---

## Objective

Write Playwright E2E tests that simulate a real CA using the app from login to CMA download.

---

## What to Do

### Setup
```bash
cd frontend
npm install -D @playwright/test
npx playwright install
```

Create: `frontend/playwright.config.ts`
Create: `frontend/e2e/` folder for test files

### Test 1: Authentication Flow
File: `frontend/e2e/auth.spec.ts`

```
1. Navigate to /dashboard → redirected to /login
2. Enter test email → click "Send Magic Link"
3. (Mock Supabase auth callback)
4. Verify: redirected to /dashboard
5. Verify: user name appears in sidebar
6. Click Sign Out → redirected to /login
```

### Test 2: Client Management
File: `frontend/e2e/clients.spec.ts`

```
1. Navigate to /clients
2. Verify: empty state shown
3. Click "Add Client" → fill form (name, entity_type)
4. Submit → verify client appears in list
5. Click client → verify details shown
6. Edit client name → verify updated
7. Search by name → verify filter works
```

### Test 3: Full CMA Journey (Happy Path)
File: `frontend/e2e/cma-journey.spec.ts`

This is the CRITICAL test — the full user journey:
```
1. Create client "Test Company" (trading)
2. Create CMA project (2024-25)
3. Navigate to project detail
4. Upload test Excel file (P&L)
5. Click "Process CMA"
6. Watch processing view → wait for completion or review
7. If review needed: approve all items
8. Click "Generate CMA"
9. Wait for generation
10. Download CMA file
11. Verify: file downloads successfully
```

### Test 4: Review Queue
File: `frontend/e2e/review.spec.ts`

```
1. Process a project that creates review items
2. Navigate to review queue
3. Approve first item → verify it disappears
4. Correct second item → select different row → verify resolved
5. Skip third item → verify skipped
6. Verify remaining count updates
```

### Test 5: Error Handling
File: `frontend/e2e/errors.spec.ts`

```
1. Upload invalid file type → verify error shown
2. Access non-existent project → verify 404 page
3. Try to process empty project → verify error message
```

### Test Configuration

- Use a test Supabase instance (or mock auth)
- Seed test data before each test suite
- Clean up after tests
- Take screenshots on failure
- Run in headless mode for CI

---

## What NOT to Do

- Don't test API endpoints directly (backend tests handle that — Phase 08)
- Don't test every UI variation (focus on critical paths)
- Don't use real Gemini API in E2E tests (mock it — too slow and costly)
- Don't test responsive design in E2E (manual QA is sufficient for V1)

---

## Verification

- [ ] `npx playwright test` → all tests pass
- [ ] Full CMA journey test completes end-to-end
- [ ] Screenshots captured on failure for debugging
- [ ] Tests run in <3 minutes total
- [ ] Tests work in CI environment (headless)

---

## Done → Move to task-11.2-security-hardening.md
