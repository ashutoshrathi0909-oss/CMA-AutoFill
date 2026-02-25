# Task 1.1: Create Project Folder Structure

> **Phase:** 01 - Project Initialization
> **Depends on:** PHASE-00 prerequisites complete
> **Agent reads:** CLAUDE.md (for project structure reference)
> **Time estimate:** 5 minutes

---

## Objective

Create the complete folder structure for the CMA AutoFill project. No packages, no code — just folders and placeholder files so the skeleton is visible in VS Code.

---

## What to Create

```
cma-autofill/
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   ├── lib/
│   │   └── types/
│   └── public/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   ├── core/
│   │   ├── models/
│   │   ├── services/
│   │   │   ├── extraction/
│   │   │   ├── classification/
│   │   │   ├── validation/
│   │   │   ├── excel/
│   │   │   └── pipeline/
│   │   └── db/
│   └── tests/
├── reference/
│   └── sample_documents/
├── .claude/
│   ├── skills/
│   │   └── cma-domain/
│   ├── commands/
│   └── context/
└── README.md
```

---

## .gitignore (create at project root)

```
# Environment
.env
.env.local
.env.production

# Dependencies
node_modules/
__pycache__/
*.pyc
.venv/

# Build
.next/
dist/
build/

# IDE
.vscode/settings.json
.idea/

# OS
.DS_Store
Thumbs.db

# Claude Code
.claude/epics/

# Supabase
supabase/.temp/
```

---

## README.md (create at project root)

Create a simple README with:
- Project name: CMA AutoFill
- One-line description: "AI-powered CMA document automation for Indian CA firms"
- Tech stack list (Next.js, FastAPI, Supabase, Gemini, Vercel)
- "Setup instructions coming soon"

---

## What NOT to Do

- Don't install any npm or pip packages
- Don't create any actual code files (components, endpoints, etc.)
- Don't initialize Next.js or FastAPI yet
- Don't create .env files yet (that's task 1.4)

---

## Verification

- [ ] Open project in VS Code → folder tree matches the structure above
- [ ] `.gitignore` exists at root with all entries listed
- [ ] `README.md` exists at root
- [ ] `reference/` folder exists (you'll manually copy files here later)
- [ ] `.claude/skills/cma-domain/` folder exists (SKILL.md goes here later)
- [ ] Run `git add . && git status` → shows new files, no .env files

---

## Done → Move to task-1.2-init-frontend.md
