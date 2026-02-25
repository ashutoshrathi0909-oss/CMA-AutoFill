# PHASE 02: Database & Authentication

> **Purpose:** Create all database tables, set up Row Level Security, configure auth, and seed test data.
> **Prerequisites:** Phase 01 complete. Supabase MCP server connected.
> **Agent context:** Read CLAUDE.md. Use Supabase MCP to execute SQL directly.
> **Result:** All tables exist, RLS prevents cross-firm data access, login works, test data is seeded.

---

## What This Phase Does

We build the entire data layer. After this phase, the database is ready for all future phases to store and retrieve data. This is like building all the rooms and plumbing before moving furniture in.

**Key principle:** Multi-tenant isolation via `firm_id`. Every table has it, every RLS policy checks it.

---

## Task 2.1: Create Core Tables — Firms & Users

**What to do:**
Create the `firms` and `users` tables in Supabase. The `firms` table is the multi-tenant root — everything else links to it.

**Tables:**

**firms:**
- `id` (UUID, primary key, default gen_random_uuid())
- `name` (text, not null) — e.g., "Mehta & Associates"
- `email` (text, unique) — firm contact email
- `phone` (text, nullable)
- `address` (text, nullable)
- `gst_number` (text, nullable) — Indian GST registration
- `plan` (text, default 'free') — subscription tier
- `is_active` (boolean, default true)
- `created_at` (timestamptz, default now())
- `updated_at` (timestamptz, default now())

**users:**
- `id` (UUID, primary key, references auth.users(id))
- `firm_id` (UUID, references firms(id), not null)
- `email` (text, not null)
- `full_name` (text, not null)
- `role` (text, default 'ca') — values: 'owner', 'ca', 'staff'
- `is_active` (boolean, default true)
- `created_at` (timestamptz, default now())
- `updated_at` (timestamptz, default now())

**Verification:**
- Both tables visible in Supabase dashboard → Table Editor
- Can manually insert a test firm and user via dashboard
- Foreign key constraint works: user must reference a valid firm

---

## Task 2.2: Create Tables — Clients & CMA Projects

**What to do:**
Create the tables that represent the actual business objects.

**clients:**
- `id` (UUID, primary key, default gen_random_uuid())
- `firm_id` (UUID, references firms(id), not null)
- `name` (text, not null) — e.g., "Mehta Computers"
- `entity_type` (text, not null) — 'trading', 'manufacturing', 'service'
- `pan_number` (text, nullable)
- `gst_number` (text, nullable)
- `contact_person` (text, nullable)
- `contact_email` (text, nullable)
- `contact_phone` (text, nullable)
- `address` (text, nullable)
- `is_active` (boolean, default true)
- `created_at` (timestamptz, default now())
- `updated_at` (timestamptz, default now())

**cma_projects:**
- `id` (UUID, primary key, default gen_random_uuid())
- `firm_id` (UUID, references firms(id), not null)
- `client_id` (UUID, references clients(id), not null)
- `financial_year` (text, not null) — e.g., "2024-25"
- `bank_name` (text, nullable) — which bank the loan is for
- `loan_type` (text, nullable) — 'term_loan', 'working_capital', 'cc_od'
- `loan_amount` (numeric, nullable)
- `status` (text, default 'draft') — 'draft', 'extracting', 'classifying', 'reviewing', 'validating', 'generating', 'completed', 'error'
- `extracted_data` (jsonb, nullable) — raw extracted line items
- `classification_results` (jsonb, nullable) — classified mappings
- `validation_errors` (jsonb, nullable) — any validation issues
- `pipeline_progress` (integer, default 0) — 0-100 percentage
- `pipeline_current_step` (text, nullable) — which step is running
- `error_message` (text, nullable) — if pipeline failed
- `created_by` (UUID, references users(id))
- `created_at` (timestamptz, default now())
- `updated_at` (timestamptz, default now())

**Verification:**
- Both tables visible in dashboard
- `entity_type` accepts only valid values (add a CHECK constraint)
- `status` accepts only valid values (add a CHECK constraint)
- Foreign keys work: client must reference a valid firm, project must reference a valid client

---

## Task 2.3: Create Tables — Files (Upload & Generated)

**What to do:**
Create tables for tracking uploaded source documents and generated CMA files.

**uploaded_files:**
- `id` (UUID, primary key, default gen_random_uuid())
- `firm_id` (UUID, references firms(id), not null)
- `cma_project_id` (UUID, references cma_projects(id), not null)
- `file_name` (text, not null)
- `file_type` (text, not null) — 'xlsx', 'xls', 'pdf', 'jpg', 'png'
- `file_size` (integer, not null) — bytes
- `storage_path` (text, not null) — path in Supabase Storage
- `document_type` (text, nullable) — 'profit_and_loss', 'balance_sheet', 'trial_balance', 'other'
- `extraction_status` (text, default 'pending') — 'pending', 'processing', 'completed', 'failed'
- `extracted_data` (jsonb, nullable) — extracted content from this specific file
- `uploaded_by` (UUID, references users(id))
- `created_at` (timestamptz, default now())

**generated_files:**
- `id` (UUID, primary key, default gen_random_uuid())
- `firm_id` (UUID, references firms(id), not null)
- `cma_project_id` (UUID, references cma_projects(id), not null)
- `file_name` (text, not null)
- `storage_path` (text, not null)
- `file_size` (integer, nullable)
- `version` (integer, default 1)
- `generated_at` (timestamptz, default now())

**Also create Supabase Storage bucket:**
- Bucket name: `cma-files`
- Private bucket (not public)
- Max file size: 10MB

**Verification:**
- Tables visible in dashboard
- Storage bucket `cma-files` visible in Supabase Storage section
- Can upload a test file via dashboard to the bucket

---

## Task 2.4: Create Tables — Review Queue & Precedents

**What to do:**
These are the tables that power the "Ask Father" review system and learning loop.

**review_queue:**
- `id` (UUID, primary key, default gen_random_uuid())
- `firm_id` (UUID, references firms(id), not null)
- `cma_project_id` (UUID, references cma_projects(id), not null)
- `source_item` (text, not null) — the original line item text
- `source_amount` (numeric, not null)
- `source_document_type` (text, not null) — 'profit_and_loss', 'balance_sheet'
- `ai_suggested_row` (integer, nullable) — what the AI thinks
- `ai_suggested_sheet` (text, nullable)
- `ai_confidence` (numeric, nullable) — 0.0 to 1.0
- `ai_reasoning` (text, nullable) — why the AI chose this
- `ca_selected_row` (integer, nullable) — what the CA chose (after review)
- `ca_selected_sheet` (text, nullable)
- `ca_notes` (text, nullable) — CA's explanation
- `status` (text, default 'pending') — 'pending', 'resolved', 'skipped'
- `resolved_by` (UUID, references users(id), nullable)
- `resolved_at` (timestamptz, nullable)
- `created_at` (timestamptz, default now())

**classification_precedents:**
- `id` (UUID, primary key, default gen_random_uuid())
- `firm_id` (UUID, references firms(id), nullable) — null = global precedent
- `source_term` (text, not null) — the financial item name
- `target_row` (integer, not null) — CMA row number
- `target_sheet` (text, not null)
- `entity_type` (text, nullable) — applies to specific entity type or all
- `confidence` (numeric, default 1.0) — CA decisions are 100% confident
- `scope` (text, default 'firm') — 'firm' or 'global'
- `source_project_id` (UUID, references cma_projects(id), nullable) — which project created this
- `created_by` (UUID, references users(id))
- `created_at` (timestamptz, default now())

**Add unique constraint on classification_precedents:**
- UNIQUE(firm_id, source_term, entity_type) — one precedent per term per firm

**Verification:**
- Tables visible in dashboard
- Can insert a test review queue item
- Unique constraint prevents duplicate precedents

---

## Task 2.5: Create Tables — Logging

**What to do:**
Create tables for LLM usage tracking and audit trail.

**llm_usage_log:**
- `id` (UUID, primary key, default gen_random_uuid())
- `firm_id` (UUID, references firms(id), not null)
- `cma_project_id` (UUID, references cma_projects(id), nullable)
- `model` (text, not null) — 'gemini-2.0-flash', 'gemini-3-flash', 'gemini-3.1-pro'
- `task_type` (text, not null) — 'extraction', 'classification', 'validation'
- `input_tokens` (integer, not null)
- `output_tokens` (integer, not null)
- `cost_usd` (numeric, not null) — calculated cost
- `latency_ms` (integer, nullable) — how long the call took
- `success` (boolean, default true)
- `error_message` (text, nullable)
- `created_at` (timestamptz, default now())

**audit_log:**
- `id` (UUID, primary key, default gen_random_uuid())
- `firm_id` (UUID, references firms(id), not null)
- `user_id` (UUID, references users(id), nullable)
- `action` (text, not null) — 'create_project', 'upload_file', 'run_extraction', 'resolve_review', etc.
- `entity_type` (text, not null) — 'cma_project', 'uploaded_file', 'review_item', etc.
- `entity_id` (UUID, nullable)
- `metadata` (jsonb, nullable) — additional context (no sensitive data!)
- `ip_address` (text, nullable)
- `created_at` (timestamptz, default now())

**Verification:**
- Tables visible in dashboard
- Both tables accept inserts
- `cost_usd` calculates correctly for test values

---

## Task 2.6: Set Up Row Level Security (RLS)

**What to do:**
Enable RLS on ALL tables and create policies that enforce multi-tenant isolation.

**Core rule:** Every SELECT, INSERT, UPDATE, DELETE must filter by `firm_id` matching the authenticated user's firm.

**Steps:**
1. Enable RLS on every table
2. Create a helper function `get_user_firm_id()` that returns the firm_id of the currently authenticated user
3. Create policies for each table:
   - SELECT: `firm_id = get_user_firm_id()`
   - INSERT: `firm_id = get_user_firm_id()`
   - UPDATE: `firm_id = get_user_firm_id()`
   - DELETE: `firm_id = get_user_firm_id()`

**Special cases:**
- `firms` table: users can only read their own firm
- `classification_precedents`: users can read their firm's precedents AND global precedents (where firm_id IS NULL)
- Service role key bypasses RLS (used by backend for admin operations)

**Verification:**
- Create two test firms (Firm A and Firm B) with one user each
- Log in as Firm A user → can only see Firm A's data
- Log in as Firm B user → can only see Firm B's data
- Try to query Firm B's data as Firm A → returns empty, NOT an error
- This test is CRITICAL — multi-tenant isolation is a security requirement

---

## Task 2.7: Configure Auth + Seed Test Data

**What to do:**
Configure Supabase Auth for magic link email login, then insert test data.

**Auth Setup:**
- Enable Email provider in Supabase → Authentication → Providers
- Enable Magic Link (passwordless)
- Set redirect URL to your Vercel frontend URL
- Disable email confirmations for development (enable in production)

**Seed Data to Insert:**

**Test Firm:**
- Name: "[Father's Firm Name]" (ask Ashutosh for actual name)
- Email: father's email

**Test User:**
- Link to the firm above
- Role: 'owner'
- Name: Father's name

**Test Client:**
- Name: "Mehta Computers"
- Entity type: "trading"
- Linked to the test firm

**Test CMA Project:**
- Client: Mehta Computers
- Financial Year: "2024-25"
- Status: "draft"

**Verification:**
- Can sign up with email → receives magic link → logs in
- After login, user can see their firm's data only
- Test firm, user, client, and project all appear in Supabase dashboard
- Auth JWT token contains user ID (verify in Supabase Auth → Users)

---

## Phase 02 Complete Checklist

- [ ] All 10 tables created (firms, users, clients, cma_projects, uploaded_files, generated_files, review_queue, classification_precedents, llm_usage_log, audit_log)
- [ ] Storage bucket `cma-files` created
- [ ] CHECK constraints on enum fields (entity_type, status, etc.)
- [ ] Foreign keys correctly reference parent tables
- [ ] RLS enabled on ALL tables
- [ ] RLS policies enforce firm_id isolation
- [ ] Multi-tenant test passes (Firm A can't see Firm B)
- [ ] Auth magic link login works
- [ ] Test data seeded (firm, user, client, project)
- [ ] Unique constraints on precedents table

**Next → PHASE-03-api-crud.md**
