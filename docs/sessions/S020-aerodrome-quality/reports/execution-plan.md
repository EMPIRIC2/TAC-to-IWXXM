# Execution plan — S020 / EV-015 (F20 + F6/F12 deepen)

> **Status**: **approved** (2026-07-22) — E15-16..19 all A  
> **Branch**: `evolve/EV-015-aerodrome-quality`  
> **Evolve cycle**: EV-015  
> **Features**: F20 (new); deepen F6.b / F6.c / F12 (SPECI + TAF)  
> **Spec sources**: feature-list §F20; ADR-028; UJ-031; TC-F20-001..006;
> COVERAGE_MATRIX T1–T4 / S1–S3 / C1; api-contract S020 review; E15-1..E15-19

## Current State

| Field | Value |
|-------|-------|
| **Active phase** | Phase C — 07-build |
| **Active milestone** | M5 — FE catalog TAF tags + smoke + verify (F20) |
| **Active task** | T5.6 (pending) |
| **Tasks** | 26 / 28 completed (through T5.5; M5 in progress) |
| **Last updated** | 2026-07-22 |

## Tech Stack Summary

| Area | Choice | Source |
|------|--------|--------|
| Registry | Reuse ADR-028 `packages/tac-validate` registry; add TAF (+ SPECI deepen) rows | E15-3 |
| Public codes | SCREAMING_SNAKE; optional `product`/`tags` (e.g. `taf`) | EV-011 pattern |
| Catalog (docs) | Regenerate `ISSUE_CATALOG.md` (+ JSON); drift tests | Existing |
| Catalog (HTTP) | Existing `GET /api/v1/lint-issue-catalog` — **extend FE filters/copy for TAF tags** | E15-14=C |
| Research | **Full mining pass** beyond vendor guidance → session research catalog | E15-13=C |
| Lint fixtures | `packages/tac-validate/tests/fixtures/{accept,negative}/taf\|speci/` | TC-F20-004 |
| Convert goldens | Extend `tac2iwxxm` `annex3_golden` + `iwxxm_us_golden` (TAF + SPECI) | TC-F20-002/003 |
| CI | Existing `ci.yml` / package pytest — **no new GHA workflow** | E15-16=A |
| New deps | **Allowed only via AskQuestion per dep** (default none) | E15-15=B |
| HTTP wire | Unchanged (convert/lint/decode/catalog) | E15-9 |
| Deploy | API+FE redeploy at M5; H1–H3 + **H4–H5 required** | E15-18=A |
| Kill-switch | HARD themes; mid-build block → AskQuestion (no silent defer) | S1.M1 |
| Mining | Full dig **TAF+SPECI only**; siblings cite-only | E15-17=A |

## Interview locks (Batch 1)

| ID | Decision |
|----|----------|
| E15-12 | Milestone order **A** — TAF lint → TAF goldens → SPECI → C1/matrix → smoke |
| E15-13 | Research **C** — full mining pass + session research catalog |
| E15-14 | FE **C** — extend catalog panel copy/filters for TAF tags |
| E15-15 | Deps **B** — AskQuestion per new dependency (prefer none) |

## Milestones & Tasks (TDD order)

`evolve_cycle_id: EV-015` · `feature_ids: [F20, F6, F12]`

### M0 — Research mining catalog (F20)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T0.1 | Docs | Mine WMO guidance + Annex/FMH/codes sources for TAF+SPECI; write `reports/taf-speci-research-catalog.md` mapping → themes T1–T4 / S1–S3 / C1 | E15-13; #735/#734 | — | completed |
| T0.2 | Docs | Link catalog from COVERAGE_MATRIX F20 section; cite-only paywall | F20 acc4 | T0.1 | completed |

### M1 — TAF lint themes T1–T3 (F20 / F12)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T1.1 | Test | Accept/negative fixtures T1 (NIL/CNL/AMD/COR) | TC-F20-004; matrix T1 | T0.2 | completed |
| T1.2 | Code | Registry rows + TAF rules for T1 | F20; ADR-028 | T1.1 | completed |
| T1.3 | Test | Fixtures T2 (FM/BECMG/TEMPO/PROB + TL/AT) | matrix T2 | T1.2 | completed |
| T1.4 | Code | Encode T2 | F20 | T1.3 | completed |
| T1.5 | Test | Fixtures T3 (TX/TN; CAVOK/NSC/NSW/VV///) | matrix T3 | T1.4 | completed |
| T1.6 | Code | Encode T3 | F20 | T1.5 | completed |

### M2 — TAF goldens T4 (F20 / F6.c)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T2.1 | Test | Expand annex3 (+ iwxxm_us) TAF golden manifests; M-xsd/M-sch stubs | TC-F20-002 | T1.6 | completed |
| T2.2 | Code | Convert fidelity fixes for TAF exceptional rules; root `iwxxm:TAF` | F6.c; #735 | T2.1 | completed |
| T2.3 | Docs | Mark matrix T1–T4 closed or AskQuestion-deferred | S1.M1 | T2.2 | completed |

### M3 — SPECI S1–S3 (F20 / F6.b / F12)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T3.1 | Test | SPECI accept/negative deepen (S1); registry codes | TC-F20-004; #734 | T2.3 | completed |
| T3.2 | Code | SPECI rule deepen via registry | F12; F20 | T3.1 | completed |
| T3.3 | Test | Mis-classification guards SPECI↔METAR (S2) | TC-F20-006 | T3.2 | completed |
| T3.4 | Code | Auto-detect / product-hint fixes if any fail | F20 | T3.3 | completed |
| T3.5 | Test | Expand SPECI goldens annex3/iwxxm_us (S3); root `iwxxm:SPECI` | TC-F20-003 | T3.4 | completed |
| T3.6 | Code | Convert fidelity for new SPECI goldens | F6.b | T3.5 | completed |

### M4 — Common C1 + matrix close (F20)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T4.1 | Test | Common-rule fixtures (reportStatus/nilReasons/CRS/one-report) where lint applies | matrix C1; #735/#734 | T3.6 | completed |
| T4.2 | Code | Encode/defer C1 with rationale | F20; guidance | T4.1 | completed |
| T4.3 | Docs | COVERAGE_MATRIX F20 acc checklist; ISSUE_CATALOG regen | F20 acc4 | T4.2 | completed |
| T4.4 | Test | TC-F20-001 registry completeness green | TC-F20-001 | T4.3 | completed |

### M5 — FE catalog TAF tags + smoke + verify (F20)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T5.1 | Test | Vitest: catalog panel filters/copy for TAF tags | E15-14; TC-F20-005 | T4.4 | completed |
| T5.2 | Code | FE: extend catalog panel filters/copy for TAF (additive) | E15-14; UJ-031 | T5.1 | completed |
| T5.3 | Test | API smoke `product=taf` + `product=speci` lint+convert + catalog GET | TC-F20-005 | T5.2 | completed |
| T5.4 | Config | 08-verify-build — lint/typecheck/format/full suites | 08 | M0–M4, T5.2 | completed |
| T5.5 | Test | 09-qa + 10-e2e — UJ-031 / TC-F20-001..006 | 09/10 | T5.4 | completed |
| T5.6 | Docs | 11-verify-impl — per-Fn F20 + F6/F12 deepen sign-off | 11 | T5.5 | pending |
| T5.7 | Test | 13-deploy-smoke — redeploy if API/FE changed; H1–H3 if API; **H4–H5 if FE** (T5.2) | 13; E15-7 | T5.6 | pending |

## Data Dependencies

| Asset | Needed by | Notes |
|-------|-----------|-------|
| Vendor `TAC-to-XML-Guidance.txt` + 2025-2 XSD/SCH | M0–M4 | Read-only vendor |
| #735/#734 exceptional-rule tables | M1–M3 | Issue bodies |
| Existing METAR/SPECI F15 fixtures | M3 S2 | Adjacency baseline |
| Existing TAF goldens (if any) | M2 | Extend |
| Mining sources (Annex/FMH/codes/EUR as needed) | M0 | Cite-only; full dig per E15-13 |

## Git Strategy

- Branch: `evolve/EV-015-aerodrome-quality`
- Atomic commits per task: `[T1.1] test: …`
- Evolve PR to `main` after M5 / Phase D
- After push: `bash scripts/ci/watch_github_ci.sh`
- **HARD themes (S1.M1)**: if blocked mid-build → AskQuestion; do **not** silently defer

## Connectivity (H0c / H4–H5)

- No new CORS / `VITE_*` knobs expected
- FE catalog filter work → **H4–H5 required** after FE deploy (E15-14)
- Re-run H0c if API image changes
- Staging secrets matrix: reuse existing rows

## Phase Gate Check (B→C)

- [x] Execution plan approved by user (E15-19=A)
- [x] 05-verify-tech — **skipped** (S9.M1); 04-exit consistency PASS (below)
- [x] 06-tech-tooling — **skipped** (Lean+build; no new hooks in plan)

## 04-exit consistency (S9.M1 substitute for 05)

| Check | Result |
|-------|--------|
| F20 ↔ milestones M0–M5 | PASS |
| UJ-031 ↔ TC-F20 ↔ tasks | PASS |
| Matrix themes ↔ M1–M4 | PASS |
| FE catalog filters ↔ T5.1–T5.2 + H4–H5 | PASS |
| No new routes vs api-contract | PASS |
| Deps policy AskQuestion-gated | PASS |
| 05/06 skip documented | PASS |

## Phase Gate Log

| Gate | Date | Result | Notes |
|------|------|--------|-------|
| A→B | 2026-07-22 | passed | D-S020-EV015-phase-a-pass |
| B plan | 2026-07-22 | approved | E15-16..19 all A; D-S020-EV015-plan-1 |
| B tech audit | 2026-07-22 | waived | 05 skipped; 04-exit consistency PASS |
| B→C | 2026-07-22 | passed | D-S020-EV015-phase-b-pass → 07 @ T0.1 |
