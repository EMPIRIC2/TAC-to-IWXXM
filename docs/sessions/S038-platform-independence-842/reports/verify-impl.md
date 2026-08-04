# Verify implementation — 11-verify-impl (EV-031 / S038)

> **Date**: 2026-08-03  
> **Status**: **awaiting user approval** (UI preview + per-Fn signoff)  
> **Inputs**: [qa-report.md](qa-report.md) · [e2e-report.md](e2e-report.md) · [verification-report.md](verification-report.md)  
> **Tip**: `06d57043`

## Collection

| Stage | Overall | Report |
|-------|---------|--------|
| 08-verify-build | PASS | verification-report.md |
| 09-qa | PASS (advisories) | qa-report.md |
| 10-e2e | PASS | e2e-report.md (T0 8/8 + T7 T3) |

## UI preview

| Field | Value |
|-------|-------|
| Offered | **yes** (this gate) |
| Accepted / declined | *pending user* |
| Local URL | `http://localhost:18000` (when started) — **non-deployed** |

## F30 — Platform independence (per AC)

| AC | TC | Evidence | Status |
|----|----|----------|--------|
| 1 No Supabase DB on product path | TC-F30-001 | T7.3 topology + migrate reports | **MET** |
| 2 Auth-only Supabase | TC-F30-002 | packages/auth JWKS; env-contract | **MET** |
| 3 F8 → DATABASE_URL | TC-F30-003 | M3/M5 worker tests + DOKS worker | **MET** |
| 4 DOKS + H0–H5 | TC-F30-004 | T6.4 + T7.2 provisional | **MET** (provisional HTTP) |
| 5 Render decommission | TC-F30-005 | T6.5 suspend + archive | **MET** (`D-S038-t65-waive`) |
| 6 Docs Auth-only data plane | TC-F30-006 | T7.3 + CORPUS note | **MET** |

**Residuals (do not block AC5):** real DNS/HTTPS (`D-S038-t63-waive`); GHCR republish.

## F31 — Hybrid sessions (per AC)

| AC | TC | Evidence | Status |
|----|----|----------|--------|
| 1 Guest convert local | TC-F31-001 | T7.1 / UJ-045 | **MET** |
| 2 Loss-of-progress notice | TC-F31-002 | T7.1 | **MET** |
| 3 Login → DO sessions; convert public | TC-F31-003 | T7.1 / T7.3 | **MET** |
| 4 Auto-upload on login | TC-F31-004 | T7.1 UJ-046 | **MET** |
| 5 F22 privacy gates | TC-F31-005 | T7.1 UJ-047 | **MET** |
| 6 H4–H5 + UJs | TC-F31-006 | T7.2 provisional + T7.1 | **MET** (provisional) |

## Journey signoff (draft)

| UJ | T0 | T3 / connectivity | Proposed |
|----|----|--------------------|----------|
| UJ-045 | covered via smoke/F31 specs | T7.1 PASS | Approve |
| UJ-046 | — | T7.1 PASS | Approve |
| UJ-047 | — | T7.1 PASS | Approve |
| UJ-048 | ops | T6.4–T6.5 + T7.2 | Approve (provisional DNS) |

## Recommendation

Approve F30/F31 for Phase D continue → **12-verify-deploy** + **13-deploy-smoke** on provisional DOKS, with residuals tracked.
