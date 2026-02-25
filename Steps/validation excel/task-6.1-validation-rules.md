# Task 6.1: Define Validation Rules

> **Phase:** 06 - Validation & Excel Generation
> **Depends on:** Phase 05 complete (classification data available)
> **Agent reads:** cma-domain SKILL → Validation Rules, CMA Template Structure
> **Time estimate:** 15 minutes

---

## Objective

Define all the mathematical and logical validation rules that a CMA document must satisfy. These are the checks a senior CA would mentally run before submitting a CMA to a bank.

---

## What to Do

### Create File
`backend/app/services/validation/rules.py`

### Validation Rule Categories

**Category 1: Balance Sheet Balancing**
- Total Assets MUST equal Total Liabilities + Equity
- If difference > ₹1 → FAIL (hard error)
- If difference = 0 → PASS

**Category 2: P&L Cross-Checks**
- Gross Profit = Net Sales - Cost of Goods Sold
- Net Profit = Gross Profit - Operating Expenses - Non-Operating Expenses + Non-Operating Income
- Depreciation in P&L must equal Depreciation in CMA schedule

**Category 3: Operating Statement Checks**
- Total of all expense lines must equal reported Total Expenses
- Revenue - Expenses = Profit (as shown)
- Manufacturing cost items should only appear for manufacturing entities

**Category 4: CMA Internal Consistency**
- Values in Operating Statement summary rows must match detailed rows
- Balance Sheet current year must match Operating Statement current year
- Previous year values should be present (warning if missing, not error)

**Category 5: Ratio Sanity Checks (warnings, not errors)**
- Current Ratio typically 1.0-3.0 → warn if outside
- Debt-to-Equity typically 0.5-4.0 → warn if outside
- Net Profit Margin typically -10% to 30% → warn if outside
- These are soft checks — unusual values flagged but not blocked

**Category 6: Completeness Checks**
- All mandatory CMA rows must have a value (even if 0)
- At minimum: Sales, Cost of Goods, Gross Profit, Net Profit, Total Assets, Total Liabilities
- Missing mandatory items → FAIL

**Category 7: Data Type Checks**
- All amounts must be numbers (not strings, not null for mandatory fields)
- No negative values where positives expected (e.g., Sales should be positive)
- Amounts within reasonable range (flag if any single item > ₹100 crore — probably an error)

### Rule Definition Format

```python
class ValidationRule:
    id: str                    # "bs_balance", "pl_gross_profit", etc.
    name: str                  # Human-readable name
    category: str              # "balance_sheet", "pl_crosscheck", "completeness", etc.
    severity: str              # "error" (blocks generation) or "warning" (flagged but allowed)
    description: str           # What this rule checks
    check_function: str        # Name of the function that performs this check
    applies_to: list[str]      # Entity types this applies to
    auto_fixable: bool         # Can the system suggest a fix?
```

### Create Rules Registry

`VALIDATION_RULES: list[ValidationRule]` — all ~20-25 rules defined as a list.

Export: `get_validation_rules(entity_type: str) → list[ValidationRule]`

---

## What NOT to Do

- Don't implement the validation logic yet (that's task 6.2)
- Don't implement auto-fix logic yet (task 6.2)
- Don't create API endpoints (task 6.6)
- Don't validate against bank-specific requirements (too complex for V1)

---

## Verification

- [ ] ~20-25 validation rules defined
- [ ] Each rule has all required fields (id, name, severity, etc.)
- [ ] Severity split: ~10 errors (hard), ~15 warnings (soft)
- [ ] Rules filtered by entity type work correctly
- [ ] Manufacturing-specific rules excluded for trading entities
- [ ] All rules have clear, human-readable descriptions

---

## Done → Move to task-6.2-validation-service.md
