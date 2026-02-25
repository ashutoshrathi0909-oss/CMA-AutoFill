# Task 9.3: Dashboard Page

> **Phase:** 09 - Frontend Shell
> **Depends on:** Task 9.2 (auth works), Phase 03 Task 3.7 (dashboard stats API)
> **Time estimate:** 20 minutes

---

## Objective

Build the main dashboard showing key metrics, recent projects, and quick actions.

---

## What to Do

### Page
`frontend/app/(dashboard)/dashboard/page.tsx`

### Layout

```
┌─────────────────────────────────────────────┐
│ Welcome back, {name}          [+ New CMA]   │
├──────────┬──────────┬──────────┬────────────┤
│ Active   │ Pending  │ Completed│ This Month │
│ Clients  │ Reviews  │ CMAs     │ Cost       │
│   10     │   8      │   15     │  ₹3.50     │
├──────────┴──────────┴──────────┴────────────┤
│                                             │
│ Projects by Status (horizontal bar/pill)    │
│ ██████████░░░░░░░░  5 Draft  15 Done  2 Err│
│                                             │
├─────────────────────────────────────────────┤
│ Recent Projects                             │
│ ┌─────────────────────────────────────────┐ │
│ │ Mehta Computers 2024-25    ● Completed  │ │
│ │ Updated 2 hours ago     [View] [↓ DL]   │ │
│ ├─────────────────────────────────────────┤ │
│ │ Sharma Textiles 2024-25   ● Reviewing   │ │
│ │ 3 items pending review  [Review Now]    │ │
│ └─────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

### Components

**Stat Cards** (`components/dashboard/stat-card.tsx`):
- Icon + label + value
- Subtle gold border on hover
- Click navigates to relevant page

**Status Bar** (`components/dashboard/status-bar.tsx`):
- Horizontal bar showing project count per status
- Color-coded segments (draft=gray, processing=blue, reviewing=amber, completed=green, error=red)

**Recent Projects Table** (`components/dashboard/recent-projects.tsx`):
- Last 5 projects with: client name, financial year, status badge, updated time
- Action buttons: View, Download (if completed), Review (if reviewing)
- Clicking row navigates to project detail

**Quick Action: "+ New CMA" button**
- Opens a modal or navigates to project creation flow

### Data Fetching

- Call `GET /api/v1/dashboard/stats` on page load
- Use React Query (TanStack Query) or SWR for data fetching with caching
- Show skeleton loaders while data loads
- Auto-refresh every 30 seconds (for processing projects)

### Install Data Fetching Library

```bash
npm install @tanstack/react-query
```

Set up QueryClientProvider in the app layout.

---

## What NOT to Do

- Don't build complex charts (V1 = simple stats and lists)
- Don't implement the "New CMA" flow yet (that's Phase 10)
- Don't make real API calls yet if API client isn't ready (use mock data, wire up in task 9.6)

---

## Verification

- [ ] Dashboard loads with stat cards showing numbers
- [ ] Status bar shows correct project distribution
- [ ] Recent projects list shows last 5 projects
- [ ] Status badges are color-coded correctly
- [ ] Clicking project row navigates to project page
- [ ] Skeleton loaders shown during data fetch
- [ ] Empty state: "No projects yet. Create your first CMA!" with action button
- [ ] Responsive: cards stack on smaller screens

---

## Done → Move to task-9.4-client-list-page.md
