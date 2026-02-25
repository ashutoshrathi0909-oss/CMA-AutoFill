# Task 7.6: Learning Loop Metrics

> **Phase:** 07 - Ask Father
> **Depends on:** Tasks 7.2-7.5 (review resolutions and precedents working)
> **Time estimate:** 15 minutes

---

## Objective

Track and expose metrics showing how the system improves over time as CAs create more precedents. This data proves the learning loop works and helps justify the product's value.

---

## What to Do

### Create File
`backend/app/services/metrics/learning_metrics.py`

### Endpoint

**`GET /api/v1/metrics/learning`**

Response:
```json
{
  "data": {
    "total_precedents": 45,
    "this_month_precedents": 8,
    "classification_accuracy_trend": [
      {"month": "2026-01", "accuracy": 0.73, "projects": 2},
      {"month": "2026-02", "accuracy": 0.81, "projects": 3}
    ],
    "classification_source_breakdown": {
      "by_precedent": 120,
      "by_rule": 340,
      "by_ai": 85,
      "ca_reviewed": 45
    },
    "ai_override_rate": 0.18,
    "top_corrected_items": [
      {"term": "Computer Repairs", "times_corrected": 3, "final_mapping": "Repairs & Maintenance"},
      {"term": "Telephone Charges", "times_corrected": 2, "final_mapping": "Communication Expenses"}
    ],
    "review_turnaround": {
      "avg_hours": 4.5,
      "median_hours": 2.0
    },
    "cost_savings": {
      "ai_calls_avoided_by_precedents": 120,
      "estimated_savings_usd": 0.12
    }
  }
}
```

### Metrics Calculated

1. **Accuracy trend:** For each completed project, compare AI's initial classification vs CA's final decisions. Track monthly.
2. **Source breakdown:** How many items classified by each tier (precedent vs rule vs AI vs CA review)
3. **AI override rate:** % of AI classifications that CAs corrected (lower = AI is getting better)
4. **Top corrected items:** Most frequently corrected terms — candidates for new rules
5. **Review turnaround:** How fast CAs resolve review items
6. **Cost savings:** Precedent matches avoid AI API calls — track how much money saved

### Data Sources

- `review_queue` table: resolutions, timing
- `classification_precedents` table: precedent count, usage
- `cma_projects.classification_data`: per-project accuracy
- `llm_usage_log`: API costs

---

## What NOT to Do

- Don't create complex analytics dashboards (V1 = API endpoint, frontend in Phase 10)
- Don't compute metrics on every request — cache for 1 hour
- Don't expose cross-firm metrics (each firm sees only their own)

---

## Verification

- [ ] Endpoint returns all metric fields
- [ ] Accuracy trend shows improvement when precedents are added
- [ ] Source breakdown counts match actual data
- [ ] After creating 5 precedents → "ai_calls_avoided" increases on next project
- [ ] Cached response (second call within 1 hour is fast)

---

## Done → Move to task-7.7-review-notifications.md
