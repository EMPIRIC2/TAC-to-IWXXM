# Session S003 — Supabase keys, config split, advisor remediation

| Field | Value |
|-------|-------|
| **ID** | S003-supabase-keys-config |
| **Type** | hotfix (security hardening) |
| **Branch** | `fix/supabase-service-key-leak` |
| **Status** | in_progress |
| **Started** | 2026-06-23 |

## Intent

On branch `fix/supabase-service-key-leak`, address the GitHub secret-scanning incident
(BUG-2026-06-23) and harden Supabase integration:

1. **Retire legacy `service_role` JWT keys** — adopt Supabase Publishable/Secret Key system
   (`sb_publishable_*` / `sb_secret_*`) everywhere server-side secrets are required.
2. **Minimal `.env.example`** — secrets only; move non-secret settings to per-environment
   `config.json` (prod first).
3. **Supabase advisor remediation** — clear database linter and auth warnings for the METAR
   project (`ktvxijislbtgqapllmuk` per bug report and edge-function source).
4. **Align env vars across Render, Supabase, and local** — single canonical contract,
   reduced duplication, and a repeatable sync/verify process.

## Scope

| In | Out |
|----|-----|
| Env var rename/consolidation | Product feature changes (F1–F4 behavior) |
| `config/prod.json` (and loader) | `dev`/`stage` config files until requested |
| Code paths using `SUPABASE_SERVICE_ROLE_KEY` | Rewriting `packages/gifts` or conversion logic |
| SQL migrations for METAR advisor gaps | Org-wide CogniChem Supabase projects (separate repos) |
| Env sync contract (Render ↔ Supabase ↔ local) + verify tooling | Full Render env-var-group automation (manual dashboard OK v1) |
| Docs: deploy, api-contract, DEVELOPMENT | Full edge-function retirement (follow-up) |

## Linked artifacts

- Bug report: `docs/bug-reports/BUG-2026-06-23-supabase-service-key-leak.md`
- Scoped context: `docs/context/supabase-keys-config.md`
- Existing advisor SQL: `apps/frontend/supabase/migrations/003_*.sql`, `004_*.sql`
- SQL optimization reference: `docs/sql-optimization/`

## Feature mapping

- **F3** — Auth / admin / airport data services (Supabase integration)
- **M4** — Auth merged into backend API (key loading in `packages/auth`)
