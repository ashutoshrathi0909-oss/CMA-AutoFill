import io
import json
import pytest
import openpyxl
from app.services.extraction.excel_parser import parse_excel
from app.services.extraction.pdf_parser import parse_pdf, is_digital_pdf
from reportlab.pdfgen import canvas

def create_dummy_excel():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Profit & Loss"
    ws.append(["Mehta Computers"])
    ws.append(["Profit and Loss Account"])
    ws.append(["For the year 2024-25"])
    ws.append([])
    ws.append(["Sales", "15,00,000.00"])
    ws.append(["Purchases", "9,00,000.00"])
    
    # Save to bytes
    f = io.BytesIO()
    wb.save(f)
    return f.getvalue()

def create_dummy_pdf():
    f = io.BytesIO()
    c = canvas.Canvas(f)
    c.drawString(100, 800, "Mehta Computers")
    c.drawString(100, 780, "Profit and Loss Account")
    c.drawString(100, 760, "Sales 1500000.00")
    c.drawString(100, 740, "Purchases 900000.00")
    c.save()
    return f.getvalue()

def test_excel_parser():
    file_bytes = create_dummy_excel()
    result = parse_excel(file_bytes, "mehta_pl.xlsx")
    
    assert result["document_type"] == "profit_and_loss"
    assert "Sales" in [item["name"] for item in result["line_items"]]
    sales_item = next(item for item in result["line_items"] if item["name"] == "Sales")
    assert sales_item["amount"] == 1500000.0
    
def test_pdf_parser():
    file_bytes = create_dummy_pdf()
    assert is_digital_pdf(file_bytes) == True
    
    result = parse_pdf(file_bytes, "mehta_pl.pdf")
    assert result["document_type"] == "profit_and_loss"
    
def test_standardized_format():
    file_bytes = create_dummy_excel()
    result = parse_excel(file_bytes, "mehta_pl.xlsx")
    
    assert "document_type" in result
    assert "line_items" in result
    assert "totals" in result
    assert "metadata" in result
    
    first_item = result["line_items"][0]
    for key in ["name", "amount", "parent_group", "level", "is_total", "raw_text"]:
        assert key in first_item
    assert isinstance(first_item["amount"], float)

def test_merger():
    extracted_data_1 = {
        "document_type": "profit_and_loss",
        "line_items": [{"name": "Sales", "amount": 1000}],
        "totals": {}
    }
    extracted_data_2 = {
        "document_type": "balance_sheet",
        "line_items": [{"name": "Assets", "amount": 2000}],
        "totals": {}
    }
    
    from app.services.extraction.merger import merge_and_save_data
    assert callable(merge_and_save_data)
