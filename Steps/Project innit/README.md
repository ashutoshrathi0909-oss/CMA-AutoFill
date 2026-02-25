# Phase 01: Project Initialization — Overview

> Complete these 7 tasks in order. Each task = one Claude Code agent session.
> Review the output after each task before moving to the next.

| # | File | What It Does | Verify By |
|---|------|-------------|-----------|
| 1.1 | task-1.1-folder-structure.md | Create all folders + .gitignore + README | Folder tree matches CLAUDE.md |
| 1.2 | task-1.2-init-frontend.md | Next.js + Tailwind + shadcn/ui + landing page | `npm run dev` shows page |
| 1.3 | task-1.3-init-backend.md | FastAPI + requirements + health endpoint | `localhost:8000/health` → OK |
| 1.4 | task-1.4-env-variables.md | .env files with API keys | Keys loaded, not in git |
| 1.5 | task-1.5-supabase-backend.md | Backend Supabase client + /health/db | DB connected response |
| 1.6 | task-1.6-supabase-frontend.md | Frontend Supabase client + status indicator | Page shows "Connected ✓" |
| 1.7 | task-1.7-first-deploy.md | Push to GitHub + Vercel auto-deploy | Live URL works |

**Phase 01 result:** Live site on Vercel, backend running locally, Supabase connected, GitHub repo ready.
