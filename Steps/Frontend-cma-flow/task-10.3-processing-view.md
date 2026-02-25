# Task 10.3: Processing View (Live Progress)

> **Phase:** 10 - Frontend CMA Flow
> **Depends on:** Task 10.1 (project detail), Phase 08 Task 8.3 (progress API)
> **Time estimate:** 15 minutes

---

## Objective

Build a satisfying processing view that shows the pipeline running in real-time with step-by-step animations.

---

## What to Do

### Component
`components/projects/processing-view.tsx`

This replaces the tab content area when a project is actively processing.

### Layout

```
┌─────────────────────────────────────────────┐
│                                             │
│         🔄 Processing your CMA...           │
│                                             │
│    ████████████████░░░░░░░░░  62%          │
│    Estimated: ~15 seconds remaining         │
│                                             │
│    ✓ Extracting data        2.5s            │
│    ✓ Classifying items      3.1s            │
│    ⏳ Validating numbers     running...      │
│    ○ Generating CMA         pending         │
│                                             │
│    Items extracted: 45                      │
│    Auto-classified: 33 (73%)                │
│    Needs review: 10                         │
│    LLM cost: $0.004                         │
│                                             │
└─────────────────────────────────────────────┘
```

### Features

**Progress Bar:**
- Smooth animated fill (not jumpy)
- Gold color filling on dark background
- Percentage label

**Step List:**
- Each step: icon + name + status + duration
- Completed: green ✓ + time taken
- Running: spinning icon + "running..." (pulsing)
- Pending: gray ○
- Failed: red ✗ + error message

**Live Stats:**
- Update as each step completes
- Items extracted count (after extraction)
- Classification breakdown (after classification)
- Running cost tally

**Polling:**
- Call `GET /projects/{id}/progress` every 2 seconds
- Update UI on each response
- Stop polling when `is_processing = false`

### Completion States

**Pipeline completes (no review needed):**
- Show confetti/celebration animation (subtle)
- "CMA generated successfully!"
- "Download CMA" button

**Pipeline pauses for review:**
- "10 items need your review"
- "Review Now →" button → navigates to Review tab

**Pipeline fails:**
- Show error message from API
- "Retry" button
- Suggestion text from API (e.g., "Check your uploaded files")

---

## What NOT to Do

- Don't use WebSockets (polling is simpler for V1)
- Don't block the page — user can navigate away and come back
- Don't show technical error details (show user-friendly messages)
- Don't poll faster than 2 seconds (unnecessary load)

---

## Verification

- [ ] Start processing → progress view appears
- [ ] Steps complete one by one with animations
- [ ] Progress bar fills smoothly
- [ ] Live stats update after each step
- [ ] Pipeline completes → celebration + download button
- [ ] Pipeline pauses for review → review prompt shown
- [ ] Pipeline fails → error with retry button
- [ ] Navigate away and back → progress still shown correctly
- [ ] Estimated time roughly accurate

---

## Done → Move to task-10.4-review-queue-page.md
