# Task 3.4: CMA Project CRUD Endpoints

> **Phase:** 03 - API CRUD Endpoints
> **Depends on:** Task 3.3 (client endpoints exist, patterns established)
> **Agent reads:** CLAUDE.md → Database Tables → cma_projects
> **Time estimate:** 15 minutes

---

## Objective

Create CRUD endpoints for CMA projects. A project is linked to a client and tracks the entire CMA pipeline from draft to completion.

---

## What to Do

### Create Files
- `backend/app/api/v1/endpoints/projects.py` — route handlers
- `backend/app/models/project.py` — Pydantic request/response models

### Pydantic Models

**ProjectCreate (request body):**
- client_id: UUID (required — must be a valid client in current firm)
- financial_year: str (required, format: '2024-25')
- bank_name: str | None
- loan_type: str | None (must be 'term_loan' | 'working_capital' | 'cc_od' | 'other')
- loan_amount: float | None

**ProjectUpdate (request body):**
- bank_name, loan_type, loan_amount — all optional
- Can NOT change client_id or financial_year after creation

**ProjectResponse (response):**
- All table fields + id, created_at, updated_at
- client_name: str (from joined clients table)
- client_entity_type: str
- uploaded_file_count: int
- review_pending_count: int (number of unresolved review items)

**ProjectListResponse (response):**
- items: list[ProjectResponse]
- total, page, per_page

### Endpoints

| Method | Path | What It Does |
|--------|------|-------------|
| POST | `/api/v1/projects` | Create a new CMA project |
| GET | `/api/v1/projects` | List all projects for current firm |
| GET | `/api/v1/projects/{id}` | Get project details + pipeline status |
| PUT | `/api/v1/projects/{id}` | Update project (only if status is 'draft') |
| DELETE | `/api/v1/projects/{id}` | Soft delete (only if status is 'draft') |

### Business Rules

- `firm_id` set from authenticated user — never from request body
- `created_by` set to current user's ID
- On create: validate that `client_id` belongs to the current firm → 404 if not
- On create: check unique constraint (client_id + financial_year) → 409 Conflict if duplicate
- Can ONLY update/delete projects in 'draft' status. If status is anything else → 409 with message "Cannot modify project in '{status}' status"
- List supports:
  - Pagination: `?page=1&per_page=20`
  - Filter by status: `?status=draft` or `?status=completed`
  - Filter by client: `?client_id=uuid`
  - Sort: `?sort_by=created_at&sort_order=desc` (default)
- GET single project includes full pipeline status info (progress %, current step, error message)

### Audit Logging

Log all create/update/delete operations to `audit_log`.

---

## What NOT to Do

- Don't create pipeline execution endpoints (that's Phase 08)
- Don't create file upload within project endpoints (that's task 3.5)
- Don't allow modifying projects that are mid-pipeline
- Don't hard-delete — soft delete by setting status to 'draft' + is_active logic, or just prevent deletion of non-draft projects

---

## Verification

- [ ] POST with valid client_id → 201, project created with status 'draft'
- [ ] POST with client_id from another firm → 404
- [ ] POST duplicate (same client + financial year) → 409 Conflict
- [ ] GET list → shows projects with client_name joined
- [ ] GET list `?status=draft` → filters correctly
- [ ] GET single → includes pipeline_progress, uploaded_file_count, review_pending_count
- [ ] PUT on draft project → updates correctly
- [ ] PUT on non-draft project → 409 "Cannot modify"
- [ ] DELETE on draft → works
- [ ] DELETE on non-draft → 409 "Cannot delete"
- [ ] All responses follow standard format

---

## Done → Move to task-3.5-file-upload.md
