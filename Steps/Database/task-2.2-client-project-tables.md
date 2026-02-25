# Task 2.2: Create Tables — Clients & CMA Projects

> **Phase:** 02 - Database & Authentication
> **Depends on:** Task 2.1 (firms + users tables exist)
> **Agent reads:** CLAUDE.md → Database Tables section
> **MCP to use:** Supabase MCP
> **Time estimate:** 10 minutes

---

## Objective

Create the `clients` and `cma_projects` tables. These are the core business objects — a firm has clients, each client can have multiple CMA projects.

---

## What to Do

### Table: clients

| Column | Type | Constraints |
|--------|------|------------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() |
| firm_id | UUID | REFERENCES firms(id) ON DELETE CASCADE, NOT NULL |
| name | TEXT | NOT NULL |
| entity_type | TEXT | NOT NULL, CHECK (entity_type IN ('trading', 'manufacturing', 'service')) |
| pan_number | TEXT | NULLABLE |
| gst_number | TEXT | NULLABLE |
| contact_person | TEXT | NULLABLE |
| contact_email | TEXT | NULLABLE |
| contact_phone | TEXT | NULLABLE |
| address | TEXT | NULLABLE |
| is_active | BOOLEAN | DEFAULT true |
| created_at | TIMESTAMPTZ | DEFAULT now() |
| updated_at | TIMESTAMPTZ | DEFAULT now() |

### Table: cma_projects

| Column | Type | Constraints |
|--------|------|------------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() |
| firm_id | UUID | REFERENCES firms(id) ON DELETE CASCADE, NOT NULL |
| client_id | UUID | REFERENCES clients(id) ON DELETE CASCADE, NOT NULL |
| financial_year | TEXT | NOT NULL (e.g., '2024-25') |
| bank_name | TEXT | NULLABLE |
| loan_type | TEXT | NULLABLE, CHECK (loan_type IN ('term_loan', 'working_capital', 'cc_od', 'other')) |
| loan_amount | NUMERIC | NULLABLE |
| status | TEXT | DEFAULT 'draft', CHECK (status IN ('draft', 'extracting', 'classifying', 'reviewing', 'validating', 'generating', 'completed', 'error')) |
| extracted_data | JSONB | NULLABLE |
| classification_results | JSONB | NULLABLE |
| validation_errors | JSONB | NULLABLE |
| pipeline_progress | INTEGER | DEFAULT 0 |
| pipeline_current_step | TEXT | NULLABLE |
| error_message | TEXT | NULLABLE |
| created_by | UUID | REFERENCES users(id), NULLABLE |
| created_at | TIMESTAMPTZ | DEFAULT now() |
| updated_at | TIMESTAMPTZ | DEFAULT now() |

### Also Create

- Index on `clients.firm_id`
- Index on `cma_projects.firm_id`
- Index on `cma_projects.client_id`
- Index on `cma_projects.status` (for filtering by pipeline status)
- Unique constraint: `UNIQUE(client_id, financial_year)` — one CMA per client per year
- Apply `updated_at` trigger to both tables

---

## What NOT to Do

- Don't enable RLS (task 2.6)
- Don't insert data (task 2.7)
- Don't create API endpoints

---

## Verification

- [ ] Both tables visible in Supabase dashboard
- [ ] `entity_type` CHECK works: `'invalid'` fails, `'trading'` succeeds
- [ ] `status` CHECK works: `'invalid'` fails, `'draft'` succeeds
- [ ] `loan_type` CHECK works
- [ ] Foreign key works: inserting a client with non-existent `firm_id` fails
- [ ] Foreign key works: inserting a project with non-existent `client_id` fails
- [ ] Unique constraint works: can't create two projects for same client + same financial year
- [ ] `updated_at` trigger fires on update

---

## Done → Move to task-2.3-file-tables.md
