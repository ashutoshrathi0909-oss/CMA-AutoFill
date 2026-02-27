import csv
import io
import re
from typing import Dict, Any
import openpyxl

from app.services.extraction.utils import clean_indian_number, detect_document_type, extract_financial_year


def _parse_sheet(rows: list[list[str]], sheet_name: str) -> Dict[str, Any]:
    """Parse a single sheet/table of rows into the standard extraction format."""
    header_rows: list[str] = []
    line_items: list[dict] = []

    entity_name = "Unknown"
    financial_year = "Unknown"
    current_parent = None
    data_started = False
    gross_total = 0.0
    net_total = 0.0

    for row_idx, cells in enumerate(rows):
        if not any(cells):
            continue

        first_text_col = next((i for i, c in enumerate(cells) if c), -1)
        if first_text_col == -1:
            continue

        first_text = cells[first_text_col]

        has_number = any(re.search(r'\d+', c) for c in cells[first_text_col + 1:]) and len(first_text) > 3

        if not data_started and not has_number:
            header_rows.append(first_text)
            if row_idx == 0:
                entity_name = first_text
            continue

        if has_number or data_started:
            data_started = True

            name = first_text
            is_total = "total" in name.lower()

            amount = 0.0
            for c in cells[first_text_col + 1:]:
                if re.search(r'\d+', c):
                    amount = clean_indian_number(c)
                    break

            level = first_text_col + 1
            if name.startswith("  "):
                level += 1

            item = {
                "name": name.strip(),
                "amount": amount,
                "parent_group": current_parent if current_parent else "Root",
                "level": level,
                "is_total": is_total,
                "raw_text": name.strip(),
            }
            line_items.append(item)

            if is_total:
                if "gross" in name.lower():
                    gross_total = amount
                elif "net" in name.lower():
                    net_total = amount
            elif amount == 0 and not is_total:
                current_parent = name.strip()

    combined_text = sheet_name + " " + " ".join(header_rows)
    doc_type = detect_document_type(combined_text)

    for h in header_rows:
        fy = extract_financial_year(h)
        if fy != "Unknown":
            financial_year = fy
            break

    return {
        "document_type": doc_type,
        "financial_year": financial_year,
        "entity_name": entity_name,
        "currency": "INR",
        "line_items": line_items,
        "totals": {
            "gross_total": gross_total,
            "net_total": net_total,
        },
        "metadata": {
            "source_file": "",
            "sheet_name": sheet_name,
            "row_count": len(line_items),
            "parser": "excel_parser",
        },
    }


def parse_excel(file_bytes: bytes, filename: str, is_csv: bool = False) -> Dict[str, Any]:
    """Parse an Excel or CSV file into the standard extraction format.

    For multi-sheet workbooks, parses all sheets and returns the one with
    the most line items (typically the most data-rich financial statement).
    """
    if is_csv:
        return _parse_csv(file_bytes, filename)

    wb = openpyxl.load_workbook(filename=io.BytesIO(file_bytes), read_only=True, data_only=True)

    best_result: Dict[str, Any] | None = None
    all_results: list[Dict[str, Any]] = []

    for sheet in wb.worksheets:
        rows: list[list[str]] = []
        for row in sheet.iter_rows(values_only=True, max_col=10):
            cells = [str(c).strip() if c is not None else "" for c in row]
            rows.append(cells)

        result = _parse_sheet(rows, sheet.title)
        result["metadata"]["source_file"] = filename
        all_results.append(result)

        if best_result is None or len(result["line_items"]) > len(best_result["line_items"]):
            best_result = result

    wb.close()

    if not best_result:
        return {
            "document_type": "other",
            "financial_year": "Unknown",
            "entity_name": "Unknown",
            "currency": "INR",
            "line_items": [],
            "totals": {"gross_total": 0.0, "net_total": 0.0},
            "metadata": {"source_file": filename, "sheet_name": "", "row_count": 0, "parser": "excel_parser"},
        }

    # If multiple sheets had data, note it in metadata
    sheets_with_data = [r for r in all_results if r["line_items"]]
    if len(sheets_with_data) > 1:
        best_result["metadata"]["additional_sheets"] = [
            {"sheet_name": r["metadata"]["sheet_name"], "document_type": r["document_type"], "row_count": len(r["line_items"])}
            for r in sheets_with_data if r is not best_result
        ]

    return best_result


def _parse_csv(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    """Parse a CSV file into the standard extraction format."""
    text = file_bytes.decode("utf-8", errors="replace")
    reader = csv.reader(io.StringIO(text))
    rows: list[list[str]] = []
    for row in reader:
        cells = [c.strip() for c in row]
        rows.append(cells)

    result = _parse_sheet(rows, "CSV")
    result["metadata"]["source_file"] = filename
    result["metadata"]["parser"] = "csv_parser"
    return result
