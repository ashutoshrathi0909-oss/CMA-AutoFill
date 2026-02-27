# Phase 05: Classification — Overview

> Complete these 7 tasks in order. Each task = one Claude Code agent session.
> This is the BRAIN of the product — maps extracted items to CMA template rows.
> Use Sequential Thinking MCP for tasks 5.4 and 5.5 (complex AI logic).

| # | File | What It Does | Verify By |
|---|------|-------------|-----------|
| 5.1 | task-5.1-rules-json.md | Convert CMA_classification.xls → classification_rules.json | JSON has all 384 rules |
| 5.2 | task-5.2-rule-filter.md | Filter rules by entity type + document type | Trading firm gets ~80 rules, not 384 |
| 5.3 | task-5.3-precedent-matcher.md | Find similar past CA decisions | Query returns relevant precedents |
| 5.4 | task-5.4-classification-prompt.md | Design the classification prompt template | Prompt produces correct JSON |
| 5.5 | task-5.5-classifier-module.md | Core classifier (rules + precedents + Gemini 3 Flash) | Mehta items get correct row numbers |
| 5.6 | task-5.6-review-queue.md | Low confidence items → review_queue table | Items <70% confidence in queue |
| 5.7 | task-5.7-classification-endpoint.md | POST /projects/{id}/classify + accuracy test | Compare vs reference, measure % |

**Phase 05 result:** Extracted items are mapped to CMA rows. High confidence = auto-classified. Low confidence = sent to Ask Father queue.
