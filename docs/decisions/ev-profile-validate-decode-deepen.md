# EV-profile-validate-decode-deepen — requirements decisions

**Session:** `EV-profile-validate-decode-deepen`  
**Date:** 2026-09-21  
**Ticket:** [#1221](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1221)  
**Corpus:** [Corpus: product §F2/F6/F7/F9/F15/F35/F36] [Corpus: domain-profiles]
[Corpus: adr/ADR-036] [Corpus: adr/ADR-044] [Corpus: adr/ADR-045] [Corpus: adr/ADR-046]
[Corpus: api] [Corpus: tests] [Corpus: journeys]

## Locked requirements (operator: recommended)

| ID | Topic | Choice |
|----|-------|--------|
| D-EVPVD-01 | Milestone spine | ADR-044 UI cutover + #1120 residual → AU/NZ → #724 → CA mining best-effort |
| D-EVPVD-02 | AU/NZ bar | Catalog `implemented` + METAR/SPECI/TAF golden convert fixtures; no national XSD |
| D-EVPVD-03 | CA mining | Best-effort promote #1029/#1030; leave #1028/#1031/#1034 open if incomplete |

### M5 outcome (2026-09-21)

AC5 satisfied by **existing** EV-098 promotions already in-tree (e.g. `CA_METAR_LWIS`,
`CA.METAR.VIS.SM`, `CA_TAF_NCLWS` provenance rows — see
`docs/domain/mining/manobs-manair-ca-mining-notes.md`). Residual MANOBS/MANAIR digs stay
open on [#1029](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1029) /
[#1030](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1030); no new fixture promote this
cycle beyond the documented bar.
| D-EVPVD-04 | UI preview | Docs/repo only (no local non-deployed preview) |
| D-EVPVD-05 | #1120 honesty | API filters (#1121) largely present — Build closes residual content (#1122), FE follow (#1123), glanceable (#1145) gaps only |
| D-EVPVD-06 | ADR-044 residual | Remove Profile Builder / library authoring UI; keep rule-catalogs + dropdowns; UJ-076* |
| D-EVPVD-07 | Decode #724 | Enrich METAR/SPECI station token + plain-language summary via existing airport lookup; soft-fail to ICAO |
| D-EVPVD-08 | OUT unchanged | #1222 exchange packaging; #1210; #970; #837/#938/#996/#1159; #1025; #1198; marketplace/dissem |

## Acceptance criteria (requirements lock)

1. **ADR-044:** Profile Builder / five-library authoring / Dissemination Bench authoring gone; five trust catalogs + selection dropdowns; TC-EVRPC-* / UJ-076* green; H4–H5 when FE catalog/dropdown calls change
2. **#1120 residual:** #1122 seed rows US+CA with provenance URLs only; #1123 workbench catalog follows Profile; #1145 glanceable summary if not already green; unknown profile still 400
3. **AU_BOM / NZ_CAA_MET:** catalog `status: implemented`; convert goldens METAR/SPECI/TAF; allowlist unchanged
4. **#724:** Decode explanation + summary show airport name when lookup hits; miss → ICAO only; no new HTTP field required
5. **CA:** At least one promoted rule/fixture from MANOBS or MANAIR mining, or explicit defer note on #1221
6. **Must-not-break:** convert, lint, soft-preview, decode-tac, dissem preflight/send + allowlist; EV-048 clean
7. **Hygiene:** close or wontfix #1196/#1203/#1146/#1147 after ADR-044 UI removal lands (or document keep-as-docs)

## Document manifest (approved — recommended)

### Mandatory (delta)

| Document | Action |
|----------|--------|
| Feature List | Deepen F7.v/F7.w Retired note, F9 #724, F36 AU/NZ + this EV |
| Spec | Point to ADR-044 residual + profile catalog filter (no new component) |
| User Journeys | Confirm UJ-076* / UJ-073; note UJ-072f–i Retired |
| Test Plan | Map TC-EVRPC + TC-EV1120 residual + TC-EVPVD-* for AU/NZ/#724 if needed |

### Recommended

| Document | Action |
|----------|--------|
| API Contract | Confirm additive `semantic_profile`/`exchange_profile` on lint-issue-catalog (likely already) |
| decisions | This file + evolve-decisions pointer |

### Excluded

- Config Spec — no new env
- Deploy Plan — stage-first PRs only; no platform change
- Data Management — mining uses existing public sources
- New ADR — ADR-044/036 sufficient; no new architecture decision

## Build order (intent)

1. ADR-044 FE hard cutover  
2. #1122 / #1123 / #1145 residual  
3. AU/NZ implemented  
4. #724 station names  
5. CA mining best-effort  

Gate remains **closed** until Spec band + documenting verify.
