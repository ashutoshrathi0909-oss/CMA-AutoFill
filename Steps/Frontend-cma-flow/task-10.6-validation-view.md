# Task 10.6: Validation Results View

> **Phase:** 10 - Frontend CMA Flow
> **Depends on:** Phase 06 Tasks 6.1-6.2 (validation API)
> **Time estimate:** 15 minutes

---

## Objective

Build the validation tab showing all checks with pass/fail status and auto-fix actions.

---

## What to Do

### Component
`components/projects/validation-tab.tsx`

### Layout

```
┌──────────────────────────────────────────────────┐
│ Validation Results            ✓ Passed (2 warns) │
│                                                  │
│ ✓ Balance Sheet Balance                          │
│   Assets ₹52,00,000 = Liabilities ₹52,00,000    │
│                                                  │
│ ✓ P&L Gross Profit                               │
│   Sales - COGS = ₹6,00,000 ✓                    │
│                                                  │
│ ✗ P&L Net Profit Mismatch                 ERROR  │
│   Expected: ₹2,50,000  Got: ₹2,45,000           │
│   Difference: ₹5,000                            │
│   [Apply Auto-Fix: Set Net Profit to ₹2,50,000] │
│                                                  │
│ ⚠ Current Ratio Outside Range             WARN  │
│   Current Ratio: 0.8 (typical: 1.0-3.0)         │
│   This may raise questions from the bank.        │
│                                                  │
│ ... more checks ...                              │
│                                                  │
│ ─────────────────────────────────────────────── │
│ 2 errors must be fixed.  [Apply All Auto-Fixes]  │
│                          [Generate Anyway]        │
└──────────────────────────────────────────────────┘
```

### Check Display

Each validation check:
- **Pass** (✓ green): rule name + values that matched
- **Error** (✗ red): rule name + expected vs actual + difference
  - Auto-fix button if available: "Apply Fix: Set X to Y"
  - Manual instruction if not auto-fixable
- **Warning** (⚠ amber): rule name + observation + context

### Auto-Fix Actions

When CA clicks "Apply Auto-Fix":
1. Call `POST /projects/{id}/apply-fixes` with the fix details
2. Show optimistic update (check turns green)
3. Re-validate in background to confirm fix worked
4. Update validation results

"Apply All Auto-Fixes" button:
- Applies all available auto-fixes at once
- Confirmation dialog first
- Re-validates after

### Bottom Actions

- If all checks pass: "Generate CMA →" button (gold, prominent)
- If errors exist: "Apply All Auto-Fixes" + "Generate Anyway" (with warning)
- "Generate Anyway" requires confirmation: "Are you sure? The CMA may have errors."

### Run Validation Button

"Re-run Validation" button to manually trigger validation:
- Useful after making manual changes
- Calls `POST /projects/{id}/validate`

---

## What NOT to Do

- Don't auto-apply fixes without CA clicking
- Don't hide warnings (they're useful context for the CA)
- Don't block generation on warnings (only on errors)

---

## Verification

- [ ] All validation checks displayed with correct pass/fail
- [ ] Error checks show expected vs actual values
- [ ] Auto-fix button works → check turns green
- [ ] "Apply All" works with confirmation
- [ ] Warnings shown but don't block generation
- [ ] "Generate CMA" button appears when validation passes
- [ ] "Generate Anyway" works with warning dialog
- [ ] Re-validate button triggers fresh validation

---

## Done → Move to task-10.7-download-page.md
