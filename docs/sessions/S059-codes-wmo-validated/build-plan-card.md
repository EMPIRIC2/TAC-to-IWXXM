# Build Plan Card

> Session: S059-codes-wmo-validated | Updated: 2026-08-09 | Active: Phase 1 / M2 / T2.2

## Goal (one sentence)

Ship offline WMO codelist harvest + `tac-validate` membership CI and all-F6
`annex3` vs `iwxxm_us` disposition (#959 / #889 Validated).

## Constraints

- [Corpus: product §F6/F12/F15/F20/F23/F24/F28] [Corpus: tests] [Corpus: tech-spec]
  [Corpus: decisions §EV-050]
- Branch: `evolve/EV-050-codes-wmo-validated` → PR base `stage`
- Locked: `D-S059-families=1a`, `fixtures=2c`, `882=3a`, `profiles=1b`,
  `04-milestones/harvest/wire/adr=1`
- No new Fn; no vendor hand-edits; no live `codes.wmo.int` HTML in PR CI
- No UI / H4–H5; 12/13 waived; no new ADR; no new runtime deps (06 skip)

## In scope (this batch — M2)

- [x] T2.1 — Test — happy + sad membership matrix (weather/recent/cloud/SIGMET+AIRMET/nil) — Spec: TC-EV050-002; AC2
- [x] T2.2 — Code — wire membership into lint/rules (+ AIRMET underscore normalize) — Spec: AC2
- [ ] T2.3 — Test+fixtures — aggressive RE*/AIRMET_/SpaceWx/TCU packs — Spec: TC-EV050-004; AC4
- [ ] T2.4 — Docs — coverage / baseline delta; deferrals — Spec: AC4

## Out of scope (explicit)

- M3–M4 (profiles + #889/#882 closeout) until M2 complete
- Full #882 notify job; `#958`; `stage`→`main`; inventing US weather tokens

## Dependencies / blockers

- Data: `wmo_membership.json` from M1
- Prior: M1 complete (T1.1–T1.4); Gate A/B PASS
- Tooling: 06 skipped

## Acceptance for this batch

- [x] M1: TC-EV050-001 / AC3 docs (`make membership-regen`)
- [x] TC-EV050-002 green (happy + sad + lint wire)
- [ ] TC-EV050-004 fixtures landed or defer+cite

## Next Plan prompt

After M2: refresh card for **M3** (T3.1–T3.4 dual-profile + true-error fixes).
