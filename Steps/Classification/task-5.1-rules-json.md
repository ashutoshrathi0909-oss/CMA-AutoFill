# Task 5.1: Convert Classification Rules to JSON

> **Phase:** 05 - Classification
> **Depends on:** Phase 04 complete. File `reference/CMA_classification.xls` available.
> **Agent reads:** cma-domain SKILL → Classification System
> **Time estimate:** 15 minutes

---

## Objective

Convert the 384-rule classification table from Excel into a structured JSON file that the classifier can load and query efficiently.

---

## What to Do

### Input
File: `reference/CMA_classification.xls` — the master classification rules table created during POC.

### Output
File: `backend/app/services/classification/classification_rules.json`

### JSON Structure

```json
{
  "version": "1.0",
  "total_rules": 384,
  "last_updated": "2026-02-25",
  "rules": [
    {
      "id": 1,
      "source_terms": ["Sales", "Revenue from Operations", "Turnover", "Sales A/c", "Income from Sales"],
      "target_row": 5,
      "target_sheet": "operating_statement",
      "target_label": "Net Sales / Income from Operations",
      "entity_types": ["trading", "manufacturing", "service"],
      "document_types": ["profit_and_loss"],
      "priority": 1,
      "match_type": "exact_or_fuzzy",
      "notes": "Primary revenue line. May appear as multiple variants."
    },
    {
      "id": 2,
      "source_terms": ["Purchases", "Purchase of Stock-in-Trade", "Cost of Goods Purchased"],
      "target_row": 10,
      "target_sheet": "operating_statement",
      "target_label": "Cost of Goods Sold - Purchases",
      "entity_types": ["trading"],
      "document_types": ["profit_and_loss"],
      "priority": 1,
      "match_type": "exact_or_fuzzy",
      "notes": "Trading firms only. Manufacturing firms use raw materials."
    }
  ]
}
```

### Fields Explained

- **id:** Unique rule ID (1-384)
- **source_terms:** Array of possible names this item might appear as in source documents. Include common variants, abbreviations, Tally-specific names.
- **target_row:** The row number in the CMA Excel template where this maps to
- **target_sheet:** Which CMA sheet it belongs to
- **target_label:** The official label in the CMA template for this row
- **entity_types:** Which business types this rule applies to (array — may be all three)
- **document_types:** Whether this comes from P&L, Balance Sheet, or either
- **priority:** 1 = most specific match, 2 = broader match, 3 = fallback
- **match_type:** "exact" (must match term exactly), "exact_or_fuzzy" (allows partial matching), "pattern" (regex-based)
- **notes:** Human-readable explanation for debugging

### Conversion Script

Create: `backend/scripts/convert_rules.py`

A Python script that:
1. Opens `reference/CMA_classification.xls` with openpyxl
2. Reads each row from the classification table
3. Expands source terms (one rule may have multiple variants — split by comma or semicolon)
4. Outputs `classification_rules.json`
5. Prints summary: total rules, rules per entity type, rules per sheet

This script is run once during setup and can be re-run if rules are updated.

### Also Create

File: `backend/app/services/classification/rules_loader.py`

A module that:
- Loads `classification_rules.json` once at startup (cached in memory)
- Exports: `get_all_rules() → list[Rule]`
- Exports: `get_rules_count() → int`
- Uses a Pydantic model `ClassificationRule` for type safety

---

## What NOT to Do

- Don't hardcode rules in Python code — they must be in JSON for easy updates
- Don't modify the original Excel file
- Don't add AI logic yet — this is pure data conversion
- Don't create matching/scoring logic (that's task 5.2 and 5.5)

---

## Verification

- [ ] `classification_rules.json` has exactly 384 rules (or close — count from source)
- [ ] Every rule has all required fields (id, source_terms, target_row, target_sheet, etc.)
- [ ] `source_terms` arrays have multiple variants where appropriate
- [ ] `entity_types` correctly filters: "Purchases" → trading only, "Raw Materials" → manufacturing only
- [ ] `rules_loader.py` loads the JSON and returns typed Rule objects
- [ ] `get_all_rules()` returns full list
- [ ] Running `convert_rules.py` twice produces identical output

---

## Done → Move to task-5.2-rule-filter.md
