# CLAUDE.md — CMA AutoFill Project Memory

> Claude Code reads this file before every interaction. It is the single source of truth for project context.

---

## Project Overview

**CMA AutoFill** is a SaaS product that automates Credit Monitoring Arrangement (CMA) document creation for Indian Chartered Accountant (CA) firms.

**What is a CMA?** A CMA is a critical financial document required by Indian banks for loan applications. It contains financial data from P&L statements, balance sheets, and trial balances, organized into a standardized Excel template with 289 rows across 15 sheets. Errors in CMAs can cause loan rejections — accuracy is non-negotiable.

**The Problem:** CAs currently create CMAs manually, which is time-consuming and error-prone. Our product automates this using AI.

**The Pipeline:**
```
Upload Documents → Extract Data (AI) → Classify Line Items (AI) → Validate Numbers → Generate CMA Excel → CA Reviews Uncertain Items
```

**Team:** Ashutosh (developer/founder) + his father (experienced CA, domain expert, handles "Ask Father" reviews)

**Current Volume:** ~5 CMAs per month initially. Target: hundreds of CA firms across India.

**Pricing Target:** ₹2,000-5,000/month per firm.

---

## Tech Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| Frontend | Next.js 15 + TypeScript + Tailwind CSS + shadcn/ui | Deployed on Vercel |
| Backend | FastAPI (Python) | Deployed on Vercel Functions OR Railway |
| Database | Supabase (PostgreSQL) | Free tier with RLS for multi-tenant isolation |
| Auth | Supabase Auth (magic link email) | No passwords |
| File Storage | Supabase Storage | For uploaded docs and generated CMAs |
| LLM - Extraction | Gemini 2.0 Flash | Best at financial table OCR, free tier |
| LLM - Classification | Gemini 3 Flash | Pro-level intelligence at Flash pricing |
| LLM - Fallback | Gemini 3.1 Pro | Only for items Flash can't classify |
| Email | Resend | Review notifications |
| Hosting | Vercel (frontend) | Auto-deploy from GitHub |
| Version Control | GitHub (private repo) | Single repo: `cma-autofill` |

---

## Project Structure

```
cma-autofill/
├── frontend/                 # Next.js app
│   ├── src/
│   │   ├── app/              # App router pages
│   │   ├── components/       # Reusable UI components
│   │   ├── lib/              # Utilities, API client, Supabase client
│   │   └── types/            # TypeScript type definitions
│   ├── public/               # Static assets
│   ├── package.json
│   └── tailwind.config.ts
├── backend/                  # FastAPI app
│   ├── app/
│   │   ├── api/              # Route handlers
│   │   │   └── v1/           # Versioned API routes
│   │   ├── core/             # Config, security, dependencies
│   │   ├── models/           # Pydantic models (request/response schemas)
│   │   ├── services/         # Business logic
│   │   │   ├── extraction/   # Document parsing + Gemini Vision
│   │   │   ├── classification/ # Rule matching + Gemini classification
│   │   │   ├── validation/   # Number checks, completeness checks
│   │   │   ├── excel/        # CMA Excel writer (cma_writer.py)
│   │   │   └── pipeline/     # Orchestrator (runs all steps)
│   │   └── db/               # Supabase client, queries
│   ├── tests/                # pytest tests
│   ├── requirements.txt
│   └── main.py
├── reference/                # Domain reference files (NOT deployed)
│   ├── CMA.xlsm             # Empty CMA template
│   ├── CMA_15092025.xls     # Completed reference (Mehta Computers)
│   ├── CMA_classification.xls # 384 classification rules
│   └── sample_documents/    # Test input documents
├── .claude/                  # Claude Code config
│   ├── CLAUDE.md             # This file (symlinked to root)
│   ├── skills/               # Custom skills
│   │   └── cma-domain/       # CMA domain knowledge skill
│   ├── commands/             # CCPM commands
│   └── context/              # CCPM context files
├── .env.local                # Frontend env vars (gitignored)
├── .env                      # Backend env vars (gitignored)
├── .gitignore
├── vercel.json               # Vercel config
└── README.md
```

---

## Coding Standards

### Python (Backend)
- Use type hints on ALL functions
- Use Pydantic models for all request/response schemas
- Async functions for all API endpoints
- Error handling: raise HTTPException with clear messages
- Naming: snake_case for files, functions, variables
- Every service function must have at least one test
- Use `python-dotenv` for environment variables
- Log important operations (extraction, classification, errors)

### TypeScript (Frontend)
- Strict TypeScript — no `any` types
- Functional components only (no class components)
- Use shadcn/ui components — don't build custom ones when shadcn has it
- Server components by default, client components only when needed (interactivity)
- Naming: kebab-case for files, PascalCase for components
- API calls through a central `api-client.ts` utility
- Loading states, error states, and empty states for EVERY page

### General Rules
- **Never hardcode API keys** — always use environment variables
- **Never skip tests** — every feature needs at least basic tests
- **Never access Supabase directly from frontend** — always go through backend API
- **Never commit `.env` files** — they are in `.gitignore`
- **Always use Row Level Security** — multi-tenant data must be isolated
- **Always validate on backend** — never trust frontend data

---

## Database Tables (Reference)

These are the core tables (created in Phase 02):

- `firms` — CA firm accounts (multi-tenant root)
- `users` — Users within firms (with roles)
- `clients` — Firm's clients (the businesses getting CMAs)
- `cma_projects` — Individual CMA projects (one per client per year)
- `uploaded_files` — Documents uploaded for extraction
- `extracted_data` — AI-extracted line items from documents
- `classification_results` — AI classification mappings
- `review_queue` — Items needing CA review ("Ask Father")
- `classification_precedents` — Past CA decisions (learning loop)
- `generated_files` — Output CMA Excel files
- `llm_usage_log` — Token usage and cost tracking
- `audit_log` — All actions for compliance

**Multi-tenant isolation:** Every table has a `firm_id` column. RLS policies ensure Firm A can never see Firm B's data.

---

## API Design Patterns

- Base URL: `/api/v1/`
- Auth: Bearer token (Supabase JWT) in Authorization header
- All responses follow: `{ "data": ..., "error": null }` or `{ "data": null, "error": { "message": "..." } }`
- Pagination: `?page=1&per_page=20`
- File uploads: multipart/form-data
- Long-running tasks: Return `202 Accepted` with task ID, poll `/tasks/{id}/status`
- CORS: Allow frontend origin only

---

## CMA Domain Rules

### Classification System
- 384 rules map financial line items to CMA template rows
- Rules are filtered by: entity type (trading/manufacturing/service) and document type (P&L/BS)
- Each rule has: source_term, target_row_number, target_sheet, confidence_weight
- Items with <70% classification confidence → sent to "Ask Father" review queue

### Accuracy Target
- Must match reference CMA (Mehta Computers) at 65/65 values
- Golden test: upload Mehta Computers documents → generated CMA must match reference exactly
- Any discrepancy = bug that must be fixed before moving forward

### Learning Loop
- When CA resolves a review item, the decision is saved as a "precedent"
- Precedents have scope: firm-level (specific to one firm) or global (applies to all)
- Future classifications check precedents BEFORE rules
- This means the system gets smarter with every CMA processed

---

## Environment Variables

### Frontend (.env.local)
```
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
NEXT_PUBLIC_API_URL=
```

### Backend (.env)
```
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
GEMINI_API_KEY=
RESEND_API_KEY=
JWT_SECRET=
ENVIRONMENT=development
```

---

## What NOT to Do

1. **Don't over-engineer.** We're building MVP for 5 CMAs/month, not enterprise scale.
2. **Don't add features not in the phase document.** Stick to the current phase's scope.
3. **Don't use Claude API or OpenAI.** We use Gemini only (cost optimization).
4. **Don't create a complex microservices architecture.** Monorepo, simple structure.
5. **Don't skip the golden test.** Every pipeline change must pass the Mehta Computers test.
6. **Don't store client financial data in logs.** Sensitive information — log metadata only.
7. **Don't build admin panel yet.** That's post-MVP.
8. **Don't deploy backend separately if Vercel Functions work.** Simplicity first.
