# 01-requirements — Session S003 Report

| Field | Value |
|-------|-------|
| **Session** | S003-supabase-keys-config |
| **Branch** | `fix/supabase-service-key-leak` |
| **Stage** | 01-requirements (delta) |
| **Completed** | 2026-06-23 |
| **Mode** | delta — security hardening hotfix |

## Intent

Delta requirements interview for:

1. Retire `SUPABASE_SERVICE_ROLE_KEY` in favor of Publishable/Secret key system
2. Minimal `.env.example`; non-secrets in `config/{local,prod}.json` (prod first)
3. Supabase database + auth advisor remediation (METAR project)
4. Align env vars across Render, Supabase, and local with verify tooling

## Decisions confirmed

| ID | Decision |
|----|----------|
| S003-R1 | `SUPABASE_PUBLISHABLE_KEY` + `SUPABASE_SECRET_KEY` canonical |
| S003-R2 | Runtime `/config.json` fetch at frontend bootstrap |
| S003-R3 | METAR `ktvxijislbtgqapllmuk`; migrations 003–004 **not applied** |
| S003-R4 | Ports 18000/18001 standardized |
| S003-R6 | Env sync contract + `make env-check` |

## Generated / updated artifacts

| Document | Action |
|----------|--------|
| `docs/config-spec.md` | **Created** — standing config spec |
| `docs/env-contract.md` | **Created** — Render ↔ Supabase ↔ local matrix |
| `docs/env-sync-runbook.md` | **Created** — operator rotation checklist |
| `docs/adr/ADR-010-supabase-keys-config-split.md` | **Created** |
| `docs/requirements-decisions.md` | **Updated** — S003-R1–R9 |
| `docs/deploy.md` | **Updated** — Integration section |
| `docs/api-contract.md` | **Updated** — admin auth + frontend config |
| `docs/test-plan.md` | **Updated** — H0e `make env-check` |
| `docs/spec.md` | **Updated** — config component + security |
| `docs/feature-list.md` | **Updated** — M4 S003 delta note |
| `docs/staging-secrets-matrix.md` | **Updated** — superseded banner |
| `config/prod.json`, `config/local.json` | **Created** |
| `config/README.md` | **Created** |
| `.env.example` | **Updated** — five secrets only |

## Advisor remediation plan

### METAR database (in scope)

- Apply migrations `003_supabase_advisor_remediation.sql` and `004_consolidate_user_profiles_policies.sql`
- Verify zero ERROR on `user_profiles`, upload, evaluation tables

### METAR auth (dashboard)

- Enable leaked-password protection (HaveIBeenPwned)

### Out of scope

- CogniChem org Supabase projects (`jobs`, `user_wallet`, etc.) — different products
- MCP not linked to METAR project `ktvxijislbtgqapllmuk`

## Gaps / follow-ups for 07-build

1. Implement `packages/shared` config loader (Python + TS)
2. Frontend bootstrap fetch `/config.json`
3. Refactor `admin_api.py`, `evaluation.py` to user-JWT + RLS
4. `scripts/env/verify-sync.sh` + `make env-check`
5. Update `render.yaml`, `docker-compose.yml`, CI secret names
6. Apply SQL migrations on live METAR project
7. Edge functions still use `SERVICE_ROLE_KEY` — follow-up

## Next step

`14-hotfix` (key rotation wiring) → `07-build` (implementation per routing plan T1–T10)
