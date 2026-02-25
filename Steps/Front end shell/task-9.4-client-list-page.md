# Task 9.4: Clients List Page

> **Phase:** 09 - Frontend Shell
> **Depends on:** Task 9.3 (dashboard pattern established), Phase 03 Task 3.3 (client CRUD API)
> **Time estimate:** 20 minutes

---

## Objective

Build the clients management page with list, search, filter, and create/edit modals.

---

## What to Do

### Page
`frontend/app/(dashboard)/clients/page.tsx`

### Layout

```
┌─────────────────────────────────────────────┐
│ Clients                    [+ Add Client]   │
├─────────────────────────────────────────────┤
│ 🔍 Search clients...  │ Type: [All ▼]      │
├─────────────────────────────────────────────┤
│ Name          │ Type     │ CMAs │ Added     │
│───────────────┼──────────┼──────┼───────────│
│ Mehta Comp.   │ Trading  │  3   │ Jan 2026  │
│ Sharma Text.  │ Mfg      │  1   │ Feb 2026  │
│ ...           │          │      │           │
├─────────────────────────────────────────────┤
│ Showing 1-10 of 12        [< 1 2 >]        │
└─────────────────────────────────────────────┘
```

### Components

**Client Table** (`components/clients/client-table.tsx`):
- Columns: Name, Entity Type (badge), CMA Count, Contact Person, Added Date
- Click row → expand or navigate to client detail
- Hover actions: Edit, Delete (soft)

**Search + Filter Bar** (`components/clients/client-filters.tsx`):
- Search: debounced text input, searches by name
- Filter: entity type dropdown (All, Trading, Manufacturing, Service)
- Results update as user types

**Add/Edit Client Modal** (`components/clients/client-form-modal.tsx`):
- shadcn Dialog component
- Fields: name*, entity_type* (select), PAN, GST, contact person, email, phone, address
- Validation: name required, entity_type required
- Submit → POST or PUT to API

**Pagination** (`components/ui/pagination.tsx`):
- Reusable pagination component
- Shows page numbers, prev/next
- Per-page selector: 10, 20, 50

### shadcn/ui Components to Install

```bash
npx shadcn-ui@latest add dialog input select table card
```

---

## What NOT to Do

- Don't build a separate client detail page (V1 = inline expand or modal)
- Don't implement client deletion in V1 (just soft-delete via API if needed)
- Don't add complex filters beyond entity type

---

## Verification

- [ ] Client list loads with data from API
- [ ] Search by name works (debounced, no page reload)
- [ ] Filter by entity type works
- [ ] "Add Client" opens modal, form validates, saves to API
- [ ] Edit client updates correctly
- [ ] Pagination works
- [ ] Empty state: "No clients yet. Add your first client!"
- [ ] Loading skeleton while data fetches

---

## Done → Move to task-9.5-project-list-page.md
