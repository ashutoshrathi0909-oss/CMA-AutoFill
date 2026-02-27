# Phase 03 Lessons Learned — Preventing These Mistakes

> **Purpose:** A reusable checklist and set of principles derived from the Phase 03 audit.
> Apply these before marking ANY future phase as "complete."

---

## Lesson 1: Tests Are Not Optional — They Are the Definition of "Done"

### What happened
Phase 03 delivered 7 working endpoint groups with zero tests. The code "works when manually tested via Swagger," but nothing is automated.

### Why it happened
- Manual testing feels faster in the moment. You hit the endpoint in Swagger, it returns 200, you move on.
- No CI pipeline enforcing test coverage. There's no gate that says "you can't merge without tests."
- The task specs had verification checklists but they were manual ("check this in Swagger"). No task said "write a pytest file."

### The rule going forward
**Every task delivery must include at minimum:**
1. One test file per endpoint group (e.g., `test_clients.py`)
2. At least these test cases per CRUD endpoint:
   - Happy path (valid input → expected output)
   - Auth failure (no token → 401)
   - Not found (invalid ID → 404)
   - Validation failure (bad input → 422)
   - Permission boundary (other firm's data → 404, not 403)
3. Run `pytest` before committing. If any test fails, the commit doesn't happen.

### Checklist to add to every future task spec
```
## Testing (Required)
- [ ] Test file created: `backend/tests/test_<feature>.py`
- [ ] Happy path test passes
- [ ] Auth failure test passes
- [ ] Edge case tests pass
- [ ] `pytest` passes with 0 failures before commit
```

### Prevention mechanism
Add a pre-commit hook or CI step:
```bash
# .github/workflows/test.yml or pre-commit hook
cd backend && python -m pytest tests/ -v --tb=short
```
If tests don't exist or fail, the deployment is blocked.

---

## Lesson 2: "Delete" Must Always Mean "Soft Delete" Unless Explicitly Decided Otherwise

### What happened
The clients endpoint correctly uses soft delete (`is_active = False`). The projects endpoint uses hard delete (`DELETE FROM`). This inconsistency happened because two different "sessions" implemented the two endpoints and the second didn't follow the pattern established by the first.

### Why it happened
- No shared "patterns" document that says "all deletes in this project are soft deletes."
- The task spec said "don't hard-delete" but also mentioned "prevent deletion of non-draft projects" — the implementer may have read the second part as the safety mechanism and ignored the first.
- Copy-paste didn't happen. The clients endpoint was the model to follow, but the projects endpoint was written independently.

### The rule going forward
**Default behavior: ALL deletes are soft deletes.** Exceptions must be explicitly documented and justified.

Soft delete pattern (copy this every time):
```python
# ALWAYS use this pattern for "delete" endpoints
db.table("table_name").update({"is_active": False}).eq("id", entity_id).eq("firm_id", firm_id).execute()
```

Hard delete is only acceptable for:
- Temporary/draft data that has no audit value
- Data the user explicitly wants permanently removed (GDPR compliance)
- Must be documented: "This endpoint hard-deletes because [reason]"

### Checklist
```
## Delete Behavior
- [ ] Delete endpoint uses soft delete (is_active = False)
- [ ] List endpoint filters out is_active = False by default
- [ ] Audit log entry created before/after delete
- [ ] Hard delete is ONLY used if explicitly justified in this spec
```

---

## Lesson 3: Shared Resources (DB Clients, HTTP Clients) Must Be Singletons

### What happened
`get_supabase()` creates a new Supabase client on every call. A single API request might create 3-5 clients.

### Why it happened
- The simplest code pattern (`return create_client(...)`) is also the wrong one. It works, it's readable, and its performance problem is invisible until you're under load.
- No code review step to catch this. If someone had reviewed the PR, they'd likely spot "why are we creating a new client every time?"
- Phase 01's initial setup created the function and Phase 03 just used it as-is.

### The rule going forward
**Any external client (database, HTTP, LLM, storage) must be created once and reused.**

Pattern:
```python
_client: SomeClient | None = None

def get_client() -> SomeClient:
    global _client
    if _client is None:
        _client = SomeClient(config)
    return _client
```

This applies to:
- Supabase client (`get_supabase()`)
- Gemini/LLM client (Phase 04)
- Resend email client (Phase 07)
- Any HTTP client (`httpx.AsyncClient`)

### Checklist
```
## Client/Connection Management
- [ ] All external clients are singletons (created once, reused)
- [ ] No `create_client()` or `Client()` calls inside request handlers
- [ ] Connection initialization happens at module level or in a startup event
```

---

## Lesson 4: Dead Code Is a Bug Waiting to Happen

### What happened
`storage.py` has an `upload_file()` function that is imported but never called. The actual upload logic was duplicated inline in the endpoint.

### Why it happened
- The storage service was created first (following the spec), then the endpoint was written and the developer found it easier to write the upload inline.
- The import was left in place, making it look like the function is used.
- No linter configured to flag unused imports or dead code.

### The rule going forward
**If you write a utility function, use it. If you don't need it, don't write it.**

- Before creating a helper/utility, ask: "Will I call this from more than one place?" If no, write it inline.
- Before committing, check: "Are all my imports used? Are all my functions called?"
- Run a linter that catches unused code.

### Prevention mechanism
Add `ruff` or `flake8` to the project:
```bash
pip install ruff
ruff check backend/ --select F401,F841  # Unused imports and variables
```

---

## Lesson 5: Specs Are Contracts — Read Every Line

### What happened
Multiple spec requirements were missed:
- Health endpoint missing `version` and `environment` fields
- `/health/llm` placed under `/api/v1` instead of root
- Project delete using hard delete instead of soft

### Why it happened
- Specs were skimmed, not read line by line. The developer got the general idea and started coding.
- The "What NOT to Do" sections were likely not read carefully enough.

### The rule going forward
**Before writing a single line of code, create a checklist from the spec.**

Workflow:
1. Read the task spec completely — including "What NOT to Do" and "Verification" sections
2. Extract every concrete requirement into a checkbox list
3. Implement each checkbox
4. Before committing, go through each checkbox and verify

Example (from task 3.2):
```
From task-3.2-health-me-endpoints.md:
- [ ] GET /health returns status, version, environment
- [ ] GET /health/db checks Supabase connection
- [ ] GET /health/llm checks Gemini API key
- [ ] Health endpoints do NOT require auth
- [ ] GET /api/v1/me requires auth
- [ ] /me returns user + firm info in standard response format
- [ ] Response format: {"data": ..., "error": null}
```

---

## Lesson 6: Don't Fetch All Rows When You Need a Count

### What happened
The dashboard endpoint fetches ALL clients, ALL projects, and ALL LLM logs into Python memory, then counts them with `len()`.

### Why it happened
- It's the most straightforward code pattern: fetch everything, loop through it.
- With test data (1-2 records per table), performance is identical. The problem only appears at scale.
- The developer may not have known about Supabase's `count` parameter.

### The rule going forward
**Use database-level counting and aggregation. Never fetch rows just to count them.**

Patterns:
```python
# BAD: Fetches all rows, counts in Python
res = db.table("clients").select("*").eq("firm_id", fid).execute()
total = len(res.data)

# GOOD: Database counts, returns just the number
res = db.table("clients").select("id", count="exact").eq("firm_id", fid).execute()
total = res.count
```

For complex aggregations (GROUP BY, SUM), create a Supabase RPC function (a PostgreSQL function) and call it:
```python
res = db.rpc("get_dashboard_stats", {"p_firm_id": firm_id}).execute()
```

### General database rule
- Need a count? Use `count="exact"` parameter
- Need a sum/average? Use an RPC function
- Need grouped data? Use an RPC function
- Only fetch full rows when you need the actual row data

---

## Lesson 7: Consistency Beats Cleverness

### What happened
- Clients use soft delete, projects use hard delete
- Some endpoints are `async def`, most are `def`
- Health endpoints are split between `main.py` (root level) and `health.py` (API level)
- The upload function exists in storage.py but the actual upload is inline

### Why it happened
Multiple coding sessions with no "style guide review" at the end. Each session solved its immediate problem without checking if it matched established patterns.

### The rule going forward
**Before committing any phase, do a consistency audit:**

```
## Consistency Checklist (run at phase end)
- [ ] All delete endpoints use the same pattern (soft delete)
- [ ] All endpoints use the same function style (sync or async — pick one)
- [ ] All utility functions that exist are actually called
- [ ] All similar operations follow the same pattern (e.g., all audit logs have same fields)
- [ ] Error responses use the same format everywhere
- [ ] All health checks are at the same URL level
```

---

## Lesson 8: Dependencies Must Be Complete and Explicit

### What happened
`EmailStr` from Pydantic requires `email-validator`, which isn't in `requirements.txt`. Works locally because it was installed as a transitive dependency. Will fail on fresh install or deployment.

### Why it happened
- `pip install pydantic` might pull in `email-validator` as an optional dependency on some systems.
- The developer tested locally where it was already installed, so no error appeared.
- No fresh-environment test was done.

### The rule going forward
**After adding any import, verify its package is in requirements.txt.**

Test procedure at the end of each phase:
```bash
# Create a fresh virtual environment and test
python -m venv test_env
source test_env/bin/activate  # or test_env\Scripts\activate on Windows
pip install -r requirements.txt
python -c "from app.models.client import ClientCreate"  # Should not error
deactivate
rm -rf test_env
```

Or simpler: just grep for it:
```bash
# For every import in your code, check if its package is in requirements.txt
pip freeze | grep email-validator  # If this shows a version but requirements.txt doesn't have it, add it
```

---

## Lesson 9: CORS Must Account for All Environments From Day One

### What happened
CORS only allows `http://localhost:3000`. The deployed frontend on Vercel will be blocked.

### Why it happened
- "I'll fix it when I deploy" thinking. It works locally, so it's not a priority.
- The env var pattern (`FRONTEND_URL`) wasn't set up during Phase 01.

### The rule going forward
**Always make CORS configurable via environment variables from the start.**

```python
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
```

This way:
- Local dev: `ALLOWED_ORIGINS=http://localhost:3000` (or just use default)
- Production: `ALLOWED_ORIGINS=https://cma-autofill.vercel.app,http://localhost:3000`
- No code change needed for deployment

---

## Lesson 10: Update Documentation When You Complete a Phase

### What happened
GEMINI.md still shows Phase 01 as the only completed phase, even though Phase 02 and 03 are done.

### Why it happened
- Documentation updates feel like overhead after the "real work" is done.
- No step in the workflow says "update GEMINI.md."

### The rule going forward
**The last commit of every phase MUST include documentation updates.**

Phase completion checklist (add to every phase README):
```
## Phase Completion Steps
1. [ ] All task specs verified against implementation
2. [ ] Tests written and passing
3. [ ] GEMINI.md roadmap updated (checkbox marked)
4. [ ] GEMINI.md "Key Directories" updated if new directories were created
5. [ ] Commit message format: "Phase XX: [description]"
```

---

## Master Pre-Commit Checklist

Copy this into every future phase's README and check every box before the final commit:

```
## Pre-Commit Audit
### Correctness
- [ ] Every spec requirement has been implemented (checklist extracted from spec)
- [ ] All "What NOT to Do" items have been respected
- [ ] Tests exist and pass (`pytest -v`)

### Patterns
- [ ] All deletes are soft deletes (unless explicitly justified)
- [ ] All external clients are singletons
- [ ] All counting uses database-level counts, not `len(fetch_all())`
- [ ] No dead code (unused imports, uncalled functions)
- [ ] Consistent style (all sync or all async, same patterns across endpoints)

### Dependencies & Config
- [ ] All imported packages are in requirements.txt
- [ ] CORS allows all necessary origins (via env vars)
- [ ] No hardcoded secrets or environment-specific values

### Documentation
- [ ] GEMINI.md updated with current phase status
- [ ] Any new patterns documented for future phases

### Security
- [ ] User input is sanitized (search params, file names)
- [ ] All queries are scoped to firm_id
- [ ] No data from other firms is ever returned (test with cross-firm IDs)
```

---

## Quick Reference: Patterns to Always Follow

| Pattern | Do This | Not This |
|---------|---------|----------|
| Delete | `update({"is_active": False})` | `.delete()` |
| DB Client | Singleton with global cache | `create_client()` per request |
| Counting | `select("id", count="exact")` | `len(select("*").execute().data)` |
| Search | Escape `%` and `_` in user input | `ilike("col", f"%{raw_input}%")` |
| CORS | `os.getenv("ALLOWED_ORIGINS").split(",")` | `["http://localhost:3000"]` |
| Health | Root-level, no auth, include version | Behind `/api/v1`, missing metadata |
| Utilities | Write it → Use it, or don't write it | Write it → Duplicate inline |
| Imports | Verify package in requirements.txt | Assume transitive deps exist |
| Docs | Update GEMINI.md in same commit | "I'll update docs later" |
| Tests | Write with the code, not after | "It works in Swagger, ship it" |
