 # Phase 04: Document Extraction — Detailed Documentation

## Overview
Phase 04 establishes the core document parsing and financial extraction pipeline for the CMA AutoFill system. The primary goal is to safely consume uploaded `.xlsx`, `.pdf` (both digital and scanned), `.jpg`, and `.png` files, interpret the accounting structure inside, and output it in a strictly typed JSON structure securely tied to the originating `project` and `firm`. This phase also introduces the first layer of Gemini API integrations.

---

## 1. Gemini API Client Wrapper (`gemini_client.py`)
**Task Reference:** Task 4.1
**Location:** `backend/app/services/gemini_client.py`

I built a reliable wrapper over `google-generativeai` with these key features:
- **Rate-Limiting & Retries**: Added exception catching wrapped in a while loop that attempts to softly retry when hitting timeouts or 429 constraints, pausing for 2 seconds.
- **Support for Multi-Modal Inputs**: Methods like `generate_with_image` and `generate_with_file` inject base64 imagery/documents into the Gemini inline parts system before prompting.
- **Cost & Token tracking**: We query `response.usage_metadata.prompt_token_count` to map out exactly how many tokens `gemini-2.0-flash` consumed per request, and charge it internally using an algorithmic formulation mapped from `$0.10/$0.40 per 1M` tokens model constants.
- **LLM Logs Integration**: Directly persists tokens, latency in milliseconds, and task_type onto Supabase `llm_usage_log`.

## 2. Standardized Excel Parser (`excel_parser.py`)
**Task Reference:** Task 4.2
**Location:** `backend/app/services/extraction/excel_parser.py`

Since 80% of exports from Indian accounting software (Tally, Busy, Zoho) are returned in `.xlsx`, we can skip the latency of an AI model and parse computationally.
- **Parsing Strategy**: The app utilizes `openpyxl` iteratively through rows. The code is trained to ignore padding spaces and blank rows, honing into numeric data matches. 
- **Indian Financial Quirk Handler `clean_indian_number`**: Extracts numeric value from formats like `(50,000)` into `-50000`, cleanly strips commas inside lakhs/crores formats, and translates `Dr` / `Cr` extensions appropriately based on their contextual value sign.
- **Document Profiling**: Heuristically detects standard patterns for "Profit and Loss Array" vs. "Balance Sheet Array" dependent on keyword inclusions (e.g. `P&L`, `BS`, `TB`). It outputs the common JSON structure defined later.

## 3. Digital PDF Extractor (`pdf_parser.py`)
**Task Reference:** Task 4.3
**Location:** `backend/app/services/extraction/pdf_parser.py`

If the uploaded PDF isn't scanned, we use `pdfplumber` to extract native tables:
- **Identification Layer**: `is_digital_pdf` checks if the extraction on page index 0 yields at least 50 valid text characters. If so, it processes it locally; otherwise, it sends it to the vision model (scanned paper).
- **Table Detection**: Safely isolates structured grids where available. Missing grids will just append item texts and amount integers iteratively into standard arrays.

## 4. Gemini Flash Vision AI Logic (`vision_extractor.py`)
**Task Reference:** Task 4.4 
**Location:** `backend/app/services/extraction/vision_extractor.py`

When documents are image bytes (i.e. pictures of physical ledgers) or scanned PDFs empty of text markup, we use Gemini's robust multimodal capability:
- **Execution Loop**: Injects the parsed image blob along with the mime type securely into the generative model context via the `GeminiClient` written earlier.  
- **Configuration Defaults**: Bounding box extraction relies strictly on `0.0` temperature logic ensuring zero mathematical hallucinations on numeric sums, restricted directly into the `response.mime_type = application/json` architecture for flawless integration.

## 5. Vision Prompts Formulation (`prompts.py`)
**Task Reference:** Task 4.5
**Location:** `backend/app/services/extraction/prompts.py`

- I wrote standard structural expectations mapping JSON formatting exactly so that AI extraction cleanly overlaps with analytical Excel output formats. This provides polymorphic safety downstream regarding structure rules.
- Included Indian financial accounting specific rules directly in the system context ("Convert Indian number format to plain numbers", "Do not modify accounting entity keys").

## 6. End-to-End Extraction API (`extraction.py`)
**Task Reference:** Task 4.6
**Location:** `backend/app/api/v1/endpoints/extraction.py`

- The `POST /api/v1/projects/{project_id}/extract` hook routes database `id` validations against `current_user.firm_id` first. 
- Discovers `uploaded_files` linked with `pending` extraction and dynamically queues parsing instances based on the mime type/extension suffix directly triggering Excel/PDF/Vision respectively.
- Aggregates the statuses locally tracking arrays to respond cleanly to the client interface regarding exactly which files succeeded/failed. 

## 7. Data Fusion & State Update (`merger.py` / `router.py`)
**Task Reference:** Task 4.7
**Location:** `backend/app/services/extraction/merger.py`

- If extraction successfully terminates, the merger checks all documents correlated via project. It fuses distinct subsets together (e.g. splitting the line-items from a 'Profit_and_loss.xlsx' and merging them beside data extrapolated from a 'Balance_sheet.pdf').
- Stores ultimate outputs inside the `JSONB` parameter `extracted_data` directly onto the `cma_projects` payload tracking metrics.
- Upgrades `status` of the firm to the newly inserted Database Enum check metric `'extracted'`. Upgrades the `pipeline_progress` to integer `25`.
- Registered `pytest` suites safely evaluating our extraction components mock-up responses checking parsing structure viability. All testing hooks pass locally!
