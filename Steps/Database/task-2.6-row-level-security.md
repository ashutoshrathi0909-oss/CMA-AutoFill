# Task 2.6: Set Up Row Level Security (RLS)

> **Phase:** 02 - Database & Authentication
> **Depends on:** Tasks 2.1-2.5 (ALL tables exist)
> **Agent reads:** CLAUDE.md → multi-tenant isolation rules
> **MCP to use:** Supabase MCP
> **Time estimate:** 20 minutes (most complex task in this phase)

---

## Objective

Enable RLS on every table and create policies that enforce multi-tenant isolation. After this task, a user from Firm A can NEVER see, edit, or delete data from Firm B. This is a critical security requirement.

---

## What to Do

### Step 1: Create Helper Function

Create a PostgreSQL function that returns the current user's `firm_id`:

```
get_user_firm_id() → UUID
```

Logic:
- Extract user ID from `auth.uid()` (Supabase's built-in function)
- Look up that user in the `users` table
- Return their `firm_id`
- If user not found, return NULL (which means no rows match → safe default)

This function is used in all RLS policies below.

### Step 2: Enable RLS on ALL Tables

Enable Row Level Security on these 10 tables:
- firms
- users
- clients
- cma_projects
- uploaded_files
- generated_files
- review_queue
- classification_precedents
- llm_usage_log
- audit_log

### Step 3: Create Policies for Standard Tables

For these tables, create 4 policies each (SELECT, INSERT, UPDATE, DELETE):

**clients, cma_projects, uploaded_files, generated_files, review_queue, llm_usage_log, audit_log:**

- **SELECT:** `firm_id = get_user_firm_id()`
- **INSERT:** `firm_id = get_user_firm_id()`
- **UPDATE:** `firm_id = get_user_firm_id()`
- **DELETE:** `firm_id = get_user_firm_id()`

### Step 4: Special Policies

**firms table:**
- SELECT: `id = get_user_firm_id()` (users can only read their own firm)
- UPDATE: `id = get_user_firm_id()` AND user role = 'owner'
- INSERT: allow (needed for initial firm creation during signup flow)
- DELETE: deny all (firms cannot be deleted through client)

**users table:**
- SELECT: `firm_id = get_user_firm_id()` (can see colleagues in same firm)
- INSERT: `firm_id = get_user_firm_id()` AND current user role = 'owner'
- UPDATE: `id = auth.uid()` OR (current user role = 'owner' AND `firm_id = get_user_firm_id()`)
- DELETE: deny all (users are deactivated, not deleted)

**classification_precedents (SPECIAL — has global scope):**
- SELECT: `firm_id = get_user_firm_id() OR firm_id IS NULL` (can see own firm's + global precedents)
- INSERT: `firm_id = get_user_firm_id()` (can only create for own firm)
- UPDATE: `firm_id = get_user_firm_id()` (can only edit own firm's)
- DELETE: `firm_id = get_user_firm_id()` (can only delete own firm's, not global)

### Step 5: Storage Bucket Policies

For the `cma-files` storage bucket, create policies:
- SELECT (download): authenticated users can download files where the path starts with their firm_id
- INSERT (upload): authenticated users can upload to paths starting with their firm_id
- DELETE: authenticated users can delete files in their firm_id path

Storage path convention: `{firm_id}/{project_id}/{filename}`

---

## What NOT to Do

- Don't create policies that bypass RLS for any regular user
- Don't use `SECURITY DEFINER` on the helper function (use `SECURITY INVOKER`)
- Don't forget the storage bucket policies
- Don't skip any table — every table must have RLS enabled

---

## Verification (CRITICAL — test thoroughly)

### Setup for Testing
1. Create two test firms: "Firm A" and "Firm B"
2. Create a test user for each firm (requires Supabase Auth signup)
3. Create a test client under each firm
4. Create a test CMA project under each firm's client

### Test Isolation
- [ ] Log in as Firm A user → query clients → sees ONLY Firm A's clients
- [ ] Log in as Firm A user → query cma_projects → sees ONLY Firm A's projects
- [ ] Log in as Firm A user → try to SELECT Firm B's client by ID → returns EMPTY (not error)
- [ ] Log in as Firm A user → try to UPDATE Firm B's client → no rows affected
- [ ] Log in as Firm A user → try to DELETE Firm B's client → no rows affected

### Test Precedents (Special Case)
- [ ] Insert a global precedent (firm_id = NULL, scope = 'global') via service role
- [ ] Log in as Firm A → can see their own precedents AND global ones
- [ ] Log in as Firm A → CANNOT see Firm B's precedents
- [ ] Log in as Firm A → CANNOT modify or delete global precedents

### Test Storage
- [ ] Firm A can upload to `firm-a-id/project-id/test.pdf`
- [ ] Firm A CANNOT access files at `firm-b-id/...`

### Clean Up
- Delete test data after all tests pass (keep the firms if they'll be used in task 2.7)

---

## Done → Move to task-2.7-auth-seed-data.md
