---
session_id: S071-pre-promote-ux-catalog
type: feature
status: open
branch: evolve/EV-061-pre-promote-ux-catalog
orchestrator: 16-evolve
evolve_cycle_id: EV-061
github_issues: [1009, 1010, 1011, 1012, 1013, 1014, 1015]
prior_session: S070-converter-operator-bugs
opened: 2026-08-18
---

# Session brief — S071-pre-promote-ux-catalog

> **Cycle**: EV-061 · **Type**: feature · **Opened**: 2026-08-18  
> **Branch**: `evolve/EV-061-pre-promote-ux-catalog` @ `stage@a1650b01`  
> **Orchestrator**: **16-evolve** · **Preset**: **Standard** · **Promote**: held until #1015 gate  
> **Issues**: epic [#1009](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1009) + children #1010–#1015 (M0)  
> **Corpus**: [Corpus: product §F2] [Corpus: product §F6] [Corpus: product §F7] [Corpus: product §F9] [Corpus: product §F10] [Corpus: product §F15] [Corpus: product §F34] [Corpus: api] [Corpus: journeys] [Corpus: tests] [Corpus: tech-spec] [Corpus: decisions §EV-061]

## Goal

Pre-promote operator UX and quality: readable IWXXM validate/decode presentation, AHL bulletin decode/convert fix, Product/Profile + parameter bar polish, dedicated lint/validation catalog tab with verified source links, stale live bulletin multipart test fix, and a stricter stage→main merge gate.

## Intent

One feature cycle **deepening** existing Fn only (no new top-level Fn). GitHub milestone **M0**. Spec-development first; Spec→Build gate **closed** until Spec band completes.

| Decision | Choice |
|----------|--------|
| D-S071-e0 | Goal = validate UX + AHL + Product/Profile UI + catalog tab; in = all listed incl. stage→main gate; API breaking OK if documented; close prior session/PRs then intake |
| D-S071-e1 | Why = pre-promote cleanup; cycle_type = feature; success = full observables + working source links; M0 epic + children |
| D-S071-e2 | Personas = public/guest ops + promote reviewers; primary flow = validate→catalog; must-not-break F21/F7/F10; UI preview at 11 |
| D-S071-e3 | Validate = item-by-item readable decode; AHL = fix decode+convert; catalog = new tab/page; stage→main = require full CI/unit/lint/typecheck/E2E |
| D-S071-e4 | Docs = product/api/journeys/tests/tech; Standard Spec 01→02→04; uat+verify-qa Spec; AHL brief before Spec edits |
| D-S071-e5 | Apps = FE/BE/tac-validate(+AHL pkgs)/CI; full H4–H5+UAT; stage then hold promote |
| D-S071-e6 | OOS = M1+ profiles, dissemination spikes, #996 unless pulled, #837 |
| D-S071-e7 | FE tab + H4–H5; no new secrets |
| D-S071-e8 | Standard bands; Build blocked until gate |
| D-S071-e9 | Open S071/EV-061 Spec-only; deepen F7/F2/F6/F9/F10/F15/F34; crawl links and block on broken |
| D-S071-ahl | AHL brief acknowledged — proceed; golden `SAUS31 KZNY` multi-METAR; #1011 vs #1012 split |
| D-S071-links | Verify all catalog source URLs; block Build on broken until user searches replacements; normalize official copies OK |

## In scope

1. **#1010** — IWXXM validate may decode; show readable item-by-item descriptions like other products. [Corpus: product §F2] [Corpus: product §F7] [Corpus: product §F9]
2. **#1011** — Live bulletin test multipart `file` → `files`. [Corpus: api] [Corpus: tests]
3. **#1012** — AHL bulletin decode + convert end-to-end + documented context. [Corpus: product §F6] [Corpus: product §F7]
4. **#1013** — Product Type + Profile no-wrap / polish; aligned mode + conversion-parameter bars. [Corpus: product §F7]
5. **#1014** — Lint + validation catalog tab/page (code, description, level, working source links). [Corpus: product §F10] [Corpus: product §F15]
6. **#1015** — Stricter stage→main required checks (full CI/unit/lint/typecheck/full E2E). [Corpus: tech-spec] [Corpus: tests]

## Out of scope

- M1+ national profile mining / regional overlays
- Dissemination spikes (#898, #909–#911, gateway spikes)
- #996 click-for-detail (related; not this cycle unless re-scoped)
- #837 decode visuals / mini-map
- Auto-promote to `main` before #1015 gate is green

## Success criteria

- Validate IWXXM path shows structured readable decode items
- AHL golden multi-report METAR decodes and converts; malformed AHL stays clear
- Top Product/Profile and parameter bars aligned / no wrap on supported desktop widths
- Catalog tab lists code / description / level / verified source URLs
- Live bulletin harness uses `files`
- stage→main cannot merge without the stricter required check set
- H4–H5 + UAT after Build gate opens

## Prior session closeout

- S070/EV-060 **closed** on stage; PR [#1007](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1007) merged
- Docs closeouts: [#1008](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1008) (S070) + [#999](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/999) (S069) **MERGED**
- Promote remains **held** pending this cycle + #1015

## Next

1. Spec band: **01-requirements** (delta) → 02 → 04 + uat/verify-qa Spec  
2. Spec→Build gate AskQuestion (mandatory) before any 07+  
3. Catalog URL crawl during Spec — pause if broken links need user research
