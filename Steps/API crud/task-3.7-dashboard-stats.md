# Task 3.7: Dashboard Stats Endpoint

> **Phase:** 03 - API CRUD Endpoints
> **Depends on:** Tasks 3.3-3.6 (all CRUD endpoints exist)
> **Agent reads:** CLAUDE.md → API Design Patterns
> **Time estimate:** 10 minutes

---

## Objective

Create a single endpoint that returns aggregate statistics for the firm's dashboard. This powers the dashboard cards in the frontend (Phase 09).

---

## What to Do

### Create File
- `backend/app/api/v1/endpoints/dashboard.py`

### Endpoint

`GET /api/v1/dashboard/stats`

Returns aggregated data for the current firm:

```json
{
  "data": {
    "total_clients": 12,
    "active_clients": 10,
    "total_projects": 25,
    "projects_by_status": {
      "draft": 5,
      "extracting": 1,
      "classifying": 0,
      "reviewing": 2,
      "validating": 0,
      "generating": 0,
      "completed": 15,
      "error": 2
    },
    "pending_reviews": 8,
    "this_month": {
      "projects_created": 3,
      "projects_completed": 2
    },
    "llm_usage": {
      "total_cost_usd": 0.0543,
      "total_tokens": 125000,
      "this_month_cost_usd": 0.0120
    },
    "recent_projects": [
      {
        "id": "uuid",
        "client_name": "Mehta Computers",
        "financial_year": "2024-25",
        "status": "completed",
        "updated_at": "2026-02-20T10:30:00Z"
      }
    ]
  }
}
```

### Query Logic

All queries are scoped to `firm_id = current_user.firm_id`:

1. **total_clients:** COUNT from clients where is_active = true
2. **active_clients:** same (for now; later could mean "has projects this year")
3. **total_projects:** COUNT from cma_projects
4. **projects_by_status:** GROUP BY status from cma_projects
5. **pending_reviews:** COUNT from review_queue where status = 'pending'
6. **this_month:** COUNT from cma_projects where created_at/updated_at in current month
7. **llm_usage:** SUM from llm_usage_log (total and current month)
8. **recent_projects:** Last 5 projects ordered by updated_at desc, joined with client name

### Performance

- Use a single database round-trip if possible (multiple queries in one call)
- Or use parallel async queries
- This endpoint will be called on every dashboard load — keep it fast

---

## What NOT to Do

- Don't create complex analytics or charts data
- Don't include per-client breakdowns (that's a future feature)
- Don't cache the results yet (premature optimization for 5 CMAs/month)
- Don't include any financial data from CMAs in the response

---

## Verification

- [ ] With seeded test data: returns correct counts (1 client, 1 project, 0 reviews)
- [ ] projects_by_status has all 8 status values (most will be 0)
- [ ] recent_projects includes client_name (joined)
- [ ] llm_usage returns 0 for now (no LLM calls made yet — that's fine)
- [ ] Endpoint is fast (<200ms)
- [ ] Requires auth → 401 without token
- [ ] Only shows data for current firm

---

## Phase 03 Complete! 🎉

All 7 tasks done. You now have:
- ✅ JWT auth middleware protecting all endpoints
- ✅ /me endpoint returning user + firm info
- ✅ Full CRUD for clients (create, list, search, update, soft-delete)
- ✅ Full CRUD for CMA projects (with status constraints)
- ✅ File upload to Supabase Storage
- ✅ File download via signed URLs
- ✅ Dashboard stats endpoint
- ✅ Audit logging on all operations
- ✅ Standard response format across all endpoints

**Next → Phase 04: Document Extraction (AI starts here!)**
