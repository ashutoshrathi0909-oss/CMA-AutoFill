---
name: cma-domain
description: CMA (Credit Monitoring Arrangement) domain knowledge for Indian banking and CA workflows. Use this skill whenever working on extraction, classification, validation, Excel generation, or any task involving financial document processing for CMA AutoFill.
---

# CMA Domain Knowledge

## What is a CMA?

A Credit Monitoring Arrangement (CMA) is a standardized financial document required by Indian banks when processing loan applications. It consolidates a business's financial data into a specific format that banks use to assess creditworthiness.

**Why it matters:** A single error in a CMA can result in a loan rejection. CAs (Chartered Accountants) stake their professional reputation on CMA accuracy. This is why our accuracy target is 100% match against known-correct reference data.

## CMA Template Structure

The CMA Excel template has **289 rows across 15 sheets**:

### Sheet Categories
- **Operating Statement (P&L based):** Revenue, expenses, operating profit, net profit
- **Balance Sheet - Assets:** Current assets (cash, debtors, inventory), fixed assets, investments
- **Balance Sheet - Liabilities:** Current liabilities (creditors, short-term loans), long-term liabilities, capital
- **Ratios:** Current ratio, debt-equity ratio, DSCR, profitability ratios
- **Fund Flow:** Sources and uses of funds, working capital changes
- **Projections:** Future year estimates based on assumptions

### Key Concepts
- **Audited vs Estimated vs Projected:** CMAs contain past audited data + current estimates + future projections
- **Financial Year:** Indian FY runs April-March (e.g., FY 2024-25 = April 2024 to March 2025)
- **Lakhs and Crores:** Indian number system. 1 Lakh = 100,000. 1 Crore = 10,000,000.

## Classification System

### The 384 Rules
Each rule maps a source term (from P&L/BS) to a target CMA row:

- **source_term:** What the item is called in the uploaded document (e.g., "Sales", "Sundry Debtors", "Depreciation")
- **target_row_number:** Which row in the CMA template this maps to
- **target_sheet:** Which sheet it belongs to
- **entity_type_filter:** Whether this rule applies to Trading, Manufacturing, or Service entities
- **document_type_filter:** Whether this comes from P&L or Balance Sheet

### Classification Confidence
- **High (>85%):** Exact match or near-exact match with a rule → auto-classified
- **Medium (70-85%):** Partial match, likely correct → auto-classified but flagged
- **Low (<70%):** Uncertain match → sent to "Ask Father" review queue

### Precedent System
When a CA manually classifies an item in the review queue:
- The decision is saved as a **precedent**
- **Firm-level precedent:** Applies only to that CA's firm (their clients use similar naming)
- **Global precedent:** Applies to all firms (verified as universally correct)
- Future classifications check precedents BEFORE rules
- Result: System accuracy improves with every CMA processed

## Common Indian Financial Terms

| Term | CMA Mapping | Notes |
|------|------------|-------|
| Sundry Debtors | Current Assets → Trade Receivables | Amounts owed by customers |
| Sundry Creditors | Current Liabilities → Trade Payables | Amounts owed to suppliers |
| Stock-in-Trade | Current Assets → Inventory | Goods held for sale |
| Depreciation | Operating Expenses → Depreciation | Non-cash expense |
| Preliminary Expenses | Miscellaneous Expenditure | One-time setup costs |
| Reserves & Surplus | Net Worth → Reserves | Accumulated profits |
| Secured Loans | Term Liabilities → Secured | Bank loans with collateral |
| Unsecured Loans | Term Liabilities → Unsecured | Loans without collateral |
| Capital Account | Net Worth → Capital | Owner's investment (partnerships/proprietorship) |
| Share Capital | Net Worth → Share Capital | Owner's investment (companies) |

## Validation Rules

### Balance Sheet Must Balance
- Total Assets = Total Liabilities + Net Worth
- If they don't balance, something is misclassified or missing

### P&L Arithmetic
- Gross Profit = Revenue - Cost of Goods Sold
- Operating Profit = Gross Profit - Operating Expenses
- Net Profit = Operating Profit + Other Income - Other Expenses - Tax

### Critical Rows (Must Not Be Empty)
- Net Sales / Revenue
- Total Current Assets
- Total Current Liabilities
- Net Worth (Capital + Reserves)
- Net Profit / Loss

### Ratio Sanity Checks
- Current Ratio should typically be 1.0-3.0 (flag if outside)
- Debt-Equity Ratio should typically be 0-3.0 (flag if outside)
- These are warnings, not errors — some businesses legitimately have unusual ratios

## The Golden Test

**Reference data:** Mehta Computers (a real client of the CA father)
- Known-correct CMA exists: `CMA_15092025.xls`
- Original source documents available for extraction testing
- **65 values must match exactly** between generated and reference CMA
- This test must pass after every pipeline change
- If it doesn't pass, the code has a bug that must be fixed before continuing

## Source Document Types We Handle

| Type | Format | Extraction Method |
|------|--------|------------------|
| Tally/Busy Excel exports | .xlsx, .xls | openpyxl direct parsing |
| Digital PDFs | .pdf (text-based) | pdfplumber text extraction |
| Scanned documents | .pdf (image), .jpg, .png | Gemini 2.0 Flash Vision |
| Manual Excel sheets | .xlsx | openpyxl with fuzzy header detection |

## What Makes CMA Classification Hard

1. **Non-standard naming:** Every business names their accounts differently. "Sales" might be "Revenue from Operations", "Turnover", "Income from Sales", etc.
2. **Grouped items:** Some P&Ls group multiple items into one line (e.g., "Salaries & Rent" needs to be split)
3. **Missing items:** Some documents don't explicitly list items that CMA requires (need to infer or mark as zero)
4. **Entity type differences:** A trading firm's CMA is structured differently from a manufacturing firm's
5. **Indian accounting quirks:** Schedule III format, old vs new format balance sheets, partnership vs company formats
