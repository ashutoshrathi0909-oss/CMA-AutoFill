# Task 3.6: File Download + List Endpoints

> **Phase:** 03 - API CRUD Endpoints
> **Depends on:** Task 3.5 (file upload works, storage service exists)
> **Agent reads:** CLAUDE.md → API Design Patterns
> **Time estimate:** 10 minutes

---

## Objective

Create endpoints to list files for a project and download individual files (both uploaded source documents and generated CMA files).

---

## What to Do

### Endpoints

| Method | Path | What It Does |
|--------|------|-------------|
| GET | `/api/v1/projects/{project_id}/files` | List all uploaded files for a project |
| GET | `/api/v1/files/{file_id}/download` | Download an uploaded file (signed URL) |
| GET | `/api/v1/projects/{project_id}/generated` | List generated CMA files for a project |
| GET | `/api/v1/generated/{file_id}/download` | Download a generated CMA file (signed URL) |

### List Uploaded Files

`GET /api/v1/projects/{project_id}/files`

- Validate project belongs to current firm
- Return all `uploaded_files` for this project
- Include: id, file_name, file_type, file_size, document_type, extraction_status, created_at
- Sort by created_at descending (newest first)
- No pagination needed (projects rarely have more than 10 files)

### Download Uploaded File

`GET /api/v1/files/{file_id}/download`

- Validate the file belongs to current firm (join through cma_project → firm_id)
- Generate a **signed URL** from Supabase Storage (expires in 1 hour)
- Return: `{"data": {"download_url": "https://...", "file_name": "...", "expires_in": 3600}}`
- The frontend will use this URL to trigger the download

### List Generated Files

`GET /api/v1/projects/{project_id}/generated`

- Same pattern as uploaded files list
- Return all `generated_files` for this project
- Include: id, file_name, file_size, version, generated_at

### Download Generated File

`GET /api/v1/generated/{file_id}/download`

- Same signed URL pattern as uploaded file download
- This is how the CA downloads the final CMA Excel file

### Add to Storage Service

Add to `backend/app/services/storage.py`:
- `get_signed_url(storage_path, expires_in=3600)` → returns a temporary download URL
- `delete_file(storage_path)` → deletes from storage (for cleanup)

---

## What NOT to Do

- Don't stream file bytes through the backend — use Supabase signed URLs (more efficient)
- Don't make signed URLs last longer than 1 hour
- Don't allow downloading files from other firms
- Don't create file deletion endpoint yet (not needed for MVP)

---

## Verification

- [ ] Upload a file (task 3.5) → list files → the file appears
- [ ] Download the file → signed URL returned → opens in browser
- [ ] Signed URL works in a new browser tab (no auth needed — URL itself is the auth)
- [ ] Try to download file from another firm → 404
- [ ] List files for empty project → returns empty array, not error
- [ ] Generated files list works (will be empty until Phase 06 creates CMA files)

---

## Done → Move to task-3.7-dashboard-stats.md
