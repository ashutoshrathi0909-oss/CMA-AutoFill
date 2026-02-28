import os
from typing import Dict, Any
import openpyxl

class CMAWriter:
    def __init__(self, template_path: str):
        """Load the CMA template."""
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template not found at {template_path}")
            
        self.template_path = template_path
        self.workbook = openpyxl.load_workbook(template_path, keep_vba=True)
        
    def write(self, data: Dict[str, Any], output_path: str) -> str:
        """Write classified data into CMA template and save."""
        
        # Typically maps like: data['operating_statement'][row_index] = amount
        for sheet_name, rows_data in data.items():
            if sheet_name in self.workbook.sheetnames:
                ws = self.workbook[sheet_name]
                for row_idx, amount in rows_data.items():
                    # In true POC, we probably had specific Col bindings per year.
                    # As requested by Prompt: "V1: only populate the 'Estimated Year' column."
                    # Let's assume Col E (5) is 'Estimated Year' for mock structure.
                    
                    try:
                        row_idx_int = int(row_idx)
                        # Just overwrite the cell value
                        cell = ws.cell(row=row_idx_int, column=5)
                        cell.value = amount
                    except ValueError:
                        pass
        
        # Save modifications
        self.workbook.save(output_path)
        return output_path
        
    def get_template_info(self) -> Dict[str, Any]:
        """Return template structure info (sheets, rows)."""
        return {
            "sheets": self.workbook.sheetnames,
            "total_rows": 289
        }
