# Task 5.2: Rule Filtering Logic

> **Phase:** 05 - Classification
> **Depends on:** Task 5.1 (rules JSON loaded)
> **Agent reads:** cma-domain SKILL → Classification System, Common Indian Financial Terms
> **Time estimate:** 15 minutes

---

## Objective

Create a filtering module that narrows down the 384 rules to only the relevant ones based on the client's entity type and the document type being classified. Also implement fuzzy term matching to score how well an extracted item matches a rule.

---

## What to Do

### Create File
`backend/app/services/classification/rule_matcher.py`

### Function 1: Filter Rules

`filter_rules(entity_type: str, document_type: str) → list[ClassificationRule]`

- From 384 total rules, return only rules where:
  - `entity_type` is in the rule's `entity_types` array
  - `document_type` is in the rule's `document_types` array
- Example: entity_type="trading", document_type="profit_and_loss" → ~80-100 rules
- Example: entity_type="manufacturing", document_type="balance_sheet" → ~60-80 rules

### Function 2: Match Score

`match_item_to_rules(item_name: str, rules: list[ClassificationRule]) → list[RuleMatch]`

For each rule, calculate how well the extracted item name matches the rule's source terms:

**Matching strategies (in priority order):**

1. **Exact match (score: 1.0):** item_name exactly equals a source_term (case-insensitive)
   - "Sales" matches rule with source_term "Sales" → 1.0

2. **Normalized match (score: 0.95):** match after removing common suffixes/prefixes
   - "Sales A/c" → "Sales" matches "Sales" → 0.95
   - Remove: "A/c", "Account", "Expenses", trailing numbers

3. **Contains match (score: 0.80):** item_name contains a source_term or vice versa
   - "Income from Sales Revenue" contains "Sales" → 0.80

4. **Fuzzy match (score: 0.60-0.79):** similar but not exact
   - Use simple string similarity (Levenshtein distance or similar)
   - "Sundry Debtrs" fuzzy matches "Sundry Debtors" → 0.75
   - Threshold: only return if similarity > 0.60

5. **No match (score: 0.0):** item doesn't match any rule → candidate for AI classification

**Return type:**
```python
class RuleMatch:
    rule: ClassificationRule
    score: float          # 0.0 to 1.0
    matched_term: str     # which source_term matched
    match_type: str       # 'exact', 'normalized', 'contains', 'fuzzy'
```

Return matches sorted by score descending. Return empty list if no matches above 0.60.

### Function 3: Classify by Rules (No AI)

`classify_by_rules(item_name: str, entity_type: str, document_type: str) → RuleMatch | None`

Convenience function:
1. Filter rules by entity_type and document_type
2. Match item against filtered rules
3. Return the best match (highest score), or None if no match above threshold

### Indian Accounting Term Normalization

Create a helper that normalizes Indian accounting terms before matching:
- Remove "A/c" suffix
- "S. Debtors" → "Sundry Debtors"
- "S. Creditors" → "Sundry Creditors"
- "Dep." → "Depreciation"
- "Prov." → "Provision"
- "Misc." → "Miscellaneous"
- Strip extra whitespace, normalize case

---

## What NOT to Do

- Don't use AI/Gemini for rule matching — this is pure string matching (fast and free)
- Don't implement the full classifier yet (that's task 5.5 which combines rules + AI)
- Don't use heavy NLP libraries (no spaCy, no transformers) — simple string ops are sufficient
- Don't modify the rules JSON

---

## Verification

- [ ] `filter_rules("trading", "profit_and_loss")` → returns ~80-100 rules (not 384)
- [ ] `filter_rules("manufacturing", "balance_sheet")` → returns different subset
- [ ] Exact match: "Sales" → score 1.0, correct target row
- [ ] Normalized: "Sales A/c" → score 0.95, correct target row
- [ ] Contains: "Income from Sales Revenue" → score ~0.80
- [ ] Fuzzy: "Sundry Debtrs" → matches "Sundry Debtors" with score ~0.75
- [ ] No match: "Random Gibberish" → returns None
- [ ] Indian term normalization works: "Dep. on Plant & Machinery" → matches "Depreciation"
- [ ] Performance: matching 100 items against 80 rules takes <100ms (fast)

---

## Done → Move to task-5.3-precedent-matcher.md
