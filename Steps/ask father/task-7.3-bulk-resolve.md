# Task 7.3: Bulk Resolve Endpoint

> **Phase:** 07 - Ask Father
> **Depends on:** Task 7.2 (single resolve works)
> **Time estimate:** 10 minutes

---

## Objective

Allow CAs to resolve multiple review items at once — especially useful when approving several AI suggestions that look correct.

---

## What to Do

### Endpoint

**`POST /api/v1/review-queue/bulk-resolve`**

Request body:
```json
{
  "resolutions": [
    {"id": "uuid1", "action": "approve"},
    {"id": "uuid2", "action": "approve"},
    {"id": "uuid3", "action": "correct", "target_row": 15, "target_sheet": "operating_statement"},
    {"id": "uuid4", "action": "skip"}
  ]
}
```

### Logic

1. Validate all items belong to current firm
2. Validate all items are in 'pending' status
3. Process each resolution using the same logic as task 7.2
4. Create precedents for each approve/correct
5. Return summary

### Response

```json
{
  "data": {
    "total": 4,
    "resolved": 3,
    "skipped": 1,
    "precedents_created": 3,
    "remaining_pending": 4,
    "errors": []
  }
}
```

### Convenience Endpoint

**`POST /api/v1/review-queue/approve-all`**

Approve ALL pending items for a project that have confidence >= 0.50 (AI's suggestion is "probably right"):

Request body:
```json
{
  "project_id": "uuid",
  "min_confidence": 0.50    // only approve items above this threshold
}
```

This is a power-user shortcut — CA trusts AI for items that were "close" but below the auto-classify threshold.

---

## What NOT to Do

- Don't process items from other firms
- Don't auto-approve items below 0.30 confidence (too risky)
- Don't skip error handling — if one item fails, continue with rest

---

## Verification

- [ ] Bulk resolve 5 items → all resolved, 5 precedents created
- [ ] One invalid item in batch → that one errors, rest succeed
- [ ] Approve-all with min_confidence=0.50 → only items ≥0.50 approved
- [ ] remaining_pending count is accurate after bulk operation

---

## Done → Move to task-7.4-reclassify-after-review.md
