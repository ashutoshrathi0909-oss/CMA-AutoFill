import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# Computed rows that are derived from other rows
COMPUTED_ROWS = {
    ("operating_statement", 12): {"operands": [5, 10], "op": "subtract", "label": "Gross Profit"},
    ("operating_statement", 25): {"operands": list(range(13, 25)), "op": "sum", "label": "Total Operating Expenses"},
    ("balance_sheet", 15): {"operands": list(range(3, 15)), "op": "sum", "label": "Total Fixed Assets"},
}


def transform_for_writer(classified_items: List[Dict[str, Any]], entity_type: str) -> Dict[str, Dict[int, float]]:
    """Transform classified items into {sheet_name: {row_number: amount}} for CMAWriter."""
    transformed_data: Dict[str, Dict[int, float]] = {}

    # 1. Group classified items by target_sheet and row
    for item in classified_items:
        sheet = item.get("target_sheet")
        row = item.get("target_row")
        val = item.get("item_amount", 0.0)

        if not sheet or not row:
            continue

        if sheet not in transformed_data:
            transformed_data[sheet] = {}

        # Sum items mapping to same row
        if row in transformed_data[sheet]:
            transformed_data[sheet][row] += float(val)
        else:
            transformed_data[sheet][row] = float(val)

    # 2. Calculate computed rows
    for (sheet, row), config in COMPUTED_ROWS.items():
        if sheet not in transformed_data:
            continue

        sheet_data = transformed_data[sheet]
        operands = config["operands"]
        op = config["op"]

        if op == "subtract" and len(operands) == 2:
            val = sheet_data.get(operands[0], 0.0) - sheet_data.get(operands[1], 0.0)
            sheet_data[row] = val
        elif op == "sum":
            val = sum(sheet_data.get(r, 0.0) for r in operands)
            if val != 0.0:
                sheet_data[row] = val

    return transformed_data
