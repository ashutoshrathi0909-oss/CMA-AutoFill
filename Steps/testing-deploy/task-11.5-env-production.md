# Task 11.5: Production Environment Configuration

> **Phase:** 11 - Testing & Production Deploy
> **Depends on:** All code complete, accounts created (Phase 00)
> **Time estimate:** 15 minutes

---

## Objective

Set up all production environment variables, secrets, and configuration.

---

## What to Do

### Step 1: Supabase Production Project

- If using Supabase free tier: same project for dev and prod (acceptable for V1)
- If separate: create a new Supabase project for production
- Run all migrations from Phase 02 on the production database
- Verify RLS policies are active
- Set up auth: configure redirect URLs for production domain

### Step 2: Backend Environment Variables (Railway)

Set these in Railway dashboard → project → Variables:

```env
# App
ENVIRONMENT=production
APP_VERSION=1.0.0
LOG_LEVEL=INFO

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...  # ⚠ Server-only, never expose to frontend
SUPABASE_JWT_SECRET=your-jwt-secret

# Gemini
GEMINI_API_KEY=AIza...

# Email
RESEND_API_KEY=re_...
ADMIN_EMAIL=ashutosh@yourdomain.com

# CORS
ALLOWED_ORIGINS=https://cma-autofill.vercel.app

# Rate Limiting
RATE_LIMIT_ENABLED=true
```

### Step 3: Frontend Environment Variables (Vercel)

Set these in Vercel dashboard → project → Environment Variables:

```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
NEXT_PUBLIC_APP_URL=https://cma-autofill.vercel.app
```

**CRITICAL:** Only `NEXT_PUBLIC_` variables are exposed to the browser. Never put secrets here.

### Step 4: Supabase Auth Configuration

In Supabase dashboard → Authentication → URL Configuration:
- Site URL: `https://cma-autofill.vercel.app`
- Redirect URLs: `https://cma-autofill.vercel.app/auth/callback`

### Step 5: Domain Setup (Optional for V1)

- Vercel auto-assigns: `your-project.vercel.app`
- Custom domain later: `app.cmaautofill.com` (when you buy the domain)
- Railway auto-assigns: `your-project.railway.app`

### Step 6: Create Production Seed Data

Create the first firm + admin user:
```sql
-- Run in Supabase SQL editor for production
INSERT INTO firms (name, plan) VALUES ('Your Father''s Firm Name', 'free');

-- After user signs up via magic link, update their role:
UPDATE users SET role = 'owner' WHERE email = 'father@email.com';
```

---

## What NOT to Do

- Don't commit .env files to Git (they're in .gitignore)
- Don't use development API keys in production
- Don't share the SUPABASE_SERVICE_ROLE_KEY with frontend
- Don't skip setting CORS — it's a security requirement

---

## Verification

- [ ] All Railway environment variables set
- [ ] All Vercel environment variables set
- [ ] Supabase auth redirect URLs point to production domain
- [ ] Backend can connect to production Supabase (test /health/db)
- [ ] Backend can connect to Gemini API (test /health/llm)
- [ ] CORS allows only the production frontend domain
- [ ] Service role key is NOT in any frontend code

---

## Done → Move to task-11.6-deploy-production.md
