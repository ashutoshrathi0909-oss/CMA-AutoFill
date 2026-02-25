# Phase 02: Database & Authentication — Overview

> Complete these 7 tasks in order. Each task = one Claude Code agent session.
> Use Supabase MCP to execute SQL directly — no copy-pasting to dashboard.
> Review tables in Supabase dashboard after each task.

| # | File | What It Does | Verify By |
|---|------|-------------|-----------|
| 2.1 | task-2.1-core-tables.md | Create firms + users tables | Tables visible in Supabase dashboard |
| 2.2 | task-2.2-client-project-tables.md | Create clients + cma_projects tables | Foreign keys work |
| 2.3 | task-2.3-file-tables.md | Create uploaded_files + generated_files + storage bucket | Bucket visible in Storage |
| 2.4 | task-2.4-review-tables.md | Create review_queue + classification_precedents | Unique constraints work |
| 2.5 | task-2.5-logging-tables.md | Create llm_usage_log + audit_log | Tables accept inserts |
| 2.6 | task-2.6-row-level-security.md | Enable RLS + create policies on ALL tables | Firm A can't see Firm B data |
| 2.7 | task-2.7-auth-seed-data.md | Configure magic link auth + seed test data | Can log in + see test data |

**Phase 02 result:** All 10 tables created, RLS enforced, auth working, test data seeded.
