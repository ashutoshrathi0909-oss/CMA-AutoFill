# CMA AutoFill — Complete Technical Blueprint for Claude Code

> **PURPOSE:** This is the complete specification for building the CMA AutoFill MVP. Follow it exactly. Every table, endpoint, file, and prompt is specified. Build in the exact order listed in Section 7.

---

## 1. PRODUCT OVERVIEW

**What it does:** Automates Credit Monitoring Arrangement (CMA) document creation for Indian Chartered Accountant (CA) firms. CAs upload financial statements (P&L, Balance Sheet, Trial Balance), AI extracts and classifies line items into the CMA template, a CA reviews uncertain items, and the system generates a completed CMA Excel file.

**6-Step Pipeline:**
1. **Document Ingestion** — Upload Excel/PDF/image files
2. **Extraction** — AI reads the document, extracts line items with amounts
3. **Classification** — AI maps each line item to the correct CMA row (384 rules)
4. **Validation** — Check: BS balances, P&L arithmetic, completeness
5. **Excel Writer** — Write values into CMA .xlsm template (ALREADY BUILT)
6. **Ask Father Interface** — CA reviews uncertain items, decisions become precedents

**Users:** Initially 1 CA firm (2 users: admin CA + junior staff). Multi-tenant SaaS later.

**Constraints:**
- Indian accounting: Lakhs format (₹1L = ₹100,000), Indian GAAP
- Input formats: Tally Excel, Busy Excel, digital PDFs, scanned PDFs, images
- Accuracy target: >95% (banks reject CMA errors)
- Budget: ₹460/month infrastructure max

---

## 2. TECH STACK (FINAL)

| Layer | Technology | Cost |
|-------|-----------|------|
| **Frontend** | Next.js 15 + shadcn/ui + TanStack Query | — |
| **Frontend Hosting** | Cloudflare Pages (free, unlimited bandwidth) | ₹0 |
| **Backend** | FastAPI (Python 3.12) | — |
| **Backend Hosting** | Railway Hobby ($5/month) | ₹420 |
| **Database** | Supabase PostgreSQL (free tier, Mumbai region) | ₹0 |
| **Auth** | Supabase Auth (email magic link + Google OAuth) | ₹0 |
| **File Storage** | Supabase Storage | ₹0 |
| **LLM - Extraction** | Gemini 2.0 Flash (Google AI Studio free tier) | ₹0 |
| **LLM - Classification** | Gemini 3 Flash ($0.50/$3.00 per MTok) | ~₹40/mo |
| **LLM - Fallback** | Gemini 3.1 Pro ($2/$12 per MTok) | as needed |
| **Email** | Resend (3K emails/month free) | ₹0 |
| **Error Tracking** | Sentry (free developer plan) | ₹0 |
| **Payments** | Razorpay (build later, 2% + GST) | ₹0 now |
| **TOTAL** | | **~₹460/month** |

**API Keys needed before building:**
- `GOOGLE_AI_API_KEY` — From Google AI Studio (free)
- `SUPABASE_URL` + `SUPABASE_ANON_KEY` + `SUPABASE_SERVICE_KEY` — From Supabase dashboard
- `RESEND_API_KEY` — From Resend dashboard (free)
- `SENTRY_DSN` — From Sentry dashboard (free)

---

## 3. DATABASE SCHEMA

**Multi-tenant approach:** Single database, every table has `firm_id`, Supabase RLS ensures isolation.

### 3.1 SQL Schema (Run this in Supabase SQL Editor)

```sql
-- ============================================================
-- CMA AutoFill Database Schema
-- Run in Supabase SQL Editor (in order)
-- ============================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For fuzzy text matching on precedents

-- ============================================================
-- FIRMS (Top-level tenant)
-- ============================================================
CREATE TABLE firms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    gst_number TEXT,
    contact_email TEXT,
    contact_phone TEXT,
    plan TEXT DEFAULT 'free' CHECK (plan IN ('free', 'basic', 'pro')),
    max_cmas_per_month INT DEFAULT 5,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- USERS (CAs and staff within a firm)
-- ============================================================
CREATE TABLE users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    firm_id UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'staff' CHECK (role IN ('admin', 'staff', 'readonly')),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_users_firm ON users(firm_id);

-- ============================================================
-- CLIENTS (Businesses whose CMAs are prepared)
-- ============================================================
CREATE TABLE clients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    firm_id UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    pan TEXT,                    -- PAN number
    entity_type TEXT CHECK (entity_type IN ('proprietorship', 'partnership', 'pvt_ltd', 'ltd', 'llp', 'trust', 'other')),
    industry TEXT CHECK (industry IN ('trading', 'manufacturing', 'services', 'mixed')),
    notes TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_clients_firm ON clients(firm_id);

-- ============================================================
-- CMA PROJECTS (Each CMA document being prepared)
-- ============================================================
CREATE TABLE cma_projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    firm_id UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    created_by UUID REFERENCES users(id),
    
    -- CMA metadata
    financial_year TEXT NOT NULL,           -- e.g., "2024-25"
    assessment_year TEXT,                   -- e.g., "2025-26"
    num_historical_years INT DEFAULT 2,    -- How many past years (1-3)
    num_projected_years INT DEFAULT 2,     -- How many projected years (1-3)
    currency TEXT DEFAULT 'INR',
    units TEXT DEFAULT 'Lakhs',
    
    -- Status tracking
    status TEXT DEFAULT 'created' CHECK (status IN (
        'created',          -- Just created, no files yet
        'uploaded',         -- Files uploaded, not processed
        'extracting',       -- AI extracting data
        'extracted',        -- Extraction complete
        'classifying',      -- AI classifying items
        'classified',       -- Classification complete
        'review_pending',   -- Items in Ask Father queue
        'reviewing',        -- CA is reviewing
        'validated',        -- Validation passed
        'generating',       -- Excel being generated
        'completed',        -- CMA ready for download
        'error'             -- Something failed
    )),
    
    -- Pipeline data (JSONB for flexibility)
    extracted_data JSONB,       -- Output of extraction step
    classified_data JSONB,      -- Output of classification step
    validation_result JSONB,    -- Output of validation step
    
    -- Error tracking
    error_message TEXT,
    error_step TEXT,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);
CREATE INDEX idx_cma_firm ON cma_projects(firm_id);
CREATE INDEX idx_cma_client ON cma_projects(client_id);
CREATE INDEX idx_cma_status ON cma_projects(status);

-- ============================================================
-- UPLOADED FILES (Source documents)
-- ============================================================
CREATE TABLE uploaded_files (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    firm_id UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    cma_id UUID NOT NULL REFERENCES cma_projects(id) ON DELETE CASCADE,
    uploaded_by UUID REFERENCES users(id),
    
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL CHECK (file_type IN ('excel', 'pdf', 'image')),
    document_type TEXT CHECK (document_type IN ('profit_loss', 'balance_sheet', 'trial_balance', 'schedules', 'other')),
    storage_path TEXT NOT NULL,       -- Supabase Storage path
    file_size_bytes BIGINT,
    mime_type TEXT,
    
    -- Extraction status for this specific file
    extraction_status TEXT DEFAULT 'pending' CHECK (extraction_status IN ('pending', 'processing', 'completed', 'failed')),
    extracted_items JSONB,            -- Extracted line items from this file
    extraction_error TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_files_cma ON uploaded_files(cma_id);

-- ============================================================
-- GENERATED FILES (Output CMA Excel files)
-- ============================================================
CREATE TABLE generated_files (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    firm_id UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    cma_id UUID NOT NULL REFERENCES cma_projects(id) ON DELETE CASCADE,
    
    filename TEXT NOT NULL,
    storage_path TEXT NOT NULL,
    file_size_bytes BIGINT,
    version INT DEFAULT 1,           -- Increment if re-generated
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_generated_cma ON generated_files(cma_id);

-- ============================================================
-- REVIEW QUEUE (Ask Father items)
-- ============================================================
CREATE TABLE review_queue (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    firm_id UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
    cma_id UUID NOT NULL REFERENCES cma_projects(id) ON DELETE CASCADE,
    
    -- The line item needing review
    source_item_name TEXT NOT NULL,       -- Original text from document
    source_amount DECIMAL,                -- Amount in original units
    source_amount_lakhs DECIMAL,          -- Amount converted to Lakhs
    source_document_type TEXT,            -- Which statement it came from
    source_context TEXT,                  -- Surrounding items for context
    
    -- AI suggestion
    ai_suggested_cma_row INT,             -- CMA row number AI suggested
    ai_suggested_cma_label TEXT,          -- Human-readable CMA row label
    ai_confidence DECIMAL,                -- 0.0 to 1.0
    ai_reasoning TEXT,                    -- Why AI suggested this
    ai_alternative_rows JSONB,            -- Other possible rows [{row, label, confidence}]
    
    -- CA decision
    ca_chosen_cma_row INT,                -- What CA actually chose
    ca_chosen_cma_label TEXT,
    ca_reasoning TEXT,                    -- CA's explanation
    ca_decided_by UUID REFERENCES users(id),
    
    -- Status
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'resolved', 'skipped')),
    
    -- Should this become a precedent?
    save_as_precedent BOOLEAN DEFAULT false,
    precedent_scope TEXT CHECK (precedent_scope IN ('global', 'firm', 'client', 'one_time')),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TIMESTAMPTZ
);
CREATE INDEX idx_review_cma ON review_queue(cma_id);
CREATE INDEX idx_review_status ON review_queue(status);
CREATE INDEX idx_review_firm_pending ON review_queue(firm_id, status) WHERE status = 'pending';

-- ============================================================
-- CLASSIFICATION PRECEDENTS (Learning loop — the gold)
-- ============================================================
CREATE TABLE classification_precedents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    firm_id UUID REFERENCES firms(id) ON DELETE CASCADE,   -- NULL = global precedent
    
    -- What was classified
    source_item_pattern TEXT NOT NULL,     -- The text pattern to match against
    source_document_type TEXT,             -- P&L / BS / TB
    entity_type TEXT,                      -- trading / manufacturing / services
    amount_range TEXT,                     -- 'small' / 'medium' / 'large' (for context)
    
    -- How it was classified
    cma_row INT NOT NULL,                 -- The correct CMA row
    cma_row_label TEXT NOT NULL,          -- Human-readable label
    reasoning TEXT,                       -- Why this classification
    
    -- Scope and metadata
    scope TEXT DEFAULT 'global' CHECK (scope IN ('global', 'firm', 'client', 'one_time')),
    client_id UUID REFERENCES clients(id),  -- Only if scope = 'client'
    created_by UUID REFERENCES users(id),
    source_review_id UUID REFERENCES review_queue(id),
    
    -- Usage tracking
    times_used INT DEFAULT 0,
    last_used_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT true,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_precedents_pattern ON classification_precedents USING gin(source_item_pattern gin_trgm_ops);
CREATE INDEX idx_precedents_firm ON classification_precedents(firm_id);
CREATE INDEX idx_precedents_scope ON classification_precedents(scope);

-- ============================================================
-- LLM USAGE LOG (Track API costs)
-- ============================================================
CREATE TABLE llm_usage_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    firm_id UUID REFERENCES firms(id),
    cma_id UUID REFERENCES cma_projects(id),
    
    model TEXT NOT NULL,                  -- 'gemini-2.0-flash', 'gemini-3-flash', etc.
    pipeline_step TEXT NOT NULL,          -- 'extraction', 'classification', 'validation'
    
    input_tokens INT,
    output_tokens INT,
    total_tokens INT,
    cost_usd DECIMAL(10, 6),
    
    prompt_summary TEXT,                  -- Brief description of what was asked
    response_time_ms INT,                 -- How long the call took
    was_cached BOOLEAN DEFAULT false,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_llm_firm ON llm_usage_log(firm_id);
CREATE INDEX idx_llm_cma ON llm_usage_log(cma_id);

-- ============================================================
-- AUDIT LOG (Who did what)
-- ============================================================
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    firm_id UUID REFERENCES firms(id),
    user_id UUID REFERENCES users(id),
    
    action TEXT NOT NULL,                 -- 'created_cma', 'uploaded_file', 'resolved_review', etc.
    entity_type TEXT,                     -- 'cma_project', 'client', 'review_queue', etc.
    entity_id UUID,
    details JSONB,                        -- Additional context
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_audit_firm ON audit_log(firm_id);
CREATE INDEX idx_audit_entity ON audit_log(entity_type, entity_id);

-- ============================================================
-- ROW LEVEL SECURITY (Multi-tenant isolation)
-- ============================================================

ALTER TABLE firms ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE clients ENABLE ROW LEVEL SECURITY;
ALTER TABLE cma_projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE uploaded_files ENABLE ROW LEVEL SECURITY;
ALTER TABLE generated_files ENABLE ROW LEVEL SECURITY;
ALTER TABLE review_queue ENABLE ROW LEVEL SECURITY;
ALTER TABLE classification_precedents ENABLE ROW LEVEL SECURITY;
ALTER TABLE llm_usage_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;

-- Users can only see their own firm's data
CREATE POLICY "Users see own firm" ON users
    FOR ALL USING (firm_id IN (SELECT firm_id FROM users WHERE id = auth.uid()));

CREATE POLICY "Clients by firm" ON clients
    FOR ALL USING (firm_id IN (SELECT firm_id FROM users WHERE id = auth.uid()));

CREATE POLICY "CMA projects by firm" ON cma_projects
    FOR ALL USING (firm_id IN (SELECT firm_id FROM users WHERE id = auth.uid()));

CREATE POLICY "Files by firm" ON uploaded_files
    FOR ALL USING (firm_id IN (SELECT firm_id FROM users WHERE id = auth.uid()));

CREATE POLICY "Generated files by firm" ON generated_files
    FOR ALL USING (firm_id IN (SELECT firm_id FROM users WHERE id = auth.uid()));

CREATE POLICY "Review by firm" ON review_queue
    FOR ALL USING (firm_id IN (SELECT firm_id FROM users WHERE id = auth.uid()));

CREATE POLICY "Precedents visible" ON classification_precedents
    FOR SELECT USING (
        scope = 'global' 
        OR firm_id IN (SELECT firm_id FROM users WHERE id = auth.uid())
    );

CREATE POLICY "Precedents insert own firm" ON classification_precedents
    FOR INSERT WITH CHECK (firm_id IN (SELECT firm_id FROM users WHERE id = auth.uid()));

CREATE POLICY "LLM log by firm" ON llm_usage_log
    FOR ALL USING (firm_id IN (SELECT firm_id FROM users WHERE id = auth.uid()));

CREATE POLICY "Audit by firm" ON audit_log
    FOR ALL USING (firm_id IN (SELECT firm_id FROM users WHERE id = auth.uid()));

-- Firms policy: users can see their own firm
CREATE POLICY "Firm access" ON firms
    FOR ALL USING (id IN (SELECT firm_id FROM users WHERE id = auth.uid()));

-- ============================================================
-- HELPER FUNCTIONS
-- ============================================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_firms_timestamp BEFORE UPDATE ON firms
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER update_users_timestamp BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER update_clients_timestamp BEFORE UPDATE ON clients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER update_cma_timestamp BEFORE UPDATE ON cma_projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ============================================================
-- SEED DATA (For development/testing)
-- ============================================================

-- This will be populated after Supabase Auth creates the first user
-- See backend/scripts/seed_data.py for seeding logic
```

### 3.2 Supabase Storage Buckets

Create these buckets in Supabase Storage dashboard:
- `uploads` — Source documents (private, RLS-protected)
- `generated` — Output CMA files (private, RLS-protected)
- `templates` — CMA template files (public read)

---

## 4. API SPECIFICATION

**Base URL:** `https://api.cmaautofill.in/api/v1` (Railway deployment)
**Auth:** All endpoints require `Authorization: Bearer <supabase_access_token>` except health check.

### 4.1 Health & Meta

```
GET /health
→ { "status": "ok", "version": "0.1.0" }

GET /me
→ { "user": { "id", "email", "full_name", "role", "firm_id", "firm_name" } }
```

### 4.2 Clients

```
GET    /clients                    → List clients for current firm
POST   /clients                    → Create client
       Body: { "name", "pan", "entity_type", "industry", "notes" }
       → { "id", "name", ... }
GET    /clients/{id}               → Get client details
PUT    /clients/{id}               → Update client
DELETE /clients/{id}               → Soft-delete (set is_active=false)
```

### 4.3 CMA Projects

```
GET    /cmas                       → List CMAs for current firm (with filters: client_id, status, financial_year)
POST   /cmas                       → Create new CMA project
       Body: { "client_id", "financial_year", "num_historical_years": 2, "num_projected_years": 2 }
       → { "id", "status": "created", ... }
GET    /cmas/{id}                  → Get CMA with all details (files, review items, status)
DELETE /cmas/{id}                  → Soft-delete CMA
GET    /cmas/{id}/status           → Lightweight status check (for polling)
       → { "status", "progress_pct", "current_step", "error_message" }
```

### 4.4 File Upload

```
POST   /cmas/{id}/upload           → Upload document(s) to CMA
       Content-Type: multipart/form-data
       Fields: files[] (multiple), document_type (per file)
       → { "uploaded": [{ "id", "filename", "file_type", "document_type" }] }
GET    /cmas/{id}/files            → List files for a CMA
DELETE /files/{file_id}            → Delete uploaded file
```

### 4.5 Pipeline (The Core)

```
POST   /cmas/{id}/process          → Start full pipeline (extraction → classification → validation)
       Body: { "skip_extraction": false }    -- Optional: skip if already extracted
       → { "message": "Processing started", "cma_id" }
       
       NOTE: This is async. Returns immediately. 
       Client polls GET /cmas/{id}/status for progress.
       Pipeline runs as a background task.

POST   /cmas/{id}/extract          → Run extraction only
       → { "message": "Extraction started" }

POST   /cmas/{id}/classify         → Run classification only (requires extracted data)
       → { "message": "Classification started" }

POST   /cmas/{id}/validate         → Run validation only (requires classified data)
       → { "validation_result": { "is_valid", "errors": [], "warnings": [] } }

POST   /cmas/{id}/generate         → Generate CMA Excel file
       → { "message": "Generation started" }

GET    /cmas/{id}/download         → Download generated CMA Excel file
       → File download (application/vnd.ms-excel.sheet.macroEnabled.12)
```

### 4.6 Review Queue (Ask Father)

```
GET    /reviews                    → List all pending reviews for current firm
       Query params: ?status=pending&cma_id=xxx
       → { "items": [{ "id", "source_item_name", "source_amount_lakhs", "ai_suggested_cma_row", "ai_confidence", ... }] }

GET    /reviews/{id}               → Get single review item with full context
       → { "id", ..., "ai_alternatives": [...], "similar_precedents": [...] }

POST   /reviews/{id}/resolve       → CA resolves a review item
       Body: { 
           "chosen_cma_row": 58, 
           "reasoning": "This is a selling expense", 
           "save_as_precedent": true, 
           "precedent_scope": "global" 
       }
       → { "resolved": true, "precedent_created": true }

POST   /reviews/bulk-resolve       → Resolve multiple items at once
       Body: { "items": [{ "review_id", "chosen_cma_row", "reasoning" }] }
       → { "resolved_count": 5 }

POST   /reviews/{id}/skip          → Skip/defer a review item
       → { "status": "skipped" }
```

### 4.7 Precedents

```
GET    /precedents                 → List precedents (firm + global)
       Query params: ?scope=global&search=rebates
       → { "items": [...] }

DELETE /precedents/{id}            → Deactivate a precedent
```

### 4.8 Dashboard Stats

```
GET    /dashboard/stats            → Dashboard summary
       → { 
           "total_cmas": 12,
           "completed_this_month": 3,
           "pending_reviews": 5,
           "avg_accuracy": 0.87,
           "cost_this_month_usd": 0.45
         }
```

---

## 5. PROJECT STRUCTURE

```
cma-autofill/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI app entry point
│   │   ├── config.py                # Settings (env vars, API keys)
│   │   ├── dependencies.py          # Auth dependency, DB session
│   │   │
│   │   ├── api/                     # Route handlers
│   │   │   ├── __init__.py
│   │   │   ├── health.py            # GET /health, GET /me
│   │   │   ├── clients.py           # CRUD for clients
│   │   │   ├── cma_projects.py      # CRUD for CMA projects
│   │   │   ├── files.py             # Upload/download
│   │   │   ├── pipeline.py          # Process/extract/classify/generate
│   │   │   ├── reviews.py           # Review queue (Ask Father)
│   │   │   ├── precedents.py        # Precedent management
│   │   │   └── dashboard.py         # Stats endpoint
│   │   │
│   │   ├── pipeline/                # THE CORE — AI pipeline
│   │   │   ├── __init__.py
│   │   │   ├── orchestrator.py      # Runs the full pipeline in sequence
│   │   │   ├── extractor.py         # Step 1: Document → structured data (Gemini 2.0 Flash)
│   │   │   ├── classifier.py        # Step 2: Items → CMA rows (Gemini 3 Flash)
│   │   │   ├── validator.py         # Step 3: Check arithmetic, completeness
│   │   │   ├── excel_writer.py      # Step 4: Write to CMA template (EXISTING MODULE)
│   │   │   └── prompts/             # Prompt templates
│   │   │       ├── __init__.py
│   │   │       ├── extraction.py    # Extraction prompt templates
│   │   │       ├── classification.py # Classification prompt templates  
│   │   │       └── validation.py    # Validation prompt templates
│   │   │
│   │   ├── services/                # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── gemini_client.py     # Gemini API wrapper (handles both Flash models)
│   │   │   ├── precedent_service.py # Find relevant precedents for classification
│   │   │   ├── review_service.py    # Create/manage review queue items
│   │   │   ├── storage_service.py   # Supabase Storage upload/download
│   │   │   └── email_service.py     # Resend email notifications
│   │   │
│   │   └── models/                  # Pydantic models (request/response schemas)
│   │       ├── __init__.py
│   │       ├── client.py
│   │       ├── cma_project.py
│   │       ├── file.py
│   │       ├── review.py
│   │       ├── precedent.py
│   │       ├── pipeline.py          # Extraction/classification data models
│   │       └── dashboard.py
│   │
│   ├── data/
│   │   ├── classification_rules.json   # 384 rules (converted from Excel)
│   │   └── cma_row_map.json            # CMA row numbers → labels mapping
│   │
│   ├── templates/
│   │   └── CMA_template.xlsm          # Blank CMA template
│   │
│   ├── tests/
│   │   ├── test_extractor.py
│   │   ├── test_classifier.py
│   │   ├── test_validator.py
│   │   ├── test_excel_writer.py
│   │   └── golden/                    # Golden test data (real CMA comparisons)
│   │       └── mehta_computers/
│   │
│   ├── scripts/
│   │   ├── seed_data.py               # Create initial firm + user
│   │   └── convert_rules_to_json.py   # Convert CMA_classification.xls → JSON
│   │
│   ├── requirements.txt
│   ├── Dockerfile                     # For Railway deployment
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── app/                       # Next.js App Router
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx               # Landing / redirect to dashboard
│   │   │   ├── login/
│   │   │   │   └── page.tsx
│   │   │   ├── dashboard/
│   │   │   │   └── page.tsx           # Main dashboard
│   │   │   ├── clients/
│   │   │   │   ├── page.tsx           # Client list
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx       # Client workspace
│   │   │   ├── cma/
│   │   │   │   ├── new/
│   │   │   │   │   └── page.tsx       # Create new CMA
│   │   │   │   └── [id]/
│   │   │   │       ├── page.tsx       # CMA detail / status
│   │   │   │       ├── upload/
│   │   │   │       │   └── page.tsx   # Upload documents
│   │   │   │       ├── review/
│   │   │   │       │   └── page.tsx   # Classification review
│   │   │   │       └── preview/
│   │   │   │           └── page.tsx   # Preview & download
│   │   │   └── reviews/
│   │   │       └── page.tsx           # Ask Father queue (all pending)
│   │   │
│   │   ├── components/
│   │   │   ├── ui/                    # shadcn/ui components
│   │   │   ├── layout/
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   ├── Header.tsx
│   │   │   │   └── AppShell.tsx
│   │   │   ├── dashboard/
│   │   │   │   ├── StatsCards.tsx
│   │   │   │   └── RecentCMAs.tsx
│   │   │   ├── cma/
│   │   │   │   ├── CMAStatusBadge.tsx
│   │   │   │   ├── FileUploader.tsx
│   │   │   │   └── ProcessingProgress.tsx
│   │   │   └── review/
│   │   │       ├── ReviewCard.tsx
│   │   │       ├── RowSelector.tsx    # Dropdown to pick CMA row
│   │   │       └── PrecedentHint.tsx  # Shows similar past decisions
│   │   │
│   │   ├── lib/
│   │   │   ├── api.ts                 # API client (fetch wrapper)
│   │   │   ├── supabase.ts            # Supabase client init
│   │   │   └── utils.ts               # Helpers (format Lakhs, etc.)
│   │   │
│   │   └── hooks/
│   │       ├── useAuth.ts
│   │       ├── useCMA.ts
│   │       └── useReviews.ts
│   │
│   ├── public/
│   ├── package.json
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   └── next.config.ts
│
├── .github/
│   └── workflows/
│       └── keep-supabase-alive.yml    # Ping Supabase every 5 days
│
├── README.md
└── .gitignore
```

---

## 6. PROMPT TEMPLATES

### 6.1 Extraction Prompt (Gemini 2.0 Flash)

```python
EXTRACTION_SYSTEM_PROMPT = """You are a financial document extraction specialist for Indian accounting documents.

TASK: Extract every line item with its amount from the financial statement provided.

INPUT: A financial statement (Profit & Loss, Balance Sheet, or Trial Balance) — may be an image, PDF, or structured text.

OUTPUT FORMAT: Return ONLY valid JSON. No markdown, no explanation.

{
    "document_type": "profit_loss" | "balance_sheet" | "trial_balance",
    "company_name": "string",
    "financial_year": "string (e.g., 2024-25)",
    "period_months": 12,
    "is_audited": true | false,
    "currency": "INR",
    "unit": "absolute" | "thousands" | "lakhs" | "crores",
    "years": ["2023-24", "2024-25"],
    "items": [
        {
            "name": "Exact text as it appears in the document",
            "category": "income" | "expense" | "asset" | "liability" | "equity",
            "sub_category": "string (e.g., 'direct_expense', 'current_asset')",
            "amounts": {
                "2023-24": 1234567.00,
                "2024-25": 2345678.00
            },
            "is_total": false,
            "is_subtotal": false,
            "parent_group": "string or null",
            "indent_level": 0,
            "notes": "any relevant context"
        }
    ]
}

CRITICAL RULES:
1. Extract ALL items, not just totals. Include every individual line item.
2. Preserve EXACT text as it appears (don't rename items).
3. Amounts must be NUMERIC (no commas, no currency symbols). Use negative for debit balances in BS where appropriate.
4. Handle Indian notation: "Lakhs" means multiply by 100,000. "Cr" means multiply by 10,000,000. Convert all to absolute rupees.
5. If amounts have parentheses like (45,000), this means NEGATIVE.
6. "Previous Year" / "Current Year" — map to actual year labels.
7. Group items maintain their hierarchy (parent_group, indent_level).
8. Mark totals and subtotals — do NOT double-count them during classification.
"""
```

### 6.2 Classification Prompt (Gemini 3 Flash)

```python
CLASSIFICATION_SYSTEM_PROMPT = """You are a CMA (Credit Monitoring Arrangement) classification expert for Indian banking.

TASK: Classify each financial line item to the correct CMA row number.

You will receive:
1. CLASSIFICATION RULES — a mapping of common item names to CMA rows
2. PRECEDENTS — past decisions made by a Chartered Accountant for similar items
3. ITEMS TO CLASSIFY — the line items extracted from financial statements

For EACH item, determine:
- The CMA row number (from the rules or your best judgment)
- Your confidence level (HIGH >90%, MEDIUM 70-90%, LOW <70%)
- Brief reasoning

OUTPUT FORMAT: Return ONLY valid JSON.

{
    "classifications": [
        {
            "item_name": "Exact item name from input",
            "item_amount": 1234567.00,
            "cma_row": 22,
            "cma_row_label": "Domestic Sales",
            "confidence": "HIGH",
            "confidence_score": 0.95,
            "reasoning": "Direct match: Domestic sales maps to CMA row 22",
            "source": "rule" | "precedent" | "inference",
            "alternatives": [
                {"cma_row": 23, "label": "Export Sales", "confidence": 0.05}
            ]
        }
    ],
    "unclassified": [
        {
            "item_name": "Some unusual item",
            "item_amount": 50000,
            "reason": "No matching rule or precedent found",
            "suggested_rows": [
                {"cma_row": 58, "label": "Selling Expenses", "confidence": 0.4},
                {"cma_row": 60, "label": "General Admin", "confidence": 0.35}
            ]
        }
    ]
}

CRITICAL CMA RULES (learned from real Indian CA practice):
1. For Trading firms: Stock-in-Trade goes to WIP (CMA Row 145), NOT Finished Goods.
2. Manufacturing section MUST be filled even for trading firms — use "N/A" or 0.
3. Proprietorship property: If proprietor's personal property is used as business asset, classify under Fixed Assets.
4. Depreciation: Use P&L depreciation figure, NOT balance sheet accumulated depreciation.
5. Sundry Debtors = CMA Row 155 (Receivables), Sundry Creditors = CMA Row 122 (Trade Creditors).
6. "Provisions" in current liabilities = CMA Row 125 (Other Current Liabilities).
7. Secured loans from banks = Term Liabilities, Unsecured loans from directors = Other Non-Current Liabilities.
8. Interest on working capital loans → CMA Interest section. Interest on term loans → CMA Interest section (separate row).
9. "Rebates & Discounts" — if GIVEN, it's Selling Expense (Row 58). If RECEIVED, it's reduction from purchases.
10. Income Tax Provision = Row 88 (Tax), NOT an operating expense.

CONFIDENCE THRESHOLDS:
- HIGH (>0.90): Direct match in rules OR strong precedent with same entity type
- MEDIUM (0.70-0.90): Partial match, or rule matches but context suggests possible alternatives
- LOW (<0.70): No clear match, inference only → MUST go to Ask Father review queue
"""

CLASSIFICATION_RULES_TEMPLATE = """
## CLASSIFICATION RULES (relevant subset for {entity_type} entity)

{rules_json}

## PRECEDENTS (past CA decisions for similar items)

{precedents_json}

## ITEMS TO CLASSIFY

{items_json}

Classify each item. Items with confidence < 0.70 MUST be flagged for review.
"""
```

### 6.3 Validation Prompt (Gemini 2.0 Flash)

```python
VALIDATION_SYSTEM_PROMPT = """You are a CMA validation specialist. Check the classified CMA data for errors.

CHECKS TO PERFORM:
1. BALANCE SHEET BALANCE: Total Assets must equal Total Liabilities + Equity (for each year)
2. P&L ARITHMETIC: Revenue - Expenses = Net Profit (verify the math)
3. COMPLETENESS: Check that critical CMA rows are filled (Sales, Purchases, Total Assets, Total Liabilities, Net Worth)
4. REASONABLENESS: Flag if any ratio seems extreme (e.g., expenses > 10x revenue, negative assets)
5. CROSS-STATEMENT: Net Profit from P&L should match retained earnings movement in BS
6. YEAR-OVER-YEAR: Flag dramatic changes (>200% increase or >80% decrease in any major item)

OUTPUT FORMAT: Return ONLY valid JSON.

{
    "is_valid": true | false,
    "errors": [
        {
            "type": "balance_mismatch",
            "severity": "critical",
            "year": "2024-25",
            "message": "Balance Sheet doesn't balance. Assets: ₹45.2L, Liabilities+Equity: ₹43.8L. Difference: ₹1.4L",
            "suggested_fix": "Check if any item was double-counted or missed"
        }
    ],
    "warnings": [
        {
            "type": "unusual_ratio",
            "severity": "warning",
            "message": "Selling expenses increased 350% YoY. Please verify."
        }
    ],
    "summary": {
        "total_items_classified": 56,
        "auto_classified": 48,
        "sent_to_review": 8,
        "balance_sheet_balanced": true,
        "pnl_arithmetic_correct": true
    }
}
"""
```

---

## 7. BUILD ORDER (Follow this EXACTLY)

Claude Code should build in this sequence. Each phase must be tested before moving to the next.

### Phase 1: Backend Foundation (Build First)
**Goal:** FastAPI app that starts, connects to Supabase, has basic auth.

1. Initialize backend project (`requirements.txt`, `app/main.py`, `app/config.py`)
2. Supabase client setup (`app/dependencies.py`)
3. Auth middleware (verify Supabase JWT token)
4. Health endpoint (`GET /health`, `GET /me`)
5. **TEST:** App starts on Railway, health check works, auth validates token

### Phase 2: Data Layer
**Goal:** CRUD endpoints for clients and CMA projects.

6. Pydantic models for Client, CMAProject
7. Client CRUD endpoints
8. CMA Project CRUD endpoints
9. File upload endpoint (multipart → Supabase Storage)
10. **TEST:** Can create client, create CMA, upload file via API

### Phase 3: AI Pipeline — Extraction
**Goal:** Upload a document → get structured line items back.

11. Gemini client service (`services/gemini_client.py`)
12. Extraction prompt templates
13. Extractor module — handles Excel (openpyxl/pandas), PDF (pdfplumber), Image/scanned PDF (Gemini Vision)
14. `POST /cmas/{id}/extract` endpoint
15. **TEST:** Upload Mehta Computers Excel → get correct extracted items JSON

### Phase 4: AI Pipeline — Classification  
**Goal:** Extracted items → classified with CMA row numbers.

16. Convert `CMA_classification.xls` → `classification_rules.json`
17. Classification prompt templates
18. Precedent service (find similar past decisions)
19. Classifier module — sends items + rules + precedents to Gemini 3 Flash
20. Review queue creation (items with confidence < 0.70 go to queue)
21. `POST /cmas/{id}/classify` endpoint
22. **TEST:** Extracted Mehta data → classified items, check accuracy vs known-correct CMA

### Phase 5: AI Pipeline — Validation & Excel Generation
**Goal:** Classified data → validated → CMA Excel file.

23. Validator module
24. Integrate existing `cma_writer.py` (adapt to use pipeline data format)
25. `POST /cmas/{id}/validate` and `POST /cmas/{id}/generate` endpoints
26. Download endpoint for generated file
27. **TEST:** Full pipeline on Mehta Computers — compare output CMA vs reference CMA

### Phase 6: Review Queue (Ask Father)
**Goal:** CA can see uncertain items and make decisions.

28. Review queue endpoints (list, resolve, bulk-resolve)
29. Precedent creation from resolved reviews
30. After all reviews resolved → re-classify with new precedents → validate → generate
31. **TEST:** Items flagged for review → resolve them → CMA regenerated correctly

### Phase 7: Pipeline Orchestrator
**Goal:** One-click processing — upload to completion.

32. Orchestrator module — runs extract → classify → (pause for review if needed) → validate → generate
33. Background task execution with status updates
34. Status polling endpoint
35. **TEST:** Full end-to-end: upload files → process → review → download CMA

### Phase 8: Frontend — Core Shell
**Goal:** Login, navigation, dashboard.

36. Next.js project setup with shadcn/ui
37. Supabase Auth integration (login page)
38. App shell (sidebar, header, navigation)
39. Dashboard page with stats

### Phase 9: Frontend — CMA Flow
**Goal:** Complete user flow in the UI.

40. Client list and create client pages
41. CMA creation page
42. File upload page (drag & drop)
43. Processing status page (progress bar, status updates)
44. Review page (Ask Father interface — the most important UI)
45. Preview & download page

### Phase 10: Polish & Deploy
46. Error handling and edge cases
47. Email notifications (Resend — notify CA when reviews are ready)
48. Sentry integration
49. Deploy frontend to Cloudflare Pages
50. Deploy backend to Railway
51. End-to-end test in production with real data

---

## 8. KEY IMPLEMENTATION NOTES

### 8.1 Gemini API Integration

```python
# services/gemini_client.py
import google.generativeai as genai
import json

class GeminiClient:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.flash_2 = genai.GenerativeModel('gemini-2.0-flash')      # Extraction
        self.flash_3 = genai.GenerativeModel('gemini-3-flash')         # Classification
        self.pro = genai.GenerativeModel('gemini-3.1-pro-preview')     # Fallback
    
    async def extract(self, file_content, file_type: str, system_prompt: str) -> dict:
        """Extract financial data from document using Gemini 2.0 Flash."""
        if file_type in ('image', 'scanned_pdf'):
            # Send as image to vision model
            response = self.flash_2.generate_content([system_prompt, file_content])
        else:
            # Send as text
            response = self.flash_2.generate_content(f"{system_prompt}\n\n{file_content}")
        return json.loads(response.text)
    
    async def classify(self, prompt: str) -> dict:
        """Classify items using Gemini 3 Flash."""
        response = self.flash_3.generate_content(prompt)
        return json.loads(response.text)
    
    async def classify_with_fallback(self, prompt: str) -> dict:
        """Try Flash first, fall back to Pro if response is poor."""
        try:
            result = await self.classify(prompt)
            # If too many LOW confidence items, retry with Pro
            low_count = sum(1 for c in result.get('classifications', []) if c['confidence'] == 'LOW')
            if low_count > len(result.get('classifications', [])) * 0.5:
                result = self.pro.generate_content(prompt)
                return json.loads(result.text)
            return result
        except Exception:
            # Fallback to Pro on any Flash error
            result = self.pro.generate_content(prompt)
            return json.loads(result.text)
```

### 8.2 Background Task Pattern

```python
# api/pipeline.py
from fastapi import BackgroundTasks

@router.post("/cmas/{cma_id}/process")
async def process_cma(cma_id: str, background_tasks: BackgroundTasks):
    # Update status immediately
    await update_cma_status(cma_id, "extracting")
    # Run pipeline in background
    background_tasks.add_task(run_full_pipeline, cma_id)
    return {"message": "Processing started", "cma_id": cma_id}

async def run_full_pipeline(cma_id: str):
    try:
        # Step 1: Extract
        await update_cma_status(cma_id, "extracting")
        extracted = await extractor.extract_all_files(cma_id)
        
        # Step 2: Classify
        await update_cma_status(cma_id, "classifying")
        classified = await classifier.classify_items(cma_id, extracted)
        
        # Step 3: Check if review needed
        pending_reviews = [c for c in classified if c['confidence_score'] < 0.70]
        if pending_reviews:
            await create_review_items(cma_id, pending_reviews)
            await update_cma_status(cma_id, "review_pending")
            return  # Pause here — CA must review before continuing
        
        # Step 4: Validate
        await update_cma_status(cma_id, "validated")
        validation = await validator.validate(classified)
        
        # Step 5: Generate
        await update_cma_status(cma_id, "generating")
        await excel_writer.generate(cma_id, classified)
        await update_cma_status(cma_id, "completed")
        
    except Exception as e:
        await update_cma_status(cma_id, "error", error_message=str(e))
```

### 8.3 Classification Rule Filtering

```python
# Don't send all 384 rules every time. Filter by document type and entity type.
def get_relevant_rules(document_type: str, entity_type: str) -> list:
    """Filter 384 rules down to ~80-120 relevant ones."""
    all_rules = load_rules()
    
    if document_type == 'profit_loss':
        rules = [r for r in all_rules if r['sheet'] == 'P&L']
    elif document_type == 'balance_sheet':
        rules = [r for r in all_rules if r['sheet'] == 'BS']
    else:
        rules = all_rules  # Trial balance — need both
    
    # Further filter by entity type (trading firms don't need manufacturing rules)
    if entity_type == 'trading':
        rules = [r for r in rules if r.get('entity_types', ['all']) in [['all'], ['trading']]]
    
    return rules
```

### 8.4 Precedent Matching

```python
# services/precedent_service.py
async def find_relevant_precedents(item_name: str, entity_type: str, firm_id: str, limit: int = 5) -> list:
    """Find similar past CA decisions for a line item."""
    
    # Use PostgreSQL trigram similarity for fuzzy matching
    query = """
        SELECT *, similarity(source_item_pattern, $1) as sim_score
        FROM classification_precedents
        WHERE is_active = true
          AND (scope = 'global' OR firm_id = $2)
          AND (entity_type IS NULL OR entity_type = $3)
          AND similarity(source_item_pattern, $1) > 0.3
        ORDER BY 
            CASE WHEN firm_id = $2 THEN 0 ELSE 1 END,  -- Firm-specific first
            sim_score DESC
        LIMIT $4
    """
    return await db.fetch(query, item_name, firm_id, entity_type, limit)
```

### 8.5 Amount Conversion to Lakhs

```python
def to_lakhs(amount: float, source_unit: str) -> float:
    """Convert any amount to Lakhs (₹1L = ₹100,000)."""
    multipliers = {
        'absolute': 1 / 100_000,
        'thousands': 1 / 100,
        'lakhs': 1,
        'crores': 100,
    }
    return round(amount * multipliers.get(source_unit, 1 / 100_000), 2)
```

---

## 9. ENVIRONMENT VARIABLES

```env
# .env.example

# Supabase
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbG...
SUPABASE_SERVICE_KEY=eyJhbG...

# Google AI (Gemini)
GOOGLE_AI_API_KEY=AIza...

# Resend (Email)
RESEND_API_KEY=re_...

# Sentry
SENTRY_DSN=https://xxxxx@sentry.io/xxxxx

# App
APP_ENV=development
APP_URL=http://localhost:3000
API_URL=http://localhost:8000
CORS_ORIGINS=http://localhost:3000
```

---

## 10. DEPENDENCIES

### Backend (requirements.txt)
```
fastapi==0.115.0
uvicorn[standard]==0.31.0
python-multipart==0.0.12
pydantic==2.10.0
pydantic-settings==2.6.0

# Supabase
supabase==2.11.0

# AI
google-generativeai==0.8.0

# Document processing
openpyxl==3.1.5
pdfplumber==0.11.0
pandas==2.2.3
Pillow==10.4.0
xlrd==2.0.1

# Email
resend==2.5.0

# Monitoring
sentry-sdk[fastapi]==2.18.0

# Utils
python-dotenv==1.0.1
httpx==0.27.0
```

### Frontend (package.json key deps)
```json
{
  "dependencies": {
    "next": "^15.0.0",
    "react": "^19.0.0",
    "@supabase/supabase-js": "^2.45.0",
    "@supabase/ssr": "^0.5.0",
    "@tanstack/react-query": "^5.60.0",
    "tailwindcss": "^3.4.0",
    "lucide-react": "^0.460.0",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.5.0"
  }
}
```

---

## 11. WHAT ALREADY EXISTS (DO NOT REBUILD)

### cma_writer.py
The Excel Writer module is COMPLETE and TESTED (65/65 values match, 100% accuracy). It lives in `backend/app/pipeline/excel_writer.py`. Adapt the input format to match the classification pipeline output, but DO NOT rewrite the core writing logic.

### CMA_classification.xls  
384 classification rules. Convert to JSON format for use in prompts (see `scripts/convert_rules_to_json.py`).

### CMA.xlsm
Blank CMA template. Copy to `backend/templates/CMA_template.xlsm`. The Excel Writer uses this as the base file.

### CMA_15092025.xls
Completed CMA for Mehta Computers. Use as golden test data.

---

## 12. DESIGN GUIDELINES (Frontend)

**Aesthetic:** Premium financial SaaS. Dark navy backgrounds (#0F172A) with gold accents (#D4A843). Clean, professional, trustworthy.

**Key Design Decisions:**
- Sidebar navigation (always visible on desktop, drawer on mobile)
- Status badges with colors: Created (gray), Processing (blue pulse), Review (amber), Complete (green), Error (red)
- Ask Father review page is the MOST IMPORTANT UI — make it intuitive:
  - Show the line item + amount prominently
  - Show AI's suggestion with confidence bar
  - Show alternatives as selectable options
  - Show similar precedents as hints
  - One-click "Accept AI suggestion" for high-confidence items
  - Bulk actions for resolving multiple items

**shadcn/ui components to install:**
button, card, badge, dialog, dropdown-menu, input, label, select, table, tabs, toast, tooltip, progress, separator, sheet, skeleton, command

---

## END OF BLUEPRINT

This document is the single source of truth. Build exactly what is specified. If something is ambiguous, flag it — don't guess.
