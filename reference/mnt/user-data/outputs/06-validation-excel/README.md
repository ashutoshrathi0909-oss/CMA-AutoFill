# Phase 06: Validation & Excel Generation — Overview

> Complete these 7 tasks in order. Each task = one Claude Code agent session.
> This phase integrates the proven cma_writer.py (100% accuracy from POC).
> The CMA Excel file is the final deliverable that goes to the bank.

| # | File | What It Does | Verify By |
|---|------|-------------|-----------|
| 6.1 | task-6.1-validation-rules.md | Cross-check numbers (P&L totals = BS totals, etc.) | Deliberate errors caught |
| 6.2 | task-6.2-validation-service.md | Validation engine + auto-fix suggestions | Returns pass/fail per check |
| 6.3 | task-6.3-integrate-cma-writer.md | Adapt cma_writer.py as a backend service | Writer module works in FastAPI |
| 6.4 | task-6.4-data-transformer.md | Transform classified items → writer input format | Classified data → row-mapped dict |
| 6.5 | task-6.5-excel-generation.md | Generate CMA Excel using template + classified data | Output file matches template |
| 6.6 | task-6.6-generation-endpoint.md | POST /projects/{id}/generate + download | API triggers generation |
| 6.7 | task-6.7-golden-test.md | End-to-end test: Mehta Computers → CMA Excel | Output matches reference file |

**Phase 06 result:** Validated, classified data is written into the CMA Excel template — the actual bank document.
