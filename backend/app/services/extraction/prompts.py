JSON_SCHEMA = """{
  "document_type": "profit_and_loss | balance_sheet | trial_balance | other",
  "financial_year": "2024-25",
  "entity_name": "Entity Name",
  "currency": "INR",
  "line_items": [
    {
      "name": "Line item name",
      "amount": 100000.00,
      "parent_group": "Group Name (e.g. Current Assets, Sales)",
      "level": 1,
      "is_total": false,
      "raw_text": "Original text"
    }
  ],
  "totals": {
    "gross_total": 0.0,
    "net_total": 0.0
  },
  "metadata": {
    "source_file": "filename",
    "parser": "vision_extractor"
  }
}"""

EXTRACTION_SYSTEM_PROMPT = """You are a specialist in reading Indian financial documents (P&L, Balance Sheet, Trial Balance).
You extract EXACT numbers — never round, estimate, or modify amounts.
Preserve all Indian accounting terms exactly as written (e.g., 'Sundry Debtors', 'Duties & Taxes').
Output ONLY valid JSON in the specified format without any markdown wrappers or explanation.
If you cannot read a value clearly, use 0 and note it in raw_text."""

EXTRACTION_USER_PROMPT = """Extract all financial line items from this {document_type} document.

Expected document type: {document_type} (or auto-detect if unknown)

Return JSON in this EXACT format:
{json_schema}

Rules:
- Extract EVERY line item, even small ones.
- Amounts must be exact numbers (not strings).
- Convert Indian number format to plain numbers: 12,34,567 -> 1234567.
- Negative amounts in brackets: (50,000) -> -50000.
- "Cr" suffix means positive, "Dr" suffix means contextual.
- Mark total/subtotal rows with "is_total": true.
- Detect parent-child grouping from indentation or formatting.
- If a line item has no amount, set amount to 0.
- Financial year format: "2024-25".

Example output for Sales = 15,00,000 and Purchases = 9,00,000:
{
  "document_type": "profit_and_loss",
  "financial_year": "2024-25",
  "entity_name": "Mehta Computers",
  "currency": "INR",
  "line_items": [
    {
      "name": "Sales",
      "amount": 1500000.0,
      "parent_group": "Revenue",
      "level": 1,
      "is_total": false,
      "raw_text": "Sales"
    },
    {
      "name": "Purchases",
      "amount": 900000.0,
      "parent_group": "Expenses",
      "level": 1,
      "is_total": false,
      "raw_text": "Purchases"
    }
  ],
  "totals": {
    "gross_total": 600000.0,
    "net_total": 200000.0
  },
  "metadata": {
    "source_file": "example.png",
    "parser": "vision_extractor"
  }
}
"""
