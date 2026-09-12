# Evolve Plan Card

> Cycle: EV-043 | Session: S052-doks-staging-prod-branch-deploys | Updated: 2026-08-08

## Goal

Dual DOKS envs + protected `stage`/`main` + dual CI/CD; promote to prod via PR after staging green (#886).

## Features

- F30 — Platform independence deepen (staging + dual CD + GH protection) — [Corpus: product §F30]

## In / out of scope

- In: DOKS staging ns + DNS; dual Deploy; staging-gate; rulesets; docs/skills
- Out: App Platform; second cluster; required reviewers; product UI

## Preset + routing

- Preset: Standard
- Stages: `00 → 16 → 01 → 02 → 03 → 04 → 05 → 07 → 08 → 09 → 10 → 11 → 12 → 13`

## Next child stage

07-build (Phase A/B docs + execution plan written; implement overlays + CI)

## Risks / open decisions

- DNS at Porkbun (not DO) — records may need manual UI if no API key
- GH rulesets need admin — script + runbook if 403
