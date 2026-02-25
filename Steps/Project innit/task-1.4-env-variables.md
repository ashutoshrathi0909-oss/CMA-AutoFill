# Task 1.4: Configure Environment Variables

> **Phase:** 01 - Project Initialization
> **Depends on:** Task 1.2 (frontend exists), Task 1.3 (backend exists)
> **Agent reads:** CLAUDE.md → Environment Variables section
> **Time estimate:** 5 minutes

---

## Objective

Create `.env` files with actual API keys and `.env.example` files with placeholders. Ensure secrets never get committed to git.

---

## What to Do

### Step 1: Create backend/.env
```
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here
GEMINI_API_KEY=your_gemini_api_key_here
RESEND_API_KEY=your_resend_api_key_here
JWT_SECRET=your_supabase_jwt_secret_here
ENVIRONMENT=development
```

**Note to Ashutosh:** Replace the placeholder values with your actual keys from Phase 00 account setup.

### Step 2: Create backend/.env.example
Same file but with dummy values — this IS safe to commit:
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
GEMINI_API_KEY=your_gemini_api_key
RESEND_API_KEY=your_resend_api_key
JWT_SECRET=your_jwt_secret
ENVIRONMENT=development
```

### Step 3: Create frontend/.env.local
```
NEXT_PUBLIC_SUPABASE_URL=https://YOUR_PROJECT.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key_here
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Step 4: Create frontend/.env.example
```
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Step 5: Verify .gitignore
Confirm these lines exist in the root `.gitignore`:
```
.env
.env.local
.env.production
```

---

## What NOT to Do

- Don't commit `.env` or `.env.local` files — EVER
- Don't hardcode any API keys in source code
- Don't print full API keys in console logs (first 5 chars max for debugging)

---

## Verification

- [ ] `backend/.env` exists with your actual keys filled in
- [ ] `backend/.env.example` exists with placeholder values
- [ ] `frontend/.env.local` exists with your actual keys filled in
- [ ] `frontend/.env.example` exists with placeholder values
- [ ] Run `git status` → `.env` and `.env.local` do NOT appear in the list
- [ ] Run `git status` → `.env.example` files DO appear (safe to commit)
- [ ] Backend can read vars: start backend → no "missing env var" errors

---

## Done → Move to task-1.5-supabase-backend.md
