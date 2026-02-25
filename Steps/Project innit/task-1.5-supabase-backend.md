# Task 1.5: Connect Supabase Client (Backend)

> **Phase:** 01 - Project Initialization
> **Depends on:** Task 1.3 (backend running), Task 1.4 (env vars configured)
> **Agent reads:** CLAUDE.md → Database Tables section (for reference only — don't create tables yet)
> **Time estimate:** 10 minutes

---

## Objective

Create a Supabase client utility in the backend and add a database health check endpoint that confirms the connection works.

---

## What to Do

### Step 1: Create Supabase Client
File: `backend/app/db/supabase_client.py`

- Import supabase library
- Read SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY from config
- Create and export a Supabase client instance
- Export a function `get_supabase()` that returns the client
- Handle connection errors gracefully (don't crash the app if Supabase is down)

### Step 2: Add Database Health Endpoint
In `backend/main.py`, add:

- `GET /health/db` endpoint that:
  - Calls Supabase with a simple query (e.g., check if connection works)
  - Returns `{"status": "connected", "project": "cma-autofill"}` on success
  - Returns `{"status": "error", "message": "reason"}` on failure
  - Should NOT crash — always returns JSON, never a 500 error

### Step 3: Create a basic test
File: `backend/tests/test_health.py`

- Test that `GET /health` returns 200 and `{"status": "ok"}`
- Test that `GET /health/db` returns 200 (may be "connected" or "error" depending on env)
- Use FastAPI TestClient

---

## What NOT to Do

- Don't create any database tables (that's Phase 02)
- Don't set up RLS policies
- Don't create complex query utilities or ORM layers
- Don't add any endpoints beyond health checks
- Don't use the anon key — backend always uses service_role key

---

## Verification

- [ ] Start backend → `localhost:8000/health/db` returns `{"status": "connected"}`
- [ ] If you temporarily break the Supabase URL → returns `{"status": "error"}` (not a crash)
- [ ] `cd backend && pytest tests/test_health.py` → tests pass
- [ ] No import errors when backend starts

---

## Done → Move to task-1.6-supabase-frontend.md
