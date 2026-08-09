# Build Plan Card

> Session: S059-codes-wmo-validated | Updated: 2026-08-09 | Active: Phase 1 / M1 / T1.1

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

## In scope (this batch — M1)

- [ ] T1.1 — Test — harvest → frozen membership for v1 families; offline-only — Spec: TC-EV050-001; AC1
- [ ] T1.2 — Code — CSV `notation` + pin RDF harvest → `tac-validate` data artifact — Spec: AC1; D-S059-04-harvest/wire
- [ ] T1.3 — Config — `make` regenerate (+ optional CI drift) — Spec: AC1; AC3
- [ ] T1.4 — Docs — cadence vs `iwxxm-codelists` pin; #859 cross-link — Spec: TC-EV050-003; AC3

## Out of scope (explicit)

- M2–M4 until M1 complete (membership wire, fixtures, profiles, #889/#882 closeout)
- Full #882 notify job; `#958`; `stage`→`main`; inventing US weather tokens

## Dependencies / blockers

- Data: in-repo `vendor/schemas/iwxxm-codelists` + pin RDF (verified present)
- Prior: Gate A PASS (`D-S059-gateA=1`); awaiting Gate B after 04 approve
- Tooling: 06 skipped

## Acceptance for this batch

- [ ] TC-EV050-001 green (offline membership artifact)
- [ ] TC-EV050-003 docs landed (or paired with T1.4)
- [ ] No network fetch of codes.wmo.int in harvest/CI path

## Next Plan prompt

After M1: refresh card for **M2** (T2.1–T2.4 membership + aggressive fixtures).
