# CMA AutoFill — Risk Mitigation & Project Kickoff Master Prompt

> **What this is:** Give this ENTIRE document to Claude Code as your FIRST coding session AFTER completing Phase 00 manually.
> **Purpose:** Fix every risk identified in the independent plan review, answer every open question, and set up safety nets so the next 77 tasks execute cleanly.
> **Do NOT start Phase 01 until this prompt's tasks are all done.**

---

## Context for the AI Agent

I am building CMA AutoFill — an AI-powered SaaS that automates Credit Monitoring Arrangement (CMA) document creation for Indian Chartered Accountant (CA) firms. I have a complete 11-phase, ~77-task development plan in my `Steps/` folder.

An independent code review of my entire plan identified **10 risks** and raised **6 unanswered questions**. Before I write a single line of production code, I need you to create **foundation patches** that prevent these risks from becoming real problems.

Think of this as **"Phase 0.5 — Risk Proofing."**

**My project structure:**
```
CMA-AutoFill/
├── Steps/                          # All 12 phase folders with task files (READ THESE)
│   ├── 00-prerequisites/
│   ├── 01-project-init/
│   ├── 02-database/
│   ├── 03-api-crud/
│   ├── 04-extraction/
│   ├── 05-classification/
│   ├── 06-validation-excel/
│   ├── 07-ask-father/
│   ├── 08-orchestrator/
│   ├── 09-frontend-shell/
│   ├── 10-frontend-cma-flow/
│   └── 11-testing-deploy/
├── reference/                      # Source-of-truth reference files
│   ├── CMA_classification.xls     # 384 classification rules
│   ├── CMA_15092025.xls           # Father's manually completed CMA (golden test)
│   ├── CMA.xlsm                   # Blank CMA template (15 sheets)
│   └── cma_writer.py              # Proven Excel writer module (100% accuracy, 65/65 values)
├── CLAUDE.md                       # Project memory file for Claude Code agents
├── cma-domain-SKILL.md            # CMA domain knowledge skill file
└── CMA_AutoFill_Blueprint.md      # Original blueprint (has OUTDATED schemas — see note in Risk 10)
```

---

## YOUR TASKS — Execute All 10 in Order

---

### TASK 1: Fix Schema Drift (Review Risk #10)

**The Problem:**
The `CMA_AutoFill_Blueprint.md` and the Phase 02 task files have CONFLICTING database schemas:
- Blueprint says `role CHECK ('admin', 'staff', 'readonly')` — Phase 02 says `('owner', 'ca', 'staff')`
- Blueprint uses `cma_id` as foreign key — Phase 02 uses `cma_project_id`
- Blueprint has `entity_type` as nullable — Phase 02 has it as NOT NULL
- Status enum values differ between documents
If different Claude Code agents read different documents, they will build incompatible schemas.

**What to Create:**

**File: `SCHEMA_AUTHORITY.md`** (project root)

1. Read ALL 7 task files in `Steps/02-database/` — these are the AUTHORITATIVE source.
2. Read the database section of `CLAUDE.md`.
3. Read the database section of `CMA_AutoFill_Blueprint.md`.
4. Create `SCHEMA_AUTHORITY.md` containing:
   - A header: **"THIS IS THE SINGLE SOURCE OF TRUTH FOR ALL DATABASE SCHEMAS. If any other document contradicts this file, THIS FILE WINS."**
   - Complete, final, copy-paste-ready SQL for ALL tables (every column, type, constraint, default, FK, index)
   - The EXACT enums locked down:
     - `cma_projects.status`: `('draft', 'extracting', 'extracted', 'classifying', 'classified', 'reviewing', 'validated', 'validating', 'generating', 'completed', 'error')`
     - `users.role`: `('owner', 'ca', 'staff')`
     - `clients.entity_type`: `('trading', 'manufacturing', 'service')`
   - Every foreign key relationship documented as a list
   - Every index that should exist
   - A table showing: "Column X in Blueprint → Column Y in SCHEMA_AUTHORITY.md" for every rename/conflict

5. Update `CLAUDE.md` → Database Schema section to match `SCHEMA_AUTHORITY.md` exactly.
6. Add this note to the TOP of `CMA_AutoFill_Blueprint.md`:
   ```
   ⚠️ DATABASE SCHEMAS IN THIS FILE ARE OUTDATED.
   The canonical schema is in SCHEMA_AUTHORITY.md.
   Phase 02 task files are the authoritative source.
   Do NOT use this file's SQL for implementation.
   ```

**Verification:**
- [ ] Every table, column, type, constraint in SCHEMA_AUTHORITY.md matches Phase 02 task files
- [ ] CLAUDE.md database section matches SCHEMA_AUTHORITY.md
- [ ] Blueprint has the deprecation warning at the top
- [ ] Zero contradictions remain between any project documents
- [ ] All foreign key names are consistent (cma_project_id, NOT cma_id)

---

### TASK 2: Abstract LLM Model Names Into Config (Review Risk #1 — HIGH)

**The Problem:**
The plan hardcodes `gemini-2.0-flash`, `gemini-3-flash`, and `gemini-3.1-pro` across multiple task files. Google frequently renames, deprecates, and version-bumps these models. The reviewer rated this as HIGH risk because it affects the two most critical phases (extraction + classification).

**What to Create:**

**File: `backend/app/core/llm_config.py`**

```python
"""
LLM Model Configuration — Single Source of Truth
=================================================
RULE: No other file in this project should hardcode model name strings.
      Always use get_model() from this file.
      Model names are overridable via environment variables.
"""
import os

# --- Model Registry ---
# Change model names HERE when Google updates/deprecates them.
# Env vars override defaults so you can switch models without code changes.

LLM_MODELS = {
    "extraction": {
        "primary": os.getenv("LLM_EXTRACTION_MODEL", "gemini-2.0-flash"),
        "description": "Vision/OCR extraction of financial documents. Needs multimodal support.",
    },
    "classification": {
        "primary": os.getenv("LLM_CLASSIFICATION_MODEL", "gemini-2.0-flash-lite"),
        "fallback": os.getenv("LLM_CLASSIFICATION_FALLBACK", "gemini-2.0-flash"),
        "description": "Reasoning + rule matching for line item classification.",
    },
    "cleanup": {
        "primary": os.getenv("LLM_CLEANUP_MODEL", "gemini-2.0-flash-lite"),
        "description": "Second-pass cleanup of messy extraction results.",
    },
}

# --- Pricing Registry ---
# Per million tokens (USD). Update when Google changes pricing.
LLM_PRICING = {
    "gemini-2.0-flash":      {"input": 0.10, "output": 0.40},
    "gemini-2.0-flash-lite": {"input": 0.0,  "output": 0.0},   # Free tier
    # Add new models here as they become available
}

def get_model(task: str, tier: str = "primary") -> str:
    """Get model name for a task. NEVER hardcode model names elsewhere."""
    config = LLM_MODELS.get(task)
    if not config:
        raise ValueError(f"Unknown LLM task: {task}. Valid: {list(LLM_MODELS.keys())}")
    model = config.get(tier)
    if not model:
        raise ValueError(f"No '{tier}' model for task '{task}'. Available: {list(config.keys())}")
    return model

def get_pricing(model: str) -> dict:
    """Get pricing for a model. Returns zeros for unknown models (safe default)."""
    return LLM_PRICING.get(model, {"input": 0.0, "output": 0.0})

def get_all_models() -> list[str]:
    """Return all unique model names currently configured."""
    models = set()
    for task_config in LLM_MODELS.values():
        for key, value in task_config.items():
            if key != "description":
                models.add(value)
    return list(models)
```

**Also add a model health-check function** (used by `/health/llm` endpoint):
```python
async def verify_model_available(model_name: str) -> tuple[bool, str]:
    """
    Quick 1-token test call to verify a model is accessible.
    Returns (is_available, error_message_or_empty_string).
    Use this in /health/llm and at pipeline startup.
    """
```

**File: `.env.example`** — Add these variables:
```
LLM_EXTRACTION_MODEL=gemini-2.0-flash
LLM_CLASSIFICATION_MODEL=gemini-2.0-flash-lite
LLM_CLASSIFICATION_FALLBACK=gemini-2.0-flash
LLM_CLEANUP_MODEL=gemini-2.0-flash-lite
```

**Update `CLAUDE.md`** → Add to the Tech Stack section:
```
## LLM Models (configured in backend/app/core/llm_config.py)
- NEVER hardcode model name strings. Always use get_model(task, tier).
- Model names are overridable via environment variables.
- Current defaults: gemini-2.0-flash (extraction), gemini-2.0-flash-lite (classification).
- If models change, update llm_config.py OR set env vars. No other code changes needed.
```

**Add warning notes to these task files** (insert at the very top of each file, before the title):
```
⚠️ MODEL NAMES: Never hardcode Gemini model strings. Use get_model() from backend/app/core/llm_config.py.
```
Files to update:
- `Steps/04-extraction/task-4.1-gemini-client.md`
- `Steps/04-extraction/task-4.4-vision-extractor.md`
- `Steps/04-extraction/task-4.5-extraction-prompt.md`
- `Steps/05-classification/task-5.4-classification-prompt.md`
- `Steps/05-classification/task-5.5-classifier-module.md`

**Finally:** Search ALL files in `Steps/` for any literal mentions of `gemini-2.0-flash`, `gemini-3-flash`, `gemini-3.1-pro`, or any other hardcoded model string. List every occurrence found so I can review them manually.

**Verification:**
- [ ] `llm_config.py` exists with models, pricing, get_model(), get_pricing(), verify_model_available()
- [ ] `.env.example` has all LLM env vars
- [ ] `CLAUDE.md` documents the "never hardcode" rule
- [ ] 5 task files have the warning note inserted at the top
- [ ] Report produced listing all remaining hardcoded model name references in Steps/

---

### TASK 3: Create Robust LLM JSON Parsing Utility (Review Risk #2 — HIGH)

**The Problem:**
The plan uses `json.loads(response.text)` directly on LLM output. Gemini frequently returns:
- JSON wrapped in ` ```json ... ``` ` markdown fences
- Extra whitespace, trailing commas
- Hallucinated fields not in the schema
- Truncated JSON when context window is large
- Explanatory text before/after the JSON object
The reviewer rated this as HIGH risk because it will crash the pipeline in production.

**What to Create:**

**File: `backend/app/utils/json_parser.py`**

Must handle ALL of these cases:
1. Clean JSON → parse normally
2. JSON inside ` ```json ... ``` ` → strip fences first
3. JSON inside ` ``` ... ``` ` (no language tag) → strip fences
4. JSON with trailing commas → remove before parsing
5. JSON with `// comments` or `/* comments */` → strip them
6. Truncated JSON (LLM ran out of tokens) → attempt recovery by closing open brackets/braces, OR return clear error
7. Text before JSON (`"Here is the result:\n{...}"`) → extract JSON portion
8. Text after JSON → extract just the JSON
9. Multiple JSON objects in one response → extract the first complete one
10. Completely invalid input → clear, actionable error message (not a raw traceback)

Function signatures:
```python
def parse_llm_json(raw_text: str) -> dict | list:
    """Parse JSON from LLM output, handling all common quirks. Raises ParseError if truly unparseable."""

def validate_against_schema(data: dict, schema_class: type[BaseModel]) -> tuple[bool, list[str]]:
    """Validate parsed JSON against Pydantic model. Returns (is_valid, error_messages). Does NOT raise."""

def safe_parse_and_validate(raw_text: str, schema_class: type[BaseModel]) -> tuple[dict | None, list[str]]:
    """Combined parse + validate. Returns (parsed_data_or_None, list_of_errors). Never raises."""
```

**File: `backend/app/models/llm_schemas.py`**

Pydantic models that the LLM output MUST conform to:
```python
class ExtractedLineItem(BaseModel):
    name: str
    amount: float
    parent_group: str | None = None
    level: int = 0
    is_total: bool = False
    raw_text: str | None = None

class ExtractionResult(BaseModel):
    document_type: str   # "profit_loss", "balance_sheet", "trial_balance"
    financial_year: str | None = None
    entity_name: str | None = None
    currency: str = "INR"
    line_items: list[ExtractedLineItem]
    totals: dict | None = None
    metadata: dict | None = None

class ClassifiedItem(BaseModel):
    item_name: str
    item_amount: float
    target_row: int | None = None
    target_sheet: str | None = None
    target_label: str | None = None
    confidence: float  # 0.0 to 1.0
    reasoning: str | None = None
    source: str | None = None  # "rule", "precedent", "ai", "ca_reviewed"
    matched_rule_id: int | None = None

class ClassificationBatchResult(BaseModel):
    items: list[ClassifiedItem]
```

**File: `backend/tests/test_json_parser.py`**

Write tests covering all 10 edge cases listed above. Each test must pass.

**Add warning notes to these task files** (insert at top):
```
⚠️ JSON PARSING: Never use json.loads() directly on LLM output. Always use safe_parse_and_validate() from backend/app/utils/json_parser.py.
```
Files to update:
- `Steps/04-extraction/task-4.4-vision-extractor.md`
- `Steps/04-extraction/task-4.5-extraction-prompt.md`
- `Steps/04-extraction/task-4.6-extraction-endpoint.md`
- `Steps/05-classification/task-5.5-classifier-module.md`
- `Steps/05-classification/task-5.7-classification-endpoint.md`

**Verification:**
- [ ] `json_parser.py` handles all 10 edge cases
- [ ] Pydantic schemas exist for extraction and classification LLM outputs
- [ ] All tests pass
- [ ] 5 task files have the warning note
- [ ] No task file anywhere recommends raw `json.loads()` on LLM output

---

### TASK 4: Fix the Review → Resume Pipeline Gap (Review Risk #3 — MEDIUM-HIGH)

**The Problem:**
The pipeline goes: Extract → Classify → Pause for Review → ??? → Validate → Generate. Task 7.4 (reclassify after review) is only 2KB with thin detail. Critical questions unanswered:
- Does reclassification re-run the ENTIRE classification or just update reviewed items?
- What triggers pipeline resume after all reviews are done?
- What if the CA changes something that affects other items?
- Can the CA undo a review decision?

**What to Create:**

**File: `Steps/07-ask-father/task-7.4-reclassify-after-review-REVISED.md`**

This REPLACES the original thin task-7.4. It must explicitly answer:

**Q: What happens when a CA resolves ONE review item?**
```
POST /api/v1/review-queue/{id}/resolve (action=approve or correct)
  1. Update review_queue row: status='resolved', resolved_by, resolved_at, resolved_row
  2. Update classification_data JSONB in cma_projects:
     - Find the matching item by source_item_name + amount
     - Set target_row = CA's chosen row
     - Set target_sheet = CA's chosen sheet
     - Set confidence = 1.0
     - Set source = 'ca_reviewed'
     - Set needs_review = false
  3. Create precedent in classification_precedents (firm scope)
  4. Check: are there ANY remaining pending review items for this project?
     - YES → keep status 'reviewing', return remaining_pending count
     - NO → auto-update project status to 'validated', pipeline_progress = 60
            → send "ready to generate" email notification
            → return {all_resolved: true, ready_to_generate: true}
```

**Q: Does reclassification re-run AI?**
A: NO. The CA's decision is written directly into classification_data. No AI re-run. Instant and free.

**Q: What triggers pipeline resume?**
A: TWO triggers (implement both):
1. **Auto-detect:** When last review item is resolved (pending_count == 0), auto-set status to 'validated'. Frontend shows "All reviewed! Generate CMA →" button.
2. **Manual:** CA clicks "Generate CMA" → calls `POST /api/v1/projects/{id}/generate` which runs validation → generation.

**Q: Does a CA correction affect other items?**
A: No. Each item is independent. But the precedent WILL affect future projects. UI text: "Your correction will apply to future CMAs automatically."

**Q: Can the CA undo?**
A: Yes. Add endpoint: `POST /api/v1/review-queue/{id}/unresolve`
- Sets status back to 'pending'
- Reverts classification_data item (restore AI's original from a backup field)
- Deletes the created precedent
- Updates project status back to 'reviewing' if needed

Include complete endpoint specs, request/response schemas, and verification checklist in the REVISED file.

**Also update:**
- `Steps/08-orchestrator/task-8.1-pipeline-service.md` → Add "Resume After Review" section
- `CLAUDE.md` → Update pipeline status flow to include review → validated auto-transition

**Verification:**
- [ ] REVISED task 7.4 is comprehensive (at least 4KB)
- [ ] Every status transition documented with exact conditions
- [ ] Auto-resume trigger (pending_count == 0) defined
- [ ] Undo/unresolve capability specified
- [ ] task-8.1 has resume flow
- [ ] CLAUDE.md pipeline section updated

---

### TASK 5: Make Pipeline Synchronous for MVP (Review Risk #4 — MEDIUM-HIGH)

**The Problem:**
FastAPI `BackgroundTasks` on Railway: containers restart during deploys, killing in-progress background tasks with no recovery. For 5 CMAs/month that take 30-60 seconds, this complexity isn't worth the risk.

**What to Create:**

**File: `Steps/08-orchestrator/ADR-001-sync-pipeline.md`**

```markdown
# ADR-001: Synchronous Pipeline for MVP

## Status: Accepted

## Context
Pipeline takes 30-60 seconds. We process ~5 CMAs/month. Railway containers restart during deploys, killing background tasks with no recovery.

## Decision
Run the pipeline SYNCHRONOUSLY within the HTTP request for V1.

## Consequences
GOOD:
- No lost work from container restarts
- No complex task queue infrastructure
- Simpler debugging — errors are in the HTTP response
- No polling needed — frontend just waits

ACCEPTABLE:
- User waits 30-60 seconds (fine for 5 CMAs/month)
- Request timeout set to 120s
- If review needed, returns IMMEDIATELY with status "reviewing"

## Migration Path (V2, >20 CMAs/month)
- Add task queue (Celery + Redis or BullMQ)
- POST /process returns job_id immediately
- Add polling endpoint
- Pipeline service itself doesn't change

## Affected Tasks
- task-8.2: SKIP ENTIRELY for V1
- task-8.3: SIMPLIFY — return step timing in sync response
- task-8.5: POST /process is synchronous, 120s timeout
- task-10.3: Frontend shows loading screen, no polling loop
```

**Update these task files** (insert note at the very top of each):

`Steps/08-orchestrator/task-8.2-background-tasks.md`:
```
⚠️ V1 DECISION: SKIP THIS TASK ENTIRELY.
Per ADR-001, the pipeline runs synchronously for MVP.
This file is preserved for V2 reference only.
See Steps/08-orchestrator/ADR-001-sync-pipeline.md
```

`Steps/08-orchestrator/task-8.3-progress-tracking.md`:
```
⚠️ V1 SIMPLIFICATION per ADR-001: No polling endpoint needed.
The sync POST /process response includes per-step timing.
Frontend shows a loading screen for 30-60s, then displays the result.
Simplify this task: include step durations in the pipeline response object.
```

`Steps/08-orchestrator/task-8.5-one-click-endpoint.md`:
```
⚠️ V1 CHANGE per ADR-001: POST /projects/{id}/process is SYNCHRONOUS.
Request timeout: 120 seconds. Returns full PipelineResult when done.
If review needed, returns immediately with {"status": "reviewing", "review_count": N}.
```

`Steps/10-frontend-cma-flow/task-10.3-processing-view.md`:
```
⚠️ V1 SIMPLIFICATION per ADR-001: No polling needed.
Show a loading screen: "Processing your CMA... usually takes 30-60 seconds."
When the fetch() resolves, display the result.
120-second timeout message: "Taking longer than expected. Refresh to check status."
```

**Verification:**
- [ ] ADR-001 file exists with clear reasoning
- [ ] task-8.2 marked SKIP
- [ ] task-8.3, 8.5, 10.3 have simplification notes at top
- [ ] No remaining BackgroundTasks references in V1 critical path

---

### TASK 6: Add Supabase Storage Monitoring (Review Risk #5 — MEDIUM)

**The Problem:**
Supabase free tier: 500MB database, 1GB file storage. JSONB columns (extracted_data, classification_data) can be large. Storage fills silently after ~50-100 CMAs.

**What to do:**

**Update `Steps/03-api-crud/task-3.7-dashboard-stats.md`** — Add section:
```markdown
### Storage Monitoring
Add to GET /api/v1/dashboard/stats response:
"storage": {
  "db_size_mb": 45,
  "db_limit_mb": 500,
  "db_usage_percent": 9,
  "files_size_mb": 120,
  "files_limit_mb": 1000,
  "files_usage_percent": 12,
  "warning": null   // "Storage above 80% — consider upgrading" when applicable
}
Query: SELECT pg_database_size(current_database()) for DB size.
```

**Update `Steps/11-testing-deploy/task-11.3-performance-tuning.md`** — Add section:
```markdown
### JSONB Size Optimization (for completed projects older than 7 days)
- Move raw extracted_data to Supabase Storage as a JSON file
- Replace JSONB column with storage reference: {"storage_ref": "path/to/file.json"}
- Keep only final classification summary in JSONB
- Frees ~80% storage per project
```

**Update `CLAUDE.md`** — Add "Known Limits" section:
```markdown
## Supabase Free Tier Limits
- Database: 500MB — monitor via dashboard stats
- File Storage: 1GB — monitor via dashboard stats
- DB pauses after 7 days inactivity — GitHub Action keep-alive configured
- Upgrade trigger: 70% storage → plan Supabase Pro ($25/month)
- JSONB optimization: compress old project data after completion
```

**Verification:**
- [ ] Dashboard stats task includes storage fields
- [ ] Performance task includes JSONB optimization
- [ ] CLAUDE.md documents limits and upgrade trigger

---

### TASK 7: Add Classification Accuracy Safety Nets (Review Risk #6 — MEDIUM)

**The Problem:**
384 rules built from ONE reference CMA (Mehta Computers, trading). Manufacturing and service entities have different structures. First non-Mehta CMAs may hit 50-60% accuracy.

**What to Create:**

**File: `Steps/05-classification/ACCURACY_STRATEGY.md`**

Document:
- Current state: 384 rules, 73% POC accuracy, trading-optimized
- Launch strategy: onboard trading entities first, expect heavy review for first 10-20 CMAs
- This is BY DESIGN — every review creates precedents that improve accuracy
- Accuracy tracking per project: save auto_rate, ai_rate, review_rate, entity_type to project metadata
- Entity-specific metrics in learning dashboard (task 7.6)
- Minimum viable accuracy: trading 65%+, manufacturing/service 40%+ (review queue handles the rest)
- V2: entity-specific rule additions after 5+ completed CMAs per type

**Update `Steps/05-classification/task-5.7-classification-endpoint.md`** — Add accuracy_metrics tracking after classification completes.

**Update `Steps/07-ask-father/task-7.6-learning-metrics.md`** — Add accuracy breakdown by entity_type.

**Verification:**
- [ ] ACCURACY_STRATEGY.md sets realistic expectations
- [ ] task-5.7 saves per-project accuracy metrics
- [ ] task-7.6 shows accuracy by entity type
- [ ] No document promises >90% accuracy on day one

---

### TASK 8: Add Manual Classification Fallback (Review Risk #8 — LOW-MEDIUM)

**The Problem:**
If Gemini API is down, the entire pipeline stops. No way to classify items without AI. Father can't be blocked from urgent work.

**What to do:**

**Update `Steps/10-frontend-cma-flow/task-10.4-review-queue-page.md`** — Add section:
```markdown
### Manual Classification Fallback (Gemini Down)
When AI classification fails, ALL unclassified items go to review queue with
confidence=0, source='manual_required'. The review queue UI already supports
manual row selection via the "Other" CMA row dropdown — no new UI needed.

Add filter: source='manual_required' to show items needing full manual classification.
These items show NO AI suggestions — just the CMA row dropdown.

### Endpoint Addition
POST /api/v1/projects/{project_id}/skip-classification
- Applies Tier 1 (precedent) and Tier 2 (rule) matches only — no AI
- Marks remaining items as needs_review=true, source='manual_required'
- Updates project status to 'reviewing'
- Use case: Gemini API down, father needs to do CMA urgently
```

**Update `Steps/05-classification/task-5.5-classifier-module.md`** — Add:
```markdown
### Total AI Failure Fallback
If ALL retry attempts fail (primary + fallback models):
- Do NOT crash the pipeline
- Still apply Tier 1 (precedent) and Tier 2 (rule) — these are FREE and LOCAL
- Mark remaining items as needs_review=true, source='unclassified_ai_failure'
- Update status to 'reviewing' and continue
- Log failure but don't block the user
```

**Verification:**
- [ ] Review queue supports manual classification without AI suggestions
- [ ] Skip-classification endpoint documented
- [ ] Classifier doesn't crash on total AI failure
- [ ] Rules + precedents still work when AI is unavailable

---

### TASK 9: Remove CCPM Hard Dependency (Review Risk #9 — LOW-MEDIUM)

**The Problem:**
Plan relies on CCPM (third-party, `curl | bash` install, may break). Not needed since task files are already self-contained agent-ready specs.

**What to do:**

**Update `Steps/00-prerequisites/` or `PHASE-00-prerequisites.md`** — Find the CCPM section and change to:
```markdown
### CCPM (Claude Code Project Manager) — OPTIONAL, NOT REQUIRED

CCPM can convert phase docs to GitHub Issues. But it is NOT a hard dependency.

**Recommended workflow WITHOUT CCPM:**
1. Open Claude Code in project directory
2. Say: "Read CLAUDE.md first, then read Steps/XX-phase/task-X.Y-name.md"
3. Claude Code executes the task
4. Verify output against task's checklist
5. Commit, move to next task

**The plan works perfectly without CCPM.** Each task file is a self-contained spec.
```

**Verification:**
- [ ] No task file lists CCPM as REQUIRED
- [ ] Manual workflow documented
- [ ] Phase 00 says CCPM is optional

---

### TASK 10: Create Pre-Flight Checklist & Execution Guide

**The Problem:**
The reviewer raised 6 questions that need answers before coding. I need a simple guide for executing 77 tasks over 3-4 weeks.

**What to Create:**

**File: `PRE_FLIGHT_CHECKLIST.md`** (project root)

Must include ALL of these sections with blanks to fill in:

1. **Account Verification** — test each: GitHub, Vercel, Supabase, Google AI Studio, Resend
2. **Gemini Model Verification** ⚠️ CRITICAL — go to AI Studio, test exact model strings, record what works, note free tier limits
3. **Reference Files Verification** — confirm all 4 reference files exist and open correctly
4. **cma_writer.py Input Schema** ⚠️ CRITICAL — document the EXACT input dict format the writer expects (keys, sheet name format, row reference format, value data types). Save as `reference/cma_writer_input_schema.md`. This is the BRIDGE between Phase 05 output and Phase 06 input.
5. **Father's Client Data** — what accounting software (Tally/Busy/other percentages), does he have a second client's data for testing, does he have manufacturing/service examples
6. **Backend Deployment Decision** — test Vercel Functions cold start time, decide Vercel vs Railway, document CORS if Railway
7. **Development Environment** — Node.js, Python, Git, Claude Code versions
8. **MCP Servers** — test each after installing
9. **Ready Check** — all items done, critical files exist, decision made

**File: `EXECUTION_GUIDE.md`** (project root)

Must include:
1. **The Workflow** — 7-step process for every single task (open Claude Code → read CLAUDE.md → read task file → execute → verify → commit → next)
2. **Daily Schedule** — 18-day plan from pre-flight through launch
3. **Five Rules** — never skip verification, one task per session, commit after every task, don't jump ahead, skip task 8.2
4. **Key Files Table** — what each safety file is for and when it's used
5. **Milestone Checkpoints** — what to verify after Phase 02, 03, 06, 08, 10, 11
6. **Troubleshooting Table** — every risk from the review mapped to its fix (Gemini names → llm_config.py, JSON errors → json_parser.py, stuck in review → check pending count, etc.)

**Verification:**
- [ ] PRE_FLIGHT_CHECKLIST.md covers all 6 reviewer questions
- [ ] EXECUTION_GUIDE.md has daily plan, rules, milestones, troubleshooting
- [ ] cma_writer.py input schema is flagged as CRITICAL
- [ ] Backend deployment decision is a checklist item
- [ ] All 10 risks from review are addressed in troubleshooting table

---

## AFTER ALL 10 TASKS — Summary of What Was Created

| Action | File | Addresses Risk # |
|--------|------|-----------------|
| CREATE | `SCHEMA_AUTHORITY.md` | #10 Schema drift |
| CREATE | `backend/app/core/llm_config.py` | #1 Model names |
| CREATE | `backend/app/utils/json_parser.py` | #2 JSON parsing |
| CREATE | `backend/app/models/llm_schemas.py` | #2 JSON parsing |
| CREATE | `backend/tests/test_json_parser.py` | #2 JSON parsing |
| CREATE | `Steps/07-ask-father/task-7.4-...-REVISED.md` | #3 Review→Resume gap |
| CREATE | `Steps/08-orchestrator/ADR-001-sync-pipeline.md` | #4 Background tasks |
| CREATE | `Steps/05-classification/ACCURACY_STRATEGY.md` | #6 Accuracy concerns |
| CREATE | `PRE_FLIGHT_CHECKLIST.md` | All questions answered |
| CREATE | `EXECUTION_GUIDE.md` | Getting started guide |
| UPDATE | `CLAUDE.md` | Schemas, pipeline flow, limits, LLM rules |
| UPDATE | `CMA_AutoFill_Blueprint.md` | Schema deprecation warning |
| UPDATE | `.env.example` | LLM env vars added |
| UPDATE | 15+ task files in Steps/ | Warning notes (models, JSON, sync, skip) |

## Risk Coverage — Every Risk Neutralized

| # | Risk | Severity | Fix |
|---|------|----------|-----|
| 1 | Gemini model names change | HIGH | Task 2: llm_config.py + env vars |
| 2 | LLM JSON parsing fragile | HIGH | Task 3: json_parser.py + Pydantic |
| 3 | Review → Resume gap | MEDIUM-HIGH | Task 4: REVISED task 7.4 |
| 4 | BackgroundTasks on Railway | MEDIUM-HIGH | Task 5: ADR-001 sync pipeline |
| 5 | Supabase free tier limits | MEDIUM | Task 6: Storage monitoring |
| 6 | Classification accuracy | MEDIUM | Task 7: ACCURACY_STRATEGY.md |
| 7 | 3-service deployment | MEDIUM | Task 10: Deployment decision in checklist |
| 8 | No offline/degraded mode | LOW-MEDIUM | Task 8: Manual classification fallback |
| 9 | CCPM dependency | LOW-MEDIUM | Task 9: Made optional |
| 10 | Schema drift | LOW | Task 1: SCHEMA_AUTHORITY.md |

**After this session, every risk is neutralized. Complete PRE_FLIGHT_CHECKLIST.md manually, then start Phase 01.**
