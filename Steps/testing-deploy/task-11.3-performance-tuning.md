# Task 11.3: Performance Tuning

> **Phase:** 11 - Testing & Production Deploy
> **Depends on:** All backend endpoints built
> **Time estimate:** 15 minutes

---

## Objective

Ensure all API endpoints respond within acceptable time limits and database queries are optimized.

---

## What to Do

### Performance Targets

| Endpoint Type | Target | Max Acceptable |
|--------------|--------|----------------|
| Health checks | < 50ms | 200ms |
| List endpoints | < 200ms | 500ms |
| Single item GET | < 100ms | 300ms |
| Create/Update | < 200ms | 500ms |
| Dashboard stats | < 300ms | 1000ms |
| Progress poll | < 50ms | 200ms |
| File upload | < 2s (per MB) | 5s |
| Pipeline process | N/A (async) | N/A |

### Step 1: Database Indexes

Add indexes for frequently queried columns:

```sql
-- Firm-scoped queries (used in every RLS policy)
CREATE INDEX idx_clients_firm_id ON clients(firm_id);
CREATE INDEX idx_cma_projects_firm_id ON cma_projects(firm_id);
CREATE INDEX idx_cma_projects_client_id ON cma_projects(client_id);
CREATE INDEX idx_cma_projects_status ON cma_projects(status);
CREATE INDEX idx_uploaded_files_project_id ON uploaded_files(cma_project_id);
CREATE INDEX idx_review_queue_firm_id ON review_queue(firm_id);
CREATE INDEX idx_review_queue_project_status ON review_queue(cma_project_id, status);
CREATE INDEX idx_precedents_firm_term ON classification_precedents(firm_id, source_term);
CREATE INDEX idx_audit_log_entity ON audit_log(entity_type, entity_id);
```

### Step 2: Query Optimization

- Dashboard stats: use a single query with CTEs instead of multiple queries
- Client list with CMA count: use LEFT JOIN + GROUP BY, not N+1 queries
- Project list: use JOIN for client_name, not separate queries
- Review queue: use compound index for firm_id + status filter

### Step 3: API Response Timing

Add middleware to log response times:

```python
@app.middleware("http")
async def add_timing(request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = (time.time() - start) * 1000
    response.headers["X-Response-Time"] = f"{duration:.0f}ms"
    if duration > 500:
        logger.warning(f"Slow endpoint: {request.url.path} took {duration:.0f}ms")
    return response
```

### Step 4: Frontend Performance

- Ensure React Query caching is configured (staleTime: 30s for lists, 5min for static data)
- Lazy load non-critical components (analytics page, precedents page)
- Optimize bundle size: check with `next build` output

---

## What NOT to Do

- Don't add indexes you don't need (they slow down writes)
- Don't prematurely optimize (we have 5 CMAs/month — focus on correctness first)
- Don't add Redis caching (overkill for V1 scale)

---

## Verification

- [ ] All list endpoints < 200ms with 50 rows of test data
- [ ] Dashboard stats < 300ms
- [ ] Progress poll < 50ms
- [ ] No N+1 queries in Supabase logs
- [ ] `X-Response-Time` header on all responses
- [ ] Slow queries (>500ms) logged as warnings
- [ ] Frontend bundle size < 500KB (first load)

---

## Done → Move to task-11.4-error-monitoring.md
