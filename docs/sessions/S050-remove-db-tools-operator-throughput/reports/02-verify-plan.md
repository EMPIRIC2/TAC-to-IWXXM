# 02-verify-plan — Gate A audit (S050 / EV-042)

**Date:** 2026-08-07  
**Mode:** delta consistency  
**Corpus:** [Corpus: product], [Corpus: system-spec], [Corpus: journeys], [Corpus: api],
[Corpus: tests], [Corpus: tech-spec], [Corpus: decisions §EV-042]

## Inventory (touched)

| Doc | Delta status |
|-----|--------------|
| feature-list.md | F33 + F7/F16–F19 deepen ACs |
| user-journeys.md | UJ-051..053; UJ-027–030 deferred note |
| test-plan.md | UJ↔TC + H4–H5 |
| api-contract.md | mass ingest + UI-hide note |
| spec.md | F33 + frontend/F16–F19 EV-042 UI-hide |
| env-contract.md | MASS_INGEST_* + body-limit note |
| evolve-decisions.md | ACs locked D-S050-ac |

## High-confidence (auto-approve — from user answers)

| # | Statement |
|---|-----------|
| H1 | Operator UI hides all F16–F19 destinations (R2 / AC1) |
| H2 | Backend dissemination APIs retained for harness (AC2) |
| H3 | F33 caps 200 / 5 MiB / 50 MiB (R1 / AC4) |
| H4 | Mass path requires auth; guest small multi-file unchanged (R3 / AC5) |
| H5 | Churn = queue + keyboard + batch convert/validate; no batch disseminate (R4 / AC3) |
| H6 | UJ-051..053 + TC-F33-* + TC-EV042-* + H4–H5 (AC6) |
| H7 | #898 restores all destinations (AC7) |
| H8 | Standard routing; no 03/06 unless needed |

## Medium / contradictions (need user)

| # | Issue | Recommendation |
|---|-------|----------------|
| **C1** | F33 total **50 MiB** vs default `MAX_REQUEST_BODY_BYTES` **2 MiB** | Dedicated mass route limit: keep global 2 MiB; set mass route effective body ≥50 MiB via `MASS_INGEST_MAX_TOTAL_BYTES` (+ uvicorn/proxy) — **do not** raise global convert body to 50 MiB |
| M1 | Planned route name `POST /api/v1/ingest/mass` | Confirm in 04 (or accept as working name) |
| M2 | H6′ UJ-027–030 operator UI deferred | Harness/mocked suites stay; operator Playwright asserts **absence** (UJ-053) |

## Consistency checklist

| Check | Result |
|-------|--------|
| Fn in feature-list | PASS — F33 Planned; F16–F19 deepen notes |
| UJ ↔ test-plan | PASS — UJ-051..053 mapped |
| API ↔ product | PASS with C1 open |
| system-spec ↔ product | PASS after EV-042 spec patch |
| Connectivity H4–H5 | PASS — required for UJ-051..053 |

## Gate A status

**PASS** (2026-08-07) — C1 resolved: dedicated mass-route limit (option 1); user Gate A option 1.
Next: **04-tech-plan**.

### C1 resolution (D-S050-C1)

Keep global `MAX_REQUEST_BODY_BYTES` at **2 MiB**. Mass ingest route uses
`MASS_INGEST_MAX_FILES` / `MASS_INGEST_MAX_FILE_BYTES` / `MASS_INGEST_MAX_TOTAL_BYTES`
(defaults 200 / 5 MiB / 50 MiB) with route-level body limit ≥50 MiB (+ proxy/uvicorn as needed).
Do **not** raise global convert body to 50 MiB.
