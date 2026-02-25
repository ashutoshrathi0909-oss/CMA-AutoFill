# Phase 04: Document Extraction — Overview

> Complete these 7 tasks in order. Each task = one Claude Code agent session.
> This is where AI integration begins — Gemini reads uploaded documents.
> Use Sequential Thinking MCP for tasks 4.4 and 4.5 (complex prompt design).

| # | File | What It Does | Verify By |
|---|------|-------------|-----------|
| 4.1 | task-4.1-gemini-client.md | Create Gemini API client wrapper | Test API call succeeds |
| 4.2 | task-4.2-excel-parser.md | Parse Tally/Busy Excel exports with openpyxl | Mehta Computers Excel → structured JSON |
| 4.3 | task-4.3-pdf-parser.md | Parse digital PDFs with pdfplumber | Test PDF → structured JSON |
| 4.4 | task-4.4-vision-extractor.md | Scanned docs via Gemini 2.0 Flash Vision | Test image → structured JSON |
| 4.5 | task-4.5-extraction-prompt.md | Design the extraction prompt template | Prompt produces correct output format |
| 4.6 | task-4.6-extraction-endpoint.md | POST /cmas/{id}/extract API endpoint | Upload Mehta file → get extracted items |
| 4.7 | task-4.7-save-extracted-data.md | Save results to DB + update project status | Data persisted, status = 'extracted' |

**Phase 04 result:** Upload any financial document → AI extracts all line items into structured JSON.
