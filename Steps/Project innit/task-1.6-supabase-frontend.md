# Task 1.6: Connect Supabase Client (Frontend)

> **Phase:** 01 - Project Initialization
> **Depends on:** Task 1.2 (frontend running), Task 1.4 (env vars configured)
> **Agent reads:** CLAUDE.md → Tech Stack, Environment Variables
> **Time estimate:** 10 minutes

---

## Objective

Create a Supabase browser client in the frontend for authentication. Update the landing page to show Supabase connection status.

---

## What to Do

### Step 1: Install Supabase JS
In `frontend/`:
```
npm install @supabase/supabase-js @supabase/ssr
```

### Step 2: Create Supabase Client
File: `frontend/src/lib/supabase.ts`

- Read `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY` from environment
- Create and export a browser Supabase client
- Throw a clear error if env vars are missing (developer-friendly message)

### Step 3: Update Landing Page
Update `frontend/src/app/page.tsx`:

- Keep the existing "CMA AutoFill — Coming Soon" design
- Add a small status indicator at the bottom:
  - On page load, make a simple Supabase call (e.g., check auth session)
  - Show "✓ Connected to Supabase" in green if successful
  - Show "✗ Not connected" in red if it fails
- This is a development-only indicator — will be removed later

---

## What NOT to Do

- Don't build a login page (that's Phase 09)
- Don't set up auth providers or magic link flow
- Don't create any protected routes or auth middleware
- Don't make API calls to the backend
- Don't install any UI libraries beyond what's already installed

---

## Verification

- [ ] `cd frontend && npm run dev` → page loads without errors
- [ ] Page shows "✓ Connected to Supabase" at the bottom
- [ ] If you temporarily break the Supabase URL in .env.local → shows "✗ Not connected"
- [ ] No TypeScript errors (`npm run build` passes)
- [ ] No console errors in browser dev tools
- [ ] `frontend/src/lib/supabase.ts` exports a working client

---

## Done → Move to task-1.7-first-deploy.md
