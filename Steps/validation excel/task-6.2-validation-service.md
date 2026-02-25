# Task 6.2: Validation Engine Service

> **Phase:** 06 - Validation & Excel Generation
> **Depends on:** Task 6.1 (validation rules defined)
> **Agent reads:** cma-domain SKILL → Validation Rules
> **Time estimate:** 20 minutes

---

## Objective

Implement the validation engine that runs all defined rules against classified data and returns a pass/fail report with auto-fix suggestions where possible.

---

## What to Do

### Create File
`backend/app/services/validation/validator.py`

### Main Function

`validate_project(project_id: UUID, classification_data: dict, entity_type: str) → ValidationResult`

### Validation Result

```python
class ValidationCheck:
    rule_id: str
    rule_name: str
    severity: str              # 'error' or 'warning'
    passed: bool
    message: str               # "Balance sheet balances: Assets ₹50L = Liabilities ₹50L" or "MISMATCH: Assets ₹50L ≠ Liabilities ₹48L"
    expected_value: float | None
    actual_value: float | None
    difference: float | None
    auto_fix: dict | None      # suggested correction if available

class ValidationResult:
    project_id: UUID
    passed: bool               # True only if ALL error-severity rules pass (warnings OK)
    total_checks: int
    errors: int                # hard failures
    warnings: int              # soft flags
    checks: list[ValidationCheck]
    can_generate: bool         # True if no errors (warnings don't block)
    summary: str               # "3 errors, 5 warnings. Fix errors before generating CMA."
```

### Implement Check Functions

For each rule from task 6.1, implement the actual check logic:

**Balance Sheet Balance:**
```python
def check_bs_balance(data):
    total_assets = sum of all asset items
    total_liabilities = sum of all liability + equity items
    diff = abs(total_assets - total_liabilities)
    passed = diff <= 1  # allow ₹1 rounding
    return ValidationCheck(...)
```

**P&L Gross Profit:**
```python
def check_pl_gross_profit(data):
    sales = get_item_amount(data, row=5, sheet="operating_statement")
    cogs = get_item_amount(data, row=10, sheet="operating_statement")
    reported_gp = get_item_amount(data, row=12, sheet="operating_statement")
    calculated_gp = sales - cogs
    passed = abs(reported_gp - calculated_gp) <= 1
    return ValidationCheck(...)
```

**Implement similar for all ~20-25 rules.**

### Auto-Fix Suggestions

For fixable errors, include an `auto_fix` dict:

```json
{
  "action": "adjust_value",
  "target_row": 12,
  "target_sheet": "operating_statement",
  "current_value": 600000,
  "suggested_value": 580000,
  "reason": "Gross Profit should be Sales (1500000) minus COGS (920000) = 580000"
}
```

The CA can accept or reject auto-fixes in Phase 07.

### Helper Functions

- `get_item_amount(classification_data, row, sheet) → float` — find a classified item by target row/sheet
- `sum_items(classification_data, rows, sheet) → float` — sum multiple rows
- `format_inr(amount) → str` — format as Indian currency (₹12,34,567)

---

## What NOT to Do

- Don't block warnings — only errors prevent CMA generation
- Don't auto-apply fixes (just suggest them — CA decides)
- Don't create the API endpoint (task 6.6)
- Don't validate things the bank might check but aren't mathematical (e.g., "is this a reasonable gross margin for this industry")

---

## Verification

- [ ] Valid Mehta Computers data → all checks pass
- [ ] Deliberately change one amount → balance sheet check fails with clear message
- [ ] Auto-fix suggestion shows the correct value
- [ ] `can_generate` is True when only warnings exist, False when errors exist
- [ ] Summary message is clear and actionable
- [ ] Format_inr works: 1234567 → "₹12,34,567"
- [ ] All 20-25 rules have working check functions

---

## Done → Move to task-6.3-integrate-cma-writer.md
