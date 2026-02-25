# Phase 11: Testing & Production Deploy — Overview

> Complete these 7 tasks in order. Each task = one Claude Code agent session.
> This phase hardens the app for real users and deploys to production.
> After this phase, your father can use CMA AutoFill for real clients.

| # | File | What It Does | Verify By |
|---|------|-------------|-----------|
| 11.1 | task-11.1-e2e-tests.md | Playwright E2E tests for full user journey | Tests pass in browser |
| 11.2 | task-11.2-security-hardening.md | RLS verification, rate limiting, input sanitization | Security checklist passes |
| 11.3 | task-11.3-performance-tuning.md | API response times, query optimization, caching | All endpoints < 500ms |
| 11.4 | task-11.4-error-monitoring.md | Structured logging + error tracking | Errors caught and logged |
| 11.5 | task-11.5-env-production.md | Production environment variables + secrets | Prod config complete |
| 11.6 | task-11.6-deploy-production.md | Deploy frontend (Vercel) + backend (Railway) | App live at production URL |
| 11.7 | task-11.7-smoke-test-launch.md | Smoke test with real data + launch checklist | Father uses it successfully |

**Phase 11 result:** CMA AutoFill is live in production. Your father processes a real CMA successfully.
