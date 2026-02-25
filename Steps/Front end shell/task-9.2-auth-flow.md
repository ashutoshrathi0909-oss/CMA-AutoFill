# Task 9.2: Authentication Flow

> **Phase:** 09 - Frontend Shell
> **Depends on:** Task 9.1 (layout exists), Phase 02 (Supabase auth configured)
> **Agent reads:** CLAUDE.md → Frontend Architecture (Supabase client)
> **Time estimate:** 20 minutes

---

## Objective

Implement login/logout using Supabase magic link authentication. No passwords — CAs enter their email, get a link, click it, and they're in.

---

## What to Do

### Pages to Create

**`frontend/app/(auth)/login/page.tsx`** — Login page

- Clean, centered form on dark background
- CMA AutoFill logo at top
- Email input field
- "Send Magic Link" button (gold accent)
- After sending: "Check your email for the login link"
- Error handling: invalid email, rate limit

**`frontend/app/(auth)/auth/callback/route.ts`** — Auth callback

- Supabase redirects here after magic link click
- Exchanges the auth code for a session
- Redirects to `/dashboard`

### Auth Context

File: `frontend/lib/auth-context.tsx`

```typescript
interface AuthContext {
  user: User | null;
  session: Session | null;
  isLoading: boolean;
  signIn: (email: string) => Promise<void>;
  signOut: () => Promise<void>;
}
```

- Wraps the app with auth state
- Listens for Supabase auth state changes
- Provides user info to all components
- Persists session across page reloads

### Route Protection

File: `frontend/middleware.ts`

Next.js middleware that:
- Checks if user has valid Supabase session
- Unauthenticated → redirect to `/login`
- Authenticated on `/login` → redirect to `/dashboard`
- Protect all routes under `/(dashboard)/*`

### Session Management

- Supabase handles JWT tokens automatically
- Frontend passes the access token in `Authorization: Bearer <token>` header for API calls
- Token refresh handled by Supabase client
- Sign out clears all tokens

### Update Layout

- User menu in sidebar shows real user name and email
- Sign out button in user menu dropdown works
- If session expires mid-use → redirect to login with "Session expired" message

---

## What NOT to Do

- Don't implement password-based login (magic link only for V1)
- Don't implement user registration (admin creates users, or self-signup later)
- Don't store tokens in localStorage manually (Supabase client handles this)
- Don't create a sign-up page (V1 = admin-created accounts only)

---

## Verification

- [ ] Navigate to `/dashboard` without login → redirected to `/login`
- [ ] Enter email → "Send Magic Link" → success message shown
- [ ] Click magic link in email → redirected to `/dashboard`
- [ ] User name and email appear in sidebar user menu
- [ ] Click "Sign Out" → redirected to `/login`, session cleared
- [ ] Refresh page → still logged in (session persisted)
- [ ] Invalid email → clear error message
- [ ] Rate limit → clear error message

---

## Done → Move to task-9.3-dashboard-page.md
