# Task 5.6: Populate Review Queue (Ask Father)

> **Phase:** 05 - Classification
> **Depends on:** Task 5.5 (classifier returns items with needs_review flag)
> **Agent reads:** CLAUDE.md → Database Tables → review_queue
> **Time estimate:** 10 minutes

---

## Objective

After classification, items with low confidence are inserted into the `review_queue` table for a senior CA to review. This is the "Ask Father" feature — the learning loop that makes the system smarter over time.

---

## What to Do

### Create File
`backend/app/services/classification/review_service.py`

### Function: Populate Review Queue

`populate_review_queue(project_id: UUID, firm_id: UUID, classified_items: list[ClassifiedItem]) → int`

1. Filter items where `needs_review = True` (confidence < 0.70)
2. For each item, insert into `review_queue`:

```
review_queue row:
  - firm_id: from project
  - cma_project_id: the project
  - source_item_name: the extracted item name
  - source_item_amount: the amount
  - suggested_row: the AI's best guess (target_row from classification)
  - suggested_sheet: AI's suggested sheet
  - suggested_label: AI's suggested label
  - confidence: the AI's confidence score
  - reasoning: the AI's explanation for why it's unsure
  - status: 'pending'
  - source: 'ai' or 'rule_low_confidence'
  - alternative_suggestions: JSON array of top 3 possible mappings
```

3. Return count of items added to queue

### Function: Get Alternative Suggestions

For each review queue item, provide the CA with up to 3 possible mappings:

`get_alternatives(item_name: str, entity_type: str) → list[dict]`

- Get top 3 rule matches (even low-score ones)
- Return as JSON array:
```json
[
  {"row": 15, "sheet": "operating_statement", "label": "Repairs & Maintenance", "score": 0.55},
  {"row": 22, "sheet": "operating_statement", "label": "Miscellaneous Expenses", "score": 0.40},
  {"row": 18, "sheet": "operating_statement", "label": "Administrative Expenses", "score": 0.35}
]
```

This helps the CA make a quick decision — they pick from suggestions rather than searching through 289 rows.

### Function: Review Queue Summary

`get_review_summary(project_id: UUID) → ReviewSummary`

Returns:
```python
class ReviewSummary:
    total_pending: int
    total_resolved: int
    total_skipped: int
    avg_confidence: float       # of pending items
    items_by_confidence: dict   # {"0.50-0.69": 5, "0.30-0.49": 3, "<0.30": 2}
```

---

## What NOT to Do

- Don't create the UI for reviewing items (that's Phase 07)
- Don't create the resolution logic (CA approving/correcting — Phase 07)
- Don't add items with confidence >= 0.70 to the queue
- Don't duplicate items if classification is re-run (upsert by project_id + source_item_name)

---

## Verification

- [ ] Classification with 5 low-confidence items → 5 rows in review_queue
- [ ] Each row has suggested_row, confidence, reasoning
- [ ] alternative_suggestions has 2-3 options per item
- [ ] Items with confidence >= 0.70 → NOT in review queue
- [ ] `get_review_summary()` returns correct counts
- [ ] Re-running classification → updates existing queue items (no duplicates)
- [ ] Queue items linked to correct project and firm

---

## Done → Move to task-5.7-classification-endpoint.md
