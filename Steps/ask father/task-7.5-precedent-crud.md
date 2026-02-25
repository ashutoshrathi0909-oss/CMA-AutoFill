# Task 7.5: Precedent Management Endpoints

> **Phase:** 07 - Ask Father
> **Depends on:** Task 7.2 (precedents being created from reviews)
> **Time estimate:** 10 minutes

---

## Objective

Create endpoints for CAs to view, edit, and delete their firm's classification precedents. This gives the CA control over the learning loop.

---

## What to Do

### Create File
`backend/app/api/v1/endpoints/precedents.py`

### Endpoints

**`GET /api/v1/precedents`**
List all precedents for current firm.
- `?entity_type=trading` — filter by entity type
- `?search=sales` — search by source_term
- `?page=1&per_page=50`

Response includes: source_term, target_row, target_sheet, target_label, entity_type, scope, created_by, created_at, usage_count (how many times this precedent was used in classification)

**`GET /api/v1/precedents/{id}`**
Single precedent details + history (which projects used it).

**`PUT /api/v1/precedents/{id}`**
Update a precedent's mapping (CA realized it should go to a different row).
- Only update target_row, target_sheet, notes
- Log the change in audit_log

**`DELETE /api/v1/precedents/{id}`**
Delete a precedent. The system will fall back to rules + AI for this term next time.
- Soft delete (set is_active=false)
- Existing classifications aren't affected — only future ones

**`POST /api/v1/precedents/promote`**
Promote a firm-level precedent to global (admin-only, for future multi-firm use).
- Request: `{"precedent_id": "uuid", "scope": "global"}`
- Requires role: 'owner'

---

## What NOT to Do

- Don't allow editing global precedents from firm endpoints
- Don't auto-propagate changes to past projects (precedent changes are forward-looking)
- Don't expose other firms' precedents

---

## Verification

- [ ] List shows all firm precedents with correct details
- [ ] Search by term works
- [ ] Update changes the mapping, audit logged
- [ ] Delete soft-deletes, precedent no longer returned in list
- [ ] Deleted precedent → future classification falls back to rules/AI
- [ ] usage_count tracks how many times precedent was applied

---

## Done → Move to task-7.6-learning-metrics.md
