import re


def clean_indian_number(text: str) -> float:
    """Parse Indian-format number strings into floats.

    Handles:
    - Indian comma grouping (12,34,567)
    - Negative in parentheses: (50,000)
    - "Cr" suffix (credit, treated as positive)
    - "Dr" suffix (debit, treated as negative — sign can be overridden by caller if context requires)
    """
    if not text:
        return 0.0
    text = str(text).strip()
    is_negative = False

    if text.endswith("Cr") or text.endswith("Cr."):
        text = text.replace("Cr.", "").replace("Cr", "").strip()
        # Cr = credit = positive (default)
    elif text.endswith("Dr") or text.endswith("Dr."):
        text = text.replace("Dr.", "").replace("Dr", "").strip()
        is_negative = True  # Dr = debit = negative by default

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


def detect_document_type(combined_text: str) -> str:
    """Detect financial document type from combined header/sheet text."""
    ll = combined_text.lower()
    # Check trial balance BEFORE balance sheet ("Trial Balance" contains "balance")
    if "trial" in ll or "tb" in ll:
        return "trial_balance"
    elif "profit" in ll or "p&l" in ll or "income" in ll:
        return "profit_and_loss"
    elif "balance" in ll or "bs" in ll:
        return "balance_sheet"
    return "other"


def extract_financial_year(text: str) -> str:
    """Extract Indian financial year from text. Supports 2024-25 and 2024-2025 formats."""
    match = re.search(r'20\d{2}[-–]\d{2,4}', text)
    return match.group(0) if match else "Unknown"
