# Task 4.2: Excel Parser (Tally/Busy Exports)

> **Phase:** 04 - Document Extraction
> **Depends on:** Task 4.1 (Gemini client exists, but not used in this task)
> **Agent reads:** cma-domain SKILL → Source Document Types, Common Indian Financial Terms
> **Reference files:** `reference/sample_documents/` (Mehta Computers Excel files)
> **Time estimate:** 20 minutes

---

## Objective

Create a parser that reads Excel files exported from Indian accounting software (Tally, Busy, Zoho Books) and extracts financial line items into a standardized JSON format. This is the most common input format — no AI needed, just openpyxl parsing.

---

## What to Do

### Create File
`backend/app/services/extraction/excel_parser.py`

### Input
An Excel file (.xlsx or .xls) that contains a P&L statement, Balance Sheet, or Trial Balance. These files come in many formats — the parser needs to handle variation.

### Output Format (Standardized)

Every parser (Excel, PDF, Vision) must output the same format:

```json
{
  "document_type": "profit_and_loss",
  "financial_year": "2024-25",
  "entity_name": "Mehta Computers",
  "currency": "INR",
  "line_items": [
    {
      "name": "Sales",
      "amount": 1500000.00,
      "parent_group": "Revenue from Operations",
      "level": 1,
      "is_total": false,
      "raw_text": "Sales A/c"
    },
    {
      "name": "Purchases",
      "amount": 900000.00,
      "parent_group": "Cost of Goods Sold",
      "level": 1,
      "is_total": false,
      "raw_text": "Purchases A/c"
    }
  ],
  "totals": {
    "gross_total": 1500000.00,
    "net_total": 250000.00
  },
  "metadata": {
    "source_file": "mehta_pl_2024.xlsx",
    "sheet_name": "Profit & Loss",
    "row_count": 45,
    "parser": "excel_parser"
  }
}
```

### Parsing Logic

1. **Open workbook** with openpyxl (read_only mode for large files)
2. **Detect document type:** Look for keywords in sheet names or headers:
   - "Profit" or "P&L" or "Income" → profit_and_loss
   - "Balance" or "BS" → balance_sheet
   - "Trial" or "TB" → trial_balance
3. **Find the data start:** Skip title rows, company name, date headers. Look for the first row with a text + number pattern.
4. **Extract line items:**
   - Column A (or first text column): item name
   - Column B/C (or first number column): amount
   - Detect indentation/grouping:
     - Items with bold/larger font or that sum sub-items → mark as group headers
     - Items with "Total" in name → mark `is_total: true`
   - Track parent_group by watching indentation level changes
5. **Handle Tally-specific quirks:**
   - Tally exports often have amounts in two columns (Debit/Credit)
   - Tally uses "Cr" and "Dr" suffixes
   - Numbers may be in Indian format (12,34,567.89)
   - Negative amounts shown in brackets: (50,000)
6. **Extract entity name** from header rows
7. **Extract financial year** from header or filename

### Edge Cases to Handle

- Multiple sheets in one file → parse each relevant sheet separately
- Empty rows between sections → skip them
- Merged cells → read the first cell of the merged range
- Numbers stored as text → convert to float
- Indian number formatting → parse correctly (lakhs, crores separators)

---

## What NOT to Do

- Don't use AI/Gemini for Excel parsing — openpyxl is sufficient and free
- Don't try to classify items into CMA rows (that's Phase 05)
- Don't handle scanned/image PDFs (that's task 4.4)
- Don't modify the source file

---

## Verification

- [ ] Parse the Mehta Computers P&L Excel → line_items array has all items with correct names and amounts
- [ ] Parse the Mehta Computers Balance Sheet Excel → same
- [ ] `document_type` is correctly detected
- [ ] Indian number formatting handled (12,34,567 = 1234567)
- [ ] Tally "Cr"/"Dr" suffixes handled
- [ ] Bracketed negatives handled: (50,000) = -50000
- [ ] `is_total` correctly identifies total/subtotal rows
- [ ] Empty/malformed file → returns clear error, not crash
- [ ] Output matches the standardized JSON format exactly

---

## Done → Move to task-4.3-pdf-parser.md
