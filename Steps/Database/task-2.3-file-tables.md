# Task 2.3: Create Tables — Files + Storage Bucket

> **Phase:** 02 - Database & Authentication
> **Depends on:** Task 2.2 (clients + cma_projects tables exist)
> **Agent reads:** CLAUDE.md → Database Tables section
> **MCP to use:** Supabase MCP
> **Time estimate:** 10 minutes

---

## Objective

Create tables for tracking uploaded documents and generated CMA files. Also create the Supabase Storage bucket for actual file storage.

---

## What to Do

### Table: uploaded_files

| Column | Type | Constraints |
|--------|------|------------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() |
| firm_id | UUID | REFERENCES firms(id) ON DELETE CASCADE, NOT NULL |
| cma_project_id | UUID | REFERENCES cma_projects(id) ON DELETE CASCADE, NOT NULL |
| file_name | TEXT | NOT NULL |
| file_type | TEXT | NOT NULL, CHECK (file_type IN ('xlsx', 'xls', 'pdf', 'jpg', 'png', 'csv')) |
| file_size | INTEGER | NOT NULL (bytes) |
| storage_path | TEXT | NOT NULL |
| document_type | TEXT | NULLABLE, CHECK (document_type IN ('profit_and_loss', 'balance_sheet', 'trial_balance', 'other')) |
| extraction_status | TEXT | DEFAULT 'pending', CHECK (extraction_status IN ('pending', 'processing', 'completed', 'failed')) |
| extracted_data | JSONB | NULLABLE |
| uploaded_by | UUID | REFERENCES users(id), NULLABLE |
| created_at | TIMESTAMPTZ | DEFAULT now() |

### Table: generated_files

| Column | Type | Constraints |
|--------|------|------------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() |
| firm_id | UUID | REFERENCES firms(id) ON DELETE CASCADE, NOT NULL |
| cma_project_id | UUID | REFERENCES cma_projects(id) ON DELETE CASCADE, NOT NULL |
| file_name | TEXT | NOT NULL |
| storage_path | TEXT | NOT NULL |
| file_size | INTEGER | NULLABLE |
| version | INTEGER | DEFAULT 1 |
| generated_at | TIMESTAMPTZ | DEFAULT now() |

### Also Create

- Index on `uploaded_files.firm_id`
- Index on `uploaded_files.cma_project_id`
- Index on `generated_files.cma_project_id`

### Supabase Storage Bucket

Create a storage bucket with these settings:
- **Bucket name:** `cma-files`
- **Public:** NO (private bucket — files accessed through signed URLs)
- **Max file size:** 10MB (10485760 bytes)
- **Allowed MIME types:** application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel, application/pdf, image/jpeg, image/png, text/csv

---

## What NOT to Do

- Don't enable RLS (task 2.6)
- Don't upload any test files yet
- Don't create file upload/download API endpoints (that's Phase 03)
- Don't set up storage policies yet (task 2.6 handles that)

---

## Verification

- [ ] `uploaded_files` table visible in Supabase dashboard
- [ ] `generated_files` table visible in Supabase dashboard
- [ ] Storage bucket `cma-files` visible in Supabase → Storage section
- [ ] Bucket is marked as private (not public)
- [ ] CHECK constraints work on `file_type`, `document_type`, `extraction_status`
- [ ] Foreign keys work: can't insert uploaded_file for non-existent project
- [ ] Can manually upload a small test file to bucket via Supabase dashboard (then delete it)

---

## Done → Move to task-2.4-review-tables.md
