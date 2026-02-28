-- Phase 08 Migration: Pipeline Orchestrator Schema Updates
-- Fixes: BUG-02 (missing columns) + BUG-04 (status CHECK too restrictive)
-- Run this against your Supabase project via SQL Editor

-- 1. Drop restrictive status CHECK and replace with expanded version
ALTER TABLE cma_projects DROP CONSTRAINT IF EXISTS cma_projects_status_check;
ALTER TABLE cma_projects ADD CONSTRAINT cma_projects_status_check
  CHECK (status IN (
    'draft', 'uploaded',
    'extracting', 'extracted',
    'classifying', 'classified',
    'reviewing',
    'validating', 'validated', 'validation_failed',
    'generating', 'completed',
    'error'
  ));

-- 2. Add missing columns needed by the pipeline orchestrator
ALTER TABLE cma_projects ADD COLUMN IF NOT EXISTS is_processing BOOLEAN NOT NULL DEFAULT false;
ALTER TABLE cma_projects ADD COLUMN IF NOT EXISTS pipeline_steps JSONB DEFAULT '{}';
ALTER TABLE cma_projects ADD COLUMN IF NOT EXISTS classification_data JSONB;

-- 3. Fix review_queue columns: add missing columns that code relies on
-- The original schema has: source_item, source_amount, ai_suggested_row, etc.
-- Code uses: source_item_name, source_item_amount, suggested_row, etc.
-- We add the code-expected columns alongside the originals for compatibility.
ALTER TABLE review_queue ADD COLUMN IF NOT EXISTS source_item_name TEXT;
ALTER TABLE review_queue ADD COLUMN IF NOT EXISTS source_item_amount NUMERIC;
ALTER TABLE review_queue ADD COLUMN IF NOT EXISTS suggested_row INTEGER;
ALTER TABLE review_queue ADD COLUMN IF NOT EXISTS suggested_sheet TEXT;
ALTER TABLE review_queue ADD COLUMN IF NOT EXISTS suggested_label TEXT;
ALTER TABLE review_queue ADD COLUMN IF NOT EXISTS confidence NUMERIC;
ALTER TABLE review_queue ADD COLUMN IF NOT EXISTS reasoning TEXT;
ALTER TABLE review_queue ADD COLUMN IF NOT EXISTS source TEXT;
ALTER TABLE review_queue ADD COLUMN IF NOT EXISTS alternative_suggestions JSONB;
ALTER TABLE review_queue ADD COLUMN IF NOT EXISTS resolved_row INTEGER;
ALTER TABLE review_queue ADD COLUMN IF NOT EXISTS resolved_sheet TEXT;
ALTER TABLE review_queue ADD COLUMN IF NOT EXISTS resolved_label TEXT;

-- 4. Backfill any existing review_queue rows (copy old column values to new columns)
UPDATE review_queue SET
  source_item_name = source_item,
  source_item_amount = source_amount,
  suggested_row = ai_suggested_row,
  suggested_sheet = ai_suggested_sheet,
  confidence = ai_confidence,
  reasoning = ai_reasoning,
  resolved_row = ca_selected_row,
  resolved_sheet = ca_selected_sheet
WHERE source_item_name IS NULL AND source_item IS NOT NULL;

-- Done!
-- After verifying the migration works, you can optionally drop the old columns
-- in a future migration if desired.
