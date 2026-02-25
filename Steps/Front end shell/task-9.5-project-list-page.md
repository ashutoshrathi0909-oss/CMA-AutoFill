# Task 9.5: Projects List Page

> **Phase:** 09 - Frontend Shell
> **Depends on:** Task 9.4 (table/filter patterns established)
> **Time estimate:** 15 minutes

---

## Objective

Build the CMA projects list page with status badges, filters, and quick actions.

---

## What to Do

### Page
`frontend/app/(dashboard)/projects/page.tsx`

### Layout

```
┌─────────────────────────────────────────────────────┐
│ CMA Projects                    [+ New CMA Project] │
├─────────────────────────────────────────────────────┤
│ 🔍 Search...  │ Status: [All ▼] │ Client: [All ▼]  │
├─────────────────────────────────────────────────────┤
│ Client       │ FY      │ Status      │ Progress │ ⚡│
│──────────────┼─────────┼─────────────┼──────────┼───│
│ Mehta Comp.  │ 2024-25 │ ● Completed │ ████ 100%│ ↓ │
│ Sharma Text. │ 2024-25 │ ● Reviewing │ ██░░  50%│ 👁 │
│ Patel Mfg.   │ 2024-25 │ ○ Draft     │ ░░░░   0%│ ▶ │
└─────────────────────────────────────────────────────┘
```

### Status Badges

Color-coded pill badges:
- `draft` → gray
- `extracting` / `classifying` / `validating` / `generating` → blue (pulsing animation)
- `reviewing` → amber
- `completed` → green
- `error` → red

### Quick Actions Column

Context-dependent actions per row:
- **Draft:** ▶ Process (start pipeline)
- **Processing:** spinner (no action, auto-progressing)
- **Reviewing:** 👁 Review (navigate to review queue filtered by project)
- **Completed:** ↓ Download CMA
- **Error:** 🔄 Retry

### New CMA Project Modal

`components/projects/new-project-modal.tsx`:
- Select client (dropdown, searchable)
- Financial year (e.g., "2024-25")
- Bank name (optional)
- Loan type (dropdown: Term Loan, Working Capital, CC/OD, Other)
- Loan amount (optional)
- Submit → creates project in 'draft' status, navigates to project detail

### Progress Bar

Thin horizontal bar in each row showing pipeline_progress (0-100%).

---

## What NOT to Do

- Don't build the project detail page here (that's Phase 10)
- Don't implement file upload in the modal (that's Phase 10)
- Don't start the pipeline from this page (just navigate to project detail)

---

## Verification

- [ ] Project list loads with correct data
- [ ] Status badges have correct colors
- [ ] Progress bars show correct percentages
- [ ] Filter by status works
- [ ] Filter by client works
- [ ] "New CMA Project" creates a project successfully
- [ ] Quick action buttons work (navigate or trigger action)
- [ ] Processing projects show pulsing animation

---

## Done → Move to task-9.6-api-client.md
