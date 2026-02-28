import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from app.services.validation.rules import get_validation_rules

logger = logging.getLogger(__name__)


class ValidationCheck(BaseModel):
    rule_id: str
    rule_name: str
    severity: str
    passed: bool
    message: str
    expected_value: Optional[float] = None
    actual_value: Optional[float] = None
    difference: Optional[float] = None
    auto_fix: Optional[Dict[str, Any]] = None


class ValidationResult(BaseModel):
    project_id: str
    passed: bool
    total_checks: int
    errors: int
    warnings: int
    checks: List[ValidationCheck]
    can_generate: bool
    summary: str


def get_item_amount(classification_data: Dict[str, Any], row: int, sheet: str) -> float:
    val = 0.0
    items = classification_data.get("items", [])
    for itm in items:
        if itm.get("target_row") == row and itm.get("target_sheet") == sheet:
            val += float(itm.get("item_amount", 0.0))
    return val


def format_inr(amount: float) -> str:
    """Format a number in Indian rupee style (e.g., 15,00,000)."""
    is_negative = amount < 0
    num = abs(int(amount))
    s = str(num)

    if len(s) <= 3:
        formatted = s
    else:
        # Last 3 digits
        last3 = s[-3:]
        remaining = s[:-3]
        # Group remaining in pairs from the right
        groups = []
        while len(remaining) > 2:
            groups.append(remaining[-2:])
            remaining = remaining[:-2]
        if remaining:
            groups.append(remaining)
        groups.reverse()
        formatted = ",".join(groups) + "," + last3

    prefix = "-" if is_negative else ""
    return f"{prefix}₹{formatted}"


def check_bs_balance(data: Dict[str, Any]) -> ValidationCheck:
    total_assets = get_item_amount(data, 82, "balance_sheet")
    total_liabilities = get_item_amount(data, 49, "balance_sheet")

    diff = abs(total_assets - total_liabilities)
    passed = diff <= 1

    return ValidationCheck(
        rule_id="bs_balance",
        rule_name="Balance Sheet Balance",
        severity="error",
        passed=passed,
        message=(
            f"Total Assets ({format_inr(total_assets)}) == Total Liabilities ({format_inr(total_liabilities)})"
            if passed
            else f"MISMATCH: Assets {format_inr(total_assets)} != Liabilities {format_inr(total_liabilities)}"
        ),
        expected_value=total_assets,
        actual_value=total_liabilities,
        difference=diff,
        auto_fix=None if passed else {
            "action": "adjust_value",
            "target_row": 49,
            "target_sheet": "balance_sheet",
            "current_value": total_liabilities,
            "suggested_value": total_assets,
            "reason": "Adjust Total Liabilities to match Total Assets",
        },
    )


def check_pl_gross_profit(data: Dict[str, Any]) -> ValidationCheck:
    sales = get_item_amount(data, 5, "operating_statement")
    cogs = get_item_amount(data, 10, "operating_statement")
    reported_gp = get_item_amount(data, 12, "operating_statement")

    calc_gp = sales - cogs
    diff = abs(reported_gp - calc_gp)
    passed = diff <= 1

    return ValidationCheck(
        rule_id="pl_gross_profit",
        rule_name="Gross Profit Cross-Check",
        severity="error",
        passed=passed,
        message=(
            "GP matches Sales - COGS"
            if passed
            else f"GP MISMATCH: Sales - COGS = {format_inr(calc_gp)}, reported = {format_inr(reported_gp)}"
        ),
        expected_value=calc_gp,
        actual_value=reported_gp,
        difference=diff,
        auto_fix=None if passed else {
            "action": "adjust_value",
            "target_row": 12,
            "target_sheet": "operating_statement",
            "current_value": reported_gp,
            "suggested_value": calc_gp,
            "reason": "Update GP to Sales - COGS",
        },
    )


def check_mandatory_sales(data: Dict[str, Any]) -> ValidationCheck:
    sales = get_item_amount(data, 5, "operating_statement")
    passed = sales > 0
    return ValidationCheck(
        rule_id="mandatory_sales",
        rule_name="Mandatory Sales Row",
        severity="error",
        passed=passed,
        message="Sales exist" if passed else "Sales amount is missing or <= 0",
        actual_value=sales,
    )


def check_current_ratio(data: Dict[str, Any]) -> ValidationCheck:
    current_assets = get_item_amount(data, 75, "balance_sheet")
    current_liabs = get_item_amount(data, 30, "balance_sheet")

    ratio = current_assets / current_liabs if current_liabs > 0 else 0
    passed = 1.0 <= ratio <= 3.0

    return ValidationCheck(
        rule_id="current_ratio",
        rule_name="Current Ratio Sanity Check",
        severity="warning",
        passed=passed,
        message=f"Current Ratio is {ratio:.2f}" if passed else f"Unusual Current Ratio: {ratio:.2f}",
        expected_value=1.5,
        actual_value=ratio,
        difference=abs(ratio - 1.5) if current_liabs > 0 else None,
    )


def check_data_types(data: Dict[str, Any]) -> ValidationCheck:
    """Verify all mapped item amounts are numeric."""
    items = data.get("items", [])
    non_numeric = []
    for itm in items:
        amt = itm.get("item_amount")
        if amt is not None:
            try:
                float(amt)
            except (ValueError, TypeError):
                non_numeric.append(itm.get("item_name", "unknown"))

    passed = len(non_numeric) == 0
    return ValidationCheck(
        rule_id="data_type_check",
        rule_name="Data Types are Numeric",
        severity="error",
        passed=passed,
        message=(
            "All mapped data is numeric"
            if passed
            else f"Non-numeric amounts found in: {', '.join(non_numeric[:5])}"
        ),
    )


def validate_project(project_id: str, classification_data: Dict[str, Any], entity_type: str) -> ValidationResult:
    rules = get_validation_rules(entity_type)

    checks: List[ValidationCheck] = []

    func_map = {
        "check_bs_balance": check_bs_balance,
        "check_pl_gross_profit": check_pl_gross_profit,
        "check_mandatory_sales": check_mandatory_sales,
        "check_current_ratio": check_current_ratio,
        "check_data_types": check_data_types,
    }

    errors = 0
    warnings = 0

    for r in rules:
        if r.check_function in func_map:
            res = func_map[r.check_function](classification_data)
            checks.append(res)

            if not res.passed:
                if res.severity == "error":
                    errors += 1
                else:
                    warnings += 1

    passed = errors == 0

    summary = (
        f"{errors} error(s) must be fixed before generating CMA. {warnings} warning(s) found."
        if not passed
        else "All validations passed."
    )

    return ValidationResult(
        project_id=project_id,
        passed=passed,
        total_checks=len(checks),
        errors=errors,
        warnings=warnings,
        checks=checks,
        can_generate=passed,
        summary=summary,
    )
