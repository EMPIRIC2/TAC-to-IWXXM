# Evolve Plan Card

> Cycle: EV-061 | Session: S071-pre-promote-ux-catalog | Updated: 2026-08-20

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

- Active phase: **Build** — **13 READY** (smokes PASS; await `D-S071-13`)
- Spec→Build gate: **open** (`D-S071-spec-build=1a`)
- Preset: **Standard**

## Spec-development band (00–06)

- Preset slice: Standard (`01 → 02 → 04`)
- Stages (ordered): `00 → 16 → 01 → 02 → 04` + dual Spec — **completed**
- Dual-mode Spec skills: `uat`, `verify-qa` — **completed**
- Skip: `03`, `05`, `06`

## Build band (07–13)

- Order: M1 #1011 → M2 #1012 → M3 #1010 → M4 #1013 → M5 #1014 → M6 #1015
- Active: **13-deploy-smoke** — #1016 → `stage` @ `86867a11`; H0c–H5 + UJ-064..068 PASS
- Deploy intent: **staging**; promote held until admin applies #1015 rulesets

## Next child stage

Await **`D-S071-13`** sign-off → closeout / board; promote held.

## Risks / open decisions

- Live GitHub rulesets empty until admin runs `apply_gh_branch_rulesets.sh`
- Lint/Typecheck restored as CI; E2E Full only on stage→main PRs
- Catalog source quality + category sort/filter → **#1017** (after promote; `D-S071-11-1017`)
- Merge #1016 done (`D-S071-12-merge=1`); 13 sign-off pending
