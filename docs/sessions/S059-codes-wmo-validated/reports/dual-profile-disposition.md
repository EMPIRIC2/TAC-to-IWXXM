# Dual-profile disposition — annex3 vs iwxxm_us (S059 / EV-050 / AC7)

**Date:** 2026-08-09  
**Task:** T3.2  
**Harness:** `tac_validate.dual_profile.compare_lint_profiles` · TC-EV050-007  
**Tip:** `848c01a7`  
**Corpus:** [Corpus: product §F6] [Corpus: tests] [Corpus: decisions §EV-050]
· [Corpus: tech-spec] · domain `TAC_VALIDATION` L3/L5

## Method

For each product in `F6_DUAL_PROFILE_PRODUCTS`, lint a representative accept TAC under
`profile=annex3`. When `iwxxm_us` is applicable, also lint under `profile=iwxxm_us` and
compare issue-code sets. Divergent codes must be listed as **intentional L5** (allowlisted
in `INTENTIONAL_PROFILE_DIVERGENCE_CODES`) or **true error** (fix in T3.3). Unsupported
`iwxxm_us` → **N/A** (not fail).

WMO L3 membership (`UNKNOWN_WMO_MEMBERSHIP` / harvested registers) is **shared SoT** for
both profiles — must not diverge. US L5 REMARKS / FMH-1 overlays apply only under
`iwxxm_us` where the product supports them (`TAC_VALIDATION` §US profile).

Applicability mirrors `tac2iwxxm.convert` `_US_PRODUCTS`:
`METAR`, `SPECI`, `TAF`, `SIGMET`, `AIRMET`.

## Disposition table (all F6 + deepen products)

| Product | `iwxxm_us` | Disposition | Divergent codes (annex3 ↔ us) | Notes / cite |
|---------|------------|-------------|-------------------------------|--------------|
| METAR | dual | **shared WMO** + **intentional L5** on REMARKS | `REMARK_US_EXTENSION` (us only) | L3 membership identical. US REMARKS info gated to `iwxxm_us` (T3.3 / AC8). Representative body: `accept/metar_basic.tac`; REMARKS: `remark_us_info` pack |
| SPECI | dual | **shared WMO** + **intentional L5** on REMARKS | `REMARK_US_EXTENSION` (us only) | Same as METAR. `accept/speci_basic.tac` |
| TAF | dual | **shared WMO** | _(none)_ | US encode path exists; lint L3 shared. `accept/taf_basic.tac` |
| SIGMET | dual | **shared WMO** | _(none)_ | US emit wrapper exists; no L5 lint overlay yet. `accept/sigmet_basic.tac` |
| AIRMET | dual | **shared WMO** | _(none)_ | Same; underscore AirWx membership shared. `accept/airmet_a2_phenomenon.tac` |
| VAA | **N/A** | **N/A** | — | `lint(..., profile=iwxxm_us)` raises; convert `UNSUPPORTED_PROFILE`. `accept/vaa_basic.tac` |
| TCA | **N/A** | **N/A** | — | Same. `accept/tca_basic.tac` |
| SWXA | **N/A** | **N/A** | — | F28 deepen; no US profile. `accept/swxa_sx1_hf_com.tac` |
| VONA | **N/A** | **N/A** | — | F32 deepen; no US profile. `accept/vona_basic.tac` |

### Classification legend

| Class | Meaning |
|-------|---------|
| **shared WMO** | Dual-applicable; issue codes match (or only allowlisted intentional L5); L3 membership SoT shared |
| **intentional L5** | Expected US-only overlay (FMH-1 / REMARKS / iwxxm-us) — cite + allowlist code |
| **true error** | Suspect wrong severity / false pass-fail / missing membership / wrong gating — fix in T3.3 |
| **N/A** | `iwxxm_us` unsupported for product — not a fail |

## Intentional L5 allowlist (harness)

| Code | Why allowlisted |
|------|-----------------|
| `REMARK_US_EXTENSION` | Intentional L5 — emitted only under `iwxxm_us` (T3.3 fix); annex3 suppresses |

**True error fixed (T3.3):** annex3 previously emitted `REMARK_US_EXTENSION` (US profile
awareness) — wrong gating. Now annex3-silent; `iwxxm_us` retains info. Regression:
TC-EV050-008 / R5 annex3 suppression tests.

## Membership sad path (dual)

| Case | annex3 | iwxxm_us | Class |
|------|--------|----------|-------|
| `negative/metar/unknown_recent_weather.tac` (`REZZZZ`) | `UNKNOWN_WMO_MEMBERSHIP` | same | **shared WMO** |

## Residual / follow-ons (T3.3–T3.4)

| Item | Disposition |
|------|-------------|
| Gate `REMARK_US_EXTENSION` to `iwxxm_us` only | **Done** (T3.3); `INVALID_REMARK` stays on both (malformed) |
| Broader dual-pack scan beyond representatives | Expand harness fixtures if further true errors appear |
| Encode-path XML diffs (`tac2iwxxm` annex3 vs iwxxm_us) | Out of AC7 lint/membership scope; convert goldens already cover encode |

## AC7 checklist

| Criterion | Status |
|-----------|--------|
| All F6 (+ deepen) products in table | **MET** |
| N/A ≠ fail for unsupported `iwxxm_us` | **MET** (harness + this table) |
| Dual rows classified | **MET** — shared WMO; no open true errors at T3.2 |
| CI fails unclassified dual divergence | **MET** — TC-EV050-007 |
| WMO L3 SoT unchanged for both profiles | **MET** |
