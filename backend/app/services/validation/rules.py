from typing import List, Dict, Any
from pydantic import BaseModel

class ValidationRule(BaseModel):
    id: str
    name: str
    category: str
    severity: str
    description: str
    check_function: str
    applies_to: List[str]
    auto_fixable: bool

VALIDATION_RULES = [
    ValidationRule(
        id="bs_balance",
        name="Balance Sheet Balance",
        category="balance_sheet",
        severity="error",
        description="Total Assets must equal Total Liabilities + Equity",
        check_function="check_bs_balance",
        applies_to=["trading", "manufacturing", "service"],
        auto_fixable=True
    ),
    ValidationRule(
        id="pl_gross_profit",
        name="Gross Profit Cross-Check",
        category="pl_crosscheck",
        severity="error",
        description="Gross Profit must equal Net Sales minus Cost of Goods Sold",
        check_function="check_pl_gross_profit",
        applies_to=["trading", "manufacturing", "service"],
        auto_fixable=True
    ),
    ValidationRule(
        id="mandatory_sales",
        name="Mandatory Sales Row",
        category="completeness",
        severity="error",
        description="Sales row must exist.",
        check_function="check_mandatory_sales",
        applies_to=["trading", "manufacturing", "service"],
        auto_fixable=False
    ),
    ValidationRule(
        id="current_ratio",
        name="Current Ratio Sanity Check",
        category="ratio_sanity",
        severity="warning",
        description="Current Ratio is typically 1.0 to 3.0",
        check_function="check_current_ratio",
        applies_to=["trading", "manufacturing", "service"],
        auto_fixable=False
    ),
    ValidationRule(
        id="data_type_check",
        name="Data Types are Numeric",
        category="data_type",
        severity="error",
        description="Amounts must be non-null and numeric.",
        check_function="check_data_types",
        applies_to=["trading", "manufacturing", "service"],
        auto_fixable=False
    )
]

def get_validation_rules(entity_type: str) -> List[ValidationRule]:
    return [r for r in VALIDATION_RULES if entity_type in r.applies_to]
