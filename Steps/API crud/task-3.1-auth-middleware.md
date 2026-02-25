# Task 3.1: Auth Middleware — Verify Supabase JWT

> **Phase:** 03 - API CRUD Endpoints
> **Depends on:** Phase 02 complete (users table exists, auth configured)
> **Agent reads:** CLAUDE.md → API Design Patterns, Coding Standards → Python
> **Time estimate:** 15 minutes

---

## Objective

Create a FastAPI dependency that extracts and verifies the Supabase JWT token from every request, returning the authenticated user's info including their firm_id.

---

## What to Do

### Step 1: Create Auth Module
File: `backend/app/core/auth.py`

Create a `get_current_user` dependency that:
1. Extracts `Authorization: Bearer <token>` from request headers
2. Decodes and verifies the JWT using the Supabase JWT secret (from env vars)
3. Extracts the `sub` field (this is the user's auth.users ID)
4. Queries the `users` table to get: user_id, firm_id, email, full_name, role
5. Returns a `CurrentUser` Pydantic model with all these fields

### Step 2: Create CurrentUser Model
File: `backend/app/models/user.py`

```
CurrentUser:
  - id: UUID
  - firm_id: UUID
  - email: str
  - full_name: str
  - role: str (owner / ca / staff)
```

### Step 3: Error Handling

Return proper HTTP errors:
- No Authorization header → `401 Unauthorized` with message "Missing authentication token"
- Invalid/expired token → `401 Unauthorized` with message "Invalid or expired token"
- Token valid but user not in `users` table → `401 Unauthorized` with message "User not found"
- User exists but `is_active = false` → `403 Forbidden` with message "Account is deactivated"

### Step 4: Create a Role-Based Dependency (optional but useful)

Create `require_role(allowed_roles)` — a dependency factory that checks if the current user has one of the allowed roles:
- `require_role(["owner"])` — only firm owners
- `require_role(["owner", "ca"])` — owners and CAs
- Returns 403 if user's role doesn't match

---

## What NOT to Do

- Don't build a login/signup endpoint (Supabase Auth handles that client-side)
- Don't create session management or cookies
- Don't store tokens in the database
- Don't create user registration endpoints
- Don't handle OAuth or social login

---

## Verification

- [ ] Request with no token → 401 with clear message
- [ ] Request with random string as token → 401
- [ ] Request with valid Supabase token → proceeds (test using Supabase dashboard → Generate Token, or sign in via frontend)
- [ ] `CurrentUser` object has correct firm_id, email, role
- [ ] Deactivated user → 403
- [ ] Import works: `from app.core.auth import get_current_user`

---

## Done → Move to task-3.2-health-me-endpoints.md
