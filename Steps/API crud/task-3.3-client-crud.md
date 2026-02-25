# Task 3.3: Client CRUD Endpoints

> **Phase:** 03 - API CRUD Endpoints
> **Depends on:** Task 3.1 (auth), Task 3.2 (router structure, response format)
> **Agent reads:** CLAUDE.md → API Design Patterns, Database Tables → clients
> **Time estimate:** 15 minutes

---

## Objective

Create full CRUD endpoints for managing clients (the businesses that need CMAs).

---

## What to Do

### Create Files
- `backend/app/api/v1/endpoints/clients.py` — route handlers
- `backend/app/models/client.py` — Pydantic request/response models

### Pydantic Models

**ClientCreate (request body):**
- name: str (required)
- entity_type: str (required, must be 'trading' | 'manufacturing' | 'service')
- pan_number: str | None
- gst_number: str | None
- contact_person: str | None
- contact_email: str | None
- contact_phone: str | None
- address: str | None

**ClientUpdate (request body):**
- All fields optional (only provided fields are updated)

**ClientResponse (response):**
- All fields from the table + id, created_at, updated_at
- cma_count: int (number of CMA projects for this client — computed via COUNT query)

**ClientListResponse (response):**
- items: list[ClientResponse]
- total: int (total matching clients, for pagination)
- page: int
- per_page: int

### Endpoints

| Method | Path | What It Does |
|--------|------|-------------|
| POST | `/api/v1/clients` | Create a new client |
| GET | `/api/v1/clients` | List clients for current firm |
| GET | `/api/v1/clients/{id}` | Get single client details |
| PUT | `/api/v1/clients/{id}` | Update client info |
| DELETE | `/api/v1/clients/{id}` | Soft delete (set is_active=false) |

### Business Rules

- `firm_id` is ALWAYS set from `current_user.firm_id` — never from request body
- List endpoint supports:
  - Pagination: `?page=1&per_page=20` (default 20, max 100)
  - Search: `?search=mehta` (searches by name, case-insensitive)
  - Filter: `?entity_type=trading`
  - Sort: `?sort_by=name&sort_order=asc` (default: created_at desc)
- Only active clients are returned by default. Add `?include_inactive=true` to see all.
- Soft delete: sets `is_active=false`, does NOT delete the row
- Cannot update a client that belongs to a different firm → 404 (not 403, to avoid leaking existence)
- Validate entity_type on create/update — reject invalid values with clear error message

### Audit Logging

After each create/update/delete, insert a row into `audit_log`:
- action: 'create_client' / 'update_client' / 'delete_client'
- entity_type: 'client'
- entity_id: the client's UUID
- metadata: `{"client_name": "Mehta Computers"}` (no sensitive data)

---

## What NOT to Do

- Don't create nested endpoints (like /clients/{id}/projects — that's in task 3.4)
- Don't hard-delete rows — always soft delete
- Don't return clients from other firms even if queried by ID
- Don't skip pagination — even if there are few clients now, it matters at scale

---

## Verification

- [ ] POST `/api/v1/clients` with valid data → 201 Created, returns new client
- [ ] POST with invalid entity_type → 422 with clear error
- [ ] POST without auth → 401
- [ ] GET `/api/v1/clients` → returns list with pagination info
- [ ] GET with `?search=meh` → returns Mehta Computers
- [ ] GET with `?entity_type=trading` → filters correctly
- [ ] GET `/api/v1/clients/{id}` → returns single client with cma_count
- [ ] GET with non-existent ID → 404
- [ ] GET with ID from another firm → 404 (not 403)
- [ ] PUT `/api/v1/clients/{id}` → updates fields, updated_at changes
- [ ] DELETE `/api/v1/clients/{id}` → sets is_active=false, client gone from default list
- [ ] Audit log has entries for all operations
- [ ] All responses follow `{"data": ..., "error": null}` format

---

## Done → Move to task-3.4-project-crud.md
