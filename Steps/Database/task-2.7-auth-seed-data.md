# Task 2.7: Configure Auth + Seed Test Data

> **Phase:** 02 - Database & Authentication
> **Depends on:** Task 2.6 (RLS policies active)
> **Agent reads:** CLAUDE.md → Environment Variables, cma-domain SKILL → golden test reference
> **MCP to use:** Supabase MCP
> **Time estimate:** 15 minutes

---

## Objective

Configure Supabase Auth for passwordless magic link login. Then seed the database with test data so future phases have something to work with.

---

## What to Do

### Step 1: Configure Supabase Auth

In Supabase dashboard → Authentication → Providers:

- **Enable Email provider:** YES
- **Enable Magic Link:** YES (passwordless — user clicks link in email to log in)
- **Confirm email:** OFF for development (turn ON in production)
- **Minimum password length:** N/A (we don't use passwords)

In Supabase dashboard → Authentication → URL Configuration:
- **Site URL:** Your Vercel URL (e.g., `https://cma-autofill.vercel.app`)
- **Redirect URLs:** Add both:
  - `http://localhost:3000` (local dev)
  - `https://cma-autofill.vercel.app` (production)
  - `https://*.vercel.app` (preview deployments)

### Step 2: Create Auth Trigger

Create a database function + trigger that automatically creates a `users` row when someone signs up through Supabase Auth.

Logic:
- When a new row is inserted into `auth.users` (signup happens)
- Check if there's a `firm_id` in the user's metadata
- If yes → create a `users` row linked to that firm
- If no → this is a new firm owner → create a new firm first, then create the user as 'owner'

This trigger handles the signup flow:
1. New user signs up with email → Supabase creates auth.users entry
2. Trigger fires → creates firm (if new) + users table entry
3. User is now linked to a firm and can access data

### Step 3: Seed Test Data

Using the Supabase service role key (bypasses RLS), insert:

**Test Firm:**
- name: "Ashutosh CA Firm" (placeholder — Ashutosh replaces with real name)
- email: father's email (placeholder)
- plan: 'free'

**Test User (via Auth signup or direct insert):**
- email: father's email
- full_name: "CA Father" (placeholder)
- role: 'owner'
- linked to the firm above

**Test Client:**
- name: "Mehta Computers"
- entity_type: "trading"
- firm_id: the test firm's ID

**Test CMA Project:**
- client_id: Mehta Computers' ID
- financial_year: "2024-25"
- status: "draft"
- bank_name: "State Bank of India"
- loan_type: "working_capital"

### Step 4: Create a Seed Script

Create file: `backend/scripts/seed.py`

A Python script that:
- Uses the Supabase service role key
- Inserts all the test data above
- Can be re-run safely (checks if data exists before inserting)
- Prints what it created

This script is useful for resetting the database during development.

---

## What NOT to Do

- Don't build the login UI (that's Phase 09)
- Don't create the full signup flow with firm creation form
- Don't set up email templates (use Supabase defaults for now)
- Don't create multiple test firms — one is enough
- Don't insert fake financial data into the CMA project (that's for extraction testing in Phase 04)

---

## Verification

- [ ] Supabase Auth → Providers → Email is enabled with Magic Link
- [ ] Redirect URLs include localhost:3000 and Vercel URL
- [ ] Auth trigger function exists in database
- [ ] Test signup: go to Supabase → Authentication → Users → "Create User" → enter email
- [ ] After signup: `users` table has a row for the new user
- [ ] After signup: `firms` table has a row (if auto-created by trigger)
- [ ] Test firm "Ashutosh CA Firm" exists in `firms` table
- [ ] Test client "Mehta Computers" exists in `clients` table
- [ ] Test CMA project exists in `cma_projects` table with status "draft"
- [ ] Running `python backend/scripts/seed.py` works without errors
- [ ] Running it again doesn't create duplicates

---

## Phase 02 Complete! 🎉

All 7 tasks done. You now have:
- ✅ 10 database tables with proper constraints
- ✅ Storage bucket for file uploads
- ✅ Row Level Security enforcing multi-tenant isolation
- ✅ Magic link authentication configured
- ✅ Auth trigger for automatic user/firm creation
- ✅ Test data seeded (firm, user, client, project)
- ✅ Seed script for resetting development data

**Next → Phase 03: API CRUD Endpoints**
