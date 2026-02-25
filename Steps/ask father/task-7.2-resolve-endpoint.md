# Task 7.2: Resolve Review Item Endpoint

> **Phase:** 07 - Ask Father
> **Depends on:** Task 7.1 (review queue endpoints), Phase 05 Task 5.3 (precedent service)
> **Agent reads:** CLAUDE.md → Database Tables → review_queue, classification_precedents
> **Time estimate:** 15 minutes

---

## Objective

Create the endpoint where a CA resolves a review queue item — either accepting the AI's suggestion, picking an alternative, or manually specifying the correct CMA row. Every resolution creates a precedent for future use.

---

## What to Do

### Endpoint

**`POST /api/v1/review-queue/{id}/resolve`**

Request body:
```json
{
  "action": "approve",           // "approve" | "correct" | "skip"
  "target_row": 15,             // required for "approve" and "correct"
  "target_sheet": "operating_statement",
  "notes": "This is definitely Repairs & Maintenance, not Miscellaneous"  // optional
}
```

### Actions

**approve** — CA confirms the AI's suggestion was correct
- Set review_queue.status = 'resolved'
- Set resolved_row = suggested_row (AI was right)
- Create precedent: source_term → suggested_row (reinforces AI's decision)

**correct** — CA overrides with the correct mapping
- Set review_queue.status = 'resolved'
- Set resolved_row = the CA's chosen row (different from AI's suggestion)
- Create precedent: source_term → CA's chosen row (teaches the system)
- Record that AI was wrong (useful for accuracy tracking)

**skip** — CA can't decide or item is irrelevant
- Set review_queue.status = 'skipped'
- No precedent created
- Item stays unclassified

### Resolution Logic

1. Validate review item belongs to current firm
2. Validate target_row + target_sheet is a valid CMA row
3. Update review_queue record:
   - status: 'resolved' or 'skipped'
   - resolved_by: current user ID
   - resolved_at: now
   - resolved_row: the final row number
   - resolved_sheet: the final sheet
4. If action is 'approve' or 'correct':
   - Call `create_precedent()` from task 5.3
   - Precedent scope: 'firm' (specific to this firm)
   - entity_type: from the project's client
5. Audit log the resolution

### Precedent Creation Details

```python
create_precedent(
    firm_id=current_user.firm_id,
    source_term=review_item.source_item_name,
    target_row=resolved_row,
    target_sheet=resolved_sheet,
    entity_type=client.entity_type,
    scope='firm',
    project_id=review_item.cma_project_id,
    user_id=current_user.id
)
```

### Response

```json
{
  "data": {
    "review_item_id": "uuid",
    "status": "resolved",
    "resolved_row": 15,
    "resolved_sheet": "operating_statement",
    "resolved_label": "Repairs & Maintenance",
    "precedent_created": true,
    "precedent_id": "uuid",
    "remaining_pending": 7
  }
}
```

---

## What NOT to Do

- Don't re-run the entire classification pipeline after each resolution (that's task 7.4)
- Don't create global precedents automatically (only firm-level; global = admin action)
- Don't allow resolving items from other firms
- Don't allow re-resolving already resolved items (must un-resolve first)

---

## Verification

- [ ] Approve → status becomes 'resolved', precedent created with AI's row
- [ ] Correct → status becomes 'resolved', precedent created with CA's row
- [ ] Skip → status becomes 'skipped', no precedent
- [ ] Precedent appears in classification_precedents table
- [ ] Next time same term appears → precedent matcher finds it (test manually)
- [ ] Invalid target_row → 422 error
- [ ] Already resolved item → 409 conflict
- [ ] remaining_pending count is accurate
- [ ] Audit log entry created

---

## Done → Move to task-7.3-bulk-resolve.md
