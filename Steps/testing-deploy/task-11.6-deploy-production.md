# Task 11.6: Deploy to Production

> **Phase:** 11 - Testing & Production Deploy
> **Depends on:** Task 11.5 (production env configured)
> **Time estimate:** 20 minutes

---

## Objective

Deploy the frontend to Vercel and backend to Railway. Make the app accessible on the internet.

---

## What to Do

### Step 1: Deploy Frontend to Vercel

Vercel auto-deploys from GitHub. Just push to main:

```bash
git add .
git commit -m "v1.0.0: CMA AutoFill production release"
git push origin main
```

Vercel will:
1. Detect Next.js project
2. Build the frontend
3. Deploy to `your-project.vercel.app`
4. Show deployment URL in dashboard

**Verify:** Visit the Vercel URL → login page should appear.

### Step 2: Deploy Backend to Railway

Option A: Railway from GitHub (recommended)
1. Go to Railway dashboard → New Project → Deploy from GitHub Repo
2. Select your repo, set root directory to `backend/`
3. Railway detects Python, installs requirements.txt
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Environment variables already set (task 11.5)
6. Deploy → Railway gives you a URL

Option B: Railway CLI
```bash
cd backend
railway up
```

**Verify:** Visit `your-backend.railway.app/health` → should return `{"status": "ok"}`

### Step 3: Connect Frontend → Backend

1. Verify `NEXT_PUBLIC_API_URL` in Vercel points to Railway URL
2. Redeploy frontend if URL changed
3. Test: login on frontend → dashboard loads data from backend API

### Step 4: Verify Full Stack

Run through the complete flow on production:

1. Visit production URL
2. Login with magic link
3. Check dashboard loads
4. Verify all navigation works
5. API calls succeed (check browser Network tab)

### Step 5: GitHub Actions CI (Optional but Recommended)

Create: `.github/workflows/ci.yml`

```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: cd backend && pip install -r requirements.txt
      - run: cd backend && pytest tests/ -v

  frontend-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: cd frontend && npm ci
      - run: cd frontend && npm run build
```

---

## What NOT to Do

- Don't deploy without testing locally first
- Don't expose debug mode in production (ENVIRONMENT=production)
- Don't deploy with console.log statements in frontend (clean up)
- Don't skip the full-stack verification step

---

## Verification

- [ ] Frontend live at Vercel URL → login page visible
- [ ] Backend live at Railway URL → /health returns OK
- [ ] /health/db → database connected
- [ ] /health/llm → Gemini API working
- [ ] Frontend can call backend API (no CORS errors)
- [ ] Magic link login works on production
- [ ] Dashboard loads with real data
- [ ] Navigation works across all pages
- [ ] GitHub Actions CI passes (if set up)

---

## Done → Move to task-11.7-smoke-test-launch.md
