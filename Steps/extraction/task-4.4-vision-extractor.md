# Task 4.4: Vision Extractor (Scanned Documents)

> **Phase:** 04 - Document Extraction
> **Depends on:** Task 4.1 (Gemini client), Task 4.2 (standardized output format)
> **Agent reads:** cma-domain SKILL → Source Document Types, Common Indian Financial Terms
> **MCP to use:** Sequential Thinking MCP (for prompt design)
> **Time estimate:** 20 minutes

---

## Objective

Create an extractor that uses Gemini 2.0 Flash Vision to read scanned PDFs and photos of financial documents. This is the AI-powered extractor for documents that can't be parsed with openpyxl or pdfplumber.

---

## What to Do

### Create File
`backend/app/services/extraction/vision_extractor.py`

### When This Is Used

- Scanned PDF (detected by `is_digital_pdf() = false` from task 4.3)
- Image files: .jpg, .png
- Photos of printed financial statements taken by phone

### Extraction Flow

1. **Prepare the image(s):**
   - For PDFs: convert each page to image (use pdf2image or Gemini's native PDF support)
   - For images: use directly
   - If multi-page: process each page separately, then merge results

2. **Call Gemini 2.0 Flash Vision:**
   - Use `gemini_client.generate_with_image()` from task 4.1
   - Model: `gemini-2.0-flash` (best for financial table OCR)
   - Temperature: 0.0 (we want exact numbers, not creativity)
   - Response format: JSON

3. **Prompt design:** (detailed in task 4.5, but basic structure here)
   - System: "You are a financial document OCR specialist for Indian accounting documents"
   - Include the expected output JSON structure in the prompt
   - Ask for exact numbers — no rounding, no estimating
   - Ask it to preserve Indian financial terms as-is

4. **Parse Gemini's response:**
   - Extract JSON from response text
   - Validate it matches our standardized format
   - Handle cases where Gemini returns partial or malformed JSON

5. **Return** standardized JSON format (same as tasks 4.2 and 4.3)

### Image Preprocessing (if needed)

- If image is very large (>4MB), resize to max 2048px on longest side
- If image is rotated, Gemini handles rotation automatically
- Don't do complex image preprocessing — Gemini 2.0 Flash is good at reading messy documents

### Cost Tracking

- Every Gemini Vision call must be logged via `log_llm_usage()`
- Expected cost: ~$0.001-0.005 per page (very cheap on 2.0 Flash)

---

## What NOT to Do

- Don't use this for digital PDFs or Excel files (waste of API calls)
- Don't use Gemini 3 Flash or 3.1 Pro for extraction (2.0 Flash is best + cheapest)
- Don't do complex image preprocessing — keep it simple
- Don't try to classify items (Phase 05)
- Don't batch multiple pages into one API call — process one at a time for reliability

---

## Verification

- [ ] Photo of a printed P&L → extracts line items with correct names and amounts
- [ ] Scanned PDF (1 page) → extracts correctly
- [ ] Scanned PDF (3 pages) → extracts from all pages, items merged
- [ ] Numbers are exact (not rounded) — verify against source document
- [ ] Indian financial terms preserved ("Sundry Debtors" not "Accounts Receivable")
- [ ] LLM usage logged in database with correct model and cost
- [ ] Blurry/low-quality image → partial results + warning, not crash
- [ ] Output format matches standardized format from task 4.2

---

## Done → Move to task-4.5-extraction-prompt.md
