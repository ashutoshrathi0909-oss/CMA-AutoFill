-- Phase 11 — Task 11.3: Performance indexes for frequently queried columns
-- These indexes support the firm-scoped RLS queries and common list/filter operations.

-- Firm-scoped lookups (used by every authenticated query)
CREATE INDEX IF NOT EXISTS idx_clients_firm_id ON clients(firm_id);
CREATE INDEX IF NOT EXISTS idx_cma_projects_firm_id ON cma_projects(firm_id);
CREATE INDEX IF NOT EXISTS idx_cma_projects_client_id ON cma_projects(client_id);
CREATE INDEX IF NOT EXISTS idx_cma_projects_status ON cma_projects(status);

-- File lookups by project
CREATE INDEX IF NOT EXISTS idx_uploaded_files_project_id ON uploaded_files(cma_project_id);
CREATE INDEX IF NOT EXISTS idx_generated_files_project_id ON generated_files(cma_project_id);

-- Review queue queries (firm + project + status)
CREATE INDEX IF NOT EXISTS idx_review_queue_firm_id ON review_queue(firm_id);
CREATE INDEX IF NOT EXISTS idx_review_queue_project_status ON review_queue(cma_project_id, status);

-- Precedent lookups (firm + source term for classification)
CREATE INDEX IF NOT EXISTS idx_precedents_firm_term ON classification_precedents(firm_id, source_term);

-- Audit log queries
CREATE INDEX IF NOT EXISTS idx_audit_log_entity ON audit_log(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_firm_id ON audit_log(firm_id);

-- Extracted data lookups by project
CREATE INDEX IF NOT EXISTS idx_extracted_data_project_id ON extracted_data(cma_project_id);

-- Classification results by project
CREATE INDEX IF NOT EXISTS idx_classification_results_project_id ON classification_results(cma_project_id);
