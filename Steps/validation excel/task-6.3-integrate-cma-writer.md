# Task 6.3: Integrate cma_writer.py as Backend Service

> **Phase:** 06 - Validation & Excel Generation
> **Depends on:** Phase 03 (backend structure), reference/cma_writer.py exists
> **Agent reads:** CLAUDE.md → Reference Files, reference/cma_writer.py source code
> **Time estimate:** 15 minutes

---

## Objective

Adapt the proven `cma_writer.py` from the POC (100% accuracy, 65/65 values match) into a proper backend service module. The writer takes structured data and fills in the CMA Excel template.

---

## What to Do

### Step 1: Copy and Adapt

Source: `reference/cma_writer.py` (POC script)
Target: `backend/app/services/excel/cma_writer.py` (backend service)

The POC script works as a standalone Python script. Adapt it to:
- Be importable as a module (no `if __name__ == "__main__"` execution)
- Accept input data as a Python dict (not read from a file)
- Accept the template path as a parameter (not hardcoded)
- Return the output file path (not print messages)
- Use proper error handling (raise exceptions, not print + exit)
- Add type hints to all functions

### Step 2: Preserve the Working Logic

**CRITICAL:** The cma_writer.py has been verified at 100% accuracy. Do NOT rewrite the core writing logic. Only refactor the interface:

Keep exactly:
- Cell mapping logic (which data goes to which Excel cell)
- Sheet handling logic (15 sheets)
- Formula preservation
- Formatting preservation

Change only:
- Input method: dict parameter instead of file read
- Output method: return path instead of print
- Error handling: exceptions instead of print + exit
- Add logging

### Step 3: Create Writer Interface

```python
class CMAWriter:
    def __init__(self, template_path: str):
        """Load the CMA template."""
        self.template_path = template_path
        self.workbook = load_workbook(template_path)
    
    def write(self, data: dict, output_path: str) -> str:
        """Write classified data into CMA template and save."""
        # ... existing logic adapted ...
        return output_path
    
    def get_template_info(self) -> dict:
        """Return template structure info (sheets, rows)."""
        return {"sheets": [...], "total_rows": 289}
```

### Step 4: Template File Management

- Store `reference/CMA.xlsm` (the blank template) in a known location
- On app startup, verify the template exists
- The writer opens a COPY of the template each time (never modifies original)

### Step 5: Add to Requirements

Ensure `openpyxl` is in `backend/requirements.txt` (should already be there from Phase 04).

---

## What NOT to Do

- **Don't rewrite the cell mapping logic** — it's been verified at 100% accuracy
- Don't change the template file format
- Don't add new features to the writer yet
- Don't remove any existing functionality
- Don't change how formulas are handled in the template

---

## Verification

- [ ] `from app.services.excel.cma_writer import CMAWriter` → imports without error
- [ ] `CMAWriter(template_path)` → loads template successfully
- [ ] `writer.write(test_data, output_path)` → creates Excel file
- [ ] Output Excel has all 15 sheets present
- [ ] Existing formulas in template are preserved
- [ ] Formatting (fonts, colors, borders) preserved
- [ ] Known test data produces same output as POC (compare cell-by-cell)

---

## Done → Move to task-6.4-data-transformer.md
