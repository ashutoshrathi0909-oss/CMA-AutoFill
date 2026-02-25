# Task 11.2: Security Hardening

> **Phase:** 11 - Testing & Production Deploy
> **Depends on:** All phases built
> **Time estimate:** 20 minutes

---

## Objective

Verify and strengthen security before going to production. CMA documents contain sensitive financial data — security is non-negotiable.

---

## What to Do

### Checklist 1: Row Level Security (RLS)

Verify EVERY table has RLS enabled and policies are correct:

```sql
-- Run this query to check RLS status
SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname = 'public';
```

For each table, verify:
- [ ] `firms` — users can only see their own firm
- [ ] `users` — users can only see users in their firm
- [ ] `clients` — firm_id filter on all operations
- [ ] `cma_projects` — firm_id filter
- [ ] `uploaded_files` — through project's firm_id
- [ ] `generated_files` — through project's firm_id
- [ ] `review_queue` — firm_id filter
- [ ] `classification_precedents` — firm_id filter (or global)
- [ ] `llm_usage_log` — firm_id filter
- [ ] `audit_log` — firm_id filter

**Test:** Sign in as Firm A user → try to access Firm B's data via direct API call → must get 404 (not 403).

### Checklist 2: API Security

- [ ] All endpoints require authentication (except /health)
- [ ] JWT tokens verified on every request
- [ ] Expired tokens rejected → 401
- [ ] Invalid tokens rejected → 401
- [ ] CORS configured: only allow frontend domain
- [ ] Rate limiting on auth endpoints (prevent brute force)
- [ ] Rate limiting on LLM endpoints (prevent abuse)
- [ ] File upload size limit enforced (10MB)
- [ ] File type validation on backend (not just frontend)

### Checklist 3: Input Validation

- [ ] All string inputs sanitized (no SQL injection via Supabase client — but double-check)
- [ ] UUID parameters validated (malformed UUID → 422, not 500)
- [ ] Pagination params bounded (per_page max 100)
- [ ] Financial amounts validated (must be numbers, reasonable range)
- [ ] File names sanitized (no path traversal: `../../etc/passwd`)

### Checklist 4: Data Protection

- [ ] Supabase Storage bucket is PRIVATE (not public)
- [ ] Signed URLs expire after 1 hour
- [ ] No sensitive data in URL parameters
- [ ] No financial data in error messages
- [ ] Audit log doesn't contain actual amounts (just actions and IDs)
- [ ] Environment variables not exposed to frontend (only NEXT_PUBLIC_ ones)

### Checklist 5: Rate Limiting

Add to FastAPI:
```python
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/projects/{id}/process")
@limiter.limit("10/hour")  # max 10 pipeline runs per hour
async def process_project(...):
```

Rate limits:
- Login: 5 attempts per minute per IP
- File upload: 20 per hour per user
- Pipeline process: 10 per hour per user
- API general: 100 requests per minute per user

### Implementation

Create: `backend/app/core/security.py`
- CORS middleware configuration
- Rate limiter setup
- Input validation utilities

---

## What NOT to Do

- Don't skip RLS testing — it's the most critical security layer
- Don't rely only on frontend validation (backend must validate too)
- Don't log full request bodies (may contain financial data)
- Don't use overly strict rate limits that block normal usage

---

## Verification

- [ ] RLS: Firm A user cannot see Firm B's data (test every table)
- [ ] Unauthenticated requests → 401 on all protected endpoints
- [ ] Expired JWT → 401
- [ ] CORS: requests from unauthorized origins blocked
- [ ] File upload: .exe file rejected, 15MB file rejected
- [ ] Rate limit: 11th pipeline run in an hour → 429 Too Many Requests
- [ ] Storage bucket: direct URL access without signed URL → 403
- [ ] No env vars leaked in frontend bundle

---

## Done → Move to task-11.3-performance-tuning.md
