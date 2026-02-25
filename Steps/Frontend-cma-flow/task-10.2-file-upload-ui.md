# Task 10.2: File Upload UI

> **Phase:** 10 - Frontend CMA Flow
> **Depends on:** Task 10.1 (project detail page), Phase 03 Task 3.5 (upload API)
> **Time estimate:** 15 minutes

---

## Objective

Build the file upload tab with drag-and-drop zone, file preview list, and upload progress.

---

## What to Do

### Component
`components/projects/files-tab.tsx`

### Drag-and-Drop Zone

```
┌─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─┐
│                                         │
│    📄 Drop files here or click to       │
│       browse                            │
│                                         │
│    Supports: xlsx, xls, pdf, csv,       │
│    jpg, png (max 10MB each)             │
│                                         │
└─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─┘
```

- Dashed border zone, highlights on drag-over (gold border)
- Click to open file picker
- Multiple file selection
- File type validation before upload
- File size validation (10MB max)

### Uploaded Files List

```
┌──────────────────────────────────────────┐
│ 📊 mehta_pl_2024.xlsx    45 KB  ✓ Ready │
│    Type: Profit & Loss                   │
├──────────────────────────────────────────┤
│ 📊 mehta_bs_2024.xlsx    38 KB  ✓ Ready │
│    Type: Balance Sheet                   │
├──────────────────────────────────────────┤
│ 📷 scan_page3.jpg       2.1 MB  ⏳ Uploading 65% │
│    Type: Auto-detect                     │
└──────────────────────────────────────────┘
```

Each file shows:
- File icon (by type)
- File name + size
- Document type selector (P&L, Balance Sheet, Trial Balance, Other, Auto-detect)
- Upload status: uploading (progress bar), ready, failed
- Actions: remove (before processing), download

### Upload Logic

1. User drops/selects files
2. Validate type and size client-side
3. Upload each file to `POST /api/v1/projects/{id}/files` with progress tracking
4. Show per-file upload progress bar
5. On complete: file appears in list with "Ready" status
6. Show total: "3 files ready for processing"

### Process Button

Below file list:
- "Process CMA →" button (gold, prominent)
- Disabled if no files uploaded
- Clicking starts the pipeline (calls `POST /projects/{id}/process`)
- Navigates to Processing view (task 10.3)

---

## What NOT to Do

- Don't allow upload after processing has started
- Don't auto-start processing on upload (user clicks when ready)
- Don't implement complex document type detection on frontend (backend handles it)

---

## Verification

- [ ] Drag file onto zone → upload starts, progress shown
- [ ] Click zone → file picker opens
- [ ] Invalid file type → error message, no upload
- [ ] File > 10MB → error message
- [ ] Multiple files → all upload simultaneously with individual progress
- [ ] Document type dropdown works
- [ ] "Process CMA" button enabled only when files exist
- [ ] Remove file before processing works

---

## Done → Move to task-10.3-processing-view.md
