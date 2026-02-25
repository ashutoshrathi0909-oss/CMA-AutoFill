# Task 10.7: Download & Output View

> **Phase:** 10 - Frontend CMA Flow
> **Depends on:** Phase 06 Task 6.6 (generation API), Task 10.6 (validation triggers generation)
> **Time estimate:** 15 minutes

---

## Objective

Build the output tab where CAs download the generated CMA Excel file, view version history, and regenerate if needed.

---

## What to Do

### Component
`components/projects/output-tab.tsx`

### Layout

```
┌──────────────────────────────────────────────────┐
│ Generated CMA                                    │
│                                                  │
│ ┌────────────────────────────────────────────┐   │
│ │  📊 CMA_MehtaComputers_2024-25_v2.xlsx    │   │
│ │  Generated: Feb 25, 2026 at 10:35 AM      │   │
│ │  Size: 245 KB  │  Version: 2              │   │
│ │                                            │   │
│ │  [⬇ Download CMA]  [🔄 Regenerate]       │   │
│ └────────────────────────────────────────────┘   │
│                                                  │
│ Pipeline Summary                                 │
│ ┌────────────────────────────────────────────┐   │
│ │ Total items classified: 45                 │   │
│ │ Auto-classified: 33 (73%)                  │   │
│ │ CA-reviewed: 10 (22%)                      │   │
│ │ Unclassified: 2 (4%)                       │   │
│ │ Validation: Passed (2 warnings)            │   │
│ │ LLM cost: ₹0.35 ($0.004)                  │   │
│ │ Total processing time: 28 seconds          │   │
│ └────────────────────────────────────────────┘   │
│                                                  │
│ Version History                                  │
│ ┌────────────────────────────────────────────┐   │
│ │ v2 — Feb 25, 2026 10:35 AM    [⬇]  Latest│   │
│ │ v1 — Feb 24, 2026 3:20 PM     [⬇]        │   │
│ └────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────┘
```

### Features

**Download Button:**
- Primary gold button
- Calls `GET /files/{id}/download` → gets signed URL → triggers browser download
- Shows file name prominently

**Regenerate Button:**
- Re-runs validation + generation
- Creates new version (v3, v4, etc.)
- Useful if CA corrected review items and wants updated CMA
- Confirmation: "This will create version 3. Continue?"

**Pipeline Summary:**
- Quick stats from the pipeline run
- Classification accuracy breakdown
- Cost in both INR and USD
- Processing time

**Version History:**
- List of all generated versions for this project
- Each version: filename, date, download button
- Latest version highlighted
- Old versions kept for reference

### Data Fetching

- Generated files: `GET /api/v1/projects/{id}/generated`
- Download URL: `GET /api/v1/generated/{file_id}/download`
- Pipeline stats: from project's classification_data + llm_usage_log

---

## What NOT to Do

- Don't auto-download (user clicks when ready)
- Don't delete old versions
- Don't show the Excel preview inline (too complex for V1)

---

## Verification

- [ ] Download button triggers file download in browser
- [ ] File downloads as .xlsx with correct name
- [ ] Regenerate creates new version, appears in history
- [ ] Version history shows all versions with download links
- [ ] Pipeline summary shows correct stats
- [ ] Cost displayed in INR (primary) and USD (secondary)
- [ ] Empty state (no generated file yet): "Generate your CMA first" with button

---

## Phase 10 Complete! 🎉

All 7 tasks done. You now have:
- ✅ Project detail page with pipeline visualization
- ✅ Drag-and-drop file upload
- ✅ Live processing view with step animations
- ✅ Review queue UI (the Ask Father interface)
- ✅ Classification view grouped by CMA sheet
- ✅ Validation results with auto-fix actions
- ✅ Download page with version history

**The complete user journey works end-to-end in the UI!**

**Next → Phase 11: Testing & Production Deploy**
