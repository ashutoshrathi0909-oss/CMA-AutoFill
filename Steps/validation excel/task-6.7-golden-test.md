# Task 6.7: End-to-End Golden Test (Mehta Computers)

> **Phase:** 06 - Validation & Excel Generation
> **Depends on:** All Phase 04, 05, 06 tasks complete
> **Agent reads:** CLAUDE.md → Reference Files, cma-domain SKILL
> **Reference files:** CMA_15092025.xls (the manually completed CMA), Mehta Computers source files
> **Time estimate:** 25 minutes

---

## Objective

Run the entire pipeline end-to-end on the Mehta Computers test data and compare the generated CMA against the reference CMA that your father manually prepared. This is the definitive test that proves the system works.

---

## What to Do

### Step 1: Create End-to-End Test

File: `backend/tests/test_e2e_golden.py`

### The Golden Test

```
Input: Mehta Computers source files (P&L + Balance Sheet)
Expected output: CMA_15092025.xls (manually prepared by father)

Pipeline:
1. Upload Mehta Computers files
2. Extract → get line items
3. Classify → map to CMA rows
4. Validate → check numbers
5. Generate → produce CMA Excel
6. COMPARE → generated vs reference cell-by-cell
```

### Step 2: Cell-by-Cell Comparison

Create: `backend/tests/utils/excel_comparator.py`

```python
def compare_cma_files(generated_path: str, reference_path: str) → ComparisonResult:
    """Compare two CMA Excel files cell by cell."""
```

**ComparisonResult:**
```python
class CellComparison:
    sheet: str
    row: int
    col: int
    reference_value: float | str
    generated_value: float | str
    match: bool
    difference: float | None    # for numeric cells
    
class ComparisonResult:
    total_cells_checked: int
    exact_matches: int
    close_matches: int          # within ₹1 (rounding)
    mismatches: int
    missing_in_generated: int   # reference has value, generated is empty
    extra_in_generated: int     # generated has value, reference is empty
    accuracy: float             # exact_matches / total_cells_checked
    details: list[CellComparison]  # only mismatches, for debugging
```

### Step 3: Comparison Logic

For each sheet in the CMA template:
1. For each data cell (skip headers, labels, formulas):
   - Get value from reference file
   - Get value from generated file
   - Compare:
     - Both numbers: match if abs(diff) <= 1 (₹1 rounding tolerance)
     - Both strings: match if equal (case-insensitive)
     - One empty, one not: mismatch
     - Both empty: skip (not a data cell)

### Step 4: Print Detailed Report

```
=== CMA AutoFill Golden Test: Mehta Computers ===

Pipeline Results:
  Extraction: 45 items from 2 files
  Classification: 73% auto-classified, 27% needs review
  Validation: PASSED (0 errors, 3 warnings)
  Generation: CMA_MehtaComputers_2024-25_v1.xlsx (240 KB)

Cell-by-Cell Comparison (vs CMA_15092025.xls):
  Total cells checked: 65
  Exact matches: 60 (92.3%)
  Close matches (±₹1): 2 (3.1%)
  Mismatches: 3 (4.6%)
  
  Mismatched cells:
  - Sheet: operating_statement, Row 15: reference=25000, generated=0 (item not classified)
  - Sheet: operating_statement, Row 22: reference=15000, generated=40000 (wrong classification)
  - Sheet: balance_sheet, Row 8: reference=180000, generated=175000 (extraction difference)

OVERALL ACCURACY: 95.4% (62/65 cells correct or close)
```

### Step 5: Define Success Criteria

| Metric | Target | POC Result |
|--------|--------|------------|
| Extraction accuracy | 100% (no missing items) | ~100% for Excel |
| Classification accuracy | >= 70% auto-classified | 73% |
| Validation pass rate | No hard errors | TBD |
| Cell-by-cell accuracy | >= 85% | TBD |

**The golden test PASSES if cell-by-cell accuracy >= 85%.**

### Step 6: Save Results as Baseline

Save the golden test results to a JSON file:
`backend/tests/fixtures/golden_test_baseline.json`

Future runs compare against this baseline to detect regressions.

### Step 7: Create Quick Regression Test

A faster version that:
- Uses pre-extracted data (skips file upload/extraction)
- Runs classification + validation + generation
- Compares output
- Runs in <30 seconds (vs full pipeline which may take minutes)

---

## What NOT to Do

- Don't adjust the reference file to match your output (that's cheating)
- Don't skip mismatched cells — document every failure
- Don't inflate accuracy by counting empty cells as "matches"
- Don't expect 100% on first run — this test reveals what needs improvement

---

## Verification

- [ ] Full pipeline runs without crashing on Mehta Computers data
- [ ] Extraction produces correct line items (compare vs task 4.7 fixture)
- [ ] Classification maps items to CMA rows (compare vs task 5.7 fixture)
- [ ] Validation passes (or only warnings)
- [ ] CMA Excel file generated successfully
- [ ] Cell-by-cell comparison runs and produces detailed report
- [ ] **Accuracy >= 85% (or documented path to 85%)**
- [ ] Golden test baseline saved as JSON
- [ ] Regression test runs in <30 seconds
- [ ] Mismatched cells documented for future improvement

---

## Phase 06 Complete! 🎉

All 7 tasks done. You now have:
- ✅ 20+ validation rules checking CMA math
- ✅ Validation engine with auto-fix suggestions
- ✅ cma_writer.py integrated as backend service
- ✅ Data transformer bridging classification → writer
- ✅ Excel generation pipeline (validate → transform → write → upload)
- ✅ API endpoints for validate/generate/apply-fixes
- ✅ End-to-end golden test with cell-by-cell comparison
- ✅ Accuracy baseline for regression tracking

**The core pipeline is now complete!**
Upload document → Extract → Classify → Validate → Generate CMA Excel

**Next → Phase 07: Ask Father (Review Queue UI + Learning Loop)**
