# Implementation verification — 11-verify-impl (S071 / EV-061)

> Generated: 2026-08-20  
> Branch: `evolve/EV-061-pre-promote-ux-catalog`  
> Tip (at stage start): `dba4e21a`  
> PR: [#1016](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1016)  
> Corpus: [Corpus: product §F2] [Corpus: product §F6] [Corpus: product §F7]
> [Corpus: product §F9] [Corpus: product §F10] [Corpus: product §F15] [Corpus: product §F34]
> [Corpus: journeys] [Corpus: tests] [Corpus: decisions §EV-061]

## Intake (recommended defaults)

| Decision | Choice |
|----------|--------|
| `D-S071-11-preview` | **1** — Yes, non-deployed local preview |
| `D-S071-11-scope` | **1** — Full EV-061 delta (UJ-064..068 + #1010–#1015) |
| `D-S071-11-1017` | **1** — Catalog deepen #1017 after EV-061 promote |

## UI preview (non-deployed)

| Item | Value |
|------|--------|
| Stack | Existing `make dev` (terminal) |
| Frontend | http://localhost:18000/ |
| API | http://localhost:18001/ (`/health` 200) |
| Label | **Local only — not staging/production** |

### Spot-check observations (agent browser, 2026-08-20)

| Surface | Observation |
|---------|-------------|
| Shell tab | **Lint & validation catalog** present alongside Convert / History / Quality metrics |
| Catalog page | Family filter (All / TAC lint / IWXXM); table Code / Level / Description / Source |
| Catalog sources | Many rows → `store.icao.int` Annex 3; PDFs without page/section anchors — tracked as **#1017** (not a #1014 AC fail) |
| Convert chrome | Product type + Profile selects; Conversion Parameters region; mode tabs include AHL bulletin + Validate IWXXM |
| AHL demo | Golden **AHL METAR multi-report** loads; Product=METAR, Profile=Annex 3, AHL bulletin mode selected |

## Phase 1 — Collected results

| Source | Result |
|--------|--------|
| `reports/qa-report.md` (09) | **PASS** delta; advisories QA-001..005 |
| `reports/e2e-report.md` (10) | **PASS** T2 local — UJ-064..068 (6 Playwright); T3/H4–H5 deferred → 12/13 |
| 08-verify-build M1–M6 | **PASS** (m1…m6 reports) |
| H0c / H0i | **PASS** |

## Phase 2 — Feature completeness (EV-061 deepen only)

| Ticket / deepen | Fn | Implemented | Tests | QA | E2E | AC (ship) |
|-----------------|----|-------------|-------|----|-----|-----------|
| #1010 readable validate decode | F2/F9/F10 | ✓ | ✓ TC-EV061-1010 | clean | UJ-064 PASS | met for ship |
| #1012 AHL decode + convert | F6/F7 | ✓ | ✓ TC-EV061-1012 | clean | UJ-065 PASS | met |
| #1013 Product/Profile + param bars | F7.u | ✓ | ✓ Vitest 1013 | clean | UJ-066/067 PASS | met |
| #1014 catalog tab/page | F7.v/F15 | ✓ | ✓ TC-EV061-1014 | clean | UJ-068 PASS | met (**#1017** follow-up) |
| #1011 multipart live harness | F6 | ✓ | ✓ TC-EV061-1011 | clean | N/A (live harness) | met |
| #1015 stage→main gate | F34 | ✓ CI jobs + docs | ✓ TC-EV061-1015 | QA-003 admin rulesets | UJ-DEV-009 CI | code met; **admin apply pending** |

### Scope analysis

```
Scope Analysis (EV-061 delta):
  Features in cycle deepen: 6 tickets (#1010–#1015)
  Features implemented: 6
  Features with passing local E2E / CI contracts: 6
  Undocumented features (scope creep): 0
  Missing features (scope gap vs #1009 ship): 0
  Deferred deepen (explicit): #1017 sources+sort/filter; #996 click-detail; staging H4–H5
```

## Phase 3a — Journey signoff

| Journey | T0 | T2 local | T3 / H4–H5 | User |
|---------|----|----------|------------|------|
| UJ-064 | PASS | PASS | deferred 12/13 | **APPROVED** |
| UJ-065 | PASS | PASS | deferred 12/13 | **APPROVED** |
| UJ-066 | PASS | PASS | deferred 12/13 | **APPROVED** |
| UJ-067 | PASS | PASS | deferred 12/13 | **APPROVED** |
| UJ-068 | PASS | PASS | deferred 12/13 | **APPROVED** (#1017 follow-up) |
| UJ-DEV-009 | PASS contracts | N/A | rulesets empty until admin | **APPROVED** |

**Decision:** `D-S071-11-ac=1a` — approve all journeys + features #1010–#1015 (2026-08-20).

T3 waiver for this stage: per `D-S071-e2` / e2e-report — staging connectivity at **12/13**, not blocking local 11 approval.

## Phase 3 — Feature approval

| Ticket | User |
|--------|------|
| #1010 / #1011 / #1012 / #1013 / #1014 / #1015 | **APPROVED** (`D-S071-11-ac=1a`) |

## Phase 5 — Scope

Creep: 0 · Gaps vs #1009 ship: 0 · Explicit defer: #1017, #996, staging H4–H5

## Advisories carried to 12/13

1. **QA-003** — Run `bash scripts/deploy/apply_gh_branch_rulesets.sh` before real promote  
2. **H4–H5** — Staging frontend after merge to `stage`  
3. **#1017** — Catalog source verifiability + category sort/filter (post-promote)

## Status

- Stage: **COMPLETED** — `D-S071-11-ac=1a`  
- Next: **12-verify-deploy** (staging via PR #1016 → `stage`)
