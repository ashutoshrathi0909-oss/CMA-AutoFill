import io
import re
from typing import Dict, Any
import pdfplumber

from app.services.extraction.utils import clean_indian_number, detect_document_type, extract_financial_year


def is_digital_pdf(file_bytes: bytes) -> bool:
    """Check if a PDF has extractable text (not scanned image)."""
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            # Check first few pages — a cover page may be an image
            for page in pdf.pages[:3]:
                text = page.extract_text()
                if text and len(text.strip()) > 50:
                    return True
    except Exception:
        pass
    return False


def parse_pdf(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    line_items: list[dict] = []

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

                    first_text = next((c for c in cells if c and not re.match(r'^[\d,.\-()]+$', c)), "")
                    amounts = [clean_indian_number(c) for c in cells if re.search(r'\d', c)]

                    if first_text and amounts:
                        amt = amounts[-1] if amounts else 0.0
                        line_items.append({
                            "name": first_text,
                            "amount": amt,
                            "parent_group": "Root",
                            "level": 1,
                            "is_total": "total" in first_text.lower(),
                            "raw_text": first_text,
                        })

        doc_type = detect_document_type(all_text)
        financial_year = extract_financial_year(all_text)

    return {
        "document_type": doc_type,
        "financial_year": financial_year,
        "entity_name": entity_name,
        "currency": "INR",
        "line_items": line_items,
        "totals": {
            "gross_total": 0.0,
            "net_total": 0.0,
        },
        "metadata": {
            "source_file": filename,
            "row_count": len(line_items),
            "parser": "pdf_parser",
        },
    }
