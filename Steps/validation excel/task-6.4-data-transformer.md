# Task 6.4: Data Transformer (Classification → Writer Input)

> **Phase:** 06 - Validation & Excel Generation
> **Depends on:** Task 6.3 (CMA writer adapted), Phase 05 (classification data format known)
> **Agent reads:** cma-domain SKILL → CMA Template Structure (289 rows, 15 sheets)
> **Time estimate:** 15 minutes

---

## Objective

Create a transformer that converts classified data (from Phase 05) into the exact dict format that `cma_writer.py` expects. This bridges the gap between AI classification output and the proven Excel writer.

---

## What to Do

### Create File
`backend/app/services/excel/data_transformer.py`

### The Problem

Classification outputs:
```json
[
  {"item_name": "Sales", "item_amount": 1500000, "target_row": 5, "target_sheet": "operating_statement"},
  {"item_name": "Purchases", "item_amount": 900000, "target_row": 10, "target_sheet": "operating_statement"}
]
```

CMA Writer expects:
```python
{
  "operating_statement": {
    5: 1500000,    # Row 5 = Net Sales
    10: 900000,    # Row 10 = Purchases
    12: 600000,    # Row 12 = Gross Profit (calculated)
  },
  "balance_sheet": {
    3: 500000,     # Row 3 = Fixed Assets
    ...
  }
}
```

### Transform Function

`transform_for_writer(classified_items: list[ClassifiedItem], entity_type: str) → dict`

Logic:
1. Group classified items by `target_sheet`
2. For each item, map `target_row` → `item_amount`
3. If multiple items map to the same row (rare but possible), SUM them
4. Calculate derived rows (totals, subtotals, computed values):
   - Gross Profit = Sales - COGS
   - Net Profit = Gross Profit - Expenses + Other Income
   - Total Current Assets = sum of all current asset items
   - Total Current Liabilities = sum of all current liability items
   - Working Capital = Current Assets - Current Liabilities
5. Handle rows that need special treatment:
   - Percentage rows (e.g., "as % of Net Sales") → calculate from data
   - Ratio rows → calculate Current Ratio, Debt-Equity, etc.
   - Year-over-year change rows → if previous year data available

### Computed Row Registry

Create a registry of rows that are CALCULATED (not directly from source data):

```python
COMPUTED_ROWS = {
    ("operating_statement", 12): {"formula": "row_5 - row_10", "label": "Gross Profit"},
    ("operating_statement", 25): {"formula": "sum(row_13:row_24)", "label": "Total Operating Expenses"},
    ("balance_sheet", 15): {"formula": "sum(row_3:row_14)", "label": "Total Fixed Assets"},
    ...
}
```

For these rows, compute the value from the data instead of expecting it from classification.

### Handle Missing Data

- If a mandatory row has no classified item → set to 0 and add a warning
- If an optional row has no data → leave blank (don't set to 0)
- Log all missing mandatory rows for debugging

### Multiple Financial Years

The CMA template has columns for:
- Audited Year 1 (2 years ago)
- Audited Year 2 (last year)  
- Estimated Year (current year)
- Projected Year 1 (next year)
- Projected Year 2 (2 years ahead)

For V1: only populate the "Estimated Year" column. Other columns stay blank or 0.
Future: user uploads multiple years → populate all columns.

---

## What NOT to Do

- Don't modify the CMA writer's internal logic
- Don't try to populate all 5 year columns (V1 = current year only)
- Don't skip computed rows — they're critical for CMA accuracy
- Don't drop items that couldn't be classified — set them aside and warn

---

## Verification

- [ ] Mehta Computers classified data → transform → dict format matches writer's expectations
- [ ] Computed rows (Gross Profit, Net Profit, totals) calculated correctly
- [ ] Multiple items on same row → summed correctly
- [ ] Missing mandatory row → warning generated
- [ ] Writer accepts the transformed data without errors
- [ ] All 15 sheets have data where applicable
- [ ] Percentage/ratio rows calculated correctly

---

## Done → Move to task-6.5-excel-generation.md
