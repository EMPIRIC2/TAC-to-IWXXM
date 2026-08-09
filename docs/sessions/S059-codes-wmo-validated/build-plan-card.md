# Build Plan Card

> Session: S059-codes-wmo-validated | Updated: 2026-08-09 | Active: Phase C gate → 08

## Goal (one sentence)

Ship offline WMO codelist harvest + `tac-validate` membership CI and all-F6
`annex3` vs `iwxxm_us` disposition (#959 / #889 Validated).

## Constraints

- [Corpus: product §F6/F12/F15/F20/F23/F24/F28] [Corpus: tests] [Corpus: tech-spec]
  [Corpus: decisions §EV-050]
- Branch: `evolve/EV-050-codes-wmo-validated` → PR base `stage`
- Locked: `D-S059-families=1a`, `fixtures=2c`, `882=3a`, `profiles=1b`,
  `04-milestones/harvest/wire/adr=1`, `validated=1`
- No new Fn; no vendor hand-edits; no live `codes.wmo.int` HTML in PR CI
- No UI / H4–H5; 12/13 waived; no new ADR; no new runtime deps (06 skip)

## In scope (this batch — M4) — COMPLETE

- [x] T4.1 — Docs — #882 compose design note (no job impl) — Spec: TC-EV050-006; AC6
- [x] T4.2 — Docs/process — #889 Validated satisfied — Spec: TC-EV050-005; AC5
- [x] T4.3 — Docs — tech-spec / domain back-add for harvest path + membership regen — Spec: AC3

## Out of scope (explicit)

- Full #882 notify job; `#958`; `stage`→`main`; inventing US weather tokens

## Dependencies / blockers

- Prior: M1–M4 complete (T1.*–T4.3); Gate A/B PASS

## Acceptance for this batch

- [x] M3: TC-EV050-007 / TC-EV050-008; AC7–AC8 (disposition + REMARK_US_EXTENSION gating)
- [x] TC-EV050-005 / AC5 — #889 Validated (`D-S059-validated=1`)
- [x] TC-EV050-006 / AC6 — #882 design-only note
- [x] Harvest path in tech-spec / domain (no ADR)

## Next Plan prompt

08-verify-build → 09-qa → 11-verify-impl; PR → `stage`.
