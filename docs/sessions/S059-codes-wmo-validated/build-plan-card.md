# Build Plan Card

> Session: S059-codes-wmo-validated | Updated: 2026-08-09 | Active: Phase 1 / M3 / T3.2

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

## In scope (this batch — M3)

- [x] T3.1 — Test — dual-profile harness (`annex3` vs `iwxxm_us`); fail unclassified dual-applicable divergent rows — Spec: TC-EV050-007; AC7
- [ ] T3.2 — Docs — disposition table for all F6 products (shared WMO · intentional L5 · true error · N/A) — Spec: AC7
- [ ] T3.3 — Code — fix true-error rows (severity / false pass-fail / missing membership / wrong gating) — Spec: TC-EV050-008; AC8
- [ ] T3.4 — Test — regressions per fixed true error; intentional/N/A retain cites; AC8 defer+cite OK — Spec: AC8

## Out of scope (explicit)

- M4 (#889/#882 closeout) until M3 complete
- Full #882 notify job; `#958`; `stage`→`main`; inventing US weather tokens
- Exhaustive 402 weather / remaining register depth (T2.4 defer+cite)

## Dependencies / blockers

- Prior: M1 + M2 complete (T1.*–T2.4); Gate A/B PASS
- T3.1 depends on T2.2 (membership wire) — satisfied
- Tooling: 06 skipped

## Acceptance for this batch

- [x] M2: TC-EV050-002 / TC-EV050-004; AC4 coverage delta + deferrals
- [ ] TC-EV050-007 dual-profile harness + disposition (T3.1–T3.2)
- [ ] TC-EV050-008 true-error fixes + regressions (or defer+cite) (T3.3–T3.4)
- [ ] `iwxxm_us` unsupported product → **N/A row (not fail)**

## Next Plan prompt

After M3: refresh card for **M4** (T4.1–T4.3 #882 design note + #889 Validated closeout + tech-spec back-add).
