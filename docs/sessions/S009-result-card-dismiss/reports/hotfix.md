# S009 Hotfix Report — result card dismiss

| Field | Value |
|-------|-------|
| **Session** | S009-result-card-dismiss |
| **Bug** | [BUG-2026-07-12-result-card-dismiss](../../bug-reports/BUG-2026-07-12-result-card-dismiss.md) |
| **Branch** | fix/S009-result-card-dismiss |
| **PR** | [#713](https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/713) |
| **Merge** | `b20158b7b29d5e5b68d3cd80c9618454743713e1` |
| **Deploy** | Frontend `dep-d9a1tql7vvec738evhmg` (live 2026-07-12) |
| **Status** | Closed — L1–4 verified; user confirmed production |

## Summary

Production UI bug: conversion results card for `manual_input.txt` stayed visible after
**Clear** or **Remove**. Root cause: `handleClear` omitted `convertedFiles`; F5 work-session
hydrate re-applied stale `converted_results` on every autosave refresh.

## Fix

- `handleClear` clears `convertedFiles` + `conversionLog`
- Hydrate guard: only on work-session **id** change
- Autosave includes `convertedFiles` / `conversionLog`

## Verification

| Layer | Result |
|-------|--------|
| L1 | Vitest repro 2/2; FileConverter 93/93; main CI green |
| L2 | Repro covers Clear + stale rehydrate |
| L3 | PR + main CI |
| L4 | Playwright prod smoke + user sign-off |

## Prevention

- Repro test in frontend CI (`npm test`)
- Cursor rule: `.cursor/rules/optional/fileconverter-f5-hydrate.mdc`
- Recurrence class: F5 hydrate overwriting local UI dismiss — review on similar changes
