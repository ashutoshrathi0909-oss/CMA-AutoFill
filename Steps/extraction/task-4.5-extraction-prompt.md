# Task 4.5: Design Extraction Prompt Template

> **Phase:** 04 - Document Extraction
> **Depends on:** Tasks 4.1-4.4 (all parsers/extractors built)
> **Agent reads:** cma-domain SKILL (entire file — domain knowledge critical here)
> **MCP to use:** Sequential Thinking MCP (think carefully about prompt design)
> **Time estimate:** 20 minutes

---

## Objective

Create the prompt templates used when Gemini Vision extracts data from scanned documents. The prompt quality directly determines extraction accuracy. This is one of the most important tasks in the entire project.

---

## What to Do

### Create File
`backend/app/services/extraction/prompts.py`

### Prompt Templates to Create

**1. EXTRACTION_SYSTEM_PROMPT**
The system instruction for all extraction calls:
- "You are a specialist in reading Indian financial documents"
- "You extract EXACT numbers — never round, estimate, or modify amounts"
- "Preserve all Indian accounting terms exactly as written"
- "Output ONLY valid JSON in the specified format"
- "If you cannot read a value clearly, use null and add a note"

**2. EXTRACTION_USER_PROMPT**
Template that gets filled per document:
```
Extract all financial line items from this {document_type} document.

Company: {entity_name} (if visible in document)
Expected document type: {expected_type} (or "auto-detect" if unknown)

Return JSON in this EXACT format:
{json_schema}

Rules:
- Extract EVERY line item, even small ones
- Amounts must be exact numbers (not formatted strings)
- Convert Indian number format to plain numbers: 12,34,567 → 1234567
- Negative amounts in brackets: (50,000) → -50000
- "Cr" suffix means positive, "Dr" suffix means contextual
- Mark total/subtotal rows with "is_total": true
- Detect parent-child grouping from indentation or formatting
- If a line item has no amount, set amount to 0 and note it
- Financial year format: "2024-25"
```

**3. EXTRACTION_CLEANUP_PROMPT**
A second-pass prompt to clean up messy first-pass results:
- Used only when first extraction has issues (missing items, malformed numbers)
- Takes the first-pass output + original image and asks Gemini to verify/fix
- "Compare this extracted data against the document. Fix any errors."

### Prompt Design Principles

1. **Be extremely specific** about output format — include the full JSON schema with examples
2. **Include Indian-specific rules** — Tally terminology, Indian number formatting, Schedule III format
3. **Temperature 0.0** — we want deterministic extraction, not creative interpretation
4. **JSON mode** — use Gemini's response_format="json" to guarantee valid JSON
5. **Include few-shot example** — one complete example of input description → expected output helps accuracy dramatically

### Create a Few-Shot Example

Include a hardcoded example in the prompt:
- Example input: "A P&L statement showing Sales 15,00,000, Purchases 9,00,000, Gross Profit 6,00,000"
- Example output: the exact JSON we expect

This grounds the model and prevents format drift.

---

## What NOT to Do

- Don't include classification logic in extraction prompts (extraction = "what items exist", classification = "where do they go")
- Don't ask Gemini to map items to CMA rows (that's Phase 05)
- Don't make prompts too long — keep under 2000 tokens to leave room for the image
- Don't use generic financial terms — use Indian accounting terminology

---

## Verification

- [ ] EXTRACTION_SYSTEM_PROMPT is clear, specific, under 500 tokens
- [ ] EXTRACTION_USER_PROMPT has placeholders for document_type, entity_name, json_schema
- [ ] JSON schema in prompt matches the standardized format from task 4.2 exactly
- [ ] Few-shot example is correct and realistic for Indian financial documents
- [ ] Test: call Gemini with the prompt + a sample document image → output matches expected format
- [ ] Test: deliberately send a blurry image → Gemini uses null + notes for unclear values (not hallucinated numbers)
- [ ] EXTRACTION_CLEANUP_PROMPT successfully catches and fixes errors from first pass
- [ ] All prompts stored as string constants in prompts.py (easy to update)

---

## Done → Move to task-4.6-extraction-endpoint.md
