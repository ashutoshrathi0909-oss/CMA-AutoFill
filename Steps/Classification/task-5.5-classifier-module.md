# Task 5.5: Core Classifier Module

> **Phase:** 05 - Classification
> **Depends on:** Tasks 5.1-5.4 (rules, rule matcher, precedents, prompts all ready)
> **Agent reads:** cma-domain SKILL, CLAUDE.md → Tech Stack (LLM section)
> **MCP to use:** Sequential Thinking MCP (complex orchestration logic)
> **Time estimate:** 25 minutes

---

## Objective

Create the core classification engine that combines rule matching, precedent lookup, and Gemini 3 Flash AI into a three-tier classification pipeline. This is the heart of the product.

---

## What to Do

### Create File
`backend/app/services/classification/classifier.py`

### Three-Tier Classification Pipeline

For each extracted line item, try classification in this order:

```
Tier 1: Precedent Match (free, instant, CA-verified)
   ↓ no match?
Tier 2: Rule Match (free, instant, pattern-based)
   ↓ no match or low score?
Tier 3: AI Classification (Gemini 3 Flash, costs tokens)
```

### Tier 1: Precedent Match
- Call `get_best_precedent(firm_id, item_name, entity_type)` from task 5.3
- If match with score >= 0.80 → CLASSIFIED
  - confidence = precedent score (0.80-1.0)
  - source = "precedent"
  - No AI call needed — free and instant

### Tier 2: Rule Match
- Call `classify_by_rules(item_name, entity_type, document_type)` from task 5.2
- If match with score >= 0.85 → CLASSIFIED
  - confidence = rule score (0.85-1.0)
  - source = "rule"
  - No AI call needed — free and instant
- If match with score 0.60-0.84 → mark as "rule_suggested" but still send to AI for confirmation

### Tier 3: AI Classification (Gemini 3 Flash)
- Collect all items that weren't classified by Tier 1 or Tier 2
- Include "rule_suggested" items for AI confirmation
- Batch items (15-20 per API call)
- Call Gemini 3 Flash with classification prompt from task 5.4
- Parse response, extract classifications
- Log LLM usage

### Classification Result

```python
class ClassifiedItem:
    item_name: str
    item_amount: float
    target_row: int | None
    target_sheet: str | None
    target_label: str | None
    confidence: float           # 0.0 to 1.0
    source: str                 # 'precedent', 'rule', 'ai', 'ai_confirmed_rule', 'unclassified'
    matched_rule_id: int | None
    matched_precedent_id: UUID | None
    reasoning: str              # why this classification was chosen
    needs_review: bool          # True if confidence < 0.70
```

### Main Function

`classify_project(project_id: UUID, firm_id: UUID) → ClassificationResult`

1. Load project's `extracted_data` from database
2. Get client's `entity_type`
3. For each line item across P&L and BS:
   a. Try Tier 1 (precedent)
   b. Try Tier 2 (rule)
   c. Collect unmatched for Tier 3
4. Batch-call Gemini 3 Flash for Tier 3 items
5. Merge all results
6. Return summary:

```python
class ClassificationResult:
    total_items: int
    classified_by_precedent: int
    classified_by_rule: int
    classified_by_ai: int
    unclassified: int           # confidence < 0.30
    needs_review: int           # confidence 0.30-0.69
    auto_classified: int        # confidence >= 0.70
    average_confidence: float
    items: list[ClassifiedItem]
    llm_cost_usd: float
    llm_tokens_used: int
```

### Fallback Handling

- If Gemini 3 Flash fails (API error, timeout) → retry once
- If retry fails → try Gemini 3.1 Pro as fallback (better but more expensive)
- If all AI fails → mark remaining items as "unclassified" with confidence 0.0, needs_review = True
- Never crash the pipeline — always return partial results

### Confidence Thresholds

| Confidence | Action | Source |
|-----------|--------|--------|
| >= 0.85 | Auto-classify, no review needed | Any tier |
| 0.70 - 0.84 | Auto-classify, but flag for optional review | Any tier |
| 0.30 - 0.69 | Send to review queue (Ask Father) | Mostly AI |
| < 0.30 | Unclassified — definitely needs manual review | AI uncertain |

---

## What NOT to Do

- Don't call Gemini for items that matched a precedent — waste of money
- Don't use Gemini 2.0 Flash for classification (use 3 Flash — better reasoning)
- Don't send more than 20 items per AI batch
- Don't skip Tier 1 and 2 — they're free and faster
- Don't modify extracted data — classification is a separate layer
- Don't write to the review queue yet (that's task 5.6)
- Don't generate the CMA Excel (that's Phase 06)

---

## Verification

- [ ] Item with existing precedent → classified by Tier 1, no AI call
- [ ] Item with exact rule match → classified by Tier 2, no AI call
- [ ] Ambiguous item → classified by Tier 3 (Gemini), LLM usage logged
- [ ] AI failure → fallback to 3.1 Pro → if that fails too → unclassified
- [ ] Batch of 40 items → split into 2 AI calls of 20
- [ ] `ClassificationResult` has correct counts per tier
- [ ] Items with confidence < 0.70 → needs_review = True
- [ ] Mehta Computers test: run classification → compare against known correct mappings → >70% accuracy
- [ ] Total LLM cost for Mehta Computers classification < $0.01

---

## Done → Move to task-5.6-review-queue.md
