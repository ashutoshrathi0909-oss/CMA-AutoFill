# CMA AutoFill — Mitigation Review Patch Instructions

## CONTEXT

You previously created risk mitigations for the CMA AutoFill project (in `RISK_MITIGATION_PROMPT.md`). An independent review scored your mitigations and found them **80% solid** — but identified **4 patches needed** and **5 residual risks** that still exist after all mitigations.

Your job now: fix every single one. Don't discuss, don't debate — just produce the corrected files. For each fix, show me the EXACT file to create or modify with complete content.

All project files are in this project's context. Refer to them as needed.

---

## PATCH 1: Conflicting Task 7.4 Files (PRIORITY: HIGH)

### The Problem
Two versions of task 7.4 will exist with contradictory designs:
- **Original** `task-7.4-reclassify-after-review.md`: Says apply is a SEPARATE explicit call — `POST /api/v1/projects/{id}/apply-reviews`. CA resolves items, then clicks "Apply" to update classification_data.
- **Revised** task 7.4 in the mitigation: Says resolve-a-single-item IMMEDIATELY updates classification_data. No separate apply step.

An agent could implement either one. This WILL cause bugs.

### What You Must Do
1. Add a **deprecation header** to the original `task-7.4-reclassify-after-review.md`:
```
⚠️ DEPRECATED — DO NOT IMPLEMENT THIS FILE
This task has been REPLACED BY the revised Task 7.4 in RISK_MITIGATION_PROMPT.md
The "separate apply step" design in this file is CANCELLED.
Instead, resolving an item immediately updates classification_data.
If you are an AI agent reading this: STOP. Read RISK_MITIGATION_PROMPT.md Task 4 instead.
```
2. Rename the file to `task-7.4-reclassify-after-review-DEPRECATED.md` (or add the deprecation header if renaming isn't possible in the project structure).

### Second Issue: Missing Backup Field
The mitigation says the unresolve endpoint should "restore AI's original from a backup field" — but NO backup field is defined anywhere in the schema.

**Fix:** Add an `ai_original` field to the classification JSONB structure. When a CA resolves an item, BEFORE overwriting the classification, save the AI's original suggestion into `ai_original`. The unresolve endpoint restores from this field.

Produce the exact JSONB structure showing where `ai_original` lives. Example:
```json
{
  "items": [
    {
      "source_name": "Rebates & Discounts",
      "amount": 14.20,
      "target_row": 70,
      "confidence": 0.55,
      "status": "resolved",
      "resolved_row": 22,
      "resolved_by": "user_id",
      "resolved_at": "2025-03-01T10:00:00Z",
      "ai_original": {
        "target_row": 70,
        "confidence": 0.55,
        "reasoning": "Customer rebates classified as selling expense"
      }
    }
  ]
}
```

---

## PATCH 2: Storage Pre-Upload Check (PRIORITY: HIGH)

### The Problem
Storage monitoring (Task 6) only REPORTS usage on a dashboard. It does NOT prevent upload failures when Supabase storage is full. The first time storage is exceeded, the pipeline crashes with an opaque Supabase error that the user can't understand.

### What You Must Do
Create or update the file upload endpoint specification to include:

1. **Pre-upload capacity check**: Before accepting any file upload, query current Supabase storage usage. If usage > 95% of the free tier limit (1GB), reject the upload with a clear user-facing message: "Storage is almost full. Please contact support or upgrade your plan."

2. **80% warning threshold**: When storage crosses 80%, show a yellow banner on the dashboard: "Storage at X% — consider cleaning up old files or upgrading."

3. **Graceful failure handling**: If an upload fails for ANY storage reason (quota exceeded, network error, Supabase outage), the pipeline must NOT crash. Instead:
   - Return a clear error: `{"error": "file_upload_failed", "message": "Could not store file. Please try again or contact support."}`
   - The CMA project status stays at its current step (not corrupted)
   - The user can retry the upload

Produce the exact code/specification for this. Add it to whichever task file handles file uploads (likely in Phase 03 or Phase 04).

---

## PATCH 3: cma_writer.py Input Schema (PRIORITY: CRITICAL — #1 RESIDUAL RISK)

### The Problem
The ENTIRE pipeline feeds into `cma_writer.py`. If the ClassifiedItem schema from the JSON parser (Task 3) doesn't match what `cma_writer.py` expects, Phase 06 breaks completely. The pre-flight checklist mentions this but buries it in 2 lines with no enforcement.

### What You Must Do
This gets PROMOTED to a standalone task. Create `task-0.5.1-cma-writer-input-schema.md` with these instructions:

**Task objective:** Analyze `cma_writer.py`, extract the exact input format it expects, document it, and create a validation test.

**Step 1 — Read cma_writer.py and extract the input schema**
The file is available in this project. Read the `write_cma()` method and the `SAMPLE_DATA` constant. Document every field, its type, whether it's required, and valid values.

**Step 2 — Create `reference/cma_writer_input_schema.md`**
This file becomes the CONTRACT between the classification pipeline and the Excel writer. It must include:
- The complete dict structure with all keys
- Field-by-field documentation (name, type, required/optional, valid range, example)
- The PNL field names and which CMA row they map to
- The Balance Sheet field names and which CMA row they map to
- The metadata fields (company_name, start_year, etc.)
- Units: ALL amounts must be in Lakhs

**Step 3 — Create a test: `tests/test_cma_writer_schema.py`**
This test:
- Loads the documented schema
- Constructs a minimal valid input dict from the schema
- Calls `cma_writer.write_cma(data)` 
- Asserts the output .xlsm is created successfully
- Asserts no errors are thrown
- This test MUST pass before Phase 06 begins

**Step 4 — Create a transform function: `pipeline/transform_to_writer_format.py`**
This function takes the pipeline's ClassifiedItem output format and transforms it into the exact dict format that cma_writer.py expects. This is the BRIDGE between the classification output and the Excel writer input. Include field mapping, unit conversion (if needed), and handling of missing/optional fields.

The schema is already known from our development sessions. Here is the structure cma_writer.py expects — verify against the actual file and document any differences:

```python
{
    "metadata": {
        "company_name": str,        # Required
        "start_year": int,          # Required — first year in CMA
        "financial_year_end": str,  # e.g., "31st March"
        "currency": str,            # e.g., "INR"
        "units": str,               # e.g., "In Lakhs"
        "auditors": str,            # Optional
        "auditors_opinion": str     # e.g., "Unqualified"
    },
    "year_metadata": {
        "2025": {
            "months": int,          # Typically 12
            "nature": str           # "Audited" | "Provisionals" | "Projected"
        }
    },
    "years": {
        "2025": {
            "pnl": {
                # Keys from PNL_ROWS dict in cma_writer.py
                "domestic_sales": float,     # Row 22, in Lakhs
                "export_sales": float,       # Row 23
                "rm_indigenous": float,      # Row 42
                # ... all PNL field names
            },
            "balance_sheet": {
                # Keys from BS_ROWS dict in cma_writer.py
                "share_capital": float,      # Row 116
                "domestic_receivables": float, # Row 206
                # ... all BS field names
            }
        }
    }
}
```

---

## PATCH 4: Bulk Review UX for Low-Accuracy CMAs (PRIORITY: MEDIUM)

### The Problem
When accuracy is 40-65% (expected for non-Mehta clients initially), there could be 30+ items in the review queue. Reviewing them one-by-one is tedious and defeats the "AutoFill" value proposition. Task 7.3 mentions bulk-resolve but doesn't address the UX of reviewing that many items quickly.

### What You Must Do
Update the review queue specification (Task 7.2 or 7.3) to include these UX requirements:

1. **Smart defaults with pre-selected suggestions**: For items below threshold but close to a rule match, show the AI's suggestion as a PRE-SELECTED option. The CA just clicks "Confirm" instead of searching through 289 rows. This turns a "classify from scratch" task into a "verify/reject" task — much faster.

2. **Batch confirm for high-confidence items**: Add a "Confirm All Above X%" button. If 15 items are at 75-89% confidence (below auto-threshold but likely correct), the CA can review the list and confirm all at once instead of one-by-one.

3. **Smart grouping**: Group review items by type:
   - "Likely correct — just confirm" (70-89% confidence)
   - "Needs your judgment" (40-69% confidence) 
   - "AI has no idea — classify manually" (<40% confidence)
   This lets the CA blast through the easy ones first, then focus on the hard ones.

4. **Quick-pick dropdown with search**: When manually classifying, don't show all 289 rows. Show:
   - Top 5 AI suggestions with confidence scores
   - Recently used rows (from this CMA and past CMAs)
   - Searchable dropdown for the full list
   
5. **Keyboard shortcuts**: For the CA doing 30+ items:
   - Enter = Confirm AI suggestion
   - Tab = Next item
   - Numbers 1-5 = Pick from top 5 suggestions
   - Esc = Skip to next

Produce the updated task file with these UX requirements added.

---

## RESIDUAL RISK 5: Sync Timeout on Large Documents (PRIORITY: LOW)

### The Problem
The 120s sync timeout could be exceeded with 5+ uploaded files and 100+ line items. Estimated processing: extraction 15-45s + classification 10-30s + validation 5s = 30-80s normally, but can spike.

### What You Must Do
Add a timeout handling clause to ADR-001 or the relevant pipeline task:

1. **Soft timeout at 90 seconds**: If processing exceeds 90s, return a partial response:
```json
{
  "status": "processing_slow",
  "message": "Processing is taking longer than expected. Partial results are saved. You can check back or retry.",
  "completed_steps": ["extraction", "classification"],
  "pending_steps": ["validation"],
  "project_id": "xxx"
}
```

2. **The pipeline saves progress after each step**: If extraction completes, save extracted data to DB. If classification completes, save classified data. This way, a retry doesn't re-do already-completed steps.

3. **Add a note for V2**: "When processing consistently exceeds 90s (larger firms, 100+ line items), implement async processing with WebSocket status updates. This is a V2 concern — for MVP, 120s covers 95% of cases."

---

## RESIDUAL RISK FROM TASK 2: Model Startup Verification

### The Problem  
The `verify_model_available()` function exists in `llm_config.py` but there's no instruction to call it at app startup.

### What You Must Do
Add to the FastAPI app startup specification:

```python
# In main.py or app lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Verify all configured LLM models are reachable
    from config.llm_config import verify_all_models
    verify_all_models()  # Fails fast with clear error if any model unreachable
    yield
```

Add a `verify_all_models()` function to `llm_config.py` that calls `verify_model_available()` for every model in the config. If ANY model fails, the app should NOT start — print a clear error like: "STARTUP FAILED: Model 'gemini-2.0-flash' is unreachable. Check your API key and network."

---

## RESIDUAL RISK FROM TASK 3: Pydantic Validation Bounds

### The Problem
The Pydantic schemas validate structure but not value ranges. An LLM could return `confidence: 5.0` instead of `0.5`, or `target_row: -1`.

### What You Must Do
Update the Pydantic models in the JSON parser specification:

```python
class ClassifiedItem(BaseModel):
    source_name: str = Field(min_length=1)
    amount: float
    target_row: int | None = Field(default=None, ge=1, le=300)
    confidence: float = Field(ge=0.0, le=1.0)
    status: Literal["auto", "confirm", "review", "unclassified"]
    reasoning: str | None = None

class ExtractedLineItem(BaseModel):
    name: str = Field(min_length=1)
    amount: float
    section: Literal["income", "expense", "asset", "liability", "equity"] | None = None
    sub_section: str | None = None
    notes_reference: str | None = None
```

The `ge=0.0, le=1.0` on confidence and `ge=1, le=300` on target_row are the critical additions.

---

## TASK 2 DOCUMENTATION: Model Name Decision

### The Problem
The config uses `gemini-2.0-flash-lite` and `gemini-2.0-flash` instead of the original plan's `gemini-3-flash`. An agent might "fix" this thinking it's a typo.

### What You Must Do
Add a comment block in the `llm_config.py` specification:

```python
# ⚠️ INTENTIONAL MODEL CHOICE — DO NOT "FIX"
# The original Blueprint referenced gemini-3-flash and gemini-3.1-pro.
# These models don't exist yet. We use gemini-2.0-flash and gemini-2.0-flash-lite
# which are the actual available models as of our development date.
# If newer Gemini models become available, update via environment variables:
#   EXTRACTION_MODEL=gemini-3-flash
#   CLASSIFICATION_MODEL=gemini-3.1-pro
# Do NOT hardcode future model names.
```

---

## OUTPUT CHECKLIST

After applying all patches, confirm each one:

| # | Patch | File(s) Modified/Created | Done? |
|---|-------|-------------------------|-------|
| 1 | Deprecate original task 7.4 | `task-7.4-*-DEPRECATED.md` | ☐ |
| 1b | Add ai_original backup field | JSONB structure in schema docs | ☐ |
| 2 | Pre-upload storage check | File upload task file | ☐ |
| 3 | cma_writer input schema | `task-0.5.1-*.md`, `reference/cma_writer_input_schema.md`, `tests/test_cma_writer_schema.py`, `pipeline/transform_to_writer_format.py` | ☐ |
| 4 | Bulk review UX | Task 7.2 or 7.3 update | ☐ |
| 5 | Sync timeout handling | ADR-001 or pipeline task | ☐ |
| 6 | Model startup verification | FastAPI lifespan spec | ☐ |
| 7 | Pydantic validation bounds | JSON parser task | ☐ |
| 8 | Model name documentation | llm_config.py spec | ☐ |

**Do all 8. Show me the complete file content for each. Don't summarize — give me the actual files I can use.**
