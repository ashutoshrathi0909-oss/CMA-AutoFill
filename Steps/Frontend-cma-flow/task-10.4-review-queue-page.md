# Task 10.4: Review Queue Page

> **Phase:** 10 - Frontend CMA Flow
> **Depends on:** Phase 07 (review API endpoints), Phase 09 Task 9.6 (API client)
> **Time estimate:** 25 minutes

---

## Objective

Build the review queue UI where CAs approve or correct AI classifications. This is the "Ask Father" interface — the most important interaction screen for improving accuracy.

---

## What to Do

### Pages

**Standalone page:** `frontend/app/(dashboard)/review/page.tsx`
- Shows ALL pending reviews across all projects
- Accessible from sidebar navigation

**Project tab:** `components/projects/review-tab.tsx`
- Shows reviews for a specific project only
- Embedded in project detail tabs

### Review Queue Layout

```
┌─────────────────────────────────────────────────────┐
│ Review Queue                    8 items pending     │
│                           [Approve All Likely ▼]    │
├─────────────────────────────────────────────────────┤
│                                                     │
│ ┌─ Item 1 ──────────────────────────────────────┐  │
│ │ "Computer Repairs Expense"        ₹25,000      │  │
│ │ Confidence: ██░░░  45%                         │  │
│ │                                                │  │
│ │ AI suggests: Miscellaneous Expenses (Row 22)   │  │
│ │ Reason: "No exact rule. Could be Repairs or    │  │
│ │          Miscellaneous."                       │  │
│ │                                                │  │
│ │ Alternatives:                                  │  │
│ │  ○ Repairs & Maintenance (Row 15)    55%       │  │
│ │  ○ Miscellaneous Expenses (Row 22)   40%       │  │
│ │  ○ Administrative Expenses (Row 18)  35%       │  │
│ │  ○ Other: [Select CMA Row ▼]                   │  │
│ │                                                │  │
│ │ [✓ Approve AI] [→ Use Selected] [Skip]        │  │
│ └────────────────────────────────────────────────┘  │
│                                                     │
│ ┌─ Item 2 ──────────────────────────────────────┐  │
│ │ "Telephone Charges"               ₹12,000      │  │
│ │ Confidence: ███░░  55%                         │  │
│ │ ...                                            │  │
│ └────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### Review Item Card

`components/review/review-item-card.tsx`

Each card shows:
- **Item name** (large, bold) + amount (formatted as ₹)
- **Confidence bar** (visual, color-coded: red <40%, amber 40-60%, yellow 60-70%)
- **AI suggestion** with row number and label
- **AI reasoning** (collapsible, shown by default for low confidence)
- **Alternative suggestions** as radio buttons (from API)
- **"Other" option** with searchable CMA row dropdown
- **Action buttons:**
  - "✓ Approve AI" (green) — accept AI's suggestion
  - "→ Use Selected" (gold) — use the alternative the CA picked
  - "Skip" (gray) — skip this item

### CMA Row Dropdown

`components/review/cma-row-selector.tsx`

- Searchable dropdown of all valid CMA rows
- Grouped by sheet (Operating Statement, Balance Sheet, etc.)
- Search by label text
- Shows row number + label
- Used when CA wants to manually specify a row not in alternatives

### Bulk Actions

- "Approve All Likely" dropdown:
  - Approve all items with confidence >= 60%
  - Approve all items with confidence >= 50%
  - Custom threshold
- Confirmation dialog before bulk action

### Progress Indicator

After resolving items, show running count:
- "5 of 8 items resolved. 3 remaining."
- When all resolved: "All items reviewed! Ready to generate CMA." + "Generate CMA →" button

### Data Flow

1. Load: `GET /api/v1/review-queue?project_id=X&status=pending`
2. Approve: `POST /api/v1/review-queue/{id}/resolve` with action="approve"
3. Correct: `POST /api/v1/review-queue/{id}/resolve` with action="correct" + target_row
4. After all resolved: `POST /api/v1/projects/{id}/apply-reviews`
5. Then: show "Generate CMA" button or auto-navigate to next step

---

## What NOT to Do

- Don't auto-approve anything without CA's explicit action
- Don't show resolved items by default (add a toggle to view history)
- Don't make the CA type row numbers — always provide searchable dropdown
- Don't reload the entire page after each resolution (optimistic UI update)

---

## Verification

- [ ] Review queue loads with pending items sorted by confidence (lowest first)
- [ ] Confidence bar is visually clear (color + percentage)
- [ ] AI suggestion and reasoning displayed clearly
- [ ] Alternative radio buttons work
- [ ] "Other" dropdown searches CMA rows
- [ ] Approve → item disappears from list, success toast
- [ ] Correct → precedent created, item resolved
- [ ] Skip → item marked skipped
- [ ] Bulk approve works with confirmation
- [ ] All resolved → "Ready to generate" message
- [ ] Optimistic updates (instant UI feedback, no page reload)

---

## Done → Move to task-10.5-classification-view.md
