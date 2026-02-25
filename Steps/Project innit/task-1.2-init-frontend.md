# Task 1.2: Initialize Frontend (Next.js)

> **Phase:** 01 - Project Initialization
> **Depends on:** Task 1.1 (folder structure exists)
> **Agent reads:** CLAUDE.md → Tech Stack section, Coding Standards → TypeScript
> **Time estimate:** 10 minutes

---

## Objective

Initialize a Next.js 15 project inside the `frontend/` folder with TypeScript, Tailwind CSS, App Router, and shadcn/ui. Create a simple landing page.

---

## What to Do

### Step 1: Initialize Next.js
Inside the `frontend/` folder:
- Next.js 15 with App Router (NOT Pages Router)
- TypeScript strict mode enabled
- Tailwind CSS configured
- ESLint included
- `src/` directory: YES (already created in task 1.1)

### Step 2: Install shadcn/ui
- Initialize with "new-york" style
- Enable dark mode support (class-based)
- Install these base components: button, card, input, label, badge

### Step 3: Create Landing Page
Create `frontend/src/app/page.tsx`:
- Dark navy background: `#0a1628`
- Gold accent color: `#c9a84c`
- White text
- Content: "CMA AutoFill" as heading, "AI-Powered CMA Document Automation" as subtitle
- A simple "Coming Soon" badge
- Clean, centered layout — nothing fancy

### Step 4: Configure Tailwind Theme
Add to tailwind config:
- Custom colors: `navy: '#0a1628'`, `gold: '#c9a84c'`
- These will be our brand colors throughout the app

---

## What NOT to Do

- Don't create login page, dashboard, or any real pages
- Don't install extra libraries beyond Next.js + Tailwind + shadcn
- Don't set up API routes or middleware
- Don't create any components beyond the landing page
- Don't set up Supabase client (that's task 1.6)

---

## Verification

- [ ] `cd frontend && npm run dev` → opens in browser at localhost:3000
- [ ] Page shows "CMA AutoFill" heading with dark navy background
- [ ] Gold accent color visible on badge or heading
- [ ] No TypeScript errors (`npm run build` passes)
- [ ] No console errors in browser
- [ ] `frontend/package.json` has correct dependencies

---

## Done → Move to task-1.3-init-backend.md
