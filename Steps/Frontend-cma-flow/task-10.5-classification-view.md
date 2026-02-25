# Task 10.5: Classification View

> **Phase:** 10 - Frontend CMA Flow
> **Depends on:** Phase 05 Task 5.7 (classification API)
> **Time estimate:** 15 minutes

---

## Objective

Build a view showing all classified items grouped by CMA sheet, so the CA can see the full mapping at a glance and spot any issues.

---

## What to Do

### Component
`components/projects/classification-tab.tsx`

### Layout

```
┌──────────────────────────────────────────────────┐
│ Classification Summary        73% auto-classified │
│ ████████░░ 33 auto  │ 10 review  │ 2 unclassified│
├──────────────────────────────────────────────────┤
│ [Operating Statement] [Balance Sheet] [All]      │
├──────────────────────────────────────────────────┤
│ Operating Statement                              │
│ ┌────────────────────────────────────────────┐   │
│ │ Row 5: Net Sales              ₹15,00,000   │   │
│ │        ← Sales (rule, 95%)                 │   │
│ │ Row 10: Purchases             ₹9,00,000    │   │
│ │        ← Purchases A/c (rule, 92%)         │   │
│ │ Row 12: Gross Profit          ₹6,00,000    │   │
│ │        ← Computed                          │   │
│ │ Row 15: Repairs & Maintenance ₹25,000      │   │
│ │        ← Computer Repairs (CA review, 100%)│   │
│ │ ...                                        │   │
│ └────────────────────────────────────────────┘   │
│                                                  │
│ Balance Sheet                                    │
│ ┌────────────────────────────────────────────┐   │
│ │ Row 3: Fixed Assets           ₹5,00,000    │   │
│ │ ...                                        │   │
│ └────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────┘
```

### Features

**Summary Bar:**
- Total items, auto-classified count, review count, unclassified count
- Visual progress bar

**Sheet Grouping:**
- Tabs or accordion to switch between CMA sheets
- "All" view shows everything

**Per-Item Display:**
- CMA row number + official label (right side: amount formatted as ₹)
- Source item name + classification source badge:
  - 🟢 "rule" — matched via rules
  - 🔵 "precedent" — matched via CA precedent
  - 🟣 "ai" — classified by Gemini
  - 🟡 "ca_review" — manually set by CA
  - ⚪ "unclassified" — no mapping
- Confidence percentage
- Click to expand: show reasoning, matched rule ID, alternative suggestions

**Empty Rows:**
- Show CMA rows that have NO classified item mapped (gaps)
- Mark as "⚠ No data" in muted text
- Helps CA spot missing items

**Export Option:**
- "Export Classification Report" button → downloads a summary as CSV or PDF
- Useful for CA's own records

---

## What NOT to Do

- Don't allow editing classifications from this view (use Review tab for that)
- Don't show every CMA row if it's empty — only show rows with data + mandatory empty rows
- Don't make this tab slow — it may have 50+ items

---

## Verification

- [ ] All classified items displayed grouped by sheet
- [ ] Source badges show correct colors
- [ ] Amounts formatted as Indian currency (₹12,34,567)
- [ ] Computed rows (Gross Profit, etc.) marked as "Computed"
- [ ] CA-reviewed items marked with "CA Review" badge
- [ ] Empty mandatory rows shown with warning
- [ ] Tab switching between sheets works
- [ ] Expand item → shows reasoning and confidence

---

## Done → Move to task-10.6-validation-view.md
