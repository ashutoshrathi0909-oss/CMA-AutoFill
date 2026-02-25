# Task 5.7: Classification API Endpoint + Accuracy Test

> **Phase:** 05 - Classification
> **Depends on:** Tasks 5.1-5.6 (entire classification pipeline built)
> **Agent reads:** CLAUDE.md → API Design Patterns
> **Time estimate:** 20 minutes

---

## Objective

Create the API endpoint that triggers classification on a project, and write the critical accuracy test against the Mehta Computers golden dataset.

---

## What to Do

### Step 1: Classification Endpoint

File: `backend/app/api/v1/endpoints/classification.py`

**`POST /api/v1/projects/{project_id}/classify`**

Request body (optional):
```json
{
  "force_reclassify": false    // re-run even if already classified
}
```

Logic:
1. Validate project belongs to firm → 404 if not
2. Check project status is 'extracted' → 409 if not ("Extraction must complete before classification")
3. Update project status → 'classifying', pipeline_progress = 30
4. Call `classify_project()` from task 5.5
5. Save classification results to `cma_projects.classification_data` (JSONB)
6. Call `populate_review_queue()` from task 5.6
7. Update project status:
   - If no items need review → status = 'validated' (skip review), pipeline_progress = 60
   - If items need review → status = 'reviewing', pipeline_progress = 50
8. Return classification summary

Response:
```json
{
  "data": {
    "project_id": "uuid",
    "total_items": 45,
    "auto_classified": 33,
    "needs_review": 10,
    "unclassified": 2,
    "accuracy_estimate": 0.73,
    "classification_breakdown": {
      "by_precedent": 5,
      "by_rule": 20,
      "by_ai": 8,
      "uncertain": 12
    },
    "review_queue_items": 10,
    "llm_cost_usd": 0.0045,
    "llm_tokens_used": 8500,
    "duration_ms": 3200
  }
}
```

**`GET /api/v1/projects/{project_id}/classification`**

Returns the full classification data for a project:
- All classified items with their mappings
- Grouped by CMA sheet for easy viewing
- Includes review queue status

### Step 2: Classification Data Storage

Save to `cma_projects.classification_data`:
```json
{
  "classified_at": "2026-02-25T10:30:00Z",
  "total_items": 45,
  "items": [
    {
      "item_name": "Sales",
      "item_amount": 1500000,
      "target_row": 5,
      "target_sheet": "operating_statement",
      "target_label": "Net Sales / Income from Operations",
      "confidence": 0.95,
      "source": "rule",
      "needs_review": false
    }
  ],
  "summary": {
    "by_precedent": 5,
    "by_rule": 20,
    "by_ai": 8,
    "uncertain": 12
  }
}
```

### Step 3: Accuracy Test (CRITICAL)

File: `backend/tests/test_classification.py`

**Golden Test: Mehta Computers**

This is the most important test in the project. It proves the system works.

1. Load the Mehta Computers reference data:
   - Input: extracted line items from Phase 04 golden test
   - Expected output: `reference/CMA_15092025.xls` — the completed CMA your father manually prepared

2. Create expected mappings fixture:
   File: `backend/tests/fixtures/mehta_expected_classification.json`
   
   For each item in the Mehta Computers P&L and BS, document the CORRECT mapping:
   ```json
   [
     {"item_name": "Sales", "expected_row": 5, "expected_sheet": "operating_statement"},
     {"item_name": "Purchases", "expected_row": 10, "expected_sheet": "operating_statement"},
     ...
   ]
   ```

3. Run the classifier on Mehta Computers data

4. Compare results against expected:
   - **Accuracy = items correctly classified / total items**
   - Count: exact matches (correct row AND sheet)
   - Count: close matches (correct sheet, wrong row — nearby)
   - Count: wrong (completely wrong mapping)
   - Count: unclassified (no mapping at all)

5. Assert: accuracy >= 0.70 (our POC achieved 73%)

6. Print detailed report:
   ```
   === Mehta Computers Classification Accuracy ===
   Total items: 45
   Correct: 33 (73.3%)
   Close (wrong row, right sheet): 5 (11.1%)
   Wrong: 4 (8.9%)
   Unclassified: 3 (6.7%)
   
   Misclassified items:
   - "Computer Repairs" → got row 22 (Misc), expected row 15 (Repairs)
   - "Electricity Charges" → got row 22 (Misc), expected row 17 (Power & Fuel)
   ...
   ```

### Step 4: Additional Tests

**Test: Rule-only classification**
- Mock Gemini to be unavailable
- Run classifier → should still classify via rules
- Assert: >50% accuracy from rules alone

**Test: Precedent override**
- Insert a precedent: "Computer Sales" → row 5
- Run classifier → "Computer Sales" should map to row 5, source = "precedent"

**Test: Empty project**
- Project with no extracted data → 409 "No extracted data"

---

## What NOT to Do

- Don't generate the CMA Excel file (that's Phase 06)
- Don't create the review UI (Phase 07)
- Don't block if review items exist — just mark status as 'reviewing'
- Don't run this in background (Phase 08)
- Don't inflate accuracy numbers — be honest about what works and what doesn't

---

## Verification

- [ ] POST classify → returns classification summary with correct counts
- [ ] GET classification → returns all classified items
- [ ] Project status updated correctly ('reviewing' if items need review)
- [ ] Review queue populated with low-confidence items
- [ ] LLM usage logged with correct model and cost
- [ ] **Golden test passes: Mehta Computers accuracy >= 70%**
- [ ] Accuracy report shows which items were misclassified (debugging aid)
- [ ] Precedent override works correctly
- [ ] Rule-only fallback works when AI is unavailable
- [ ] Re-classification (force_reclassify=true) works without errors

---

## Phase 05 Complete! 🎉

All 7 tasks done. You now have:
- ✅ 384 classification rules in structured JSON
- ✅ Rule filtering by entity type + document type
- ✅ Precedent matching (CA decisions override rules)
- ✅ Optimized classification prompts for Gemini 3 Flash
- ✅ Three-tier classifier: Precedent → Rule → AI
- ✅ Review queue populated for low-confidence items
- ✅ Classification API endpoint
- ✅ Golden test: Mehta Computers accuracy measured and tracked
- ✅ Pipeline: extracted → classifying → reviewing/validated

**Next → Phase 06: Validation & Excel Generation**
