# Phase 07: Ask Father — Review Queue & Learning Loop

> Complete these 7 tasks in order. Each task = one Claude Code agent session.
> This phase builds the review interface where senior CAs correct AI classifications.
> Every correction becomes a precedent — the system gets smarter over time.

| # | File | What It Does | Verify By |
|---|------|-------------|-----------|
| 7.1 | task-7.1-review-list-endpoint.md | GET review queue items with filters | List shows pending items |
| 7.2 | task-7.2-resolve-endpoint.md | CA approves/corrects a review item | Item resolved, precedent created |
| 7.3 | task-7.3-bulk-resolve.md | Approve/reject multiple items at once | 5 items resolved in 1 call |
| 7.4 | task-7.4-reclassify-after-review.md | Apply CA decisions back to classification data | Classification data updated |
| 7.5 | task-7.5-precedent-crud.md | View, edit, delete precedents | Precedent list works |
| 7.6 | task-7.6-learning-metrics.md | Track how precedents improve accuracy over time | Metrics endpoint returns data |
| 7.7 | task-7.7-review-notifications.md | Email notification when items need review | Resend email sent |

**Phase 07 result:** CAs can review AI decisions, correct mistakes, and the system learns from every correction.
