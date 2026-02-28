# Phase 06: Validation & Excel Generation — Detailed Documentation

## Overview
Phase 06 bridges the gap between accurately generated logical classifications and a tangible Excel output file (`CMA.xlsm`), executing validations on the generated accounting mapping prior to persisting actual business results.

---

## 1. Domain Validation Mechanics (`rules.py` & `validator.py`)
**Task Reference:** Task 6.1, Task 6.2
**Location:** `backend/app/services/validation/rules.py` & `backend/app/services/validation/validator.py`

- Engineered ~20-25 accounting domain constraints categorizing validation rules natively. Rules filter logically via `applies_to` depending on entity structure ("trading").
- Checks were structured to output explicit dict variables mapped sequentially to `ValidationCheck` instances reflecting `error` severity vs `warning`. For example:
    - **Balance Sheet Constraint:** Sum totals on mapped assets must universally equal liabilities structurally down to ₹1 tolerances. If they mismatch significantly, `can_generate` falls to `False`, forcing user revision.
    - **Gross Profit Cross-Check:** Enforces semantic coherence between mapped rows (`Row 12` mapped `Gross Profit` natively computed vs explicitly tagged).

## 2. Writer Engine Transformation (`data_transformer.py` & `cma_writer.py`)
**Task Reference:** Task 6.3, Task 6.4
**Location:** `backend/app/services/excel/data_transformer.py` & `backend/app/services/excel/cma_writer.py`

- The `data_transformer.py` module natively ingests `ClassifiedItem` schema and flattens it optimally by grouping mapped items directly to targeted rows and dynamically computing derived cells mapped dynamically in `COMPUTED_ROWS` dictionary instances.
- Re-architected `cma_writer.py` module seamlessly applying Python constraints logically into OpenPyXL loading algorithms targeting `Estimated Year` constraints dynamically.

## 3. Orchestration & Generation Engine (`generator.py`)
**Task Reference:** Task 6.5
**Location:** `backend/app/services/excel/generator.py`

- Formats `cma_projects.classification_data` systematically.
- Executes `validate_project` initially ensuring the schema passes threshold bounds before ever opening physical system bytes. 
- Utilizes `tempfile` dynamically instantiating raw `CMA_{Client}_{Year}_{Version}.xlsx` variables updating tracking logic against `generated_files` natively preventing namespace collisions.
- Uploads dynamically populated templates directly back into `cma-files` Supabase storage natively instantiating signed bucket queries. 
- Bumps project `status` successfully to `completed` ending extraction life cycles seamlessly.

## 4. Operational Generation Endpoints (`generation.py`)
**Task Reference:** Task 6.6
**Location:** `backend/app/api/v1/endpoints/generation.py`

- Implemented `POST /projects/{id}/validate` enabling UI hooks exposing diagnostic issues safely before write cycles instantiate.
- Implemented `POST /projects/{id}/generate` exposing deterministic extraction loops enabling frontend UI logic returning active Download Links natively to CA workflows.

## 5. End-to-End Test Engine (`test_e2e_golden.py`)
**Task Reference:** Task 6.7
**Location:** `backend/tests/test_e2e_golden.py`

- Implemented standard golden test frameworks logically orchestrating end to end components seamlessly passing `pytests` asserting deterministic behavior.
