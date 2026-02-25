# Task 5.4: Design Classification Prompt Template

> **Phase:** 05 - Classification
> **Depends on:** Tasks 5.1-5.3 (rules and precedents available)
> **Agent reads:** cma-domain SKILL (entire file), reference/CMA_classification.xls
> **MCP to use:** Sequential Thinking MCP (critical prompt design)
> **Time estimate:** 25 minutes

---

## Objective

Design the prompt that tells Gemini 3 Flash how to classify financial line items into CMA template rows. This prompt is the single most important factor in classification accuracy. Spend time getting it right.

---

## What to Do

### Create File
`backend/app/services/classification/prompts.py`

### The Classification Challenge

The AI receives:
- A list of extracted financial items (name + amount)
- The relevant classification rules (filtered by entity type)
- Any existing precedents from past CA decisions
- The client's entity type

The AI must output:
- For each item: which CMA row it maps to, which sheet, and a confidence score

### Prompt Templates

**1. CLASSIFICATION_SYSTEM_PROMPT**

```
You are an expert Indian Chartered Accountant specializing in CMA (Credit Monitoring Arrangement) document preparation for bank loan applications.

Your task: Map financial line items from P&L statements and Balance Sheets to the correct rows in a standardized CMA Excel template.

Critical rules:
- Accuracy is paramount. Errors cause bank loan rejections.
- Use the provided classification rules as your primary guide.
- If precedents exist (past CA decisions), those ALWAYS override rules.
- If you're unsure about a mapping, set confidence below 0.70 — the item will be reviewed by a senior CA.
- Never guess. A low confidence that gets reviewed is better than a wrong classification.
- Output ONLY valid JSON.
```

**2. CLASSIFICATION_USER_PROMPT**

Template with placeholders:

```
Classify these financial line items for a {entity_type} entity.

## Classification Rules
These are the valid CMA rows you can map items to:
{rules_json}

## Precedents (Past CA Decisions)
These items have been classified before by a CA. ALWAYS use these mappings:
{precedents_json}

## Items to Classify
{items_json}

## Output Format
Return a JSON array with one entry per item:
{output_schema}

## Important Notes
- Each item MUST map to exactly one rule (target_row + target_sheet)
- confidence: 1.0 = certain, 0.85 = very likely, 0.70 = probable, below 0.70 = uncertain
- Items matching precedents should have confidence 0.95+
- Items with exact rule matches should have confidence 0.85+
- Items that partially match rules should have confidence 0.70-0.85
- Items you're unsure about should have confidence below 0.70
- reasoning: brief explanation of why you chose this mapping
```

**3. OUTPUT_SCHEMA**

```json
[
  {
    "item_name": "Sales",
    "item_amount": 1500000,
    "target_row": 5,
    "target_sheet": "operating_statement",
    "target_label": "Net Sales / Income from Operations",
    "confidence": 0.95,
    "reasoning": "Exact match with rule #1: Sales → Row 5 Operating Statement",
    "source": "rule",
    "matched_rule_id": 1
  },
  {
    "item_name": "Computer Repairs Expense",
    "item_amount": 25000,
    "target_row": null,
    "target_sheet": null,
    "target_label": null,
    "confidence": 0.45,
    "reasoning": "No exact rule match. Could be Repairs & Maintenance or Miscellaneous Expenses. Needs CA review.",
    "source": "ai_uncertain",
    "matched_rule_id": null
  }
]
```

**4. BATCH_CLASSIFICATION_PROMPT**

For projects with many items (>30), split into batches:
- Batch size: 15-20 items per API call
- Each batch gets the same rules and precedents context
- This prevents hitting Gemini's output token limits
- Include a note: "This is batch {n} of {total}. Previously classified items: {summary}"

### Prompt Optimization Principles

1. **Rules as structured reference, not wall of text:** Format rules as a compact table, not verbose descriptions
2. **Precedents first, rules second:** Prompt says "check precedents first, then rules"
3. **Few-shot example included:** One complete example of 5 items being classified
4. **Confidence calibration:** Explicitly define what each confidence level means
5. **Force JSON mode:** Use `response_format="json"` in Gemini call
6. **Temperature 0.1:** Mostly deterministic, tiny bit of flexibility for ambiguous items

### Context Window Management

Calculate and document token budgets:
- System prompt: ~300 tokens
- Rules (filtered): ~2000-4000 tokens (depends on entity type)
- Precedents: ~500-1500 tokens (grows over time)
- Items batch: ~500-1000 tokens (15-20 items)
- Output schema + examples: ~500 tokens
- **Total per call: ~4000-7000 tokens** (well within Gemini 3 Flash's 1M context)

---

## What NOT to Do

- Don't include ALL 384 rules — only filtered ones for the entity type
- Don't send all items at once if >30 (batch them)
- Don't use Gemini 2.0 Flash for classification (3 Flash is better for reasoning)
- Don't include actual financial amounts in the rules section (only item names and mappings)
- Don't make the prompt so long it wastes tokens — be compact

---

## Verification

- [ ] CLASSIFICATION_SYSTEM_PROMPT is clear, authoritative, under 400 tokens
- [ ] CLASSIFICATION_USER_PROMPT has all placeholders: entity_type, rules_json, precedents_json, items_json, output_schema
- [ ] Output schema example shows both confident and uncertain items
- [ ] Few-shot example is correct and realistic
- [ ] Test: manually call Gemini with the prompt + 5 sample items → output matches schema
- [ ] Test: item with existing precedent → confidence 0.95+
- [ ] Test: item with exact rule match → confidence 0.85+
- [ ] Test: ambiguous item → confidence below 0.70
- [ ] Batch prompt correctly references previous batches
- [ ] All prompts stored as string constants with clear variable names

---

## Done → Move to task-5.5-classifier-module.md
