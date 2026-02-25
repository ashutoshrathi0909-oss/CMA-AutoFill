# Task 7.1: Review Queue List Endpoint

> **Phase:** 07 - Ask Father
> **Depends on:** Phase 05 Task 5.6 (review_queue table populated)
> **Agent reads:** CLAUDE.md → Database Tables → review_queue
> **Time estimate:** 15 minutes

---

## Objective

Create API endpoints to list and filter review queue items so the CA can see what needs their attention.

---

## What to Do

### Create File
`backend/app/api/v1/endpoints/review.py`

### Endpoints

**`GET /api/v1/review-queue`**

List all pending review items for the current firm.

Query parameters:
- `?status=pending` (default) / `resolved` / `skipped` / `all`
- `?project_id=uuid` — filter to specific project
- `?sort_by=confidence` — sort by confidence ascending (most uncertain first)
- `?sort_by=created_at` — sort by date
- `?page=1&per_page=20`

Response:
```json
{
  "data": {
    "items": [
      {
        "id": "uuid",
        "source_item_name": "Computer Repairs Expense",
        "source_item_amount": 25000,
        "suggested_row": 22,
        "suggested_sheet": "operating_statement",
        "suggested_label": "Miscellaneous Expenses",
        "confidence": 0.45,
        "reasoning": "No exact rule match. Could be Repairs or Miscellaneous.",
        "alternative_suggestions": [
          {"row": 15, "sheet": "operating_statement", "label": "Repairs & Maintenance", "score": 0.55},
          {"row": 22, "sheet": "operating_statement", "label": "Miscellaneous Expenses", "score": 0.40}
        ],
        "project_name": "Mehta Computers 2024-25",
        "client_name": "Mehta Computers",
        "status": "pending",
        "created_at": "2026-02-25T10:30:00Z"
      }
    ],
    "total": 10,
    "page": 1,
    "per_page": 20,
    "summary": {
      "pending": 8,
      "resolved": 15,
      "skipped": 2
    }
  }
}
```

**`GET /api/v1/review-queue/{id}`**

Get single review item with full context:
- The item details (name, amount, AI suggestion)
- All alternative suggestions with scores
- The AI's reasoning
- The project and client context
- Available CMA rows for manual selection (grouped by sheet)

### Available Rows Endpoint

**`GET /api/v1/cma-rows`**

Returns all valid CMA template rows grouped by sheet, for the CA to pick from when manually classifying:

```json
{
  "data": {
    "operating_statement": [
      {"row": 5, "label": "Net Sales / Income from Operations"},
      {"row": 10, "label": "Cost of Goods Sold - Purchases"},
      ...
    ],
    "balance_sheet": [
      {"row": 3, "label": "Gross Block - Fixed Assets"},
      ...
    ]
  }
}
```

Filter by entity_type: `?entity_type=trading`

---

## What NOT to Do

- Don't create resolve/update logic (that's task 7.2)
- Don't expose review items from other firms
- Don't show resolved items by default (only pending)

---

## Verification

- [ ] GET review-queue → returns pending items sorted by confidence
- [ ] Filter by project_id → shows only that project's items
- [ ] Filter by status=resolved → shows resolved items
- [ ] Summary counts are correct
- [ ] GET single item → includes alternatives and reasoning
- [ ] GET cma-rows → returns all valid rows grouped by sheet
- [ ] Auth required, firm-scoped

---

## Done → Move to task-7.2-resolve-endpoint.md
