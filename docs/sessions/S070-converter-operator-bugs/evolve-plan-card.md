# Evolve Plan Card

> Cycle: EV-060 | Session: S070-converter-operator-bugs | Updated: 2026-08-18

## Goal

Operator converter bugs + IWXXM product pass-through + Auth UAT, tracked by epic #1000 on GitHub milestone M0; Spec-development first.

## Features

- F7.t — IWXXM as product pass-through (#1003) — [Corpus: product §F7]
- F6/F7 — AHL bulletin quality (#1001); profile picker (#1002); Bulletin ID / Issuing Center (#1005) — [Corpus: product §F6] [Corpus: product §F7]
- F2/F10 — validate + lint console for pass-through and AHL — [Corpus: product §F2] [Corpus: product §F10]
- F29 — `log_level` actually applied (#1004) — [Corpus: product §F29]
- F31/F21 — Auth/Register UAT (#1006) — [Corpus: product §F31] [Corpus: journeys]

## In / out of scope

- In: #1001–#1006; FileConverter/accumulate/QM honor shared params; API `product=iwxxm` + existing bulletin/log_level fields; H4–H5 after Build
- Out: #933/#924 profile editor; #912 national packs; F16–F19/#898; F8 auto-push; stage→main promote; new auth providers; live log panel; new CLI product

## Phase split

- Active phase: **Build**
- Spec→Build gate: **open** (`D-S070-spec-build=1a`)
- Preset: **Standard**

## Spec-development band (00–06)

- Preset slice: Standard (`01 → 02 → 04`)
- Stages (ordered): `00 → 16 → 01 → 02 → 04`
- Dual-mode Spec skills: `uat`, `verify-qa`
- Skip: `03`, `05`, `06`

## Build band (07–13) — blocked until gate

- Stages (ordered): `07 → 08 → 09 → 10 → 11 → 12 → 13`
- Dual-mode Build skills: `uat`
- Deploy intent: **staging** smoke; promote held
- Execution-plan slices (≠ GitHub M0): M1 AHL #1001; M2 IWXXM product #1003; M3 profile+bulletin+log_level #1002/#1005/#1004; M4 Auth UAT #1006

## Next child stage

**08-verify-build M3 PASS** — next 07-build M4 Auth UAT (#1006); PR #1007 stacks M1–M3; promote held

## Risks / open decisions

- F7.s Validate-only (#838) stays alongside F7.t product=IWXXM — do not silently delete
- `log_level` already on the API as client-echoed process-issue filter; EV-060 also wires **logger verbosity**
- Quality metrics honor (not redesign) profile/IWXXM product
