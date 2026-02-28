# Project Memory & Knowledge Base

This file serves as the **Main Memory** for all AI agents working on this project.
Update this file whenever there are major changes to the architecture, tech stack, or project goals.

---

## 🚀 Project Overview
CMA AutoFill — a SaaS product that automates the creation of Credit Monitoring Arrangement (CMA) documents for Indian CA firms. Reduces manual work from 3-4 hours to under 5 minutes per client.

**Target:** CA firms & bank branch managers across India.

## 🛠️ Tech Stack
- **Frontend:** Next.js 15 (App Router), TypeScript, Tailwind CSS
- **Backend:** FastAPI (Python 3.12)
- **Database:** Supabase (PostgreSQL + Auth + Storage)
- **AI:** Gemini 2.0 Flash (extraction), Gemini 3 Flash (classification)
- **Hosting:** Vercel (frontend), Railway (backend)
- **Email:** Resend
- **Error monitoring:** Sentry (Phase 11)

## 🏗️ Core Architecture
Multi-tenant SaaS. Pipeline: Upload → Extract → Classify → Validate → Generate Excel → Review → Download.
All pipelines are synchronous for MVP (V1). Background tasks deferred to V2.

## 📋 Rules & Standards
- **Coding Style:** TypeScript (frontend), Python snake_case (backend), functional components
- **Naming:** camelCase JS/TS, snake_case Python
- **Indian Constraints:** Lakhs format (₹1,00,000), Indian GAAP, IST timezone
- **Never hardcode:** LLM model names — use environment variables via `llm_config.py`
- **LLM Models:** Set via `LLM_EXTRACTION_MODEL` and `LLM_CLASSIFICATION_MODEL` env vars. Do NOT hardcode strings like "gemini-2.0-flash".

## 🤖 Auto-Debug Rule
**RULE: When any code change causes a test failure, build error, or runtime error — automatically run the debug framework before asking the user for help.**

Trigger auto-debug when:
- A terminal command fails with a non-zero exit code
- A test (pytest or Playwright) reports failures
- The browser console shows errors after a UI change
- A backend endpoint returns 4xx/5xx unexpectedly

Auto-debug procedure:
1. Run `.\debug.ps1 --fix --Verbose` from project root
2. Read `debug-output/last-run.txt` for errors
3. Identify root cause from the `FIX_NEEDED:` lines
4. Apply the fix directly (no need to ask for permission for obvious fixes)
5. Re-run `.\debug.ps1` to confirm fix worked
6. Commit with `git commit -m "fix: <description>"`
7. Only escalate to user if fix attempt fails twice

## 📂 Key Directories & Files
- `/frontend`: Next.js 15 app (Phase 09-10)
- `/backend`: FastAPI app (Phases 03-08)
- `/reference`: CMA template, classification rules, sample documents
- `/Steps/CMA_AutoFill_Blueprint.md`: Main technical specification
- `/Steps/CLAUDE.md`: Shared context for Claude Code sessions
- `debug.ps1`: Local debug runner
- `smoke.test.ts`: Playwright smoke tests
- `.github/workflows/`: CI automation

## 🏁 Current Status & Roadmap
- [x] Phase 00: Prerequisites (in progress — Vercel pending)
- [x] Phase 01: Project Init — ✅ Next.js 15 frontend (`:3000`), FastAPI backend (`:8000`), Supabase connected. Note: `gotrue` pinned to `2.10.0` (pure-Python wheel) to avoid Rust DLL blocked by Windows WDAC. `supabase` pinned to `2.10.0`.
- [x] Phase 02: Database schema & RLS — ✅ All tables, RLS policies, auth trigger created.
- [x] Phase 03: API CRUD — ✅ Auth middleware, /me, client CRUD, project CRUD, file upload/download, dashboard stats. Audit fixes applied (soft delete, singleton DB client, tests).
- [x] Phase 04: Document extraction — ✅ Gemini 2.0 Flash extraction, PDF/image support, multi-file merge.
- [x] Phase 05: Classification AI — ✅ Three-tier pipeline (precedent→rule→AI), review queue, Gemini 3 Flash.
- [x] Phase 06: Validation & Excel — ✅ BS/PL/ratio validation, CMA writer, data transformer, generation pipeline.
- [x] Phase 07: Review queue — ✅ Ask Father flow, resolve/bulk-resolve, precedent CRUD, learning metrics, email notifications.
- [x] Phase 08: Pipeline orchestrator — ✅ One-click /process, background tasks, progress tracking, error recovery, hooks, integration tests.
- [x] Phase 09: Frontend shell — ✅ Complete auth, layout, dashboard, clients, projects list.
- [x] Phase 10: Frontend CMA flow — ✅ End-to-end CMA pipeline UI (Upload, Processing, Ask Father review, Download).
- [x] Phase 11: Testing & deploy — ✅ E2E tests (Playwright), security hardening (rate limiting, CORS, exception handler), performance (DB indexes, timing middleware), structured logging (structlog), CI/CD (GitHub Actions), LAUNCH_NOTES.md.

---

## 💡 Context for New Agents
> **Instructions for Agents:** Read this file first before starting any task. Follow the standards defined here. LLM model names MUST come from environment variables. Run `/debug` if you hit any errors. Run `/auto-commit` after completing any task.
