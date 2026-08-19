# Build Plan Card

> Cycle: EV-061 | Session: S071-pre-promote-ux-catalog | Updated: 2026-08-19  
> Active: **07-build M2 #1012** — Spec→Build **open** (`D-S071-spec-build=1a`)  
> M1 PR: https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1016 (open → `stage`, CI green)

## Goal

Well-formed multi-report METAR AHL (`SAUS31 KZNY`) decodes with item-by-item rows per
report and convert-bulletin succeeds; malformed heading/body yields clear `INVALID_AHL`
/ `empty_bulletin`. Promote held until #1015.

## Constraints

- [Corpus: product §F6] [Corpus: product §F7] [Corpus: product §F9] [Corpus: api]
  [Corpus: tests §TC-EV061-1012] [Corpus: journeys §UJ-065]
- Branch `evolve/EV-061-pre-promote-ux-catalog` → PRs to `stage`
- No new deps / ADR / CORS origins
- Decode-tac **no new required fields** (`D-S071-api`); `INVALID_AHL` additive
- Operator copy: no internal doc refs (EV-048)
- Alias vs replace: prefer `INVALID_AHL` for malformed heading; keep
  `bulletin_split_failed` as `detail.alias` (`D-S071-ahl-code` in 07)

## In scope (this batch — M2)

- [ ] T2.1 — Test — Red golden multi-METAR decode + convert; malformed `INVALID_AHL` — Spec: UJ-065 TC-EV061-1012-001..004
- [ ] T2.2 — Code — AHL split/decode: per-report F9 rows + convert-bulletin success — Spec: feature-list F6 EV-061
- [ ] T2.3 — Code — Malformed AHL → `INVALID_AHL` / `empty_bulletin` (no silent 200) — Spec: [Corpus: api]
- [ ] T2.4 — Docs — OpenAPI / operator copy for AHL errors (no internal doc refs) — Spec: [Corpus: api] EV-048

## Out of scope (explicit)

#1011 harness (M1 done); #1010 validate decode (M3); #1013 bars; #1014 catalog;
#1015 promote gate; #996; #837; M1+ national profiles; dissemination spikes

## Parallelism

T2.1 → T2.2 / T2.3 (T2.3 independent of T2.2 after T2.1) → T2.4. Sequential in parent
(shared convert-bulletin error mapping).

## Verify / PR

08-verify-build M2 after T2.1–T2.4; minor PR to `stage` (stacked on #1016 or new).

## Gate

Spec→Build **open** (`D-S071-spec-build=1a`).
