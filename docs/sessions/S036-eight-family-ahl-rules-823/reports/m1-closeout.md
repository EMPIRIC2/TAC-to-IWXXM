# M1 closeout — AHL / COM / shared bulletin (EV-029)

**Date**: 2026-08-02  
**Milestone**: M1 — AHL / COM / shared bulletin model (F6.bulletin)  
**TC**: TC-EV029-003 · **Issue**: #823 B1–B3

## Delivered

| Task | SHA | Summary |
|------|-----|---------|
| T1.1 | `8214b90` | Red fixtures: all TAC `T1T2`, BBB accept/reject, filename SA→LA, TC-F6-030 regression |
| T1.2 | `4cace9c` | `parse_ahl` / `format_ahl` / `map_t1t2` / `bbb_to_report_status` / `iwxxm_filename`; dissemination `format_wmo_ahl` thin wrap |
| T1.3 | `f1e87c5` | `.github/workflows/ahl-com-quality.yml` + `make test-ahl-com-quality` |
| T1.4 | (this) | Matrix / theme map / inventory / IWXXM_CONVERSION updated; #823 stays open |

## Closed vs residual

| Item | Status |
|------|--------|
| Shared AHL/`T1T2`/BBB/filename API | **Closed** |
| Y/Z BBB for reportStatus | **Rejected** (x ∈ A…X) — fixtures document choice |
| Body `split_bulletin` beyond METAR/SPECI | **Residual** → M2–M11 |
| Per-family multi-report bodies | **Residual** → #823 / FIXTURE_GAPS |

## Next

**M2** — METAR deepen @ T2.1 (after 08-verify-build + minor PR per build-execution).
