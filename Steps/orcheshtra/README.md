# Phase 08: Pipeline Orchestrator — Overview

> Complete these 7 tasks in order. Each task = one Claude Code agent session.
> This phase wires the full pipeline into a one-click workflow with background processing.
> Previously each step was a separate API call — now they chain automatically.

| # | File | What It Does | Verify By |
|---|------|-------------|-----------|
| 8.1 | task-8.1-pipeline-service.md | Core orchestrator: extract → classify → validate → generate | One function runs full pipeline |
| 8.2 | task-8.2-background-tasks.md | Run pipeline steps as background tasks | API returns immediately, processes async |
| 8.3 | task-8.3-progress-tracking.md | Real-time progress via polling endpoint | Frontend can show progress bar |
| 8.4 | task-8.4-error-recovery.md | Handle failures, retry logic, partial results | Failed step → retry or manual fix |
| 8.5 | task-8.5-one-click-endpoint.md | POST /projects/{id}/process — runs everything | Upload → download in one click |
| 8.6 | task-8.6-pipeline-hooks.md | Pre/post hooks for notifications and logging | Email sent at right stages |
| 8.7 | task-8.7-pipeline-tests.md | Integration tests for full pipeline | End-to-end pipeline passes |

**Phase 08 result:** One API call triggers the entire pipeline. Background processing with real-time progress. Error recovery built in.
