# Execution plan — S067 / EV-057 (M0 Ready: #948 / #903 / #838)

> **Generated**: 2026-08-15  
> **Skill**: 04-tech-plan (delta)  
> **Branch**: `evolve/EV-057-m0-ready-apex-accumulate-validate`  
> **Issues**: [#948](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/948),
> [#903](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/903),
> [#838](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/838)  
> **Build Plan Card**: `docs/sessions/S067-m0-ready-apex-accumulate-validate/build-plan-card.md`

**Corpus**: [Corpus: product §F7] [Corpus: product §F30] [Corpus: product §F2]
[Corpus: product §F4] [Corpus: deploy] [Corpus: journeys] [Corpus: tests]
[Corpus: decisions §EV-057]

## Current State

| Field | Value |
|-------|-------|
| **Active phase** | Phase 1: EV-057 M0 Ready pack |
| **Active milestone** | M1–M3 complete (incl. #948 **live** UJ-OPS-002) |
| **Active task** | — (next **08-verify-build**) |
| **Tasks completed** | 14 / 14 |
| **Stage** | 07-build |
| **Last updated** | 2026-08-16 |
| **Plan approval** | **approved** `D-S067-04-plan=1` (2026-08-15) |
| **PR** | — |

## Tech decisions (proposed — confirm with `D-S067-04-plan`)

| ID | Choice |
|----|--------|
| D-S067-m-order | **M1 #948 → M2 #903 → M3 #838** (issue order; infra first) |
| D-S067-948-impl | **Sibling prod Ingress** `metar-frontend-apex` + **`metar-apex-redirect`** nginx pod (`return 301 …$request_uri`). ingress-nginx v1.12 webhook rejects `$` on `permanent-redirect`; snippets disabled (`D-S067-948-redirect=1a`). Same overlay as FE Ingress; **do not** redirect `metar-frontend` / `app.`. TLS secret `metar-frontend-apex-tls`. Realizes `D-S067-948-ingress=2a`. |
| D-S067-903-state | FE accumulate list in workbench state (FileConverter / result cards); clear control; cap **≤200** with clear error. |
| D-S067-903-zip | Extend `outputArchiveName` / helpers: empty custom → `{stem8}_{yyyyMMddHHmmss}.zip` from first success TAC; custom → `{base}.zip`. |
| D-S067-838-ui | Dedicated Validate mode: paste + single `.xml` upload; call existing `POST /api/v1/validate`; F4 controls shared. |
| D-S067-838-api | **No wire change** unless 04 spike finds gap (multipart file + text already). Re-open api-contract only on gap. |
| D-S067-deps | **No new** npm/PyPI deps (`D-S067-04-deps=1a`). |
| D-S067-adr | **No new ADR** unless cert/DNS forces a platform decision. |
| D-S067-connectivity | No new CORS origins for UI APIs. #948 is ops/Ingress. H4–H5 for UJ-057/058 via 12/13; UJ-OPS-002 on prod after promote (or curl against prod when #948 lands — note apex is **prod-only**). |
| D-S067-board | Keep WIP≤2: #948 In progress through M1; move #903/#838 In progress when their milestones start. |

### Locked (Gate A)

| ID | Choice |
|----|--------|
| D-S067-903-cap | **≤200** |
| D-S067-948-ingress | Extend prod FE Ingress family (sibling apex Ingress) |
| D-S067-gateA | PASS |
| D-S067-promote | Stage all three; promote after re-approve |

## Tech Stack Summary

| Category | Choice | Source |
|----------|--------|--------|
| Apex redirect | nginx Ingress permanent-redirect (sibling) | `D-S067-948-impl` |
| Accumulate UI | React workbench state | F7.r |
| ZIP naming | `apps/frontend/src/utils/outputFilename.ts` | #664 / #903 |
| Validate API | Existing `POST /api/v1/validate` | [Corpus: api] |
| Tests | Vitest + Playwright + ops curl | TC-EV057-* |
| Connectivity | Existing H0c/H4–H5 | connectivity-gates |

## Data Dependencies

| Asset | Status | Notes |
|-------|--------|-------|
| Prod TLS / DNS for apex (+ www) | **verify in M1** | Block #948 Done if cert/DNS missing — escalate |
| IWXXM validate fixtures | in-repo | UJ-058 good/bad fixtures |
| None (ML weights) | n/a | — |

## Implementation Phases

### Phase 1: EV-057 M0 Ready pack

**Entry**: Gate A PASS; `D-S067-04-plan` approved.  
**Exit**: AC for #948/#903/#838 met on `stage`; ready for 08→…→13; promote AskQuestion later.

#### M1: Apex → app redirect (#948 / F30) — P0

**Goal**: Prod apex (+ www if covered) permanently redirects to `app` with path/query.  
**Acceptance**: TC-EV057-948-001..003; UJ-OPS-002; feature-list F30 AC.

| # | Task | Type | Status | Spec Source | Depends On | Data Deps |
|---|------|------|--------|-------------|------------|-----------|
| T1.1 | Verify DNS/TLS coverage for `tac-to-iwxxm.com` (+ `www`); document gaps | Spike/Docs | **completed** | #948 AC4; deploy.md | — | DNS/cert |
| T1.2 | Add sibling Ingress `metar-frontend-apex` (hosts + permanent-redirect + TLS) in prod overlay | Impl | **completed** | `D-S067-948-impl`; deploy.md | T1.1 | — |
| T1.3 | Update `docs/deploy.md` with applied resource names; ops curl checklist | Docs | **completed** | TC-EV057-948-003 | T1.2 | — |
| T1.4 | Ops smoke script or Makefile target notes for UJ-OPS-002 (prod) | Test/Docs | **completed** | TC-EV057-948-001..002 | T1.2 | prod LB |

#### M2: Accumulate conversions → one ZIP (#903 / F7.r) — P0

**Goal**: Sequential successes accumulate; Download all ZIP; stem naming; clear; cap ≤200.  
**Acceptance**: TC-EV057-903-001..007; UJ-057.

| # | Task | Type | Status | Spec Source | Depends On | Data Deps |
|---|------|------|--------|-------------|------------|-----------|
| T2.1 | Red tests: accumulate N≥2; clear; fail leaves priors; cap≤200 | Test | **completed** | TC-EV057-903-001/005/007 | — | — |
| T2.2 | Red tests: default ZIP stem from first TAC (~8); custom `{base}.zip` | Test | **completed** | TC-EV057-903-003/004 | — | — |
| T2.3 | Implement accumulate state + clear + cap in FileConverter (or extract) | Impl | **completed** | F7.r AC1/5/6/7 | T2.1 | — |
| T2.4 | Implement ZIP Download all + `outputArchiveName` stem rules | Impl | **completed** | F7.r AC2–4 | T2.2, T2.3 | — |
| T2.5 | Playwright UJ-057 smoke (local) | Test | **completed** | TC-EV057-903-006 | T2.3, T2.4 | — |

#### M3: Validate existing IWXXM (#838 / F7.s) — P0

**Goal**: Validate mode paste + single XML upload without TAC convert.  
**Acceptance**: TC-EV057-838-001..005; UJ-058.

| # | Task | Type | Status | Spec Source | Depends On | Data Deps |
|---|------|------|--------|-------------|------------|-----------|
| T3.1 | Spike: confirm `POST /api/v1/validate` accepts paste text + single file; note gap | Spike | **completed** | `D-S067-838-api` | — | — |
| T3.2 | Red tests: paste good → pass; broken → structured fail; upload one xml | Test | **completed** | TC-EV057-838-001..003 | T3.1 | fixtures |
| T3.3 | Implement Validate mode UI (paste + upload) + F4 controls; wire validate API | Impl | **completed** | F7.s AC1–5 | T3.2 | — |
| T3.4 | Playwright UJ-058 smoke (guest) | Test | **completed** | TC-EV057-838-005 | T3.3 | — |
| T3.5 | api-contract delta **only if** T3.1 found wire gap; else doc note “reuse” | Docs | **completed** | `D-S067-01-api` | T3.1 | — |

## Git Strategy

- Branch: `evolve/EV-057-m0-ready-apex-accumulate-validate` → PR → **`stage`**
- One atomic commit per task id when practical
- Milestone minor PRs optional; default one evolve PR to stage after M1–M3 + 08
- Promote `stage`→`main` only after separate re-approve (`D-S067-promote=2b`)

## PR checklist (minor → stage)

- [ ] M1–M3 tasks completed; tests green
- [ ] No new deps without inventory AskQuestion
- [ ] deploy.md apex section matches applied Ingress
- [ ] Board: issues → In review / On stage as appropriate
- [ ] H4–H5 planned for 13 (UJ-057/058); UJ-OPS-002 on prod when #948 live

## Risks

| Risk | Mitigation |
|------|------------|
| Apex DNS/cert missing | T1.1 blocks; escalate to user |
| permanent-redirect on shared Ingress | Use sibling Ingress only |
| Accumulate state vs replace-card regressions | T2.1 red first; clear control |
| Validate multipart gap | T3.1 spike; reopen api-contract if needed |
| #948 only verifiable on prod | Document; staging apex OOS |

## Approval

**Approved** `D-S067-04-plan=1` — sibling apex Ingress; M1→M2→M3; no new deps; skip 05/06 → 07 M1.
