# Task 4.1: Create Gemini API Client Wrapper

> **Phase:** 04 - Document Extraction
> **Depends on:** Phase 03 complete, Gemini API key configured in .env
> **Agent reads:** CLAUDE.md → Tech Stack (LLM section), cma-domain SKILL
> **Time estimate:** 15 minutes

---

## Objective

Create a reusable Gemini API client service that all AI tasks (extraction, classification, validation) will use. Handles API calls, error handling, token counting, and cost logging.

---

## What to Do

### Create File
`backend/app/services/gemini_client.py`

### Models We Use

| Model | Purpose | Pricing |
|-------|---------|---------|
| gemini-2.0-flash | OCR/extraction of financial documents, vision tasks | $0.10/$0.40 per MTok |
| gemini-3-flash | Classification (rule matching), structured output | $0.50/$3.00 per MTok |
| gemini-3.1-pro | Fallback for hard cases only | $2.00/$12.00 per MTok |

### Client Features

**GeminiClient class with methods:**

1. `generate(model, prompt, system_instruction=None, temperature=0.1, response_format=None)` → returns response text
   - model: which Gemini model to use
   - prompt: the user message
   - system_instruction: system prompt
   - temperature: 0.1 for extraction/classification (we want deterministic)
   - response_format: "json" to force JSON output mode

2. `generate_with_image(model, prompt, image_bytes, mime_type, system_instruction=None)` → returns response text
   - For vision tasks (scanned PDFs, images)
   - Sends image as inline data

3. `generate_with_file(model, prompt, file_bytes, mime_type, system_instruction=None)` → returns response text
   - For PDF processing via Gemini's file API

### Token Tracking

After every API call, capture:
- input_tokens (from response.usage_metadata.prompt_token_count)
- output_tokens (from response.usage_metadata.candidates_token_count)
- Calculate cost_usd based on model pricing
- latency_ms (time the call took)

Return a `GeminiResponse` dataclass:
```
GeminiResponse:
  - text: str (the response content)
  - input_tokens: int
  - output_tokens: int
  - cost_usd: float
  - latency_ms: int
  - model: str
```

### Cost Calculation

Hardcode pricing (update if prices change):
```
PRICING = {
    "gemini-2.0-flash": {"input": 0.10, "output": 0.40},    # per million tokens
    "gemini-3-flash":   {"input": 0.50, "output": 3.00},
    "gemini-3.1-pro":   {"input": 2.00, "output": 12.00},
}
```

Formula: `cost = (input_tokens * input_price / 1_000_000) + (output_tokens * output_price / 1_000_000)`

### Error Handling

- API key invalid → raise clear error "Gemini API key is invalid"
- Rate limit (429) → retry once after 2 seconds, then raise
- Timeout → retry once, then raise
- Safety filter blocked → return empty response with warning, don't crash
- All errors should be catchable by callers, not crash the app

### LLM Usage Logging

Create a helper function `log_llm_usage(firm_id, project_id, model, task_type, gemini_response, success)`:
- Inserts a row into `llm_usage_log` table
- Called after every Gemini API call
- task_type: 'extraction', 'classification', 'validation', 'fallback'

---

## What NOT to Do

- Don't create extraction prompts yet (that's task 4.5)
- Don't call classification or validation logic
- Don't use OpenAI or Claude API — Gemini only
- Don't implement caching yet (future optimization)
- Don't use Gemini's file upload API for small files — inline data is simpler

---

## Verification

- [ ] Simple test call: `client.generate("gemini-2.0-flash", "What is 2+2?")` → returns "4" or similar
- [ ] Response includes token counts and cost
- [ ] Vision test: send a simple image → get description back
- [ ] Cost calculation is correct (manually verify with known token counts)
- [ ] Invalid API key → clear error message, not crash
- [ ] `log_llm_usage()` creates a row in `llm_usage_log` table
- [ ] `/health/llm` endpoint still works (from Phase 03)

---

## Done → Move to task-4.2-excel-parser.md
