# Phase 10: Frontend CMA Flow

## Objective
Build the complete end-to-end CMA workflow inside the existing frontend shell. Users should be able to:
1. Create a CMA project from the client workspace
2. Upload financial documents (drag & drop)
3. Monitor real-time processing progress
4. Review uncertain AI classifications (Ask Father — THE most important UI)
5. Preview validation results and download the generated CMA Excel

## Tasks (6 sub-tasks, to be split across 6 agents)
1. **Task 10.1** — CMA Detail Page + Pipeline Status
2. **Task 10.2** — File Upload Interface
3. **Task 10.3** — Processing Progress (Real-time polling)
4. **Task 10.4** — Ask Father Review UI ← MOST CRITICAL
5. **Task 10.5** — Preview & Download Page
6. **Task 10.6** — Wiring + React Query Hooks + Type Enhancements

## Design System
Already implemented in Phase 09:
- Dark navy (`#0A1628`) backgrounds, gold (`#D4AF37`) accents
- Inter font, shadcn/ui, Tailwind CSS v4
- All components in `components/ui/`

## Verification Per Task
- `npm run build` must pass with 0 errors
- Browser visual check of each page
- No console errors
