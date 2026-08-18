# Build Plan Card

> Cycle: EV-060 | Session: S070-converter-operator-bugs | Updated: 2026-08-17
> Active: Build / M1 / T1.1

## Goal

Ship epic #1000 children to `stage` in four PRs. This batch: M1 AHL bulletin quality (#1001).

## Constraints

- [Corpus: product §F6] [Corpus: product §F7] [Corpus: api] [Corpus: tests]
- Branch `evolve/EV-060-converter-operator-bugs` → PRs to `stage`; promote held
- No new deps / ADR / CORS origins

## In scope (this batch)

- [x] T1.1 — Test — Red AHL heading-flood + split fixtures — Spec: [Corpus: tests §TC-EV060-1001]
- [x] T1.2 — Code — `tac-validate` / splitter: heading COM vs product syntax — Spec: [Corpus: product §F6]
- [x] T1.3 — Code — `/convert-bulletin` + workbench/FileConverter parity — Spec: [Corpus: product §F7]
- [x] T1.4 — Docs — Fixture notes if needed

## Out of scope (explicit)

#933/#924; #912; F16–F19; F8 auto-push; promote; M2–M4 this batch

## Parallelism

T1.1 then T1.2 (TDD). T1.3 after T1.2. T1.4 last.

## Verify / PR

08-verify-build after M1; PR → `stage` for #1001.

## Gate

Spec→Build **open** (`D-S070-spec-build=1a`).
