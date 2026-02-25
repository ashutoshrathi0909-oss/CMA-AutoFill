# Task 4.7: Save Extracted Data + Update Project Status

> **Phase:** 04 - Document Extraction
> **Depends on:** Task 4.6 (extraction endpoint works)
> **Agent reads:** CLAUDE.md → Database Tables → cma_projects, uploaded_files
> **Time estimate:** 15 minutes

---

## Objective

After extraction, merge data from all files into a single consolidated dataset on the project, update the project status, and write tests that verify extraction against the Mehta Computers reference data.

---

## What to Do

### Step 1: Create Data Merger
File: `backend/app/services/extraction/merger.py`

When a project has multiple uploaded files (e.g., separate P&L and Balance Sheet), merge their extracted line items into one consolidated dataset.

**Merge logic:**
1. Collect all `extracted_data` from `uploaded_files` where extraction_status = 'completed'
2. Group by `document_type` (P&L items stay separate from BS items)
3. Deduplicate: if same item appears in two files, keep the one with higher amount (or flag for review)
4. Create consolidated structure:

```json
{
  "profit_and_loss": {
    "line_items": [...],
    "totals": {...}
  },
  "balance_sheet": {
    "line_items": [...],
    "totals": {...}
  },
  "trial_balance": null,
  "metadata": {
    "source_files": ["file1.xlsx", "file2.pdf"],
    "total_line_items": 87,
    "merged_at": "2026-02-23T10:30:00Z"
  }
}
```

### Step 2: Save to Project
After successful extraction + merge:
- Save merged data to `cma_projects.extracted_data` (JSONB column)
- Update `status` to `'classifying'` wait state (ready for Phase 05)
  - Actually, set to a transitional status. Use `'extracted'` — add this to the status CHECK constraint if not already there. Status flow: draft → extracting → extracted → classifying → ...
- Update `pipeline_progress` to 25

**IMPORTANT:** If the CHECK constraint on `cma_projects.status` doesn't include 'extracted', ALTER the constraint to add it. Full status list should be: 'draft', 'extracting', 'extracted', 'classifying', 'reviewing', 'validating', 'generating', 'completed', 'error'

### Step 3: Create Extraction Tests
File: `backend/tests/test_extraction.py`

**Test 1: Excel Parser**
- Input: Mehta Computers P&L Excel file (from reference/)
- Assert: extracted line_items contain "Sales" with correct amount
- Assert: extracted line_items count matches expected count
- Assert: document_type detected as "profit_and_loss"

**Test 2: PDF Parser**
- Input: a simple test PDF (create a minimal one for testing)
- Assert: parser detects digital vs scanned correctly
- Assert: line items extracted

**Test 3: Standardized Format**
- Input: any parsed output
- Assert: output has all required fields (document_type, line_items, totals, metadata)
- Assert: every line_item has: name, amount, parent_group, level, is_total, raw_text
- Assert: amounts are numbers (not strings)

**Test 4: Merger**
- Input: two extracted datasets (P&L + BS)
- Assert: merged output has both sections
- Assert: deduplication works
- Assert: metadata shows source files

**Test 5: Golden Test (Mehta Computers)**
- Upload Mehta Computers files → run full extraction → compare output against known expected values
- This is the first piece of the end-to-end golden test
- Store expected values as a fixture file: `backend/tests/fixtures/mehta_expected_extraction.json`

### Step 4: Audit Logging
Log extraction events:
- action: 'run_extraction'
- metadata: `{"files_processed": 3, "line_items_extracted": 87, "duration_ms": 1500}`

---

## What NOT to Do

- Don't run classification (Phase 05)
- Don't validate numbers (Phase 06)
- Don't delete uploaded files after extraction
- Don't overwrite per-file extracted_data when saving merged data to project (keep both)

---

## Verification

- [ ] After extraction, `cma_projects.extracted_data` has the merged consolidated JSON
- [ ] `cma_projects.status` is 'extracted'
- [ ] `cma_projects.pipeline_progress` is 25
- [ ] Per-file `uploaded_files.extracted_data` still has individual file data
- [ ] `pytest backend/tests/test_extraction.py` → all tests pass
- [ ] Golden test: Mehta Computers extraction matches expected fixture data
- [ ] Merger handles single-file projects (only P&L, no BS) gracefully
- [ ] Merger handles empty extraction results gracefully
- [ ] Audit log has extraction event

---

## Phase 04 Complete! 🎉

All 7 tasks done. You now have:
- ✅ Gemini API client with token tracking and cost logging
- ✅ Excel parser for Tally/Busy exports
- ✅ PDF parser for digital documents
- ✅ Vision extractor for scanned documents (Gemini 2.0 Flash)
- ✅ Optimized extraction prompts
- ✅ Extraction API endpoint with per-file routing
- ✅ Data merger for multi-file projects
- ✅ Tests including Mehta Computers golden test
- ✅ Pipeline status tracking (extracting → extracted)

**Next → Phase 05: Classification (AI maps items to CMA rows)**
