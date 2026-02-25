# Task 7.4: Apply Review Decisions to Classification Data

> **Phase:** 07 - Ask Father
> **Depends on:** Tasks 7.2-7.3 (review resolution works)
> **Time estimate:** 15 minutes

---

## Objective

After a CA resolves review items, update the project's classification_data with the correct mappings and advance the project status.

---

## What to Do

### Create File
`backend/app/services/classification/review_applier.py`

### Function

`apply_review_decisions(project_id: UUID) → ApplyResult`

### Logic

1. Load project's `classification_data`
2. Get all resolved review items for this project
3. For each resolved item:
   - Find the matching classified item (by source_item_name + amount)
   - Update its target_row, target_sheet, target_label
   - Set confidence = 1.0 (CA-verified)
   - Set source = 'ca_reviewed'
   - Set needs_review = False
4. Save updated classification_data back to project
5. Check if ANY pending review items remain:
   - All resolved → update status to 'validated', pipeline_progress = 60
   - Some still pending → keep status 'reviewing'
6. Return summary

### Endpoint

**`POST /api/v1/projects/{project_id}/apply-reviews`**

Triggers `apply_review_decisions()` and returns result.

Response:
```json
{
  "data": {
    "items_updated": 8,
    "items_still_pending": 2,
    "project_status": "reviewing",
    "ready_to_generate": false,
    "message": "8 items updated. 2 items still need review."
  }
}
```

### Auto-Apply Option

Add a setting (per firm) to auto-apply decisions immediately when a review item is resolved, instead of requiring a separate apply step. For V1, default to manual apply.

---

## What NOT to Do

- Don't re-run AI classification — just apply CA decisions
- Don't delete review queue records (keep for audit trail)
- Don't auto-generate the CMA after applying (CA should trigger that explicitly)

---

## Verification

- [ ] Resolve 3 review items → apply → classification_data updated with CA's decisions
- [ ] Updated items have confidence=1.0, source='ca_reviewed'
- [ ] All items resolved → project status changes to 'validated'
- [ ] Some items still pending → status stays 'reviewing'
- [ ] Apply is idempotent (running twice doesn't cause issues)

---

## Done → Move to task-7.5-precedent-crud.md
