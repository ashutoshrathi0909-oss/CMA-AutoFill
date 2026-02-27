import io
import re
from typing import Dict, Any, List
import pdfplumber

def is_digital_pdf(file_bytes: bytes) -> bool:
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            if len(pdf.pages) > 0:
                text = pdf.pages[0].extract_text()
                return len(text.strip()) > 50 if text else False
    except Exception:
        pass
    return False
    
def clean_indian_number(text: str) -> float:
    if not text:
        return 0.0
    text = str(text).strip()
    is_negative = False
    if text.endswith("Cr") or text.endswith("Cr."):
        text = text.replace("Cr.", "").replace("Cr", "").strip()
    elif text.endswith("Dr") or text.endswith("Dr."):
        text = text.replace("Dr.", "").replace("Dr", "").strip()
        
    if text.startswith("(") and text.endswith(")"):
        is_negative = True
        text = text[1:-1].strip()
        
    text = text.replace(",", "")
    try:
        val = float(text)
        return -val if is_negative else val
    except ValueError:
        return 0.0

def parse_pdf(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    line_items = []
    
    doc_type = "other"
    entity_name = "Unknown"
    financial_year = "Unknown"
    
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        all_text = ""
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                all_text += text + "\n"
                
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    cells = [str(c).strip() if c else "" for c in row]
                    if not any(cells):
                         continue
                         
                    first_text = next((c for c in cells if c), "")
                    amounts = [clean_indian_number(c) for c in cells if re.search(r'\d', c)]
                    
                    if first_text and amounts:
                        amt = amounts[-1] if amounts else 0.0
                        line_items.append({
                            "name": first_text,
                            "amount": amt,
                            "parent_group": "Root",
                            "level": 1,
                            "is_total": "total" in first_text.lower(),
                            "raw_text": first_text
                        })
                        
        ll = all_text.lower()
        if "profit" in ll or "p&l" in ll or "income" in ll:
            doc_type = "profit_and_loss"
        elif "balance" in ll or "bs" in ll:
            doc_type = "balance_sheet"
        elif "trial" in ll or "tb" in ll:
            doc_type = "trial_balance"
            
    return {
        "document_type": doc_type,
        "financial_year": financial_year,
        "entity_name": entity_name,
        "currency": "INR",
        "line_items": line_items,
        "totals": {
            "gross_total": 0.0,
            "net_total": 0.0
        },
        "metadata": {
            "source_file": filename,
            "row_count": len(line_items),
            "parser": "pdf_parser"
        }
    }
