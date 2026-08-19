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

- In: #1009–#1015; FE tab/route; H4–H5 after Build; additive API; catalog 3-tier sources
- Out: #996 click-detail; #837 mini-map; M1+ profiles; dissemination spikes; auto-promote before #1015

## Phase split

- Active phase: **Build** — M4 #1013
- Spec→Build gate: **open** (`D-S071-spec-build=1a`)
- Preset: **Standard**

## Spec-development band (00–06)

- Preset slice: Standard (`01 → 02 → 04`)
- Stages (ordered): `00 → 16 → 01 → 02 → 04` + dual Spec — **completed**
- Dual-mode Spec skills: `uat`, `verify-qa` — **completed**
- Skip: `03`, `05`, `06`

## Build band (07–13)

- Order: M1 #1011 → M2 #1012 → M3 #1010 → M4 #1013 → M5 #1014 → M6 #1015
- Active: **M3 #1010 complete** — next **M4 #1013**
- Deploy intent: **staging**; promote held until #1015

## Next child stage

07-build M4 T4.1 → T4.2 (#1013); then 08-verify-build + stack on PR to `stage`.

## Risks / open decisions

- `INVALID_AHL` vs existing `bulletin_split_failed` — alias vs replace (07)
- Lint/typecheck are local pre-commit today; #1015 restores them as CI required checks
- Branch protection admin for `stage`→`main` (no app secrets)
