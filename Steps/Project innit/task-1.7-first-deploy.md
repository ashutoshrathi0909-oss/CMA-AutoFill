# Task 1.7: First Deploy — Push to GitHub + Deploy to Vercel

> **Phase:** 01 - Project Initialization
> **Depends on:** Tasks 1.1-1.6 all complete
> **Agent reads:** CLAUDE.md → general reference
> **Time estimate:** 10 minutes

---

## Objective

Commit all Phase 01 work, push to GitHub, verify Vercel auto-deploys the frontend. This confirms the entire development → deploy pipeline works.

---

## What to Do

### Step 1: Verify No Secrets in Git
Run `git status` and check that NONE of these appear:
- `.env`
- `.env.local`
- `.env.production`
- Any file containing actual API keys

If any appear → fix `.gitignore` first!

### Step 2: Stage and Commit
```
git add .
git commit -m "Phase 01: Project initialization - frontend, backend, Supabase connection"
```

### Step 3: Push to GitHub
```
git push origin main
```

### Step 4: Verify GitHub
- Go to github.com/YOUR-USERNAME/cma-autofill
- Confirm all folders are visible: `frontend/`, `backend/`, `reference/`, `.claude/`
- Confirm `.env` files are NOT visible (gitignored)
- Confirm `README.md` shows at the bottom of the repo page

### Step 5: Verify Vercel Auto-Deploy
- Go to vercel.com dashboard
- The push should trigger an automatic deployment
- Wait for it to complete (green checkmark)
- Click the deployment URL (e.g., `cma-autofill.vercel.app`)

### Step 6: Test Live Site
- Visit the Vercel URL in your browser
- Should show the "CMA AutoFill — Coming Soon" landing page
- The Supabase connection indicator may show "Not connected" on Vercel (that's OK — we haven't set Vercel env vars yet)

### Step 7: Add Vercel Environment Variables (optional now)
If you want the live site to also show Supabase connected:
- Vercel dashboard → Project → Settings → Environment Variables
- Add: `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- Redeploy

---

## What NOT to Do

- Don't deploy the backend to Vercel yet (we decide platform in Phase 03)
- Don't create branches — work on `main` for MVP
- Don't set up CI/CD pipelines or GitHub Actions
- Don't add deployment scripts

---

## Verification

- [ ] `git log` shows clean commit with message "Phase 01: Project initialization..."
- [ ] GitHub repo shows correct folder structure
- [ ] `.env` files are NOT visible on GitHub
- [ ] Vercel deployment succeeded (green checkmark on dashboard)
- [ ] Live Vercel URL shows the landing page
- [ ] Backend runs locally: `localhost:8000/health` → OK
- [ ] Backend DB check: `localhost:8000/health/db` → connected
- [ ] Frontend runs locally: `localhost:3000` → landing page with Supabase status

---

## Phase 01 Complete! 🎉

All 7 tasks done. You now have:
- ✅ Project structure on GitHub
- ✅ Next.js frontend running + deployed to Vercel
- ✅ FastAPI backend running locally
- ✅ Supabase connected (both frontend and backend)
- ✅ Environment variables secure
- ✅ Auto-deploy pipeline working

**Next → Phase 02: Database & Authentication**
