# Task 2.1: Create Core Tables — Firms & Users

> **Phase:** 02 - Database & Authentication
> **Depends on:** Phase 01 complete. Supabase project exists.
> **Agent reads:** CLAUDE.md → Database Tables section
> **MCP to use:** Supabase MCP (execute SQL directly)
> **Time estimate:** 10 minutes

---

## Objective

Create the `firms` and `users` tables. `firms` is the multi-tenant root — every other table links to it through `firm_id`.

---

## What to Do

### Table: firms

| Column | Type | Constraints |
|--------|------|------------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() |
| name | TEXT | NOT NULL |
| email | TEXT | UNIQUE, NOT NULL |
| phone | TEXT | NULLABLE |
| address | TEXT | NULLABLE |
| gst_number | TEXT | NULLABLE |
| plan | TEXT | DEFAULT 'free', CHECK (plan IN ('free', 'starter', 'pro')) |
| is_active | BOOLEAN | DEFAULT true |
| created_at | TIMESTAMPTZ | DEFAULT now() |
| updated_at | TIMESTAMPTZ | DEFAULT now() |

### Table: users

| Column | Type | Constraints |
|--------|------|------------|
| id | UUID | PRIMARY KEY, REFERENCES auth.users(id) ON DELETE CASCADE |
| firm_id | UUID | REFERENCES firms(id) ON DELETE CASCADE, NOT NULL |
| email | TEXT | NOT NULL |
| full_name | TEXT | NOT NULL |
| role | TEXT | DEFAULT 'ca', CHECK (role IN ('owner', 'ca', 'staff')) |
| is_active | BOOLEAN | DEFAULT true |
| created_at | TIMESTAMPTZ | DEFAULT now() |
| updated_at | TIMESTAMPTZ | DEFAULT now() |

### Also Create

- An index on `users.firm_id` (frequently queried)
- An `updated_at` trigger function that auto-updates the timestamp on row changes
- Apply the trigger to both tables

---

## What NOT to Do

- Don't create any other tables (those are tasks 2.2-2.5)
- Don't enable RLS yet (that's task 2.6)
- Don't insert any data (that's task 2.7)
- Don't create API endpoints for these tables

---

## Verification

- [ ] `firms` table visible in Supabase → Table Editor
- [ ] `users` table visible in Supabase → Table Editor
- [ ] Can insert a test firm manually via SQL: `INSERT INTO firms (name, email) VALUES ('Test Firm', 'test@test.com')`
- [ ] Can insert a test user linked to that firm (requires an auth.users entry or skip FK check temporarily)
- [ ] CHECK constraint works: inserting `role = 'invalid'` fails
- [ ] CHECK constraint works: inserting `plan = 'invalid'` fails
- [ ] `updated_at` auto-updates when a row is modified
- [ ] Delete test data after verification

---

## Done → Move to task-2.2-client-project-tables.md
