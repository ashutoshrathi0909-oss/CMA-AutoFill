# Task 5.3: Precedent Matching Service

> **Phase:** 05 - Classification
> **Depends on:** Phase 02 Task 2.4 (classification_precedents table exists)
> **Agent reads:** cma-domain SKILL → Precedent System
> **Time estimate:** 10 minutes

---

## Objective

Create a service that checks if a CA has previously classified a similar item. Precedents override rules — if a CA has manually decided where "Computer Sales" goes, we use that decision for all future occurrences, not the AI.

---

## What to Do

### Create File
`backend/app/services/classification/precedent_matcher.py`

### Function 1: Find Precedents

`find_precedents(firm_id: UUID, source_term: str, entity_type: str) → list[Precedent]`

Query `classification_precedents` table for matches:

**Search order (priority):**

1. **Exact firm + exact term + exact entity_type** (score: 1.0)
   - "Computer Sales" for trading firm in this specific firm
   - Most specific match — always wins

2. **Exact firm + exact term + any entity_type** (score: 0.95)
   - "Computer Sales" in this firm, regardless of entity type

3. **Global + exact term + exact entity_type** (score: 0.90)
   - "Computer Sales" as a global precedent for trading firms
   - Global = firm_id IS NULL, scope = 'global'

4. **Exact firm + fuzzy term + exact entity_type** (score: 0.80)
   - "Comp. Sales" fuzzy matches "Computer Sales" in this firm
   - Use same normalization as task 5.2

5. **Global + fuzzy term** (score: 0.70)
   - Broadest match

Return matches sorted by score. Return empty list if no matches.

### Function 2: Apply Precedent

`get_best_precedent(firm_id: UUID, source_term: str, entity_type: str) → PrecedentMatch | None`

Convenience function:
1. Call `find_precedents()`
2. Return the highest-scoring match, or None if no matches
3. Return type includes: target_row, target_sheet, confidence, source (which precedent matched)

```python
class PrecedentMatch:
    precedent_id: UUID
    target_row: int
    target_sheet: str
    confidence: float     # the match score (0.70 - 1.0)
    source_term: str      # the original term from the precedent
    scope: str            # 'firm' or 'global'
    match_type: str       # 'exact' or 'fuzzy'
```

### Function 3: Create Precedent

`create_precedent(firm_id, source_term, target_row, target_sheet, entity_type, scope, project_id, user_id) → Precedent`

- Called when a CA resolves a review queue item (Phase 07)
- Handles the UNIQUE constraint: if precedent already exists for this firm+term+entity, UPDATE it instead of INSERT
- Returns the created/updated precedent

---

## What NOT to Do

- Don't create the review queue resolution logic (that's Phase 07)
- Don't call the Gemini API — precedent matching is database queries only
- Don't create precedents automatically — only CAs create them through the review queue
- Don't implement bulk precedent operations

---

## Verification

- [ ] With no precedents in DB → `get_best_precedent()` returns None
- [ ] Insert a test precedent for "Sales" → query "Sales" → returns it with score 1.0
- [ ] Insert a firm-level precedent → only that firm finds it
- [ ] Insert a global precedent → all firms find it
- [ ] Firm-level precedent wins over global for same term (higher score)
- [ ] Fuzzy match: precedent for "Sundry Debtors" found when querying "S. Debtors"
- [ ] `create_precedent()` handles duplicate gracefully (upsert)
- [ ] Clean up test data after verification

---

## Done → Move to task-5.4-classification-prompt.md
