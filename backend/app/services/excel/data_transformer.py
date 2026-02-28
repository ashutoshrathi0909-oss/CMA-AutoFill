from typing import List, Dict, Any
import logging

COMPUTED_ROWS = {
    ("operating_statement", 12): {"formula": "row_5 - row_10", "label": "Gross Profit"},
    ("operating_statement", 25): {"formula": "sum(row_13:row_24)", "label": "Total Operating Expenses"},
    ("balance_sheet", 15): {"formula": "sum(row_3:row_14)", "label": "Total Fixed Assets"}
}

def transform_for_writer(classified_items: List[Dict[str, Any]], entity_type: str) -> Dict[str, Dict[int, float]]:
    logger = logging.getLogger("cma.transformer")
    
    transformed_data = {}
    
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
            
    # Calculate computed rows dynamically
    op_sheet = transformed_data.get("operating_statement", {})
    r5 = op_sheet.get(5, 0.0)
    r10 = op_sheet.get(10, 0.0)
    op_sheet[12] = r5 - r10
    
    transformed_data["operating_statement"] = op_sheet
    
    return transformed_data
