# Task 9.7: Error States, Loading, & Toast Notifications

> **Phase:** 09 - Frontend Shell
> **Depends on:** Tasks 9.1-9.6 (all pages and API client exist)
> **Time estimate:** 15 minutes

---

## Objective

Ensure every page handles loading, empty, and error states gracefully. Add a toast notification system for action feedback.

---

## What to Do

### Install
```bash
npx shadcn-ui@latest add toast skeleton alert-dialog
```

### Toast Notification System

File: `components/ui/toast-provider.tsx`

Using shadcn toast (or sonner):
- Success: green accent — "Client created successfully"
- Error: red accent — "Failed to save. Please try again."
- Info: blue accent — "Pipeline started. You'll be notified when complete."
- Warning: amber accent — "3 items need review before CMA generation."

Show toast after every API mutation (create, update, delete, process).

### Loading States

Create: `components/ui/page-skeleton.tsx`

Skeleton patterns for each page type:
- **Dashboard:** stat card skeletons (4 rectangles) + table skeleton
- **List page:** table header + 5 skeleton rows
- **Detail page:** header skeleton + content blocks

Use shadcn `<Skeleton>` component. Show while `useQuery` isLoading.

### Empty States

Create: `components/ui/empty-state.tsx`

Reusable empty state with:
- Illustration or icon (subtle, matching dark theme)
- Title: "No clients yet"
- Description: "Add your first client to start creating CMAs"
- Action button: "Add Client"

Each page gets a contextual empty state:
- Clients: "No clients yet" → Add Client
- Projects: "No CMA projects yet" → New CMA Project
- Review Queue: "All caught up! No items need review." (positive state)
- Precedents: "No precedents yet. They'll appear as you review items."

### Error States

Create: `components/ui/error-state.tsx`

- API error: "Something went wrong. Please try again." + Retry button
- Not found: "This page doesn't exist." + Go to Dashboard
- Unauthorized: redirect to login
- Network error: "Can't connect to server. Check your connection."

### Error Boundary

Create: `frontend/app/error.tsx` (Next.js error boundary)

Catches unhandled errors and shows a clean error page with retry option.

### Apply to All Existing Pages

Go through dashboard, clients, projects pages and ensure:
- Loading → skeleton shown
- Empty → empty state shown
- Error → error state with retry
- Success action → toast shown

---

## What NOT to Do

- Don't show raw error messages to users (sanitize backend errors)
- Don't leave any page without a loading state
- Don't use browser alert() — always use toast
- Don't show empty tables with "No data" text — use proper empty state component

---

## Verification

- [ ] Every page shows skeleton while loading
- [ ] Every list page shows empty state when no data
- [ ] API error → error state with retry button
- [ ] Create client → success toast appears
- [ ] Delete action → confirmation dialog first, then toast
- [ ] Network disconnect → "Can't connect" error state
- [ ] Unhandled error → error boundary catches it, shows clean page
- [ ] Toast auto-dismisses after 4 seconds

---

## Phase 09 Complete! 🎉

All 7 tasks done. You now have:
- ✅ Premium dark theme layout with sidebar navigation
- ✅ Magic link authentication with session management
- ✅ Dashboard with real metrics from API
- ✅ Client management (list, search, create, edit)
- ✅ Project list with status badges and quick actions
- ✅ Typed API client with React Query hooks
- ✅ Polished loading, empty, and error states everywhere

**Next → Phase 10: Frontend CMA Flow (the main user workflow)**
