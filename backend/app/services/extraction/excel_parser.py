import io
import re
from typing import Dict, Any, List
import openpyxl

def clean_indian_number(text: str) -> float:
    if not text:
        return 0.0
    # Handle "Cr" / "Dr"
    text = str(text).strip()
    is_negative = False
    if text.endswith("Cr") or text.endswith("Cr."):
        text = text.replace("Cr.", "").replace("Cr", "").strip()
    elif text.endswith("Dr") or text.endswith("Dr."):
        text = text.replace("Dr.", "").replace("Dr", "").strip()
        
    if text.startswith("(") and text.endswith(")"):
        is_negative = True
        text = text[1:-1].strip()
        
    # Remove commas
    text = text.replace(",", "")
    try:
        val = float(text)
        return -val if is_negative else val
    except ValueError:
        return 0.0

def detect_document_type(sheet_name: str, header_rows: list[str]) -> str:
    combined_text = (sheet_name + " " + " ".join(header_rows)).lower()
    if "profit" in combined_text or "p&l" in combined_text or "income" in combined_text:
        return "profit_and_loss"
    elif "balance" in combined_text or "bs" in combined_text:
        return "balance_sheet"
    elif "trial" in combined_text or "tb" in combined_text:
        return "trial_balance"
    return "other"

def parse_excel(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    wb = openpyxl.load_workbook(filename=io.BytesIO(file_bytes), read_only=True, data_only=True)
    
    # We will pick the first relevant sheet or just the active one if small
    sheet = wb.active
    
    header_rows = []
    line_items = []
    
    # Heuristics for entity and year
    entity_name = "Unknown"
    financial_year = "Unknown"
    
    current_parent = None
    last_indent = 0
    
    data_started = False
    
    gross_total = 0.0
    net_total = 0.0
    
    for row_idx, row in enumerate(sheet.iter_rows(values_only=True, max_col=10)):
        # Identify non-empty cells
        cells = [str(c).strip() if c is not None else "" for c in row]
        if not any(cells):
            continue
            
        first_text_col = next((i for i, c in enumerate(cells) if c), -1)
        if first_text_col == -1:
            continue
            
        first_text = cells[first_text_col]
        
        # Heuristics for headers vs data
        has_number = any(re.search(r'\d+', c) for c in cells[first_text_col+1:]) and len(first_text) > 3
        
        if not data_started and not has_number:
            header_rows.append(first_text)
            # Try to grab entity name from first row
            if row_idx == 0:
                entity_name = first_text
            continue
            
        if has_number or data_started:
            data_started = True
            
            name = first_text
            is_total = "total" in name.lower()
            
            # Find the first valid number column
            amount = 0.0
            for c in cells[first_text_col+1:]:
                if re.search(r'\d+', c):
                    amount = clean_indian_number(c)
                    break
                    
            # Tally indent hint: sometimes it uses spaces, sometimes it relies on bold cols
            # For this simple parser, we'll pseudo route it
            level = first_text_col + 1
            if name.startswith("  "):
                level += 1
                
            item = {
                "name": name.strip(),
                "amount": amount,
                "parent_group": current_parent if current_parent else "Root",
                "level": level,
                "is_total": is_total,
                "raw_text": name.strip()
            }
            line_items.append(item)
            
            if is_total:
                if "gross" in name.lower():
                    gross_total = amount
                elif "net" in name.lower():
                    net_total = amount
                # A total might reset parent
            elif amount == 0 and not is_total:
                # Group header
                current_parent = name.strip()
    
    doc_type = detect_document_type(sheet.title, header_rows)
    
    # Try finding financial year
    for h in header_rows:
        match = re.search(r'20\d{2}-\d{2}', h)
        if match:
            financial_year = match.group(0)
            break
            
    return {
        "document_type": doc_type,
        "financial_year": financial_year,
        "entity_name": entity_name,
        "currency": "INR",
        "line_items": line_items,
        "totals": {
            "gross_total": gross_total,
            "net_total": net_total
        },
        "metadata": {
            "source_file": filename,
            "sheet_name": sheet.title,
            "row_count": len(line_items),
            "parser": "excel_parser"
        }
    }
