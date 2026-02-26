# Phase 03 (Part 2) — API CRUD Endpoints: Agent Handoff Prompt

**To the AI Agent taking over this task:**
Please read this entire document carefully. It contains the full context of the "CMA AutoFill" project, what has been completed so far, and your specific instructions for finishing Phase 03.

---

## 1. Project Overview: CMA AutoFill
CMA AutoFill is a SaaS product designed to automate the creation of Credit Monitoring Arrangement (CMA) documents for Indian CA firms. It reduces manual work from 3-4 hours to under 5 minutes per client.
- **Tech Stack:**
  - **Frontend:** Next.js 15 (App Router), TypeScript, Tailwind CSS
  - **Backend:** FastAPI (Python 3.12)
  - **Database & Auth:** Supabase (PostgreSQL + Auth + Storage)
  - **AI:** Gemini 2.0 Flash (via `google-generativeai`)
- **Key Architecture:** Multi-tenant SaaS where data isolation relies heavily on the `firm_id` via Row Level Security (RLS) policies in Supabase.

---

## 2. What Has Been Completed So Far
You are stepping in midway through **Phase 03**. Here is what is already built and working:

**Phase 01:**
- Project initialized. FastAPI running on `:8000`, Next.js on `:3000`.
- Supabase SDKs (`supabase==2.10.0`, `gotrue==2.10.0`) are installed and functional.

**Phase 02 (Database & Auth):**
- All PostgreSQL tables (`firms`, `users`, `clients`, `cma_projects`, `uploaded_files`, `generated_files`, `review_queue`, etc.) are created.
- Auth triggers are running: when a user signs up via Supabase Auth, they are automatically added to the `users` and `firms` tables.
- Row Level Security (RLS) is strictly enforced on all tables based on the user's `firm_id`.

**Phase 03 (Part 1) — ALREADY DONE:**
- **Task 3.1 (Auth Middleware):** Located in `backend/app/core/auth.py`. We have a working `get_current_user` dependency that uses `PyJWT` to verify the Supabase token and fetch the user's `CurrentUser` object (which includes `id`, `firm_id`, `email`, `role`).
- **Task 3.2 (Health & `/me`):** Located in `backend/app/api/v1/endpoints/health.py` and `auth.py`. 
- **Standard Response Model:** Located in `backend/app/models/response.py`. All API outputs must use the `StandardResponse[T]` format: `{"data": ..., "error": null}`.
- **API Router Setup:** `backend/app/api/v1/router.py` is configured and attached to `/api/v1` in `main.py`.

---

## 3. Your Mission: Complete Phase 03 (Tasks 3.3 to 3.7)

Your objective is to build out the remaining CRUD operations. All endpoints must be secured using the `get_current_user` dependency and return data using the `StandardResponse` model.

**Important Note on DB Queries:** 
Because Supabase RLS is enabled, you **MUST** pass the user's JWT token to the Supabase client when making calls on their behalf, OR manually filter by `eq('firm_id', current_user.firm_id)` if using the service role key. Currently, `get_supabase()` in our code uses the service role key, so **you must explicitly include `.eq("firm_id", current_user.firm_id)` in all queries to securely isolate tenant data**.

Here are your specific tasks:

### Task 3.3: Client CRUD (`backend/app/api/v1/endpoints/clients.py`)
- Create Pydantic models for `ClientCreate` and `ClientUpdate`.
- **POST `/api/v1/clients`**: Create a new client. Explicitly set `firm_id = current_user.firm_id`.
- **GET `/api/v1/clients`**: List all clients for the firm.
- **GET `/api/v1/clients/{id}`**: Get a specific client.
- **PUT `/api/v1/clients/{id}`**: Update a client.
- **DELETE `/api/v1/clients/{id}`**: Delete a client (or deactivate them).

### Task 3.4: CMA Project CRUD (`backend/app/api/v1/endpoints/projects.py`)
- Pydantic models: `ProjectCreate`, `ProjectUpdate`.
- **POST `/api/v1/projects`**: Create a new CMA project. Ensure it links to a valid `client_id` belonging to the firm.
- **GET `/api/v1/projects`**: List all projects for the firm (can accept `client_id` as a query param filter).
- **GET `/api/v1/projects/{id}`**: Get specific project details.
- **PUT `/api/v1/projects/{id}`**: Update project fields (status, bank_name, etc.).

### Task 3.5: File Upload (`backend/app/api/v1/endpoints/files.py`)
- **POST `/api/v1/files/upload`**: Use FastAPI's `UploadFile`.
- Logic:
  1. Validate the file extension (PDF, Excel, images).
  2. Upload the file binary to the Supabase Storage bucket `cma-files`. The path should be `{firm_id}/{project_id}/{filename}`.
  3. Insert a record into the `uploaded_files` table mapping the DB record to the storage path.

### Task 3.6: File Download/List
- **GET `/api/v1/files`**: List all files associated with a specific `project_id`.
- **GET `/api/v1/files/{file_id}/download`**: Generate and return a signed URL from Supabase Storage for the client to download/view the file securely.

### Task 3.7: Dashboard Stats (`backend/app/api/v1/endpoints/dashboard.py`)
- **GET `/api/v1/dashboard/stats`**: Return a summary for the current user's firm.
- Calculate: Total Active Clients, Total CMA Projects, Projects by Status (Draft vs Completed), and the Most Recent Projects.

---

## 4. Strict Rules & Architecture Standards To Follow

1. **Auto-Debug Rule:** If you encounter a Python error, use the provided `debug.ps1` script to test things. If FastAPI crashes, auto-fix it immediately.
2. **Never hardcode LLM models:** Use `os.getenv("LLM_CLASSIFICATION_MODEL")` for any AI calls (not needed much in Phase 03, but keep in mind).
3. **Pydantic Validation:** Always use Pydantic models for incoming request bodies to guarantee type safety.
4. **Error Handling:** Use `HTTPException` with proper status codes (400, 403, 404, 500) so the standard response wrapper works effectively.
5. **No Frontend Code:** Do not write anything in the `/frontend` directory. This task is strictly backend API.
6. **Register Routers:** Remember to bind every new router (clients, projects, files, dashboard) inside `backend/app/api/v1/router.py`.

**Once you have successfully built and verified Tasks 3.3 through 3.7 locally via the Swagger docs (`http://127.0.0.1:8000/docs`), report completion and use the `/auto-commit` workflow.**
