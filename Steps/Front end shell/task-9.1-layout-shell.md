# Task 9.1: App Layout Shell

> **Phase:** 09 - Frontend Shell
> **Depends on:** Phase 01 (Next.js app exists with Tailwind + shadcn/ui)
> **Agent reads:** CLAUDE.md → Frontend Architecture, Coding Standards → TypeScript
> **Time estimate:** 20 minutes

---

## Objective

Create the main app layout with sidebar navigation, header, and content area. This is the container for every page in the app.

---

## What to Do

### Design System

**Color palette (dark financial SaaS):**
- Background: `#0A1628` (dark navy)
- Sidebar: `#0D1F3C` (slightly lighter navy)
- Cards: `#1A2A44` (card surfaces)
- Primary accent: `#D4AF37` (gold)
- Text primary: `#F1F5F9` (off-white)
- Text secondary: `#94A3B8` (muted gray)
- Success: `#22C55E`
- Error: `#EF4444`
- Warning: `#F59E0B`

Add these as CSS variables in `globals.css` and configure in `tailwind.config.ts`.

### Layout Structure

File: `frontend/app/(dashboard)/layout.tsx`

```
┌──────────────────────────────────────────┐
│ ┌────────┐ ┌────────────────────────────┐│
│ │        │ │ Header (firm name, user,   ││
│ │Sidebar │ │ notifications bell)        ││
│ │        │ ├────────────────────────────┤│
│ │ Logo   │ │                            ││
│ │        │ │                            ││
│ │ Nav    │ │   Page Content             ││
│ │ items  │ │                            ││
│ │        │ │                            ││
│ │        │ │                            ││
│ │        │ │                            ││
│ │ ────── │ │                            ││
│ │ User   │ │                            ││
│ │ menu   │ │                            ││
│ └────────┘ └────────────────────────────┘│
└──────────────────────────────────────────┘
```

### Sidebar Navigation

Items:
1. **Dashboard** — icon: LayoutDashboard → `/dashboard`
2. **Clients** — icon: Users → `/clients`
3. **CMA Projects** — icon: FileSpreadsheet → `/projects`
4. **Review Queue** — icon: ClipboardCheck → `/review` (with badge count for pending items)
5. **Precedents** — icon: BookOpen → `/precedents`
6. **Analytics** — icon: BarChart → `/analytics`

Bottom:
- **Settings** — icon: Settings → `/settings`
- **User menu** — avatar + name + role, dropdown with sign out

### Sidebar Features

- Collapsible (toggle button, remember state in localStorage)
- Active item highlighted with gold accent
- Badge on "Review Queue" showing pending count (fetch from API)
- Responsive: on mobile, sidebar becomes a slide-out drawer

### Header

- Breadcrumb: `Dashboard > Clients > Mehta Computers`
- Right side: notification bell (future), user avatar dropdown
- Firm name displayed subtly

### Components to Create

- `components/layout/sidebar.tsx`
- `components/layout/header.tsx`
- `components/layout/breadcrumb.tsx`
- `components/layout/user-menu.tsx`
- `components/ui/badge-count.tsx` (for review queue count)

### shadcn/ui Components to Install

```bash
npx shadcn-ui@latest add button avatar dropdown-menu sheet tooltip badge separator
```

---

## What NOT to Do

- Don't build page content (just the shell/container)
- Don't implement auth yet (task 9.2)
- Don't fetch real data yet (task 9.6)
- Don't build mobile-first — desktop is primary for CAs working on computers

---

## Verification

- [ ] App renders with sidebar + header + empty content area
- [ ] All 6 navigation items visible with correct icons
- [ ] Clicking nav items routes to correct pages (pages can be empty)
- [ ] Sidebar collapses/expands smoothly
- [ ] Active nav item has gold highlight
- [ ] User menu dropdown opens (with mock data for now)
- [ ] Responsive: sidebar becomes drawer on mobile
- [ ] Colors match design system (dark navy + gold)
- [ ] No console errors

---

## Done → Move to task-9.2-auth-flow.md
