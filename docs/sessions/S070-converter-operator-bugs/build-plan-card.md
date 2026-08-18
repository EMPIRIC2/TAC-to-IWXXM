# Build Plan Card

> Cycle: EV-060 | Session: S070-converter-operator-bugs | Updated: 2026-08-18
> Active: Build / M3 T3.1–T3.6 — profile + bulletin fields + log_level

## Goal

Ship epic #1000 children to `stage`. This batch: M3 Profile picker (#1002), Bulletin ID / Issuing Center (#1005), log_level verbosity (#1004).

## Constraints

- [Corpus: product §F7] [Corpus: product §F6] [Corpus: product §F29] [Corpus: api] [Corpus: tests]
- Branch `evolve/EV-060-converter-operator-bugs` → PRs to `stage`; promote held
- No new deps / ADR / CORS origins
- Keep F7.s Validate-only; not #933 profile editor; no live log panel

## In scope (this batch)

- [x] T3.1 — Test — Profile a11y + applied `profile=` — Spec: [Corpus: tests §TC-EV060-1002]
- [x] T3.2 — Code — Profile control at converter top — Spec: [Corpus: product §F7]
- [ ] T3.3 — Test — Bulletin ID / Issuing Center round-trip + invalid CCCC — Spec: [Corpus: tests §TC-EV060-1005]
- [ ] T3.4 — Code — Labeled editable fields wired to existing API — Spec: [Corpus: product §F6]
- [ ] T3.5 — Test — DEBUG vs ERROR verbosity; no secrets — Spec: [Corpus: tests §TC-EV060-1004]
- [ ] T3.6 — Code — Apply `log_level` to loggers — Spec: [Corpus: product §F29]

## Out of scope (explicit)

#933/#924; #912; F16–F19; F8 auto-push; promote; M4 Auth UAT; merge #1007 without user OK

## Parallelism

T3.1 → T3.2 (TDD). T3.3 → T3.4. T3.5 → T3.6. Profile vs bulletin vs log_level are independent after T3.1 starts.

## Verify / PR

08-verify-build M3 after T3.1–T3.6; stack on PR #1007 (M1+M2 already on this branch) unless split.

## Gate

Spec→Build **open** (`D-S070-spec-build=1a`).
