# PHASE 01: Project Initialization

> **Purpose:** Create the project skeleton — repo structure, frontend scaffold, backend scaffold, first deploy.
> **Prerequisites:** ALL items in PHASE-00 checklist must be complete.
> **Agent context:** Read CLAUDE.md before starting. Read cma-domain SKILL.md for domain understanding.
> **Result:** A live URL on Vercel showing a "Hello CMA AutoFill" page, with backend health check working.

---

## What This Phase Does

We create the empty project structure that every future phase builds on. Think of it as laying the foundation of a house — no rooms yet, just the slab and walls.

After this phase:
- GitHub repo has proper folder structure
- Next.js frontend runs locally and is deployed to Vercel
- FastAPI backend runs locally
- Environment variables are configured
- Both frontend and backend can connect to Supabase (but no tables yet)

---

## Task 1.1: Create Project Folder Structure

**What to do:**
Create the folder structure as defined in CLAUDE.md under "Project Structure". Create empty placeholder files where needed so the structure is visible in VS Code.

**Input:** CLAUDE.md project structure section

**Verification:**
- Open the project in VS Code → folder tree matches CLAUDE.md structure
- `frontend/`, `backend/`, `reference/`, `.claude/` folders all exist
- `.gitignore` includes: `.env`, `.env.local`, `node_modules/`, `__pycache__/`, `.claude/epics/`

**What NOT to do:**
- Don't install any packages yet (that's task 1.2 and 1.3)
- Don't create actual component/page files yet

---

## Task 1.2: Initialize Frontend (Next.js)

**What to do:**
Inside the `frontend/` folder, initialize a Next.js 15 project with TypeScript, Tailwind CSS, and App Router. Install shadcn/ui.

**Specific requirements:**
- Next.js 15 with App Router (not Pages Router)
- TypeScript strict mode enabled
- Tailwind CSS configured
- shadcn/ui initialized with "new-york" style and dark mode support
- Create a simple home page that says "CMA AutoFill — Coming Soon"
- Design theme: dark navy background (#0a1628), gold accent (#c9a84c), white text

**Verification:**
- `cd frontend && npm run dev` → opens in browser at localhost:3000
- Page shows "CMA AutoFill — Coming Soon" with dark navy background
- No TypeScript errors
- No console errors

**What NOT to do:**
- Don't create login page, dashboard, or any real pages yet
- Don't install extra libraries beyond Next.js + Tailwind + shadcn
- Don't set up API routes yet

---

## Task 1.3: Initialize Backend (FastAPI)

**What to do:**
Inside the `backend/` folder, set up a FastAPI project with proper structure.

**Specific requirements:**
- Create `requirements.txt` with: fastapi, uvicorn, python-dotenv, pydantic, httpx, supabase, google-generativeai, openpyxl, pdfplumber, python-multipart
- Create `main.py` with a FastAPI app that has:
  - A health check endpoint: `GET /health` → returns `{"status": "ok", "service": "cma-autofill-api"}`
  - CORS middleware allowing the frontend origin
  - A root endpoint: `GET /` → returns `{"message": "CMA AutoFill API v1"}`
- Create empty `__init__.py` files in all subdirectories
- Create `.env` file with placeholder values for all backend env vars (from CLAUDE.md)

**Verification:**
- `cd backend && pip install -r requirements.txt` → installs without errors
- `uvicorn main:app --reload` → starts server at localhost:8000
- `localhost:8000/health` returns `{"status": "ok"}`
- `localhost:8000/docs` shows FastAPI Swagger UI

**What NOT to do:**
- Don't create any real API endpoints yet (that's Phase 03)
- Don't set up database connections yet (that's task 1.5)
- Don't create service modules yet

---

## Task 1.4: Configure Environment Variables

**What to do:**
Create `.env` files with the actual API keys and URLs (from Phase 00 account setup).

**Files to create/update:**
- `frontend/.env.local` — Supabase URL, anon key, API URL
- `backend/.env` — Supabase URL, service role key, Gemini key, Resend key, JWT secret

**Also create:**
- `frontend/.env.example` — Same keys but with placeholder values (safe to commit)
- `backend/.env.example` — Same keys but with placeholder values (safe to commit)

**Verification:**
- `.env` and `.env.local` are in `.gitignore` (confirmed by running `git status` — they should NOT appear)
- `.env.example` files ARE tracked by git
- Backend can read env vars: add a temporary print statement in main.py that prints "Supabase URL loaded" on startup

**What NOT to do:**
- Don't commit actual API keys to git — ever
- Don't hardcode any values — always read from environment

---

## Task 1.5: Connect Supabase Client (Backend)

**What to do:**
Create a Supabase client utility in the backend that other modules will use to interact with the database.

**Create file:** `backend/app/db/supabase_client.py`

**Requirements:**
- Initialize Supabase client using URL and service_role key from environment
- Export a function `get_supabase()` that returns the client
- Add a test endpoint: `GET /health/db` that calls Supabase and returns connection status

**Verification:**
- Start backend → `localhost:8000/health/db` returns `{"status": "connected", "database": "cma-autofill"}`
- If Supabase credentials are wrong, it returns `{"status": "error", "message": "..."}`

**What NOT to do:**
- Don't create any tables (that's Phase 02)
- Don't set up RLS policies
- Don't create complex query utilities — just the basic client

---

## Task 1.6: Connect Supabase Client (Frontend)

**What to do:**
Create a Supabase client utility in the frontend for authentication (login/signup).

**Create file:** `frontend/src/lib/supabase.ts`

**Requirements:**
- Initialize Supabase browser client using public URL and anon key
- Export the client for use in auth components
- Update the home page to show "Connected to Supabase ✓" or "Not connected ✗" based on a simple ping

**Verification:**
- Open frontend in browser → shows "Connected to Supabase ✓"
- If Supabase URL is wrong → shows "Not connected ✗" with error message
- No TypeScript errors, no console errors

**What NOT to do:**
- Don't build the login page yet (that's Phase 09)
- Don't set up auth providers yet
- Don't make API calls to the backend yet

---

## Task 1.7: First Deploy — Push to GitHub + Deploy to Vercel

**What to do:**
Commit all work from tasks 1.1-1.6, push to GitHub, and verify Vercel auto-deploys.

**Steps:**
1. Stage all files: `git add .`
2. Verify `.env` files are NOT staged: `git status`
3. Commit: `git commit -m "Phase 01: Project initialization — frontend, backend, Supabase connection"`
4. Push: `git push origin main`
5. Check Vercel dashboard — should auto-deploy the frontend
6. Visit the live Vercel URL — should show "CMA AutoFill — Coming Soon"

**Verification:**
- GitHub repo shows all files with correct folder structure
- Vercel deployment succeeds (green checkmark)
- Live URL shows the frontend page
- Backend is running locally (Vercel deploy is frontend only for now)
- `git log` shows clean commit history

**What NOT to do:**
- Don't deploy backend to Vercel yet (we'll decide Vercel Functions vs Railway in Phase 03)
- Don't set up CI/CD pipelines
- Don't create branches — work on `main` for MVP

---

## Phase 01 Complete Checklist

- [ ] Folder structure matches CLAUDE.md
- [ ] Frontend runs locally (`npm run dev`)
- [ ] Backend runs locally (`uvicorn main:app`)
- [ ] Health check works (`/health` returns OK)
- [ ] DB check works (`/health/db` returns connected)
- [ ] Frontend shows Supabase connection status
- [ ] Environment variables configured (not in git)
- [ ] Code pushed to GitHub
- [ ] Vercel auto-deployed frontend
- [ ] Live URL works

**Next → PHASE-02-database.md**
