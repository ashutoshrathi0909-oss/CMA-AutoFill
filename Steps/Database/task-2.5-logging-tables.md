# Task 2.5: Create Tables — Logging (LLM Usage + Audit)

> **Phase:** 02 - Database & Authentication
> **Depends on:** Task 2.1 (firms + users tables exist)
> **Agent reads:** CLAUDE.md → Database Tables section
> **MCP to use:** Supabase MCP
> **Time estimate:** 5 minutes

---

## Objective

Create tables for tracking LLM API costs and audit trail. These are write-heavy, read-occasionally tables used for billing, debugging, and compliance.

---

## What to Do

### Table: llm_usage_log

| Column | Type | Constraints |
|--------|------|------------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() |
| firm_id | UUID | REFERENCES firms(id) ON DELETE CASCADE, NOT NULL |
| cma_project_id | UUID | REFERENCES cma_projects(id) ON DELETE SET NULL, NULLABLE |
| model | TEXT | NOT NULL (e.g., 'gemini-2.0-flash', 'gemini-3-flash', 'gemini-3.1-pro') |
| task_type | TEXT | NOT NULL, CHECK (task_type IN ('extraction', 'classification', 'validation', 'fallback')) |
| input_tokens | INTEGER | NOT NULL |
| output_tokens | INTEGER | NOT NULL |
| cost_usd | NUMERIC(10,6) | NOT NULL (up to 6 decimal places for micro-costs) |
| latency_ms | INTEGER | NULLABLE |
| success | BOOLEAN | DEFAULT true |
| error_message | TEXT | NULLABLE |
| created_at | TIMESTAMPTZ | DEFAULT now() |

### Table: audit_log

| Column | Type | Constraints |
|--------|------|------------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() |
| firm_id | UUID | REFERENCES firms(id) ON DELETE CASCADE, NOT NULL |
| user_id | UUID | REFERENCES users(id) ON DELETE SET NULL, NULLABLE |
| action | TEXT | NOT NULL (e.g., 'create_project', 'upload_file', 'run_extraction', 'resolve_review', 'download_cma') |
| entity_type | TEXT | NOT NULL (e.g., 'cma_project', 'uploaded_file', 'review_item', 'generated_file') |
| entity_id | UUID | NULLABLE |
| metadata | JSONB | NULLABLE (additional context — NO sensitive financial data here!) |
| ip_address | TEXT | NULLABLE |
| created_at | TIMESTAMPTZ | DEFAULT now() |

### Also Create

- Index on `llm_usage_log.firm_id`
- Index on `llm_usage_log.cma_project_id`
- Index on `llm_usage_log.created_at` (for date-range queries on usage)
- Index on `audit_log.firm_id`
- Index on `audit_log.created_at`
- Index on `audit_log.action` (for filtering specific actions)

---

## What NOT to Do

- Don't enable RLS (task 2.6)
- Don't insert test data yet
- Don't store any actual financial data in audit_log metadata — only references and counts
- Don't create views or materialized views for cost aggregation yet

---

## Verification

- [ ] `llm_usage_log` table visible in dashboard
- [ ] `audit_log` table visible in dashboard
- [ ] Can insert a test LLM log entry with cost_usd = 0.000124 (micro-cost precision works)
- [ ] CHECK constraint on `task_type` works
- [ ] `ON DELETE SET NULL` works: deleting a project doesn't delete its log entries (just nulls the reference)
- [ ] Delete test entries after verification

---

## Done → Move to task-2.6-row-level-security.md
