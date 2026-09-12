# Implementation verification — S020 / EV-015 (11-verify-impl)

> Generated: 2026-07-22  
> Inputs: `qa-report.md`, `e2e-report.md`  
> Branch: `evolve/EV-015-aerodrome-quality` @ `766606b`  
> Status: **PASS** — user approved 2026-07-22 (`D-S020-EV015-11-A`); H4–H5 deferred to T5.7

## Sources

| Artifact | Result |
|----------|--------|
| 09-qa | pass_with_advisories (H4–H5 → 13) |
| 10-e2e | T0 PASS; T2/T3 pending 13 |
| 08-verify-build | PASS (`verification-report.md`) |
| Tip | `766606b` (through T5.5); T5.6 docs this commit |
| Sign-off | **A** — approve F20 + F6/F12 deepen; live UJ at T5.7 |

## F20 acceptance criteria

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | TAF/SPECI lint emissions use registry codes; CI fails on unknown | **met** | ADR-028; TC-F20-001 |
| 2 | #735 exceptional-rule table has accept + negative (or deferrals) | **met** | T1–T3 fixtures + registry; research catalog |
| 3 | #734 SPECI exceptional + mis-classification guards | **met** | S1 packs; TC-F20-006 |
| 4 | Coverage-matrix TAF + SPECI rows updated | **met** | T4.3 COVERAGE_MATRIX + ISSUE_CATALOG |
| 5 | Accept TAF/SPECI → convert → XSD+Schematron; roots `iwxxm:TAF`/`SPECI` | **met** | TC-F20-002 / TC-F20-003 |
| 6 | Workbench `product=taf` + `product=speci` smoke; H4–H5 when FE touched | **met (T0)** / **pending live** | T5.1–T5.5; live H4–H5 at T5.7 |

## Deepen notes

| Feature | Status |
|---------|--------|
| F6.b SPECI convert/golden fidelity | Deepened (annex3 + iwxxm_us packs) |
| F6.c TAF Annex-3 + forecast extensions | Deepened (T4 goldens + exceptional encode) |
| F12 TAF + SPECI checklist via registry | Deepened (T1–T3 / S1 / C1 rows) |

## UJ-031

| Aspect | Status |
|--------|--------|
| T0 operator/CI paths (TC-F20-001..006) | PASS (162 pytest + 10 Vitest) |
| Browser catalog TAF tags / live H4–H5 | Deferred to T5.7 (documented; same posture as S015) |

## Sign-off

**Approved** (option A, 2026-07-22): F20 + F6/F12 deepen match HARD scope for merge-ready review.
**Deploy/live UJ** (H1–H5) requires T5.7 / 13-deploy-smoke.

**11-verify-impl: PASS** (connectivity live proof deferred to 13 per E15-7 / E15-18).
