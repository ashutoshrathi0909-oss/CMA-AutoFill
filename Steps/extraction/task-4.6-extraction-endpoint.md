# Task 4.6: Extraction API Endpoint

> **Phase:** 04 - Document Extraction
> **Depends on:** Tasks 4.1-4.5 (all parsers, extractors, and prompts ready)
> **Agent reads:** CLAUDE.md → API Design Patterns
> **Time estimate:** 15 minutes

---

## Objective

Create the API endpoint that triggers extraction on uploaded files for a CMA project. This is the first step of the AI pipeline.

---

## What to Do

### Create File
`backend/app/api/v1/endpoints/extraction.py`

### Endpoint

`POST /api/v1/projects/{project_id}/extract`

### Request Body (optional)
```json
{
  "file_ids": ["uuid1", "uuid2"],     // specific files to extract (optional — default: all pending files)
  "force_reextract": false             // re-extract even if already done
}
```

### Extraction Logic

1. **Validate** project belongs to current firm → 404 if not
2. **Get files to extract:**
   - If `file_ids` provided → extract only those files
   - If not → extract all `uploaded_files` with `extraction_status = 'pending'`
   - If no files to extract → return 400 "No files pending extraction"
3. **Update project status** → `status = 'extracting'`, `pipeline_progress = 10`
4. **For each file, route to correct parser:**

   | File Type | Parser | AI Used? |
   |-----------|--------|----------|
   | .xlsx, .xls | excel_parser (task 4.2) | No |
   | .csv | excel_parser (adapted) | No |
   | .pdf (digital) | pdf_parser (task 4.3) | No |
   | .pdf (scanned) | vision_extractor (task 4.4) | Yes (Gemini 2.0 Flash) |
   | .jpg, .png | vision_extractor (task 4.4) | Yes (Gemini 2.0 Flash) |

5. **For each file:**
   - Update `extraction_status = 'processing'`
   - Download file from Supabase Storage
   - Route to correct parser
   - On success: save extracted data to `uploaded_files.extracted_data`, set `extraction_status = 'completed'`
   - On failure: set `extraction_status = 'failed'`, save error message
   - Log LLM usage if AI was used

6. **Update pipeline progress** incrementally (10% base + proportional per file)

### Response
```json
{
  "data": {
    "project_id": "uuid",
    "files_processed": 3,
    "files_succeeded": 2,
    "files_failed": 1,
    "total_line_items_extracted": 87,
    "results": [
      {
        "file_id": "uuid",
        "file_name": "mehta_pl.xlsx",
        "status": "completed",
        "line_items_count": 45,
        "document_type": "profit_and_loss"
      },
      {
        "file_id": "uuid",
        "file_name": "blurry_scan.jpg",
        "status": "failed",
        "error": "Could not extract readable data from image"
      }
    ]
  }
}
```

### Error Handling

- If ALL files fail → update project status to 'error' with message
- If SOME files fail → continue with successful ones, report failures in response
- If extraction takes too long (>60s per file) → timeout and mark as failed

---

## What NOT to Do

- Don't run classification after extraction (that's Phase 05)
- Don't run this in background yet (Phase 08 handles async pipeline)
- Don't merge extracted data from multiple files yet (that happens in classification)
- Don't validate numbers (that's Phase 06)

---

## Verification

- [ ] Upload Mehta Computers Excel → run extraction → all line items extracted with correct amounts
- [ ] Upload a test PDF → extraction works
- [ ] Upload a test image → Gemini Vision extracts data
- [ ] Project status updated to 'extracting' during process
- [ ] Each file's extraction_status updated correctly
- [ ] Failed file doesn't crash the entire batch
- [ ] LLM usage logged for Vision calls
- [ ] Response includes per-file results
- [ ] Auth required → 401 without token
- [ ] Wrong firm's project → 404

---

## Done → Move to task-4.7-save-extracted-data.md
