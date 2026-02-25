# Task 3.5: File Upload Endpoint

> **Phase:** 03 - API CRUD Endpoints
> **Depends on:** Task 3.4 (projects exist), Phase 02 Task 2.3 (storage bucket exists)
> **Agent reads:** CLAUDE.md → Database Tables → uploaded_files
> **Time estimate:** 15 minutes

---

## Objective

Create an endpoint that accepts file uploads (Excel, PDF, images), stores them in Supabase Storage, and tracks them in the `uploaded_files` table.

---

## What to Do

### Create Files
- `backend/app/api/v1/endpoints/files.py` — route handlers
- `backend/app/models/file.py` — Pydantic models
- `backend/app/services/storage.py` — Supabase Storage utility functions

### Storage Service
File: `backend/app/services/storage.py`

Create utility functions:
- `upload_file(firm_id, project_id, file_name, file_bytes, content_type)` → returns storage_path
- Storage path convention: `{firm_id}/{project_id}/{timestamp}_{file_name}`
- The timestamp prefix prevents filename collisions

### Upload Endpoint

`POST /api/v1/projects/{project_id}/files`

- Accepts: multipart/form-data
- Fields:
  - `file`: the actual file (required)
  - `document_type`: string (optional — 'profit_and_loss', 'balance_sheet', 'trial_balance', 'other')

### Upload Logic

1. Validate project_id belongs to current firm → 404 if not
2. Validate file type — only allow: xlsx, xls, pdf, jpg, png, csv
3. Validate file size — max 10MB
4. Upload file bytes to Supabase Storage bucket `cma-files`
5. Create row in `uploaded_files` table with:
   - firm_id from current user
   - cma_project_id from URL
   - file_name, file_type, file_size from uploaded file
   - storage_path from storage service
   - document_type from form field (or null)
   - extraction_status: 'pending'
   - uploaded_by: current user ID
6. Return the created file record

### Response Model

**FileResponse:**
- id, file_name, file_type, file_size, document_type
- extraction_status
- storage_path (for internal use)
- uploaded_by, created_at

### Error Handling

- Invalid file type → 422 "File type '.docx' not supported. Allowed: xlsx, xls, pdf, jpg, png, csv"
- File too large → 413 "File size exceeds 10MB limit"
- Project not found or wrong firm → 404
- Storage upload fails → 500 with clear error message, don't create DB record

---

## What NOT to Do

- Don't process/extract the file content (that's Phase 04)
- Don't auto-detect document type from content (keep it simple — user selects or null)
- Don't allow uploading to non-draft projects (status must be 'draft' or 'extracting')
- Don't create download endpoint here (that's task 3.6)

---

## Verification

- [ ] Upload a small .xlsx file → 201 Created, file record returned
- [ ] File appears in Supabase Storage → cma-files bucket at correct path
- [ ] Row created in `uploaded_files` table with correct metadata
- [ ] Upload .docx file → 422 rejection with clear message
- [ ] Upload 15MB file → 413 rejection
- [ ] Upload to project from another firm → 404
- [ ] Upload without auth → 401
- [ ] extraction_status is 'pending' after upload
- [ ] Audit log entry created

---

## Done → Move to task-3.6-file-download.md
