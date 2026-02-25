# Task 2.4: Create Tables — Review Queue & Precedents

> **Phase:** 02 - Database & Authentication
> **Depends on:** Task 2.2 (cma_projects table exists)
> **Agent reads:** CLAUDE.md → Database Tables, cma-domain SKILL → Precedent System
> **MCP to use:** Supabase MCP
> **Time estimate:** 10 minutes

---

## Objective

Create the tables that power the "Ask Father" review system and the learning loop. These are the most important tables for the product's intelligence — they store CA decisions that make future classifications smarter.

---

## What to Do

### Table: review_queue

| Column | Type | Constraints |
|--------|------|------------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() |
| firm_id | UUID | REFERENCES firms(id) ON DELETE CASCADE, NOT NULL |
| cma_project_id | UUID | REFERENCES cma_projects(id) ON DELETE CASCADE, NOT NULL |
| source_item | TEXT | NOT NULL (the original line item text from document) |
| source_amount | NUMERIC | NOT NULL |
| source_document_type | TEXT | NOT NULL, CHECK (source_document_type IN ('profit_and_loss', 'balance_sheet', 'trial_balance')) |
| ai_suggested_row | INTEGER | NULLABLE (what the AI thinks) |
| ai_suggested_sheet | TEXT | NULLABLE |
| ai_confidence | NUMERIC | NULLABLE (0.0 to 1.0) |
| ai_reasoning | TEXT | NULLABLE (why the AI chose this) |
| ca_selected_row | INTEGER | NULLABLE (what the CA chose after review) |
| ca_selected_sheet | TEXT | NULLABLE |
| ca_notes | TEXT | NULLABLE (CA's explanation) |
| status | TEXT | DEFAULT 'pending', CHECK (status IN ('pending', 'resolved', 'skipped')) |
| resolved_by | UUID | REFERENCES users(id), NULLABLE |
| resolved_at | TIMESTAMPTZ | NULLABLE |
| created_at | TIMESTAMPTZ | DEFAULT now() |

### Table: classification_precedents

| Column | Type | Constraints |
|--------|------|------------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() |
| firm_id | UUID | REFERENCES firms(id) ON DELETE CASCADE, NULLABLE (NULL = global precedent) |
| source_term | TEXT | NOT NULL (the financial item name) |
| target_row | INTEGER | NOT NULL (CMA row number) |
| target_sheet | TEXT | NOT NULL |
| entity_type | TEXT | NULLABLE, CHECK (entity_type IN ('trading', 'manufacturing', 'service')) |
| confidence | NUMERIC | DEFAULT 1.0 |
| scope | TEXT | DEFAULT 'firm', CHECK (scope IN ('firm', 'global')) |
| source_project_id | UUID | REFERENCES cma_projects(id), NULLABLE |
| created_by | UUID | REFERENCES users(id), NOT NULL |
| created_at | TIMESTAMPTZ | DEFAULT now() |

### Also Create

- Index on `review_queue.firm_id`
- Index on `review_queue.cma_project_id`
- Index on `review_queue.status` (for filtering pending items)
- Index on `classification_precedents.firm_id`
- Index on `classification_precedents.source_term` (for matching during classification)
- **Unique constraint on precedents:** `UNIQUE(firm_id, source_term, entity_type)` — one precedent per term per firm per entity type
- Partial index on precedents where `scope = 'global'` for fast global lookups

---

## What NOT to Do

- Don't enable RLS (task 2.6)
- Don't insert test data (task 2.7)
- Don't create review/resolve API endpoints (that's Phase 07)
- Don't build the precedent matching logic (that's Phase 05)

---

## Verification

- [ ] `review_queue` table visible in dashboard
- [ ] `classification_precedents` table visible in dashboard
- [ ] CHECK constraints work on `status`, `source_document_type`, `scope`, `entity_type`
- [ ] Unique constraint works: can't insert two precedents with same firm_id + source_term + entity_type
- [ ] NULL firm_id allowed on precedents (for global scope)
- [ ] `ai_confidence` accepts decimals like 0.73

---

## Done → Move to task-2.5-logging-tables.md
