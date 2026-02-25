# Task 6.6: Generation & Validation API Endpoints

> **Phase:** 06 - Validation & Excel Generation
> **Depends on:** Tasks 6.2 (validator), 6.5 (generator)
> **Agent reads:** CLAUDE.md → API Design Patterns
> **Time estimate:** 15 minutes

---

## Objective

Create API endpoints for running validation and generating the CMA Excel file.

---

## What to Do

### Create File
`backend/app/api/v1/endpoints/generation.py`

### Endpoints

**`POST /api/v1/projects/{project_id}/validate`**

Runs validation without generating the file. Useful for the CA to check data before committing.

Response:
```json
{
  "data": {
    "passed": false,
    "total_checks": 22,
    "errors": 2,
    "warnings": 5,
    "can_generate": false,
    "checks": [
      {
        "rule_id": "bs_balance",
        "rule_name": "Balance Sheet Balance",
        "severity": "error",
        "passed": false,
        "message": "Total Assets (₹52,00,000) ≠ Total Liabilities (₹50,00,000). Difference: ₹2,00,000",
        "auto_fix": {
          "action": "adjust_value",
          "target_row": 45,
          "suggested_value": 5200000,
          "reason": "Adjust Total Liabilities to match Total Assets"
        }
      }
    ],
    "summary": "2 errors must be fixed before generating CMA. 5 warnings can be reviewed."
  }
}
```

**`POST /api/v1/projects/{project_id}/generate`**

Runs validation + generates the CMA Excel file.

Request body (optional):
```json
{
  "skip_validation": false,
  "apply_auto_fixes": false   // if true, apply all auto-fix suggestions before generating
}
```

Response:
```json
{
  "data": {
    "success": true,
    "file_id": "uuid",
    "file_name": "CMA_MehtaComputers_2024-25_v1.xlsx",
    "file_size": 245760,
    "version": 1,
    "download_url": "https://...",
    "validation": {
      "passed": true,
      "warnings": 3
    },
    "generation_time_ms": 1500
  }
}
```

**`POST /api/v1/projects/{project_id}/apply-fixes`**

Apply auto-fix suggestions from validation:

Request body:
```json
{
  "fixes": [
    {"rule_id": "bs_balance", "accepted": true},
    {"rule_id": "pl_gross_profit", "accepted": false}
  ]
}
```

Logic:
1. For each accepted fix, update the classification_data
2. Re-run validation to confirm fixes resolved the errors
3. Return updated validation result

### Business Rules

- Can only validate/generate projects in status: 'reviewing', 'validated', 'completed'
- Cannot generate if project has unresolved review queue errors AND skip_validation is false
- Each generation creates a new version (never overwrites)
- Download URL uses signed URL pattern from Phase 03

---

## What NOT to Do

- Don't auto-apply fixes without explicit user request
- Don't delete previous generated versions
- Don't run generation in background yet (Phase 08)
- Don't expose internal file paths in response

---

## Verification

- [ ] POST validate → returns detailed check results
- [ ] POST validate with deliberate error → error caught, can_generate = false
- [ ] POST generate with clean data → file generated, download URL works
- [ ] POST generate with errors → blocked with clear message
- [ ] POST generate with skip_validation=true → generates despite errors
- [ ] POST apply-fixes → fixes applied, re-validation passes
- [ ] Version increments on repeated generation
- [ ] Download URL works (returns the actual Excel file)
- [ ] Auth required on all endpoints

---

## Done → Move to task-6.7-golden-test.md
