# Phase 10: Frontend CMA Flow — Agent Prompt

> **PURPOSE:** This is the complete specification for Phase 10 of CMA AutoFill. It covers the full CMA workflow UI — from creating a project, uploading documents, monitoring AI processing, reviewing uncertain classifications (Ask Father), and downloading the final CMA Excel. Build EXACTLY what is specified here. 
> 
> **IMPORTANT: You are deploying 6 parallel agents. Read Section 8 (Agent Deployment Strategy) carefully BEFORE starting any work.**

---

## 1. PROJECT CONTEXT

CMA AutoFill is a SaaS product that automates Credit Monitoring Arrangement (CMA) document creation for Indian CA firms. Phase 09 (Frontend Shell) is **COMPLETE** — the app has a working layout, auth, dashboard, client management, and project list. Phase 10 builds the **actual CMA workflow** inside this shell.

### What was built in Phase 09 (DO NOT REBUILD):
- ✅ Dark navy theme (`#0A1628`) + gold accents (`#D4AF37`) in `globals.css`
- ✅ Root layout with `QueryProvider`, `AuthProvider`, `Toaster`
- ✅ Auth flow: login page (magic link), middleware, callback
- ✅ Collapsible sidebar with 6 nav items + header with breadcrumbs
- ✅ Dashboard page with stat cards, status bar, recent projects
- ✅ Clients page with CRUD, search, filters, modals
- ✅ Projects list page with status badges, progress bars, filters
- ✅ Error/empty/skeleton states, 404 page, error boundary
- ✅ Typed API client (`lib/api/client.ts`) with auto auth
- ✅ API functions for all endpoints (`lib/api/*.ts`)
- ✅ React Query hooks (`lib/hooks/use-*.ts`)
- ✅ 15+ shadcn/ui components installed

### What you're building in Phase 10:
The 6-step CMA pipeline UI:
1. **CMA Detail Page** — project workspace showing current step + metadata
2. **File Upload** — drag & drop uploader for Excel/PDF/images
3. **Processing Progress** — real-time pipeline status with polling
4. **Ask Father Review** — CA reviews uncertain AI classifications (THIS IS THE MOST IMPORTANT UI)
5. **Preview & Download** — validation results + CMA Excel download
6. **Hooks & Wiring** — new React Query hooks, type updates, route integration

---

## 2. TECH STACK (Already configured — do NOT change)

| Layer | Technology |
|-------|-----------|
| **Framework** | Next.js 16 (App Router), TypeScript |
| **Styling** | Tailwind CSS v4 (CSS-based config, NOT `tailwind.config.ts`) |
| **Components** | shadcn/ui (new-york style) |
| **Data Fetching** | @tanstack/react-query v5 |
| **Auth** | Supabase (@supabase/supabase-js + @supabase/ssr) |
| **Icons** | Lucide React |
| **Toasts** | Sonner |
| **Backend API** | FastAPI at `http://localhost:8000` (NEXT_PUBLIC_API_URL) |

### Rules:
- **DO NOT modify backend code.** Frontend ONLY.
- **DO NOT modify `globals.css`** — theme is finalized.
- Use App Router (`app/` directory) with `'use client'` for interactive components.
- All components must be TypeScript (`.tsx`).
- Use existing API client (`lib/api/client.ts`), existing types (`lib/api/types.ts`).
- Indian formatting: Lakhs (₹1,00,000), IST timezone, Indian GAAP.
- Functional components only, no class components.
- Use `sonner` for toast notifications (`toast.success`, `toast.error`).

---

## 3. EXISTING FILE STRUCTURE (What you inherit from Phase 09)

```
frontend/
├── app/
│   ├── layout.tsx              # Root: Inter font, providers, dark mode
│   ├── page.tsx                # Redirects to /dashboard
│   ├── globals.css             # CMA dark theme (DO NOT MODIFY)
│   ├── error.tsx               # Error boundary
│   ├── not-found.tsx           # 404 page
│   ├── (auth)/
│   │   ├── layout.tsx          # Centered auth layout
│   │   ├── login/page.tsx      # Magic link login
│   │   └── auth/callback/route.ts
│   └── (dashboard)/
│       ├── layout.tsx          # Sidebar + header + content
│       ├── dashboard/page.tsx  # Stats, status bar, recent projects
│       ├── clients/page.tsx    # Client list + CRUD
│       ├── projects/page.tsx   # Project list + new project modal
│       ├── review/page.tsx     # PLACEHOLDER — replace with full review UI
│       ├── precedents/page.tsx # PLACEHOLDER — keep as-is
│       ├── analytics/page.tsx  # PLACEHOLDER — keep as-is
│       └── settings/page.tsx   # PLACEHOLDER — keep as-is
├── components/
│   ├── layout/ (sidebar, header, breadcrumb, user-menu)
│   ├── dashboard/ (stat-card, status-bar, recent-projects)
│   ├── clients/ (client-form-modal)
│   ├── projects/ (new-project-modal)
│   └── ui/ (badge-count, empty-state, error-state, page-skeleton + 15 shadcn)
├── lib/
│   ├── api/
│   │   ├── client.ts           # Base HTTP client with auth token
│   │   ├── types.ts            # All TypeScript interfaces
│   │   ├── clients.ts          # Client CRUD
│   │   ├── projects.ts         # Project CRUD
│   │   ├── dashboard.ts        # Dashboard stats
│   │   ├── review.ts           # Review queue CRUD
│   │   ├── pipeline.ts         # Process, progress, retry, resume
│   │   ├── files.ts            # Upload, getProjectFiles, getGeneratedFiles
│   │   ├── extraction.ts       # Extraction trigger
│   │   ├── classification.ts   # Classification trigger
│   │   ├── generation.ts       # Generation trigger
│   │   └── index.ts            # Barrel export
│   ├── hooks/
│   │   ├── query-provider.tsx  # React Query provider
│   │   ├── use-clients.ts     # Client hooks
│   │   ├── use-projects.ts    # Project hooks
│   │   ├── use-dashboard.ts   # Dashboard hooks
│   │   └── use-review.ts      # Review hooks
│   ├── auth-context.tsx        # Auth provider + useAuth hook
│   ├── supabase.ts             # Supabase client
│   └── utils.ts                # cn() utility
└── middleware.ts               # Auth route protection
```

---

## 4. BACKEND API ENDPOINTS (Read-only reference)

These endpoints are ALREADY BUILT in the backend. Your job is to call them from the frontend.

### 4.1 Pipeline Endpoints
```
POST   /api/v1/projects/{id}/process      → Start full pipeline (async)
GET    /api/v1/projects/{id}/progress      → Poll pipeline progress
POST   /api/v1/projects/{id}/retry         → Retry failed pipeline
POST   /api/v1/projects/{id}/resume        → Resume after review
```

**Progress response shape:**
```typescript
interface PipelineProgress {
    project_id: string;
    status: ProjectStatus;             // 'extracting' | 'classifying' | 'validating' etc.
    pipeline_progress: number;         // 0-100
    current_step?: string;             // Human-readable step name
    steps: PipelineStep[];
    error_message?: string;
}

interface PipelineStep {
    name: string;
    status: 'pending' | 'running' | 'completed' | 'failed' | 'skipped';
    started_at?: string;
    completed_at?: string;
    error?: string;
}
```

### 4.2 File Endpoints
```
POST   /api/v1/projects/{id}/files        → Upload files (multipart/form-data)
GET    /api/v1/projects/{id}/files         → List uploaded files
GET    /api/v1/projects/{id}/generated-files → List generated CMA files
DELETE /api/v1/files/{file_id}             → Delete uploaded file
```

### 4.3 Review Queue Endpoints
```
GET    /api/v1/review-queue?project_id=xxx&status=pending  → List review items
POST   /api/v1/review-queue/{id}/resolve                   → Resolve single item
POST   /api/v1/review-queue/bulk-resolve                   → Bulk resolve
POST   /api/v1/review-queue/approve-all                    → Accept all AI suggestions
```

**Review item shape:**
```typescript
interface ReviewItem {
    id: string;
    project_id: string;
    source_item_name: string;           // "Rebates & Discounts"
    suggested_category: string;          // "Selling Expenses"
    suggested_subcategory?: string;      // "Row 58"
    confidence: number;                  // 0.0 to 1.0
    classification_source: 'precedent' | 'rule' | 'ai';
    status: 'pending' | 'resolved' | 'auto_approved';
    resolved_category?: string;
    resolved_subcategory?: string;
    resolved_by?: string;
    resolved_at?: string;
}
```

### 4.4 Project Details
```
GET    /api/v1/projects/{id}              → Full project with metadata
PUT    /api/v1/projects/{id}              → Update project
DELETE /api/v1/projects/{id}              → Soft-delete project
```

### 4.5 Download
```
GET    /api/v1/projects/{id}/download     → Download generated CMA Excel
```

---

## 5. DESIGN SYSTEM (Already in globals.css — use these tokens)

```css
/* Backgrounds */
--bg-sidebar: #0D1F3C;           /* Sidebar + header */
--bg-card: #1A2A44;              /* Cards, modals */
--background: #0A1628;           /* Page background */

/* Gold accent */
--gold: #D4AF37;                 /* Primary action, badges */
--gold-hover: #E5C04B;           /* Hover state */

/* Status colors (use directly, not as CSS variables) */
Draft:      bg-gray-500/20 text-gray-300
Processing: bg-blue-500/20 text-blue-300 (add animate-pulse-soft)
Reviewing:  bg-amber-500/20 text-amber-300
Completed:  bg-green-500/20 text-green-300
Error:      bg-red-500/20 text-red-300

/* Semantic */
--success: #22C55E;
--warning: #F59E0B;
--destructive: #EF4444;
```

### Available CSS animation classes:
- `animate-pulse-soft` — subtle pulsing for processing states
- `animate-fade-in` — fade-in on page load
- `card-hover-glow` — gold glow on card hover

### Card pattern:
```tsx
<div className="rounded-xl border border-border/20 p-6" style={{ backgroundColor: 'var(--bg-card)' }}>
  {/* content */}
</div>
```

---

## 6. TASKS — DETAILED SPECIFICATIONS

---

### Task 10.1: CMA Detail Page + Pipeline Status

**Goal:** Create the project workspace page at `/projects/[id]` that shows the current CMA state and acts as the hub for all pipeline operations.

**New files to create:**
```
app/(dashboard)/projects/[id]/page.tsx           # Main CMA detail page
components/cma/cma-header.tsx                     # Project title, client, FY, status badge
components/cma/pipeline-stepper.tsx                # Visual stepper showing 5 pipeline steps
components/cma/cma-metadata.tsx                    # Bank, loan type, amount, dates panel
```

**CMA Detail Page Layout:**
```
┌────────────────────────────────────────────────────┐
│ ← Back to Projects  │  CMA: Mehta Computers (FY 2024-25)  │  Status Badge  │
├────────────────────────────────────────────────────┤
│                                                    │
│  ┌──────────────────────────────────────────────┐  │
│  │  Pipeline Stepper (5 steps — horizontal)     │  │
│  │  [Upload] → [Extract] → [Classify] → [Review] → [Generate]  │
│  │   ✅         ✅          🔄 Running    ○ Pending   ○ Pending   │
│  └──────────────────────────────────────────────┘  │
│                                                    │
│  ┌──────── Tab Navigation ─────────┐              │
│  │ Files (3) │ Progress │ Review (5) │ Download │  │
│  └─────────────────────────────────┘              │
│                                                    │
│  ┌── Content area (changes per active tab) ──────┐ │
│  │                                                │ │
│  │  [Tab content rendered here]                   │ │
│  │                                                │ │
│  └────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────┘
```

**Pipeline Stepper Design:**
- 5 circles connected by lines: Upload → Extract → Classify → Review → Generate
- States: `completed` (green ✓), `running` (gold pulsing), `pending` (gray outline), `failed` (red ✗), `skipped` (gray dash)
- The currently running step should have a `animate-pulse-soft` gold ring
- Clicking a completed step shows its details in a tooltip

**Action Buttons (context-dependent):**
| Project Status | Primary Action |
|---|---|
| `draft` (files uploaded) | "Process CMA" button (gold) |
| `extracting/classifying/validating/generating` | Spinner + "Processing..." (disabled) |
| `reviewing` | "Review Items (5)" button (amber) |
| `completed` | "Download CMA" button (green) |
| `error` | "Retry" button (red outline) |

**Metadata Panel (sidebar or card below stepper):**
- Client name, Entity type, Financial year
- Bank name, Loan type, Loan amount (formatted in ₹ Lakhs)
- Created date, Last updated
- File count, Review items count

**Install shadcn component if needed:** `tabs` (for the tab navigation)

---

### Task 10.2: File Upload Interface

**Goal:** Drag-and-drop file uploader with file list management.

**New files to create:**
```
components/cma/file-uploader.tsx                  # Drag & drop zone + file picker
components/cma/file-list.tsx                      # Uploaded files table with actions
```

**File Uploader Design:**
```
┌─────────────────────────────────────────────────┐
│                                                 │
│        ┌──── Drop Zone (dashed border) ────┐    │
│        │                                   │    │
│        │   📄 Drag & drop files here       │    │
│        │   or click to browse              │    │
│        │                                   │    │
│        │   Supports: Excel, PDF, Images    │    │
│        │   Max 10 files, 25MB each         │    │
│        │                                   │    │
│        └───────────────────────────────────┘    │
│                                                 │
│  ┌── Uploaded Files ──────────────────────────┐  │
│  │ Filename         │ Type    │ Size  │ ✕     │  │
│  │ tally_pl.xlsx    │ Excel   │ 1.2MB │ ✕     │  │
│  │ balance_sheet.pdf│ PDF     │ 3.4MB │ ✕     │  │
│  └────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

**Implementation Details:**
- Use native HTML5 drag & drop (`onDragEnter`, `onDragOver`, `onDrop`) for the drop zone
- Accept: `.xlsx`, `.xls`, `.pdf`, `.png`, `.jpg`, `.jpeg`, `.tiff`
- Max file size: 25MB per file, max 10 files per project
- Show upload progress per file with a slim progress bar
- Show file type icons: 📊 Excel, 📄 PDF, 🖼️ Image
- Allow removing files (DELETE `/api/v1/files/{file_id}`)
- After all files uploaded, show "Process CMA" button
- On drag-over, change border to gold with subtle glow
- On upload error, show toast + inline error badge on the file

**File List Columns:**
| Column | Content |
|---|---|
| File icon | 📊 / 📄 / 🖼️ based on mime type |
| Filename | Original filename, truncate if long |
| Type | Excel / PDF / Image |
| Size | Human-readable (KB/MB) |
| Status | Uploaded ✓ / Uploading... / Error ✗ |
| Actions | Delete button |

---

### Task 10.3: Processing Progress (Real-time Polling)

**Goal:** Show real-time pipeline progress when a CMA is being processed.

**New files to create:**
```
components/cma/processing-progress.tsx            # Full processing UI with steps + logs
lib/hooks/use-pipeline.ts                          # React Query hook with polling
```

**Processing Progress Design:**
```
┌─────────────────────────────────────────────────┐
│  Processing Your CMA                            │
│                                                 │
│  ┌── Overall Progress ─────────────────────┐    │
│  │  ████████████░░░░░░░░  65%              │    │
│  └─────────────────────────────────────────┘    │
│                                                 │
│  ┌── Step Details ─────────────────────────┐    │
│  │ ✅ Extraction       Completed  (12.3s)  │    │
│  │ ✅ Classification   Completed  (8.7s)   │    │
│  │ 🔄 Validation       Running... (3.2s)   │    │
│  │ ○  Review           Pending             │    │
│  │ ○  Generation       Pending             │    │
│  └─────────────────────────────────────────┘    │
│                                                 │
│  Current Step: Validating balance sheet...      │
│                                                 │
│  [Cancel] (outline)                             │
└─────────────────────────────────────────────────┘
```

**Implementation Details:**
- **Polling:** Use React Query with `refetchInterval: 2000` (2 second intervals) while status is processing
- **Stop polling** when status is `completed`, `reviewing`, or `error`
- Progress bar should animate smoothly (CSS transition on width)
- Each step shows: icon (✅/🔄/○/✗), name, status, duration
- Running step has gold pulsing animation
- When pipeline completes:
  - If no review items → auto-switch to Download tab with success toast
  - If review items exist → auto-switch to Review tab with amber toast ("5 items need your review")
- On error → show error message, "Retry" button, and "View Logs" expandable
- Show estimated time remaining if possible (based on step durations)

**`use-pipeline.ts` Hook:**
```typescript
// This hook should:
// 1. Poll GET /projects/{id}/progress every 2 seconds
// 2. Stop polling when status is terminal (completed/error/reviewing)
// 3. Expose: data, isLoading, error, isProcessing, startProcessing, retryProcessing
// 4. startProcessing calls POST /projects/{id}/process
// 5. retryProcessing calls POST /projects/{id}/retry
// 6. resumeProcessing calls POST /projects/{id}/resume (after review)
```

---

### Task 10.4: Ask Father Review UI ← THE MOST IMPORTANT PAGE

**Goal:** The review interface where CAs decide on uncertain AI classifications. This is THE key differentiator of CMA AutoFill. It must be intuitive, fast, and professional.

**New files to create:**
```
app/(dashboard)/review/page.tsx                   # REPLACE the placeholder — full review page
components/review/review-card.tsx                 # Individual review item card
components/review/review-toolbar.tsx               # Bulk actions bar
components/review/confidence-bar.tsx               # Visual confidence indicator
components/review/category-selector.tsx            # Dropdown to pick correct CMA category
components/review/review-filters.tsx               # Filter by project, status, confidence
```

**Review Page Layout:**
```
┌────────────────────────────────────────────────────────────────┐
│ Review Queue                                    │ 5 pending   │
├────────────────────────────────────────────────────────────────┤
│ Filters: [Project ▼] [Status ▼] [Confidence ▼]  │ Bulk Actions│
│          [Search items...]                        [✓ All AI]   │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌── Review Card ──────────────────────────────────────────┐   │
│  │                                                          │   │
│  │  "Rebates & Discounts"                  ₹2,45,000       │   │
│  │  Source: Profit & Loss                                   │   │
│  │                                                          │   │
│  │  AI Suggestion:  Selling Expenses (Row 58)               │   │
│  │  Confidence: ████████░░ 82%  [Medium]                    │   │
│  │  Source: rule                                            │   │
│  │                                                          │   │
│  │  ┌── Your Decision ────────────────────────────────┐     │   │
│  │  │ [Accept AI ✓]  or  Choose Category: [▼ Row 58 - Selling Expenses]  │   │
│  │  │                    Reasoning: [____________]     │     │   │
│  │  │                    [✓ Save as precedent]         │     │   │
│  │  │                    [Submit ▶]                    │     │   │
│  │  └─────────────────────────────────────────────────┘     │   │
│  │                                                          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                │
│  ┌── Review Card 2 ─────────────────────────────────────────┐  │
│  │  ...                                                      │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌── Pagination ────────────────────────────────────────────┐  │
│  │  Showing 1-10 of 5 items  │  [Previous] [1] [2] [Next]  │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

**Review Card — DETAILED SPEC:**

Each card shows:
1. **Item name** — big, bold, prominent (e.g., "Rebates & Discounts")
2. **Amount** — formatted in ₹ Lakhs (e.g., ₹2,45,000)
3. **Source document type** — where it was extracted from (P&L / BS / TB)
4. **AI Suggestion** — the CMA category AI chose, with row number
5. **Confidence bar** — visual bar from 0-100%, color-coded:
   - ≥90% = green (HIGH) — show "Accept AI ✓" button prominently
   - 70-89% = amber (MEDIUM)
   - <70% = red (LOW) — show alternatives more prominently
6. **Classification source** — "rule" (blue badge), "ai" (purple badge), "precedent" (green badge)
7. **Decision section:**
   - "Accept AI Suggestion" button (one-click for high confidence)
   - OR Category dropdown selector (searchable, show row number + label)
   - Optional: reasoning text field
   - Checkbox: "Save as precedent" (default checked for first occurrence)
   - Submit button

**Bulk Actions Toolbar:**
- Checkbox on each card for multi-select
- "Accept All AI" button — resolves all selected with AI suggestion
- "Accept All" (for all pending items with confidence ≥ 90%)
- Item count indicator: "3 of 5 selected"

**Confidence Bar Component:**
```tsx
// Visual: horizontal bar, color transitions from red → amber → green
// Below bar: percentage text + label (LOW/MEDIUM/HIGH)
// Width animates on mount
```

**Category Selector (CMA Row Picker):**
- Searchable dropdown
- Groups: "Income", "Expenses", "Assets", "Liabilities", "Other"
- Each option shows: Row number + Label (e.g., "Row 58 — Selling Expenses")
- Show the AI suggestion first, highlighted in gold
- Install shadcn `command` component if needed for the searchable combobox

**After ALL reviews resolved:**
- Show success message: "All items reviewed! Generating CMA..."
- Auto-trigger pipeline resume (`POST /projects/{id}/resume`)
- Switch to Processing Progress tab

---

### Task 10.5: Preview & Download Page

**Goal:** Show validation results and provide download for the generated CMA Excel.

**New files to create:**
```
components/cma/validation-results.tsx              # Validation errors/warnings display
components/cma/download-section.tsx                 # Download button + file info
```

**Validation Results Display:**
```
┌─────────────────────────────────────────────────┐
│  Validation Results                             │
│                                                 │
│  ✅ Balance Sheet Balanced       (All years)    │
│  ✅ P&L Arithmetic Correct       (All years)    │
│  ⚠️  Selling Expenses increased 350% YoY       │
│  ❌ Missing: Trade Creditors for FY 2023-24     │
│                                                 │
│  Summary: 56 items classified                   │
│           48 auto-classified                    │
│           8 reviewed by CA                      │
└─────────────────────────────────────────────────┘
```

**Download Section:**
```
┌─────────────────────────────────────────────────┐
│  🎉 CMA Ready for Download                     │
│                                                 │
│  ┌──────────────────────────────────────────┐   │
│  │ 📊 CMA_MehtaComputers_FY2024-25.xlsm    │   │
│  │    Generated: 28 Feb 2026, 3:15 PM IST   │   │
│  │    Size: 245 KB                           │   │
│  │                                           │   │
│  │    [⬇ Download CMA]  [🔄 Regenerate]     │   │
│  └──────────────────────────────────────────┘   │
│                                                 │
│  Version History (if re-generated):             │
│  • v2 — 28 Feb 2026 (current)                  │
│  • v1 — 27 Feb 2026                            │
└─────────────────────────────────────────────────┘
```

**Implementation Details:**
- Download button triggers `GET /projects/{id}/download` and saves as blob
- Use `window.URL.createObjectURL()` and anchor click pattern for download
- Show validation errors (red bg) vs warnings (amber bg) distinctly
- If there are critical errors, show warning before download
- "Regenerate" button re-triggers generation stage

---

### Task 10.6: Wiring + React Query Hooks + Type Enhancements

**Goal:** Create all the connecting pieces — new hooks, type updates, navigation wiring.

**New/Updated files:**
```
lib/hooks/use-pipeline.ts                       # NEW — pipeline polling hook
lib/hooks/use-files.ts                          # NEW — file upload/list hooks
lib/api/types.ts                                # UPDATE — add new types for download, validation
lib/api/files.ts                                # UPDATE — add deleteFile function
lib/api/pipeline.ts                             # UPDATE — add download function
```

**New hooks to create:**

```typescript
// use-pipeline.ts
export function usePipelineProgress(projectId: string) { ... }    // Polls every 2s
export function useStartProcessing() { ... }                       // Mutation
export function useRetryProcessing() { ... }                       // Mutation
export function useResumeProcessing() { ... }                      // Mutation

// use-files.ts  
export function useProjectFiles(projectId: string) { ... }        // Query
export function useUploadFiles() { ... }                           // Mutation
export function useDeleteFile() { ... }                            // Mutation
export function useGeneratedFiles(projectId: string) { ... }      // Query
```

**API types to add/update in `types.ts`:**
```typescript
// Add to files.ts API
export async function deleteFile(fileId: string): Promise<void>;
export async function downloadCMA(projectId: string): Promise<Blob>;

// Add to types.ts
export interface DownloadInfo {
    filename: string;
    file_size: number;
    generated_at: string;
    version: number;
}
```

**Route Integration:**
- Clicking a project row in the projects list page → navigates to `/projects/[id]`
- The project detail page tabs load the correct content per tab
- Review page should support `?project_id=xxx` query param to filter
- Download actions throughout the app should work consistently

---

## 7. ADDITIONAL shadcn COMPONENTS TO INSTALL

Some of these may already be installed. Only install what's missing:

```bash
npx shadcn@latest add tabs
npx shadcn@latest add progress
npx shadcn@latest add command
```

- `tabs` — for CMA detail page tab navigation
- `progress` — for pipeline progress bar
- `command` — for searchable CMA category selector in review

---

## 8. AGENT DEPLOYMENT STRATEGY — READ THIS FIRST

You are deploying **6 parallel agents**. Each agent works on an independent set of files to avoid merge conflicts. Here is the optimal split:

### Agent Team Overview

| Agent | Name | Scope | Files Owned | Dependencies |
|-------|------|-------|-------------|-------------|
| **1** | Foundation Agent | CMA detail page + stepper | `app/(dashboard)/projects/[id]/page.tsx`, `components/cma/cma-header.tsx`, `components/cma/pipeline-stepper.tsx`, `components/cma/cma-metadata.tsx` | None — can start immediately |
| **2** | Upload Agent | File upload + file list | `components/cma/file-uploader.tsx`, `components/cma/file-list.tsx`, `lib/hooks/use-files.ts` | None — can start immediately |
| **3** | Progress Agent | Processing progress UI | `components/cma/processing-progress.tsx`, `lib/hooks/use-pipeline.ts` | None — can start immediately |
| **4** | Review Agent | Ask Father review UI (MOST IMPORTANT) | `app/(dashboard)/review/page.tsx` (REPLACE), `components/review/review-card.tsx`, `components/review/review-toolbar.tsx`, `components/review/confidence-bar.tsx`, `components/review/category-selector.tsx`, `components/review/review-filters.tsx` | None — can start immediately |
| **5** | Download Agent | Preview, validation, download | `components/cma/validation-results.tsx`, `components/cma/download-section.tsx` | None — can start immediately |
| **6** | Wiring Agent | Hooks, types, API updates, navigation | `lib/api/types.ts` (UPDATE), `lib/api/files.ts` (UPDATE), `lib/api/pipeline.ts` (UPDATE), route integration, install missing shadcn components | Runs FIRST because other agents import from here |

### How to Deploy Agents

**Step 1: Start Agent 6 (Wiring) FIRST**
This agent updates shared types and API functions that other agents import. It should:
1. Install missing shadcn components (`tabs`, `progress`, `command`)
2. Add new types to `lib/api/types.ts` (DownloadInfo, etc.)
3. Add `deleteFile()` and `downloadCMA()` to API functions
4. Create `lib/hooks/use-pipeline.ts` and `lib/hooks/use-files.ts`
5. Commit when done → other agents can proceed

**Step 2: Start Agents 1–5 in PARALLEL** (after Agent 6 finishes)
Each agent works in its own directory:
- Agent 1: `app/(dashboard)/projects/[id]/` + `components/cma/cma-header.tsx`, `pipeline-stepper.tsx`, `cma-metadata.tsx`
- Agent 2: `components/cma/file-uploader.tsx`, `file-list.tsx`
- Agent 3: `components/cma/processing-progress.tsx`
- Agent 4: `app/(dashboard)/review/page.tsx` + `components/review/*`
- Agent 5: `components/cma/validation-results.tsx`, `download-section.tsx`

**Step 3: Integration Agent (You, the orchestrator)**
After all 5 agents finish, YOU:
1. Wire up the project detail page tabs to render each agent's components
2. Run `npm run build` to verify 0 errors
3. Run `npm run dev` and browser-test each page
4. Fix any import or integration issues

### ⚠️ CRITICAL RULES FOR PARALLEL AGENTS
1. **NO agent modifies `globals.css`** — theme is finalized
2. **NO agent modifies the root `layout.tsx`** — already configured
3. **NO agent modifies files owned by another agent** — avoid conflicts
4. **Agent 6 runs FIRST** to create shared types/hooks
5. **Each agent must run `npm run build`** before declaring done
6. **Each agent imports only from existing shared files** (`lib/api/*`, `lib/hooks/*`, `components/ui/*`)
7. **Use relative imports** only within your own component folder; use `@/` alias for shared imports

---

## 9. ACCEPTANCE CRITERIA

### Per-Agent Verification
Each agent must verify:
- [ ] `npm run build` passes with 0 TypeScript errors
- [ ] Component renders correctly in the browser (visual check)
- [ ] No console errors
- [ ] All API calls use existing typed API client
- [ ] Toast notifications for success/error states
- [ ] Loading/error/empty states handled
- [ ] Mobile responsive (sidebar collapses, content reflows)

### Integration Verification (After all agents)
- [ ] Can navigate from Projects list → Project Detail → each tab
- [ ] File upload drag & drop works, shows progress
- [ ] "Process CMA" triggers pipeline, progress polls in real-time
- [ ] Review page shows items with confidence bars and category selector
- [ ] "Accept AI" and bulk actions work correctly
- [ ] After all reviews → pipeline resumes → CMA downloads
- [ ] Error/retry flows work end-to-end
- [ ] `npm run build` passes with 0 errors

### Design Verification
- [ ] Dark navy backgrounds throughout
- [ ] Gold accents on primary actions and active states
- [ ] Status badges match the color scheme
- [ ] Animations: pulse for processing, fade-in for pages
- [ ] Cards use `var(--bg-card)` with `border-border/20`
- [ ] Typography: Inter font, proper hierarchy
- [ ] Indian formatting: ₹ Lakhs, IST dates

---

## 10. WHAT NOT TO DO

- ❌ Do NOT modify backend Python code
- ❌ Do NOT modify `globals.css` or the design system
- ❌ Do NOT create new shadcn components from scratch — install via `npx shadcn@latest add`
- ❌ Do NOT use `getServerSideProps` or `getStaticProps` — use App Router patterns only
- ❌ Do NOT hardcode API URLs — use `NEXT_PUBLIC_API_URL` env variable (already set up)
- ❌ Do NOT create separate pages for each pipeline step — use tabs within the project detail page
- ❌ Do NOT rebuild existing components (sidebar, header, dashboard, client pages)
- ❌ Do NOT install new CSS frameworks (no Tailwind v3, no Chakra, no MUI)

---

## END OF PROMPT

Follow this specification exactly. The Ask Father review UI (Task 10.4) is the most critical — it's what CA firms will use daily. Make it intuitive, fast, and beautiful.
