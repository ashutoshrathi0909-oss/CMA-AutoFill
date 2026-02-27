# Phase 03 Audit Report — Issues, Risks & Fixes

> **Audited:** 2026-02-26
> **Scope:** All 7 tasks of Phase 03 (API CRUD Endpoints)
> **Files reviewed:** Every `.py` file under `backend/app/`, all task specs under `Steps/API crud/`

---

## Table of Contents

1. [Critical Issues](#critical-issues)
   - C1: Zero Test Coverage
   - C2: Project DELETE Is a Hard Delete
   - C3: Supabase Client Re-Created on Every Request
2. [Moderate Issues](#moderate-issues)
   - M1: Dead Code in storage.py
   - M2: Health Endpoint Missing Spec Fields
   - M3: /health/llm Behind API Prefix
   - M4: Dashboard Loads All Data Into Memory
   - M5: Search Parameter Not Sanitized
   - M6: review_queue firm_id Assumption
3. [Minor Issues](#minor-issues)
   - m1: GEMINI.md Outdated
   - m2: Unused Import in projects.py
   - m3: All Endpoints Are Synchronous
   - m4: CORS Only Allows localhost
   - m5: Missing email-validator Dependency

---

## Critical Issues

### C1: Zero Test Coverage

**Location:** `backend/tests/` — empty directory (only `__init__.py`)

**What's wrong:**
There are no tests for any of the 7 tasks delivered in Phase 03. The `tests/` directory contains a single empty `__init__.py` file.

**How this can go wrong:**
- **Silent regressions:** When Phase 04-08 adds extraction, classification, and pipeline logic, any change to the CRUD layer (models, auth, response format) could break existing endpoints. Without tests, you won't know until a user hits the bug in production.
- **Refactoring fear:** You'll eventually need to refactor (e.g., making endpoints async, changing the Supabase client pattern). Without tests, every refactor is a gamble.
- **Integration failures:** The frontend team (or you, in Phase 09-10) will build against these API contracts. If the contract silently changes, the frontend breaks with no warning.
- **Spec violations undetected:** Some issues in this very audit (like the hard-delete bug) would have been caught by even basic tests.

**Your own rules violated:**
- CLAUDE.md: "Never skip tests — every feature needs at least basic tests"
- CLAUDE.md: "Every service function must have at least one test"

**How to fix:**

Create test files for each endpoint group. At minimum:

```
backend/tests/
├── conftest.py                 # Shared fixtures (mock Supabase, mock auth)
├── test_auth.py                # Auth middleware tests
├── test_clients.py             # Client CRUD tests
├── test_projects.py            # Project CRUD tests
├── test_files.py               # File upload/download tests
├── test_dashboard.py           # Dashboard stats tests
└── test_storage.py             # Storage service tests
```

**Step 1:** Create `conftest.py` with test fixtures:

```python
# backend/tests/conftest.py
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from app.models.user import CurrentUser
from uuid import uuid4

# A reusable mock user
TEST_USER = CurrentUser(
    id=uuid4(),
    firm_id=uuid4(),
    email="test@example.com",
    full_name="Test User",
    role="owner"
)

@pytest.fixture
def mock_current_user():
    """Override the get_current_user dependency."""
    return TEST_USER

@pytest.fixture
def client(mock_current_user):
    """FastAPI test client with mocked auth."""
    from main import app
    from app.core.auth import get_current_user

    app.dependency_overrides[get_current_user] = lambda: mock_current_user
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
def mock_supabase():
    """Mock Supabase client to avoid real DB calls in unit tests."""
    with patch("app.db.supabase_client.get_supabase") as mock:
        db = MagicMock()
        mock.return_value = db
        yield db
```

**Step 2:** Write tests for each endpoint. Example for clients:

```python
# backend/tests/test_clients.py
def test_create_client_success(client, mock_supabase):
    mock_supabase.table().insert().execute.return_value.data = [{
        "id": "some-uuid", "firm_id": "firm-uuid", "name": "Test Corp",
        "entity_type": "trading", "is_active": True,
        "created_at": "2026-01-01T00:00:00Z", "updated_at": "2026-01-01T00:00:00Z",
        # ... other fields
    }]
    response = client.post("/api/v1/clients", json={
        "name": "Test Corp", "entity_type": "trading"
    })
    assert response.status_code == 201
    assert response.json()["data"]["name"] == "Test Corp"

def test_create_client_invalid_entity_type(client):
    response = client.post("/api/v1/clients", json={
        "name": "Test", "entity_type": "invalid"
    })
    assert response.status_code == 422

def test_create_client_no_auth():
    """Without the auth override, should get 401."""
    from main import app
    from fastapi.testclient import TestClient
    app.dependency_overrides.clear()
    c = TestClient(app)
    response = c.post("/api/v1/clients", json={"name": "X", "entity_type": "trading"})
    assert response.status_code == 401
```

**Step 3:** Add `pytest` and `httpx` to requirements.txt (httpx is already there).

**Step 4:** Run tests:
```bash
cd backend && python -m pytest tests/ -v
```

**Priority:** HIGH — do this before starting Phase 04.

---

### C2: Project DELETE Is a Hard Delete (Spec Says Soft Delete)

**Location:** `backend/app/api/v1/endpoints/projects.py`, line 156

**What's wrong:**
```python
db.table("cma_projects").delete().eq("id", project_id).eq("firm_id", str(current_user.firm_id)).execute()
```

This executes a real SQL `DELETE` statement. The row is permanently gone from the database.

**What the spec says:**
- Task 3.4: "Don't hard-delete"
- Task 3.4: "soft delete by setting status to 'draft' + is_active logic, or just prevent deletion of non-draft projects"
- The clients endpoint correctly uses soft delete (`is_active=False`)

**How this can go wrong:**
- **Data loss is irreversible.** If a CA accidentally deletes a project, all associated data relationships (uploaded files, extracted data, classification results) become orphaned. Even if those child records exist, the parent project is gone.
- **Audit trail becomes meaningless.** You log the delete in `audit_log`, but the referenced `entity_id` now points to a row that doesn't exist. You can't investigate what was deleted.
- **Foreign key cascades.** If `uploaded_files`, `extracted_data`, etc. have `ON DELETE CASCADE` on their `cma_project_id` foreign key, deleting the project silently deletes ALL child data too — files, extractions, classifications, reviews. Months of work vanished with one API call.
- **Inconsistency with clients.** Clients use soft delete, projects use hard delete. This inconsistent pattern will confuse future development.

**How to fix:**

Option A — Add `is_active` column to `cma_projects` (consistent with clients):
```python
# In projects.py, replace the delete endpoint:
@router.delete("/{project_id}", response_model=StandardResponse[dict])
def delete_project(project_id: str, current_user: CurrentUser = Depends(get_current_user)):
    db = get_supabase()
    check_resp = db.table("cma_projects").select("id, status").eq("id", project_id).eq("firm_id", str(current_user.firm_id)).execute()
    if not check_resp.data:
        raise HTTPException(status_code=404, detail="Project not found")

    if check_resp.data[0]["status"] != "draft":
        raise HTTPException(status_code=409, detail=f"Cannot delete project in '{check_resp.data[0]['status']}' status")

    # SOFT DELETE — mark inactive instead of removing the row
    db.table("cma_projects").update({"is_active": False}).eq("id", project_id).eq("firm_id", str(current_user.firm_id)).execute()

    db.table("audit_log").insert({
        "firm_id": str(current_user.firm_id),
        "user_id": str(current_user.id),
        "action": "delete_project",
        "entity_type": "cma_project",
        "entity_id": project_id,
        "metadata": {}
    }).execute()

    return StandardResponse(data={"success": True, "message": "Project deleted successfully"})
```

Option B — If the `cma_projects` table doesn't have an `is_active` column, you need to add it in Supabase:
```sql
ALTER TABLE cma_projects ADD COLUMN is_active boolean DEFAULT true;
```

Then update the `list_projects` query to filter out inactive:
```python
query = query.eq("is_active", True)  # Add to list_projects
```

**Priority:** HIGH — data loss bug.

---

### C3: Supabase Client Re-Created on Every Request

**Location:** `backend/app/db/supabase_client.py`

**What's wrong:**
```python
def get_supabase() -> Client:
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    return create_client(url, key)  # New client EVERY call
```

Every API request calls `get_supabase()` multiple times (once per DB query). Each call creates a brand new Supabase client with a new HTTP connection pool.

For example, the `list_clients` endpoint calls `get_supabase()` at least twice (once for clients query, once for CMA count query). The `dashboard/stats` endpoint calls it 5+ times.

**How this can go wrong:**
- **Connection exhaustion.** Each `create_client()` opens a new HTTP connection. Under load, this can exhaust the OS's available sockets/file descriptors. You'll see `ConnectionError` or `Too many open files` errors.
- **Increased latency.** Every request pays the cost of TCP handshake + TLS negotiation to Supabase. A cached client reuses connections.
- **Memory leaks.** Old client objects may not be garbage collected immediately, especially if they hold open connections. Over time, memory usage creeps up.
- **Rate limiting.** Supabase may see rapid connection creation as abusive behavior and throttle you.

**How to fix:**

Use a module-level singleton:

```python
# backend/app/db/supabase_client.py
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

_supabase_client: Client | None = None

def get_supabase() -> Client:
    global _supabase_client
    if _supabase_client is None:
        url = os.getenv("SUPABASE_URL", "")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
        if not url or not key:
            raise ValueError("Supabase URL or Key not found in environment variables.")
        _supabase_client = create_client(url, key)
    return _supabase_client
```

This creates the client once on first use and reuses it for all subsequent requests. The Supabase Python client is thread-safe for read operations.

**Priority:** HIGH — affects every single API call's performance.

---

## Moderate Issues

### M1: Dead Code — `upload_file()` in storage.py

**Location:** `backend/app/services/storage.py:7-26` and `backend/app/api/v1/endpoints/files.py:8`

**What's wrong:**
The `upload_file()` function exists in `storage.py` and is imported in `files.py`, but the actual upload logic is written inline in the endpoint (lines 45-55 of `files.py`). The imported function is never called.

**How this can go wrong:**
- **Confusion for future developers.** Someone sees `upload_file` in storage.py and assumes it's the upload path. They modify it, test it, and nothing changes because the real logic is in the endpoint.
- **Inconsistent behavior.** The inline code and the `upload_file()` function have slightly different implementations (e.g., the inline code adds space-to-underscore sanitization that the function doesn't).
- **Wasted maintenance.** Any bug fix needs to be applied to the right place. Dead code creates ambiguity about which is "the real one."

**How to fix:**

Either use the function or remove it. Best approach — use it:

```python
# In files.py, replace the inline upload (lines 45-55) with:
from app.services.storage import upload_file

try:
    storage_path = upload_file(
        firm_id=str(current_user.firm_id),
        project_id=project_id,
        file_name=file.filename,
        file_bytes=file_bytes,
        content_type=file.content_type
    )
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Failed to upload to storage: {str(e)}")
```

And update `upload_file()` in storage.py to include the filename sanitization:
```python
def upload_file(firm_id: str, project_id: str, file_name: str, file_bytes: bytes, content_type: str) -> str:
    db = get_supabase()
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    safe_filename = file_name.replace(" ", "_")
    storage_path = f"{firm_id}/{project_id}/{timestamp}_{safe_filename}"
    db.storage.from_("cma-files").upload(
        file=file_bytes,
        path=storage_path,
        file_options={"content-type": content_type}
    )
    return storage_path
```

---

### M2: Health Endpoint Missing Spec Fields

**Location:** `backend/main.py:18-20`

**What's wrong:**
Current response:
```json
{"status": "ok", "service": "cma-autofill-api"}
```

Spec (task 3.2) requires:
```json
{"status": "ok", "version": "0.1.0", "environment": "development"}
```

**How this can go wrong:**
- **Deployment debugging.** When you deploy to Vercel/Railway, you won't be able to confirm which version is running or which environment (dev/staging/prod) the instance is configured for.
- **Health check monitoring.** If you set up uptime monitoring (e.g., UptimeRobot, Vercel health checks), the response schema won't match what monitoring tools expect.

**How to fix:**
```python
# In main.py
@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "version": "0.1.0",
        "environment": os.getenv("ENVIRONMENT", "development")
    }
```

---

### M3: `/health/llm` Is Behind the `/api/v1` Prefix

**Location:** `backend/app/api/v1/router.py:12`

**What's wrong:**
The health router is mounted inside the v1 API router:
```python
api_router.include_router(health.router, prefix="/health", tags=["health"])
```

Combined with `main.py:8`:
```python
app.include_router(api_router, prefix="/api/v1")
```

The actual path becomes `/api/v1/health/llm`, not `/health/llm`.

**How this can go wrong:**
- **Health checks shouldn't require API versioning.** If you ever deprecate `/api/v1`, the health check disappears.
- **Load balancer confusion.** Health check endpoints are typically at predictable root paths (`/health`, `/health/db`, `/health/llm`). Putting them behind `/api/v1` breaks standard conventions.
- **The LLM health check is inconsistent with `/health` and `/health/db`.** Those two are at root level (defined in `main.py`), but `/health/llm` is under `/api/v1/`.

**How to fix:**

Move the LLM health check to `main.py` alongside the other health endpoints:

```python
# In main.py, add:
@app.get("/health/llm")
def health_llm():
    # Move the logic from health.py here
    ...
```

Then either remove `health.py` from the v1 router, or keep it but also register it at root level.

---

### M4: Dashboard Loads All Data Into Memory

**Location:** `backend/app/api/v1/endpoints/dashboard.py`

**What's wrong:**
The dashboard endpoint fetches ALL rows from multiple tables and counts them in Python:
```python
# Line 16: Fetches ALL clients
clients_res = db.table("clients").select("is_active").eq("firm_id", firm_id).execute()
total_clients = len(clients_res.data)

# Line 21: Fetches ALL projects with all fields
projects_res = db.table("cma_projects").select("id, status, created_at, updated_at").eq("firm_id", firm_id).execute()

# Line 68: Fetches ALL LLM usage logs
llm_res = db.table("llm_usage_log").select("cost_usd, input_tokens, output_tokens, created_at").eq("firm_id", firm_id).execute()
```

**How this can go wrong:**
- **Memory blowup.** A firm with 500 clients, 2000 projects, and 50,000 LLM log entries would load all of that into Python memory on every dashboard page load.
- **Slow response times.** The spec says "<200ms." With 10,000+ rows being transferred over the network and counted in Python, this could take seconds.
- **Supabase row limits.** Supabase PostgREST has a default limit of 1000 rows per query. If a firm has >1000 projects, the counts will be wrong (silently capped at 1000).

**How to fix:**

Use Supabase's `count` feature and PostgreSQL aggregation instead of fetching all rows:

```python
# Instead of fetching all clients and counting in Python:
clients_res = db.table("clients").select("id", count="exact").eq("firm_id", firm_id).eq("is_active", True).execute()
active_clients = clients_res.count or 0

# For projects_by_status, use separate count queries or an RPC function:
for status_val in ["draft", "extracting", "classifying", "reviewing", "validating", "generating", "completed", "error"]:
    res = db.table("cma_projects").select("id", count="exact").eq("firm_id", firm_id).eq("status", status_val).execute()
    projects_by_status[status_val] = res.count or 0

# For LLM usage, create a Supabase RPC (SQL function):
# CREATE FUNCTION get_llm_usage_stats(p_firm_id uuid)
# RETURNS TABLE(total_cost numeric, total_tokens bigint, month_cost numeric)
# Then call: db.rpc("get_llm_usage_stats", {"p_firm_id": firm_id}).execute()
```

For MVP: this works fine at 5 CMAs/month. But fix it before scaling.

---

### M5: Search Parameter Not Sanitized for PostgREST

**Location:** `backend/app/api/v1/endpoints/clients.py:51`

**What's wrong:**
```python
query = query.ilike("name", f"%{search}%")
```

The `search` string is directly interpolated into the `ilike` pattern. PostgREST's `ilike` uses `%` as wildcard and `_` as single-character wildcard.

**How this can go wrong:**
- A search for `100%` would match any name starting with `100` (because `%` is a wildcard).
- A search for `A_B` would match `AAB`, `AXB`, `A1B` etc. (because `_` matches any single character).
- This isn't a SQL injection risk (Supabase handles that), but it produces incorrect results.

**How to fix:**

Escape the special PostgREST pattern characters:
```python
if search:
    # Escape PostgREST LIKE wildcards in user input
    safe_search = search.replace("%", "\\%").replace("_", "\\_")
    query = query.ilike("name", f"%{safe_search}%")
```

---

### M6: review_queue `firm_id` Assumption

**Location:** `backend/app/api/v1/endpoints/dashboard.py:64`

**What's wrong:**
```python
reviews_res = db.table("review_queue").select("id").eq("firm_id", firm_id).eq("status", "pending").execute()
```

This assumes `review_queue` has a direct `firm_id` column. Looking at the database schema design (Phase 02, task 2.4), the `review_queue` may only have `cma_project_id` and rely on a join through `cma_projects` to reach `firm_id`.

**How this can go wrong:**
- If `review_queue` doesn't have `firm_id`, the `.eq("firm_id", firm_id)` filter either errors out or returns zero rows always — giving a permanently wrong "0 pending reviews" on the dashboard.
- The dashboard would silently show incorrect data without any error visible to the user.

**How to fix:**

Verify the table schema. If `firm_id` exists, the code is fine. If not, join through `cma_projects`:

```python
# Option 1: If review_queue has firm_id — keep as is
# Option 2: If it doesn't, query via project join:
reviews_res = db.table("review_queue").select(
    "id, cma_projects!inner(firm_id)"
).eq("cma_projects.firm_id", firm_id).eq("status", "pending").execute()
pending_reviews = len(reviews_res.data) if reviews_res.data else 0
```

Or add `firm_id` to `review_queue` for denormalized fast queries (recommended for a column you'll filter on frequently).

---

## Minor Issues

### m1: GEMINI.md Outdated

**Location:** `GEMINI.md:63-73`

The roadmap shows only Phase 01 as complete. Phase 02 and 03 are unchecked even though both are committed and done.

**Risk:** Any AI agent reading GEMINI.md will think Phase 02-03 aren't done and might try to redo them.

**Fix:** Update the checkboxes:
```markdown
- [x] Phase 01: Project Init
- [x] Phase 02: Database schema & RLS
- [x] Phase 03: API CRUD
- [ ] Phase 04: Document extraction
```

---

### m2: Unused Import in projects.py

**Location:** `backend/app/api/v1/endpoints/projects.py:8`

```python
import uuid  # Never used
```

**Risk:** Linter warnings, code clutter.

**Fix:** Remove `import uuid`.

---

### m3: All Endpoints Are Synchronous (except file upload)

**Location:** Every endpoint file

**What's wrong:**
All endpoints use `def` instead of `async def`. FastAPI handles sync functions by running them in a threadpool, which adds overhead. The Supabase Python client supports sync calls, so this works — but it means each request occupies a thread.

**Risk:** Under concurrent load, the threadpool becomes a bottleneck. FastAPI's default threadpool is 40 threads.

**Fix for later (not urgent for MVP):**
When you move to an async Supabase client or use `httpx` for Supabase calls, switch endpoints to `async def`.

---

### m4: CORS Only Allows localhost:3000

**Location:** `backend/main.py:11`

```python
allow_origins=["http://localhost:3000"]
```

**Risk:** When you deploy the frontend to Vercel (e.g., `https://cma-autofill.vercel.app`), all API calls from the deployed frontend will be blocked by CORS.

**Fix:**
```python
import os

allowed_origins = [
    "http://localhost:3000",
]

# Add production origin if set
prod_origin = os.getenv("FRONTEND_URL")
if prod_origin:
    allowed_origins.append(prod_origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Then set `FRONTEND_URL=https://your-app.vercel.app` in production env vars.

---

### m5: Missing `email-validator` Dependency

**Location:** `backend/requirements.txt` and `backend/app/models/client.py:1`

**What's wrong:**
```python
from pydantic import BaseModel, Field, EmailStr
```

`EmailStr` requires the `email-validator` package. It's not listed in `requirements.txt`. This may work locally if it was installed as a transitive dependency, but will fail on a fresh `pip install -r requirements.txt`.

**Risk:** Deployment fails with `ImportError: email-validator is not installed`.

**Fix:** Add to requirements.txt:
```
email-validator
```

---

## Fix Priority Order

| # | Issue | Priority | Effort | Do When |
|---|-------|----------|--------|---------|
| C2 | Project hard delete → soft delete | Critical | 15 min | Now |
| C3 | Supabase client singleton | Critical | 5 min | Now |
| m5 | Add email-validator to requirements | Critical (deploy blocker) | 1 min | Now |
| M2 | Health endpoint fields | Low effort | 2 min | Now |
| M3 | Move /health/llm to root | Low effort | 5 min | Now |
| m1 | Update GEMINI.md | Low effort | 2 min | Now |
| m2 | Remove unused import | Low effort | 1 min | Now |
| M1 | Use upload_file() or remove dead code | Moderate | 10 min | Now |
| M5 | Sanitize search parameter | Moderate | 5 min | Now |
| m4 | CORS for production | Moderate | 5 min | Before deploy |
| C1 | Write tests | Critical | 2-3 hours | Before Phase 04 |
| M4 | Dashboard query optimization | Moderate | 1 hour | Before scaling |
| M6 | Verify review_queue schema | Moderate | 10 min | Before Phase 07 |
| m3 | Async endpoints | Low | 1-2 hours | V2 |
