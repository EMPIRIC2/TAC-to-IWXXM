# 01-requirements summary — S046 / EV-038

**Date:** 2026-08-05  
**Mode:** delta · deepen F2 / F4 / F6 / F7 / F32 · no new Fn · #854 UI  
**Milestones:** M1 docs → M2 release-line → M3 soft → M4 encode (`D-S046-mplan`)  
**UI preview:** Yes at M2/#854 (local non-deployed)  
**Corpus:** `[Corpus: product]` · `[Corpus: tech-spec]` · `[Corpus: api]` · `[Corpus: tests]` ·
`[Corpus: decisions]` · `[docs/domain/iwxxm/RELEASE_LINE_ADOPTABILITY.md]` ·
`[docs/domain/rules/COVERAGE_MATRIX.md]`

## Interview plan

| Doc | Action |
|-----|--------|
| Feature List | Deepen F2/F4/F6/F7/F32 + corpus #846 status — draft below |
| Test Plan | TC-EV038-001..013 (one per ticket) — draft below |
| User journeys | **UJ-050** added in 02 for #854 picker Latest/Previous |
| Spec / Deploy / Deps / ADR | Skip unless M2 SoT forces API enum doc; ADR only if encode invents packing |
| COVERAGE_MATRIX / RELEASE_LINE_* | Spec targets for **07-build** (edited in build, not 01) |

## Acceptance criteria (EV-038) — **approved** (`D-S046-ac` = 1)

### M1 — Docs / process (#858, #861, #855)

| ID | Criterion | Ticket | TC |
|----|-----------|--------|-----|
| AC1 | Durable OOS row for WAFS / QVACI / SIGWX (XML-only); cited from #846 + COVERAGE_MATRIX; no encode | #858 | TC-EV038-001 |
| AC2 | iwxxm-modelling delta-watch checklist step on sync PRs; linked from RELEASE_LINE_ADOPTABILITY; no duplicate #807 mine | #861 | TC-EV038-002 |
| AC3 | Deprecation-calendar / reminder GitHub issue template + dry-run note; links VERSION_SUPPORT_POLICY + staff guide | #855 | TC-EV038-003 |

### M2 — Release-line automation + UX (#851–#854)

| ID | Criterion | Ticket | TC |
|----|-----------|--------|-----|
| AC4 | Single SoT drives FE picker options + documented API enum; CI fails on drift | #851 | TC-EV038-004 |
| AC5 | Sync-PR tip-diff script/job lists XSD/SCH/example stem deltas; linked from adopt checklist; no hand-edit vendor | #852 | TC-EV038-005 |
| AC6 | iwxxm-us compatibility checklist (+ optional CI smoke) when WMO default moves; lag decision documented | #853 | TC-EV038-006 |
| AC7 | Version picker (or help) shows Latest / Previous roles; stays in sync with SoT; no convert-semantics change | #854 | TC-EV038-007 |

### M3 — Corpus soft / gates (#859, #860, #857)

| ID | Criterion | Ticket | TC |
|----|-----------|--------|-----|
| AC8 | Documented codes.wmo.int vs vendor codelist URI drift check cadence + failure disposition; optional non-flake CI | #859 | TC-EV038-008 |
| AC9 | Inventory of `*-translation-failed*` peers vs soft path; fixtures **or** explicit deferral with rationale | #860 | TC-EV038-009 |
| AC10 | SWXA A7-4 / A7-5 inventory disposition; catalog entries only with vendor peers (no invented TAC) | #857 | TC-EV038-010 |

### M4 — Encode deepen (#849, #850, #856)

| ID | Criterion | Ticket | TC |
|----|-----------|--------|-----|
| AC11 | When TAC supplies HGT SOURCE / MOV beyond A7-1 inapplicable ash, encode vertical extent per XSD (no invented packing); fixtures + SCH green; matrix row | #849 | TC-EV038-011 |
| AC12 | RESUSPENDED_VOLCANIC_ASH path when normative TAC known — else cite-only deferral stays documented; matrix row | #850 | TC-EV038-012 |
| AC13 | Promote `sigmet-VA-EGGX` to `wmoPass` when ADR-032 equality greens (or document irreducible diffs); catalog + matrix | #856 | TC-EV038-013 |

### Roll-up

| ID | Criterion | TC |
|----|-----------|-----|
| AC14 | Close or explicitly defer #849–#861 with residual tickets; update epic #846 roll-up | TC-EV038-014 |

## Out of scope

Metrics UI (#836) · workbench epic (#840) unless tiny catalog-tier · hand-edit
`vendor/schemas/*` · re-pin as primary goal · inventing TAC without WMO peer

## 07-build targets (by milestone)

1. **M1** — COVERAGE_MATRIX OOS; RELEASE_LINE_* watch + issue template; close #858/#861/#855  
2. **M2** — `iwxxm_versions` SoT export + FE/OpenAPI sync + CI; tip-diff script; US gate docs/CI; picker labels  
3. **M3** — codes drift check; translation-failed inventory; SWXA peer disposition  
4. **M4** — VONA encode deepen; VA-EGGX equality / tier flip  
