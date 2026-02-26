-- ============================================================
-- CMA AutoFill — Phase 02 Database Schema
-- Run this against your Supabase project via psql or SQL editor
-- ============================================================

-- ────────────────────────────────────────────────────────────
-- HELPER: updated_at trigger function
-- ────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- ============================================================
-- TASK 2.1: CORE TABLES — firms & users
-- ============================================================

CREATE TABLE IF NOT EXISTS firms (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name        TEXT NOT NULL,
  email       TEXT UNIQUE NOT NULL,
  phone       TEXT,
  address     TEXT,
  gst_number  TEXT,
  plan        TEXT NOT NULL DEFAULT 'free' CHECK (plan IN ('free', 'starter', 'pro')),
  is_active   BOOLEAN NOT NULL DEFAULT true,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS users (
  id          UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  firm_id     UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
  email       TEXT NOT NULL,
  full_name   TEXT NOT NULL,
  role        TEXT NOT NULL DEFAULT 'ca' CHECK (role IN ('owner', 'ca', 'staff')),
  is_active   BOOLEAN NOT NULL DEFAULT true,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_users_firm_id ON users(firm_id);

-- Triggers for firms & users
DROP TRIGGER IF EXISTS set_updated_at_firms ON firms;
CREATE TRIGGER set_updated_at_firms
  BEFORE UPDATE ON firms
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS set_updated_at_users ON users;
CREATE TRIGGER set_updated_at_users
  BEFORE UPDATE ON users
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


-- ============================================================
-- TASK 2.2: CLIENTS & CMA PROJECTS
-- ============================================================

CREATE TABLE IF NOT EXISTS clients (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  firm_id         UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
  name            TEXT NOT NULL,
  entity_type     TEXT NOT NULL CHECK (entity_type IN ('trading', 'manufacturing', 'service')),
  pan_number      TEXT,
  gst_number      TEXT,
  contact_person  TEXT,
  contact_email   TEXT,
  contact_phone   TEXT,
  address         TEXT,
  is_active       BOOLEAN NOT NULL DEFAULT true,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_clients_firm_id ON clients(firm_id);

DROP TRIGGER IF EXISTS set_updated_at_clients ON clients;
CREATE TRIGGER set_updated_at_clients
  BEFORE UPDATE ON clients
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


CREATE TABLE IF NOT EXISTS cma_projects (
  id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  firm_id                 UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
  client_id               UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
  financial_year          TEXT NOT NULL,
  bank_name               TEXT,
  loan_type               TEXT CHECK (loan_type IN ('term_loan', 'working_capital', 'cc_od', 'other')),
  loan_amount             NUMERIC,
  status                  TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'extracting', 'classifying', 'reviewing', 'validating', 'generating', 'completed', 'error')),
  extracted_data          JSONB,
  classification_results  JSONB,
  validation_errors       JSONB,
  pipeline_progress       INTEGER NOT NULL DEFAULT 0,
  pipeline_current_step   TEXT,
  error_message           TEXT,
  created_by              UUID REFERENCES users(id),
  created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (client_id, financial_year)
);

CREATE INDEX IF NOT EXISTS idx_cma_projects_firm_id   ON cma_projects(firm_id);
CREATE INDEX IF NOT EXISTS idx_cma_projects_client_id ON cma_projects(client_id);
CREATE INDEX IF NOT EXISTS idx_cma_projects_status    ON cma_projects(status);

DROP TRIGGER IF EXISTS set_updated_at_cma_projects ON cma_projects;
CREATE TRIGGER set_updated_at_cma_projects
  BEFORE UPDATE ON cma_projects
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


-- ============================================================
-- TASK 2.3: FILE TABLES
-- ============================================================

CREATE TABLE IF NOT EXISTS uploaded_files (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  firm_id             UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
  cma_project_id      UUID NOT NULL REFERENCES cma_projects(id) ON DELETE CASCADE,
  file_name           TEXT NOT NULL,
  file_type           TEXT NOT NULL CHECK (file_type IN ('xlsx', 'xls', 'pdf', 'jpg', 'png', 'csv')),
  file_size           INTEGER NOT NULL,
  storage_path        TEXT NOT NULL,
  document_type       TEXT CHECK (document_type IN ('profit_and_loss', 'balance_sheet', 'trial_balance', 'other')),
  extraction_status   TEXT NOT NULL DEFAULT 'pending' CHECK (extraction_status IN ('pending', 'processing', 'completed', 'failed')),
  extracted_data      JSONB,
  uploaded_by         UUID REFERENCES users(id),
  created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_uploaded_files_firm_id        ON uploaded_files(firm_id);
CREATE INDEX IF NOT EXISTS idx_uploaded_files_project_id     ON uploaded_files(cma_project_id);


CREATE TABLE IF NOT EXISTS generated_files (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  firm_id         UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
  cma_project_id  UUID NOT NULL REFERENCES cma_projects(id) ON DELETE CASCADE,
  file_name       TEXT NOT NULL,
  storage_path    TEXT NOT NULL,
  file_size       INTEGER,
  version         INTEGER NOT NULL DEFAULT 1,
  generated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_generated_files_project_id ON generated_files(cma_project_id);


-- ============================================================
-- TASK 2.4: REVIEW QUEUE & CLASSIFICATION PRECEDENTS
-- ============================================================

CREATE TABLE IF NOT EXISTS review_queue (
  id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  firm_id               UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
  cma_project_id        UUID NOT NULL REFERENCES cma_projects(id) ON DELETE CASCADE,
  source_item           TEXT NOT NULL,
  source_amount         NUMERIC NOT NULL,
  source_document_type  TEXT NOT NULL CHECK (source_document_type IN ('profit_and_loss', 'balance_sheet', 'trial_balance')),
  ai_suggested_row      INTEGER,
  ai_suggested_sheet    TEXT,
  ai_confidence         NUMERIC,
  ai_reasoning          TEXT,
  ca_selected_row       INTEGER,
  ca_selected_sheet     TEXT,
  ca_notes              TEXT,
  status                TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'resolved', 'skipped')),
  resolved_by           UUID REFERENCES users(id),
  resolved_at           TIMESTAMPTZ,
  created_at            TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_review_queue_firm_id    ON review_queue(firm_id);
CREATE INDEX IF NOT EXISTS idx_review_queue_project_id ON review_queue(cma_project_id);
CREATE INDEX IF NOT EXISTS idx_review_queue_status     ON review_queue(status);


CREATE TABLE IF NOT EXISTS classification_precedents (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  firm_id             UUID REFERENCES firms(id) ON DELETE CASCADE,
  source_term         TEXT NOT NULL,
  target_row          INTEGER NOT NULL,
  target_sheet        TEXT NOT NULL,
  entity_type         TEXT CHECK (entity_type IN ('trading', 'manufacturing', 'service')),
  confidence          NUMERIC NOT NULL DEFAULT 1.0,
  scope               TEXT NOT NULL DEFAULT 'firm' CHECK (scope IN ('firm', 'global')),
  source_project_id   UUID REFERENCES cma_projects(id),
  created_by          UUID NOT NULL REFERENCES users(id),
  created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (firm_id, source_term, entity_type)
);

CREATE INDEX IF NOT EXISTS idx_precedents_firm_id     ON classification_precedents(firm_id);
CREATE INDEX IF NOT EXISTS idx_precedents_source_term ON classification_precedents(source_term);
CREATE INDEX IF NOT EXISTS idx_precedents_global       ON classification_precedents(scope) WHERE scope = 'global';


-- ============================================================
-- TASK 2.5: LOGGING TABLES
-- ============================================================

CREATE TABLE IF NOT EXISTS llm_usage_log (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  firm_id         UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
  cma_project_id  UUID REFERENCES cma_projects(id) ON DELETE SET NULL,
  model           TEXT NOT NULL,
  task_type       TEXT NOT NULL CHECK (task_type IN ('extraction', 'classification', 'validation', 'fallback')),
  input_tokens    INTEGER NOT NULL,
  output_tokens   INTEGER NOT NULL,
  cost_usd        NUMERIC(10, 6) NOT NULL,
  latency_ms      INTEGER,
  success         BOOLEAN NOT NULL DEFAULT true,
  error_message   TEXT,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_llm_log_firm_id    ON llm_usage_log(firm_id);
CREATE INDEX IF NOT EXISTS idx_llm_log_project_id ON llm_usage_log(cma_project_id);
CREATE INDEX IF NOT EXISTS idx_llm_log_created_at ON llm_usage_log(created_at);


CREATE TABLE IF NOT EXISTS audit_log (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  firm_id      UUID NOT NULL REFERENCES firms(id) ON DELETE CASCADE,
  user_id      UUID REFERENCES users(id) ON DELETE SET NULL,
  action       TEXT NOT NULL,
  entity_type  TEXT NOT NULL,
  entity_id    UUID,
  metadata     JSONB,
  ip_address   TEXT,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_audit_log_firm_id    ON audit_log(firm_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_created_at ON audit_log(created_at);
CREATE INDEX IF NOT EXISTS idx_audit_log_action     ON audit_log(action);


-- ============================================================
-- TASK 2.6: ROW LEVEL SECURITY
-- ============================================================

-- Helper: returns the firm_id of the currently authenticated user
CREATE OR REPLACE FUNCTION get_user_firm_id()
RETURNS UUID
LANGUAGE sql
STABLE
SECURITY INVOKER
AS $$
  SELECT firm_id FROM users WHERE id = auth.uid() LIMIT 1;
$$;

-- Enable RLS on all tables
ALTER TABLE firms                    ENABLE ROW LEVEL SECURITY;
ALTER TABLE users                    ENABLE ROW LEVEL SECURITY;
ALTER TABLE clients                  ENABLE ROW LEVEL SECURITY;
ALTER TABLE cma_projects             ENABLE ROW LEVEL SECURITY;
ALTER TABLE uploaded_files           ENABLE ROW LEVEL SECURITY;
ALTER TABLE generated_files          ENABLE ROW LEVEL SECURITY;
ALTER TABLE review_queue             ENABLE ROW LEVEL SECURITY;
ALTER TABLE classification_precedents ENABLE ROW LEVEL SECURITY;
ALTER TABLE llm_usage_log            ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_log                ENABLE ROW LEVEL SECURITY;

-- ── firms policies ───────────────────────────────────────────
DROP POLICY IF EXISTS "firms_select" ON firms;
CREATE POLICY "firms_select" ON firms
  FOR SELECT USING (id = get_user_firm_id());

DROP POLICY IF EXISTS "firms_insert" ON firms;
CREATE POLICY "firms_insert" ON firms
  FOR INSERT WITH CHECK (true);

DROP POLICY IF EXISTS "firms_update" ON firms;
CREATE POLICY "firms_update" ON firms
  FOR UPDATE USING (id = get_user_firm_id())
  WITH CHECK (id = get_user_firm_id());

-- No DELETE policy on firms — deny by default

-- ── users policies ───────────────────────────────────────────
DROP POLICY IF EXISTS "users_select" ON users;
CREATE POLICY "users_select" ON users
  FOR SELECT USING (firm_id = get_user_firm_id());

DROP POLICY IF EXISTS "users_insert" ON users;
CREATE POLICY "users_insert" ON users
  FOR INSERT WITH CHECK (firm_id = get_user_firm_id());

DROP POLICY IF EXISTS "users_update" ON users;
CREATE POLICY "users_update" ON users
  FOR UPDATE USING (
    id = auth.uid() OR (
      firm_id = get_user_firm_id() AND
      EXISTS (SELECT 1 FROM users u WHERE u.id = auth.uid() AND u.role = 'owner')
    )
  );

-- No DELETE policy on users — they are deactivated, not deleted

-- ── Standard CRUD policies for remaining tables ──────────────
-- clients
DROP POLICY IF EXISTS "clients_select" ON clients;
CREATE POLICY "clients_select" ON clients FOR SELECT USING (firm_id = get_user_firm_id());
DROP POLICY IF EXISTS "clients_insert" ON clients;
CREATE POLICY "clients_insert" ON clients FOR INSERT WITH CHECK (firm_id = get_user_firm_id());
DROP POLICY IF EXISTS "clients_update" ON clients;
CREATE POLICY "clients_update" ON clients FOR UPDATE USING (firm_id = get_user_firm_id()) WITH CHECK (firm_id = get_user_firm_id());
DROP POLICY IF EXISTS "clients_delete" ON clients;
CREATE POLICY "clients_delete" ON clients FOR DELETE USING (firm_id = get_user_firm_id());

-- cma_projects
DROP POLICY IF EXISTS "cma_projects_select" ON cma_projects;
CREATE POLICY "cma_projects_select" ON cma_projects FOR SELECT USING (firm_id = get_user_firm_id());
DROP POLICY IF EXISTS "cma_projects_insert" ON cma_projects;
CREATE POLICY "cma_projects_insert" ON cma_projects FOR INSERT WITH CHECK (firm_id = get_user_firm_id());
DROP POLICY IF EXISTS "cma_projects_update" ON cma_projects;
CREATE POLICY "cma_projects_update" ON cma_projects FOR UPDATE USING (firm_id = get_user_firm_id()) WITH CHECK (firm_id = get_user_firm_id());
DROP POLICY IF EXISTS "cma_projects_delete" ON cma_projects;
CREATE POLICY "cma_projects_delete" ON cma_projects FOR DELETE USING (firm_id = get_user_firm_id());

-- uploaded_files
DROP POLICY IF EXISTS "uploaded_files_select" ON uploaded_files;
CREATE POLICY "uploaded_files_select" ON uploaded_files FOR SELECT USING (firm_id = get_user_firm_id());
DROP POLICY IF EXISTS "uploaded_files_insert" ON uploaded_files;
CREATE POLICY "uploaded_files_insert" ON uploaded_files FOR INSERT WITH CHECK (firm_id = get_user_firm_id());
DROP POLICY IF EXISTS "uploaded_files_update" ON uploaded_files;
CREATE POLICY "uploaded_files_update" ON uploaded_files FOR UPDATE USING (firm_id = get_user_firm_id()) WITH CHECK (firm_id = get_user_firm_id());
DROP POLICY IF EXISTS "uploaded_files_delete" ON uploaded_files;
CREATE POLICY "uploaded_files_delete" ON uploaded_files FOR DELETE USING (firm_id = get_user_firm_id());

-- generated_files
DROP POLICY IF EXISTS "generated_files_select" ON generated_files;
CREATE POLICY "generated_files_select" ON generated_files FOR SELECT USING (firm_id = get_user_firm_id());
DROP POLICY IF EXISTS "generated_files_insert" ON generated_files;
CREATE POLICY "generated_files_insert" ON generated_files FOR INSERT WITH CHECK (firm_id = get_user_firm_id());
DROP POLICY IF EXISTS "generated_files_update" ON generated_files;
CREATE POLICY "generated_files_update" ON generated_files FOR UPDATE USING (firm_id = get_user_firm_id()) WITH CHECK (firm_id = get_user_firm_id());
DROP POLICY IF EXISTS "generated_files_delete" ON generated_files;
CREATE POLICY "generated_files_delete" ON generated_files FOR DELETE USING (firm_id = get_user_firm_id());

-- review_queue
DROP POLICY IF EXISTS "review_queue_select" ON review_queue;
CREATE POLICY "review_queue_select" ON review_queue FOR SELECT USING (firm_id = get_user_firm_id());
DROP POLICY IF EXISTS "review_queue_insert" ON review_queue;
CREATE POLICY "review_queue_insert" ON review_queue FOR INSERT WITH CHECK (firm_id = get_user_firm_id());
DROP POLICY IF EXISTS "review_queue_update" ON review_queue;
CREATE POLICY "review_queue_update" ON review_queue FOR UPDATE USING (firm_id = get_user_firm_id()) WITH CHECK (firm_id = get_user_firm_id());
DROP POLICY IF EXISTS "review_queue_delete" ON review_queue;
CREATE POLICY "review_queue_delete" ON review_queue FOR DELETE USING (firm_id = get_user_firm_id());

-- classification_precedents (SPECIAL: also allow reading global firm_id IS NULL rows)
DROP POLICY IF EXISTS "precedents_select" ON classification_precedents;
CREATE POLICY "precedents_select" ON classification_precedents
  FOR SELECT USING (firm_id = get_user_firm_id() OR firm_id IS NULL);
DROP POLICY IF EXISTS "precedents_insert" ON classification_precedents;
CREATE POLICY "precedents_insert" ON classification_precedents
  FOR INSERT WITH CHECK (firm_id = get_user_firm_id());
DROP POLICY IF EXISTS "precedents_update" ON classification_precedents;
CREATE POLICY "precedents_update" ON classification_precedents
  FOR UPDATE USING (firm_id = get_user_firm_id()) WITH CHECK (firm_id = get_user_firm_id());
DROP POLICY IF EXISTS "precedents_delete" ON classification_precedents;
CREATE POLICY "precedents_delete" ON classification_precedents
  FOR DELETE USING (firm_id = get_user_firm_id());

-- llm_usage_log
DROP POLICY IF EXISTS "llm_log_select" ON llm_usage_log;
CREATE POLICY "llm_log_select" ON llm_usage_log FOR SELECT USING (firm_id = get_user_firm_id());
DROP POLICY IF EXISTS "llm_log_insert" ON llm_usage_log;
CREATE POLICY "llm_log_insert" ON llm_usage_log FOR INSERT WITH CHECK (firm_id = get_user_firm_id());

-- audit_log
DROP POLICY IF EXISTS "audit_log_select" ON audit_log;
CREATE POLICY "audit_log_select" ON audit_log FOR SELECT USING (firm_id = get_user_firm_id());
DROP POLICY IF EXISTS "audit_log_insert" ON audit_log;
CREATE POLICY "audit_log_insert" ON audit_log FOR INSERT WITH CHECK (firm_id = get_user_firm_id());


-- ============================================================
-- TASK 2.7: AUTH TRIGGER (auto-create user/firm on signup)
-- ============================================================

CREATE OR REPLACE FUNCTION handle_new_auth_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  _firm_id  UUID;
  _firm_name TEXT;
  _full_name TEXT;
BEGIN
  -- Pull optional metadata from auth.users raw_user_meta_data
  _firm_id   := (NEW.raw_user_meta_data->>'firm_id')::UUID;
  _firm_name := COALESCE(NEW.raw_user_meta_data->>'firm_name', 'My CA Firm');
  _full_name := COALESCE(NEW.raw_user_meta_data->>'full_name', split_part(NEW.email, '@', 1));

  IF _firm_id IS NULL THEN
    -- No firm_id in metadata → new firm owner signing up
    INSERT INTO firms (name, email, plan)
    VALUES (_firm_name, NEW.email, 'free')
    RETURNING id INTO _firm_id;

    INSERT INTO users (id, firm_id, email, full_name, role)
    VALUES (NEW.id, _firm_id, NEW.email, _full_name, 'owner');
  ELSE
    -- Invited to existing firm
    INSERT INTO users (id, firm_id, email, full_name, role)
    VALUES (NEW.id, _firm_id, NEW.email, _full_name, 'ca');
  END IF;

  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION handle_new_auth_user();

-- ============================================================
-- DONE — All Phase 02 schema objects created
-- ============================================================
