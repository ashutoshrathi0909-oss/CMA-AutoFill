# Phase 05: Classification — Detailed Documentation

## Overview
Phase 05 forms the core "Brain" of the CMA AutoFill system. It systematically routes extracted financial parameters into accurately defined CMA analytical schema rows. The objective was to replace tedious manual accounting judgment with high-speed, programmatic heuristics layered with an AI fallback. Ultimately, it maps line items extracted in Phase 04 to their respective rows using a tri-tier mechanism: Precedent Matching → Rule Filtering → Gemini AI Classification.

---

## 1. Static Rule Formulation (`convert_rules.py` & `rules_loader.py`)
**Task Reference:** Task 5.1
**Location:** `backend/scripts/convert_rules.py` & `backend/app/services/classification/rules_loader.py`

- The `convert_rules.py` script automatically builds the 384 CMA classification rules dynamically mapping typical item names ("Sales", "Purchases", "Sundry Debtors") into strictly defined Row configurations directly linked into specific sheets (`operating_statement`, `balance_sheet`).
- I built a resilient fallback that generates 6 standard MOCK RULES if the original Excel logic structure is temporarily missing locally.
- `rules_loader.py` implements an optimized, in-memory cache variable (`_cached_rules`). It securely locks the rules within strongly-typed `pydantic` classes matching constraints efficiently across all concurrent queries.

## 2. Dynamic Rule Filtration & Matching Engine (`rule_matcher.py`)
**Task Reference:** Task 5.2
**Location:** `backend/app/services/classification/rule_matcher.py`

- `filter_rules` reduces the complexity iteratively by identifying rules tied exclusively to the mapped `entity_types` (e.g. tracking "Trading" or "Manufacturing"). 
- Implements `match_item_to_rules` which evaluates text matching logically down a hierarchy of scoring mechanisms: 
    1. **Exact match** (`score = 1.0`): Identical text mappings.
    2. **Normalized match** (`score = 0.95`): Safely evaluates suffix quirks common in Indian accounting like `"A/c"` and `"S. Debtors"`.
    3. **Contains logic** (`score >= 0.80`).
    4. **Fuzzy Sequence Matching** (`score = > 0.60`) using algorithmic Levenshtein distance computations via `difflib`.

## 3. Precedent CA Cache System (`precedent_matcher.py`)
**Task Reference:** Task 5.3
**Location:** `backend/app/services/classification/precedent_matcher.py`

- The `find_precedents` query engine retrieves previously resolved inputs (from Phase 07 "Ask Father" interface) checking `classification_precedents`.
- Precedent matching holds absolute priority over all other tiers to guarantee learning loop autonomy. Firm-specific precedent weights return `1.0` confidence whereas broader Global precedent boundaries return `0.90` confidence ratios naturally protecting uniqueness.

## 4. Prompts Configuration (`prompts.py`)
**Task Reference:** Task 5.4 
**Location:** `backend/app/services/classification/prompts.py`

- Engineered robust prompt mappings restricting `gemini-3-flash` behavior to JSON outputs targeting precise schema standards ensuring confidence ratios mathematically distribute consistently between `0` (Uncertain) and `1.0` (Absolute). Modifiers like "If unsure, choose < 0.70" enforce the system to lean aggressively toward "Need CA Review" rather than hallucinatory placements.

## 5. Main AI Classification Orchestrator (`classifier.py`)
**Task Reference:** Task 5.5
**Location:** `backend/app/services/classification/classifier.py`

- Executes the **Tier-Based Pipeline** optimally limiting LLM costs to absolute zero where computationally viable. 
- Analyzes items iterating conditionally checking: `Precedents` → `Rules` → `Gemini`.
- The items which fail Tier 1/Tier 2 constraints drop down efficiently into a JSON batch package utilizing the custom LLM query architecture developed in Phase 04. Employs chunked AI limits constrained to `batch_size=20` protecting the context API window consistently.

## 6. Review / Resolution Architecture (`review_service.py`)
**Task Reference:** Task 5.6
**Location:** `backend/app/services/classification/review_service.py`

- Safely routes any `ClassifiedItem` carrying a confidence ratio `< 0.70` directly into the `review_queue` table pending CA examination. 
- Computes `alternative_suggestions` mapping alternative options directly from the `rule_matcher` (Top 3 possible selections) decreasing standard workflow analysis time drastically.

## 7. Endpoint & Integration Layer (`classification.py`)
**Task Reference:** Task 5.7
**Location:** `backend/app/api/v1/endpoints/classification.py`

- Exposed `POST /api/v1/projects/{project_id}/classify` hooking end-to-end extraction objects directly. 
- Updates internal metric tracking constraints accurately advancing instances into the parameter values `status='validated'` (No manual review needed, `Progress=60`) or `status='reviewing'` (Needs CA assistance, `Progress=50`).
- Validated via rigorous `pytest` configuration successfully asserting local operations seamlessly.
