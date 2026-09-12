# Scoped context — platform-independence-842

**Status:** active · **Created:** 2026-08-03 · **Session:** S038 / EV-031  
**Issues:** [#842](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/842) (epic), [#830](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/830), [#712](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/712)

## Intent

Umbrella for reducing platform lock-in: remaining Supabase runtime coupling and Render → DOKS hosting move. User chose **full epic including DOKS planning + IaC** this cycle (`D-S038-open`=3).

## Resolutions (local)

| ID | Topic | Resolution |
|----|-------|------------|
| R1 | Epic children | #830 + #712 both in-cycle; prefer #830 before #712 secrets redesign |
| R2 | Cycle type | `general` platform independence; allocate Fn in Phase 1 (candidate **F30**) |
| R3 | Preset | Standard routing |
| R4 | UI | Non-deployed local Vite preview accepted |
| R5 | DOKS depth | **3** — full production cutover this cycle (`D-S038-doks-depth`) |
| R6 | F8 | Keep; persist on **DigitalOcean Postgres** (`D-S038-f8`=1) |
| R7 | Topology | Supabase = **Auth / session verification only**; DO = **all DB components** + DOKS |
| R8 | Routing | Standard approved (`D-S038-route`=1) |
| R9 | Auth vs F21 | **Amend F21** — login restored for **long-term storage**; guests remain usable locally (`D-S038-auth-model`=1) |
| R10 | Sessions | Logged-in → DO Postgres; guest → IndexedDB + **loss-of-progress notice**; honor **F22** privacy/cookie prefs (`D-S038-session-store`=1) |
| R11 | #830 | Amend in-place: Auth-kept, strip data plane (`D-S038-830-amend`=1) |

## Target topology (locked — 2026-08-03)

```
Guest (transient) ── local/IndexedDB only + UI notice ("log in to keep progress")
                     └── storage gated by F22 privacy preferences

Logged-in operator ── Supabase Auth (JWT) ──► API on DOKS
                                              ├── verify JWT via Supabase Auth only
                                              └── work sessions → DigitalOcean Postgres

F8 worker on DOKS ── DATABASE_URL ──► DigitalOcean Postgres
Static UI ── DO edge (CDN/Ingress)
Supabase ── Auth / verification ONLY (no product PostgREST tables)
```

## Discovery snapshot (pre-inventory)

Residual Supabase coupling still visible after S023 / EV-017 (#783) operator-auth removal:

| Area | Evidence (examples) |
|------|---------------------|
| Env / deploy | `.env.example`, `render.yaml` `SUPABASE_*`; worker service-role |
| Shared | `packages/shared/.../supabase_env.py`, config_loader |
| Worker F8 | `apps/worker` settings/store — PostgREST/service-role writers |
| Backend | `apps/backend/src/services/database.py`, security utilities |
| Frontend | `apps/frontend/src/utils/supabase/*`, runtime-config, tests |
| Docs | `docs/deploy.md`, ops runbooks, test-plan F8 secrets notes |
| CI / supabase dir | `supabase/migrations/`, sync workflows (docs-referenced) |

## Non-goals (epic + product)

- Rewrite convert/validate engines
- Force operators off generic Postgres BYOC (F16) if URI is plain Postgres
- Dual-run production hosts in the epic itself — **unless** depth Decision waives for a controlled cutover

## Open decisions for Phase 1 / 01

1. Fn split (proposed F30 platform + F31 hybrid sessions) — `D-S038-fn`
2. Guest→login migration of local drafts (merge / discard / prompt) — detail in 01
3. Privacy: which F22 categories gate IndexedDB vs auth cookies vs analytics — detail in 01
4. Reintroduce `packages/auth` vs inline JWT verify — ADR in 04
5. BYOC “Supabase Postgres URI” — allow as plain Postgres vs refuse
6. Legacy Supabase `tac_work_sessions` archive policy
7. DOKS soak window / DNS / Render decommission checklist detail

## Links

- [Corpus: product] `docs/feature-list.md` — F5 IndexedDB, F8 worker, F16 BYOC, F21 public app
- [Corpus: tech-spec] / `docs/deploy.md` — Render + Supabase env
- ADR-018 (worker), ADR-006 (Render), ADR-021/029 (dissemination)
