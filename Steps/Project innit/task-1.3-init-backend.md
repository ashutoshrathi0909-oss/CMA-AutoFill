# Task 1.3: Initialize Backend (FastAPI)

> **Phase:** 01 - Project Initialization
> **Depends on:** Task 1.1 (folder structure exists)
> **Agent reads:** CLAUDE.md → Tech Stack, Coding Standards → Python
> **Time estimate:** 10 minutes

---

## Objective

Set up a FastAPI project inside the `backend/` folder with a working health check endpoint and Swagger docs.

---

## What to Do

### Step 1: Create requirements.txt
File: `backend/requirements.txt`

```
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
python-dotenv>=1.0.0
pydantic>=2.0.0
httpx>=0.27.0
supabase>=2.0.0
google-generativeai>=0.8.0
openpyxl>=3.1.0
pdfplumber>=0.11.0
python-multipart>=0.0.9
python-jose[cryptography]>=3.3.0
pytest>=8.0.0
pytest-asyncio>=0.23.0
```

### Step 2: Create main.py
File: `backend/main.py`

- Create FastAPI app with title "CMA AutoFill API", version "0.1.0"
- Add CORS middleware:
  - Allow origins: `["http://localhost:3000", "https://*.vercel.app"]`
  - Allow methods: all
  - Allow headers: all
  - Allow credentials: true
- Add two endpoints:
  - `GET /` → `{"message": "CMA AutoFill API v1", "docs": "/docs"}`
  - `GET /health` → `{"status": "ok", "service": "cma-autofill-api", "version": "0.1.0"}`

### Step 3: Create __init__.py Files
Add empty `__init__.py` in every Python subdirectory:
- `backend/app/__init__.py`
- `backend/app/api/__init__.py`
- `backend/app/api/v1/__init__.py`
- `backend/app/core/__init__.py`
- `backend/app/models/__init__.py`
- `backend/app/services/__init__.py`
- `backend/app/services/extraction/__init__.py`
- `backend/app/services/classification/__init__.py`
- `backend/app/services/validation/__init__.py`
- `backend/app/services/excel/__init__.py`
- `backend/app/services/pipeline/__init__.py`
- `backend/app/db/__init__.py`
- `backend/tests/__init__.py`

### Step 4: Create config.py
File: `backend/app/core/config.py`

- Use pydantic `BaseSettings` to load environment variables
- Fields: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, GEMINI_API_KEY, RESEND_API_KEY, ENVIRONMENT (default "development")
- Load from `.env` file using `env_file = ".env"`

---

## What NOT to Do

- Don't create any real API endpoints (that's Phase 03)
- Don't set up database connections (that's task 1.5)
- Don't create service modules or business logic
- Don't create Pydantic request/response models yet
- Don't install packages globally — use a virtual environment if preferred

---

## Verification

- [ ] `cd backend && pip install -r requirements.txt` → installs without errors
- [ ] `uvicorn main:app --reload` → starts server at localhost:8000
- [ ] `localhost:8000/` returns the welcome message JSON
- [ ] `localhost:8000/health` returns `{"status": "ok"}`
- [ ] `localhost:8000/docs` shows FastAPI Swagger UI with both endpoints
- [ ] All `__init__.py` files exist in subdirectories
- [ ] `config.py` loads settings from environment

---

## Done → Move to task-1.4-env-variables.md
