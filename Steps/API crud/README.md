# Phase 03: API CRUD Endpoints — Overview

> Complete these 7 tasks in order. Each task = one Claude Code agent session.
> No AI/LLM logic in this phase — just standard CRUD operations.
> Test every endpoint via Swagger UI (localhost:8000/docs) after each task.

| # | File | What It Does | Verify By |
|---|------|-------------|-----------|
| 3.1 | task-3.1-auth-middleware.md | JWT verification + get_current_user dependency | Unauthorized request → 401 |
| 3.2 | task-3.2-health-me-endpoints.md | Health checks + /me endpoint | /me returns user info |
| 3.3 | task-3.3-client-crud.md | Create, list, get, update, delete clients | CRUD works via Swagger |
| 3.4 | task-3.4-project-crud.md | Create, list, get, update CMA projects | Project linked to client |
| 3.5 | task-3.5-file-upload.md | Upload files to Supabase Storage | File appears in bucket |
| 3.6 | task-3.6-file-download.md | Download + list files for a project | Can download uploaded file |
| 3.7 | task-3.7-dashboard-stats.md | Aggregate stats endpoint for dashboard | Returns correct counts |

**Phase 03 result:** Full working API — auth protected, CRUD for all entities, file upload/download, dashboard stats.
