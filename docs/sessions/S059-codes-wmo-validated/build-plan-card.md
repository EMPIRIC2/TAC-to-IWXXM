# Build Plan Card

> Session: S059-codes-wmo-validated | Updated: 2026-08-09 | Active: Phase 1 / M4 / T4.1

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

## In scope (this batch — M4)

- [ ] T4.1 — Docs — #882 compose design note (no job impl) — Spec: TC-EV050-006; AC6
- [ ] T4.2 — Docs/process — #889 Validated satisfied (or re-scope) — Spec: TC-EV050-005; AC5
- [ ] T4.3 — Docs — tech-spec / domain back-add for harvest path + membership regen — Spec: AC3

## Out of scope (explicit)

- Full #882 notify job; `#958`; `stage`→`main`; inventing US weather tokens

## Dependencies / blockers

- Prior: M1–M3 complete (T1.*–T3.4); Gate A/B PASS
- T4.2 depends on T2.2 + T3.4 — satisfied
- T4.1 parallelizable anytime; T4.3 depends on T1.4 — satisfied

## Acceptance for this batch

- [x] M3: TC-EV050-007 / TC-EV050-008; AC7–AC8 (disposition + REMARK_US_EXTENSION gating)
- [ ] TC-EV050-005 / AC5 — #889 Validated close criteria
- [ ] TC-EV050-006 / AC6 — #882 design-only note
- [ ] Harvest path in tech-spec / domain (no ADR)

## Next Plan prompt

After M4: 08-verify-build → 09-qa → 11-verify-impl; PR → `stage`.
