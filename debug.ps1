#!/usr/bin/env pwsh
# =============================================================================
# CMA AutoFill Debug Framework
# Usage: .\debug.ps1 [--backend-only] [--frontend-only] [--fix]
# =============================================================================

param(
    [switch]$BackendOnly,
    [switch]$FrontendOnly,
    [switch]$Fix,         # Pass --fix to auto-trigger Antigravity after errors
    [switch]$Verbose
)

$ErrorActionPreference = "Continue"
$ROOT = $PSScriptRoot
$ERRORS_FOUND = @()
$LOG_FILE = "$ROOT\debug-output\$(Get-Date -Format 'yyyy-MM-dd_HH-mm-ss').log"

# ── Helpers ────────────────────────────────────────────────────────────────────
function Log($msg, $colour = "Cyan") {
    $line = "[$(Get-Date -Format 'HH:mm:ss')] $msg"
    Write-Host $line -ForegroundColor $colour
    Add-Content -Path $LOG_FILE -Value $line -Force
}

function Error($msg) {
    $script:ERRORS_FOUND += $msg
    Log "ERROR: $msg" "Red"
}

function Ok($msg)    { Log "OK:    $msg" "Green" }
function Warn($msg)  { Log "WARN:  $msg" "Yellow" }

# ── Ensure output dir ──────────────────────────────────────────────────────────
New-Item -ItemType Directory -Force -Path "$ROOT\debug-output" | Out-Null

Log "========================================" "White"
Log " CMA AutoFill Local Debug Runner" "White"
Log "========================================" "White"

# ── 1. Pre-flight checks ───────────────────────────────────────────────────────
Log "Phase 1: Pre-flight checks"

# Node.js
$nodeVer = (node --version 2>&1)
if ($LASTEXITCODE -ne 0) { Error "Node.js not found. Install from nodejs.org" }
else { Ok "Node.js $nodeVer" }

# Python
$pyVer = (python --version 2>&1)
if ($LASTEXITCODE -ne 0) { Error "Python not found. Install from python.org" }
else { Ok "Python $pyVer" }

# .env files
if (-not (Test-Path "$ROOT\backend\.env")) {
    Warn "backend/.env missing — backend will fail without API keys"
}
if (-not (Test-Path "$ROOT\frontend\.env.local")) {
    Warn "frontend/.env.local missing — frontend may show blank data"
}

# ── 2. Start Backend ──────────────────────────────────────────────────────────
if (-not $FrontendOnly) {
    Log "Phase 2: Starting FastAPI backend on :8000"
    $backendJob = Start-Job -ScriptBlock {
        Set-Location $using:ROOT\backend
        python -m uvicorn main:app --reload --port 8000 2>&1
    }
    Start-Sleep -Seconds 4

    # Health check
    try {
        $health = Invoke-RestMethod "http://localhost:8000/health" -TimeoutSec 5
        Ok "Backend health: $($health | ConvertTo-Json -Compress)"
    } catch {
        Error "Backend health check failed: $_"
        if ($Verbose) { Receive-Job $backendJob | Write-Host }
    }
}

# ── 3. Start Frontend ─────────────────────────────────────────────────────────
if (-not $BackendOnly) {
    Log "Phase 3: Starting Next.js frontend on :3000"
    $frontendJob = Start-Job -ScriptBlock {
        Set-Location $using:ROOT\frontend
        npm run dev 2>&1
    }
    Start-Sleep -Seconds 7

    # Page check
    try {
        $resp = Invoke-WebRequest "http://localhost:3000" -TimeoutSec 10 -UseBasicParsing
        if ($resp.StatusCode -lt 400) { Ok "Frontend returned HTTP $($resp.StatusCode)" }
        else { Error "Frontend returned HTTP $($resp.StatusCode)" }
    } catch {
        Error "Frontend unreachable: $_"
        if ($Verbose) { Receive-Job $frontendJob | Write-Host }
    }
}

# ── 4. Run Playwright smoke tests ─────────────────────────────────────────────
Log "Phase 4: Running Playwright smoke tests"
if (Test-Path "$ROOT\smoke.test.ts") {
    $env:APP_URL = "http://localhost:3000"
    $env:BACKEND_URL = "http://localhost:8000"
    npx playwright test smoke.test.ts --reporter=list 2>&1 | Tee-Object -FilePath $LOG_FILE -Append
    if ($LASTEXITCODE -ne 0) { Error "Playwright smoke tests failed — see log above" }
    else { Ok "All Playwright smoke tests passed" }
} else {
    Warn "smoke.test.ts not found — skipping browser tests"
}

# ── 5. Run backend unit tests ────────────────────────────────────────────────
if (-not $FrontendOnly -and (Test-Path "$ROOT\backend\tests")) {
    Log "Phase 5: Running backend pytest"
    Set-Location "$ROOT\backend"
    python -m pytest tests/ -v --tb=short 2>&1 | Tee-Object -FilePath $LOG_FILE -Append
    if ($LASTEXITCODE -ne 0) { Error "Backend tests failed" }
    else { Ok "All backend tests passed" }
    Set-Location $ROOT
}

# ── 6. Summary ────────────────────────────────────────────────────────────────
Log "========================================" "White"
if ($ERRORS_FOUND.Count -eq 0) {
    Log "ALL CHECKS PASSED ✅" "Green"
} else {
    Log "$($ERRORS_FOUND.Count) ERROR(S) FOUND ❌" "Red"
    $ERRORS_FOUND | ForEach-Object { Log "  • $_" "Red" }
    Log ""
    Log "Debug log saved to: $LOG_FILE" "Yellow"
    if ($Fix) {
        Log "Opening error log for Antigravity to analyse..." "Cyan"
        # Print a summary for Antigravity to pick up
        Log "=== ERRORS FOR AUTO-DEBUG ===" "Magenta"
        $ERRORS_FOUND | ForEach-Object { Log "FIX_NEEDED: $_" "Magenta" }
    }
}

# ── Cleanup ───────────────────────────────────────────────────────────────────
if ($backendJob)  { Stop-Job $backendJob;  Remove-Job $backendJob }
if ($frontendJob) { Stop-Job $frontendJob; Remove-Job $frontendJob }
