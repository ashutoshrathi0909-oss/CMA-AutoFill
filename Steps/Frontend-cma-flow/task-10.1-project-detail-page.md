# Task 10.1: Project Detail Page

> **Phase:** 10 - Frontend CMA Flow
> **Depends on:** Phase 09 (app shell, API client, project list)
> **Time estimate:** 20 minutes

---

## Objective

Build the project detail page — the central hub where CAs manage a single CMA project through its lifecycle.

---

## What to Do

### Page
`frontend/app/(dashboard)/projects/[id]/page.tsx`

### Layout

```
┌─────────────────────────────────────────────────┐
│ ← Back   Mehta Computers — 2024-25    ● Review  │
│          SBI Term Loan ₹50,00,000               │
├─────────────────────────────────────────────────┤
│ Pipeline: ████████████░░░░░░░░  50%  Reviewing  │
│ Extract ✓ → Classify ✓ → Review ⏳ → Valid → Gen │
├─────────────────────────────────────────────────┤
│ [Files] [Classification] [Review] [Validation]  │
├─────────────────────────────────────────────────┤
│                                                 │
│              Tab Content Area                   │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Header Section

- Back button → projects list
- Client name + financial year (large)
- Bank name + loan type + amount (subtitle)
- Status badge (color-coded, same as project list)
- Action button (context-dependent):
  - Draft: "Upload Files" or "Start Processing"
  - Reviewing: "Review Items (8)"
  - Validated: "Generate CMA"
  - Completed: "Download CMA"
  - Error: "Retry"

### Pipeline Progress Bar

Visual step indicator:
- 5 steps: Extract → Classify → Review → Validate → Generate
- Each step: circle icon + label
- States: completed (green ✓), active (blue pulsing), pending (gray), error (red ✗)
- Connecting lines between steps fill as progress advances
- Tooltip on each step: "Completed in 2.5s" or "8 items pending review"

### Tab Navigation

Tabs shown below pipeline bar (using shadcn Tabs):
1. **Files** — uploaded files (task 10.2)
2. **Classification** — all classified items (task 10.5)
3. **Review** — pending review items (task 10.4)
4. **Validation** — validation results (task 10.6)
5. **Output** — download CMA (task 10.7)

Tabs are enabled/disabled based on pipeline progress:
- Draft: only Files tab active
- Extracting+: Files + Classification
- Reviewing+: Files + Classification + Review
- Validated+: all tabs
- Completed: all tabs, Output tab auto-selected

### Data Fetching

- Fetch project details on load: `GET /api/v1/projects/{id}`
- Fetch progress if processing: `GET /api/v1/projects/{id}/progress` (poll every 2s)
- Stop polling when `is_processing = false`

---

## What NOT to Do

- Don't build tab content (tasks 10.2-10.7 handle each tab)
- Don't allow editing project details after processing starts
- Don't show tabs for steps that haven't been reached

---

## Verification

- [ ] Project detail loads with correct header info
- [ ] Pipeline progress bar shows current state
- [ ] Tabs switch correctly
- [ ] Context-dependent action button works
- [ ] Processing project → progress bar animates (polling)
- [ ] Completed project → all tabs available
- [ ] Draft project → only Files tab

---

## Done → Move to task-10.2-file-upload-ui.md
