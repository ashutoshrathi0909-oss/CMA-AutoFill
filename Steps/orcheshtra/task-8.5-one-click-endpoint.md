# Task 8.5: One-Click Process Endpoint

> **Phase:** 08 - Pipeline Orchestrator
> **Depends on:** Tasks 8.1-8.4 (orchestrator, background, progress, retry all working)
> **Time estimate:** 10 minutes

---

## Objective

Create the single endpoint that the frontend's "Process CMA" button calls. Upload files + run the entire pipeline in one flow.

---

## What to Do

### Endpoint

**`POST /api/v1/projects/{project_id}/process`**

Request body (optional):
```json
{
  "skip_review": false,
  "auto_approve_above": 0.70,     // auto-approve review items above this confidence
  "notify_on_review": true
}
```

### Logic

1. Validate project has uploaded files → 400 if no files
2. Check project isn't already processing → 409 if processing
3. Start background pipeline with options
4. Return immediately with tracking info

Response:
```json
{
  "data": {
    "project_id": "uuid",
    "status": "processing",
    "message": "Pipeline started. Track progress at /projects/{id}/progress",
    "estimated_duration_seconds": 30,
    "files_to_process": 3
  }
}
```

### Also Create: Quick Upload + Process

**`POST /api/v1/projects/{project_id}/upload-and-process`**

Combines file upload (task 3.5) + process (this task) into one call:
- Accepts multipart/form-data with files
- Uploads all files to storage
- Starts pipeline immediately
- Returns processing status

This is the "one-click" experience: drag files → everything happens automatically.

### Status Transition Summary

After this task, the complete project lifecycle is:

```
draft → (upload files) → draft
      → (start processing) → extracting → extracted
      → classifying → classified
      → reviewing (if items need review) ← CA reviews → validated
      → validating → validated
      → generating → completed
      
      → error (at any step, with retry option)
```

---

## What NOT to Do

- Don't make this synchronous — must return immediately
- Don't bypass auth checks
- Don't allow processing empty projects
- Don't create a new project — this processes an existing one

---

## Verification

- [ ] POST process → returns immediately, pipeline starts in background
- [ ] Poll progress → see steps completing
- [ ] Pipeline completes → status = 'completed', CMA file downloadable
- [ ] Pipeline pauses at review → status = 'reviewing', email sent
- [ ] Upload-and-process → files uploaded + pipeline starts in one call
- [ ] Already processing → 409 error
- [ ] No files → 400 error

---

## Done → Move to task-8.6-pipeline-hooks.md
