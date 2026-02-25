# Task 3.2: Health Checks + /me Endpoint

> **Phase:** 03 - API CRUD Endpoints
> **Depends on:** Task 3.1 (auth middleware exists)
> **Agent reads:** CLAUDE.md → API Design Patterns
> **Time estimate:** 10 minutes

---

## Objective

Expand health check endpoints and create the `/me` endpoint that returns the current authenticated user's information.

---

## What to Do

### Step 1: Organize API Router Structure

Create a v1 router structure:
- File: `backend/app/api/v1/router.py` — main v1 router that includes all sub-routers
- File: `backend/app/api/v1/endpoints/auth.py` — auth-related endpoints
- File: `backend/app/api/v1/endpoints/health.py` — health endpoints

Update `backend/main.py` to include the v1 router at prefix `/api/v1`

Keep the root `/health` endpoint on main.py (no auth required for basic health).

### Step 2: Health Endpoints (NO auth required)

- `GET /health` → `{"status": "ok", "version": "0.1.0", "environment": "development"}`
- `GET /health/db` → checks Supabase connection (already exists from Phase 01)
- `GET /health/llm` → checks Gemini API key by making a tiny test call
  - Call Gemini with a 1-token prompt like "Hi"
  - Return `{"status": "ok", "model": "gemini-2.0-flash"}` on success
  - Return `{"status": "error", "message": "..."}` on failure
  - This confirms the API key works before we need it in Phase 04

### Step 3: /me Endpoint (auth required)

- `GET /api/v1/me` → returns current user info

Response:
```json
{
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "owner",
    "firm": {
      "id": "uuid",
      "name": "Ashutosh CA Firm",
      "plan": "free"
    }
  }
}
```

This fetches user info AND their firm info in one call.

### Step 4: Standard Response Format

Create a response helper in `backend/app/models/response.py`:
- Success: `{"data": ..., "error": null}`
- Error: `{"data": null, "error": {"message": "...", "code": "..."}}`

All future endpoints will use this format.

---

## What NOT to Do

- Don't create CRUD endpoints yet (those are tasks 3.3-3.7)
- Don't create user management endpoints (signup, update profile, etc.)
- Don't make health endpoints require auth

---

## Verification

- [ ] `GET /health` → returns OK (no auth needed)
- [ ] `GET /health/db` → returns connected
- [ ] `GET /health/llm` → returns OK (Gemini key works)
- [ ] `GET /api/v1/me` without token → 401
- [ ] `GET /api/v1/me` with valid token → returns user + firm info
- [ ] Response format matches the standard `{"data": ..., "error": null}` pattern
- [ ] Swagger UI at `/docs` shows all endpoints organized by tags

---

## Done → Move to task-3.3-client-crud.md
