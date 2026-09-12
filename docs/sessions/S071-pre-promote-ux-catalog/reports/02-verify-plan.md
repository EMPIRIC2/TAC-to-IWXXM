# 02-verify-plan — S071 / EV-061 (delta)

**Status:** Gate A **PASS** (`D-S071-gateA=1a`)  
**Preset:** Standard Spec  
**Corpus:** [Corpus: product §F2] [Corpus: product §F6] [Corpus: product §F7] [Corpus: product §F9]
[Corpus: product §F10] [Corpus: product §F15] [Corpus: product §F34] [Corpus: journeys]
[Corpus: tests] [Corpus: deploy] [Corpus: decisions §EV-061]

## Startup

EV0–EV9 + 01 locked (`D-S071-01-*`, `D-S071-links-resolve`). 02 depth: changed
sections + cross-doc identifier consistency. Spec→Build remains **closed**.

## Document inventory (delta)

| # | Document | Path | EV-061 delta | Status |
|---|----------|------|--------------|--------|
| 1 | Feature List | `docs/feature-list.md` | F2/F6/F7.u/F7.v/F9/F15/F34 deepen #1010–#1015 | audited |
| 2 | User Journeys | `docs/user-journeys.md` | UJ-064..068 + UJ-DEV-009 | audited + C1/M1 fixed |
| 3 | Test Plan | `docs/test-plan.md` | Journey map TC-EV061-* + LIVE-F6-030 | audited |
| 4 | Deploy | `docs/deploy.md` | Promote #1015 required checks | audited |
| 5 | Evolve decisions | `docs/decisions/evolve-decisions.md` | §EV-061 | reference |
| 6 | Catalog policy | mining note + crawl report + RULE_SOURCE_URLS | `D-S071-links-resolve` | audited |
| 7 | API contract | `docs/api-contract.md` | deferred to 04 (`D-S071-02-m3`) | flagged → deferred |
| 8 | Spec | `docs/spec.md` | no structural component change | N/A deepen-only |

## Consistency checklist (delta)

| Check | Result |
|-------|--------|
| #1010–#1015 mapped in feature-list | PASS |
| UJ-064..068 + UJ-DEV-009 in journeys index + bodies | PASS |
| Journey ↔ test-plan map rows | PASS (IDs reserved) |
| H4–H5 for UI journeys UJ-064/065/066/067/068 | PASS (after M1) |
| Journeys header vs `D-S071-links-resolve` | PASS (after C1) |
| TC-EV061-* detailed sections | DEFERRED to 04 (`D-S071-02-m2`) |
| api-contract EV-061 shapes | DEFERRED to 04 (`D-S071-02-m3`) |
| #1011 harness vs #1012 product split | PASS |
| F7.s / F7.t kept alongside #1010 | PASS |
| #996 / #837 OOS | PASS |
| No new CORS origins | PASS |
| Catalog operator hrefs verified; semantic IDs OK | PASS |
| stage→main stricter than Staging gate alone | PASS |
| Template static+api+worker | PASS |

## High-confidence (auto-approved)

10 intake statements (#1010–#1015 deepen, AHL split, catalog policy, no new CORS, OOS).

## Verdicts (user 2026-08-18)

| ID | Verdict | Action |
|----|---------|--------|
| C1 | **modify** | Journeys header + changelog → links resolved / #1014 unblocked |
| M1 | **modify** | UJ-067 index + body → include H4–H5 |
| M2 | **approve** | Reserve TC-EV061-* IDs; detail in 04 |
| M3 | **approve** | Defer api-contract delta to 04 |
| M4 | **approve** | Spec UI minimum now; richer catalog schema in 04/Build |
| Gate A | **PASS** | Proceed to 04-tech-plan; Spec→Build stays closed |

## Connectivity

UI journeys UJ-064..068 require **H4–H5** after Build gate opens. UJ-DEV-009 is CI.
H0c CORS unchanged. Vitest ≠ T3 live proof.

## Next

**04-tech-plan** (delta) — flesh TC-EV061-*, api-contract additive shapes, execution plan + Build Plan Card.
