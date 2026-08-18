# Evolve Plan Card

> Cycle: EV-061 | Session: S071-pre-promote-ux-catalog | Updated: 2026-08-18

## Goal

Pre-promote operator UX + AHL decode/convert + lint/validation catalog tab + stricter stage→main gate (epic #1009 on M0).

## Features

- F7 deepen — Product/Profile bars (#1013); catalog tab (#1014); validate presentation (#1010) — [Corpus: product §F7]
- F2 / F9 / F10 deepen — IWXXM validate readable item-by-item decode (#1010) — [Corpus: product §F2] [Corpus: product §F9] [Corpus: product §F10]
- F6 deepen — AHL bulletin decode + convert (#1012); live multipart chore (#1011) — [Corpus: product §F6]
- F15 deepen — catalog source links verified / normalized (#1014) — [Corpus: product §F15]
- F34 / CI deepen — stricter stage→main required checks (#1015) — [Corpus: product §F34] [Corpus: tech-spec]

## In / out of scope

- In: #1009–#1015; FE tab/route; H4–H5 after Build; API field rename OK if documented; block on broken catalog URLs
- Out: #996 click-detail; #837 mini-map; M1+ profiles; dissemination spikes; auto-promote before #1015

## Phase split

- Active phase: **Spec-development**
- Spec→Build gate: **closed**
- Preset: **Standard**

## Spec-development band (00–06)

- Preset slice: Standard (`01 → 02 → 04`)
- Stages (ordered): `00 → 16 → 01 → 02 → 04`
- Dual-mode Spec skills: `uat`, `verify-qa`
- Skip: `03`, `05`, `06` (unless 04 finds gaps)

## Build band (07–13) — blocked until gate

- Stages (ordered): `07 → 08 → 09 → 10 → 11 → 12 → 13`
- Dual-mode Build skills: `uat`
- Deploy intent: **staging**; promote held until #1015

## Next child stage

**01-requirements** (delta) — Spec-band only; crawl catalog source URLs; document AHL context for #1012

## Risks / open decisions

- Broken catalog source links → **block** until user supplies replacements (`D-S071-links`)
- AHL failures may need operator-pasted samples if golden fixture already converts
- Multipart `file`→`files` is test-only (#1011) vs product AHL (#1012)
- stage→main gate may need GitHub required-check admin (no app secrets)
