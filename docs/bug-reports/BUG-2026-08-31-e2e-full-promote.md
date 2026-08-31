# BUG-2026-08-31 — E2E Full red on stage→main promote

## Error description

Promote PR [#1067](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1067) (`stage` → `main`)
failed required check **E2E Full (Playwright)** while stage push smoke stayed green.

CI run: https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/33413710703

## Error logs

Hard failures:

1. `metar-work-history.e2e.spec.ts` — `convert-and-send-button` Expected count 0, Received 1
2. `tac-file-upload-database.e2e.spec.ts` — No TAC fixtures under `data/iwxxm-translation/...`
3. `uj027-030-dissemination-drawer.e2e.spec.ts` — missing
   `dissemination-progress-multi-partial-fail-chromium-linux.png`

## Investigation

| Hypothesis | Result |
|---|---|
| Product wrongly shows Convert&Send on finished sessions | Rejected — EV-091 / Vitest keep button mounted+disabled when destinations enabled |
| E2E assertion outdated vs EV-091 | Confirmed |
| Fixture path still pre-monorepo `data/` | Confirmed — fixtures live in `vendor/schemas/iwxxm-translation/` |
| Darwin-only screenshot committed | Confirmed — CI is ubuntu / `*-linux.png` |

## Repro / fix

- Session: `HF-e2e-full-promote-1067`
- Fix branch: `fix/e2e-full-promote-1067` (#1108 merged)
- Align E2E with Vitest; resolve vendor fixture path; commit Linux snapshot from CI actual

## Follow-up (post-#1108 … #1111)

1. #1108: fixtures path / EV-091 / linux snapshot
2. #1109: file-input strict mode
3. #1110: IWXXM `<pre>` assert
4. #1111: clean METAR still returns lint `issues` → Convert&Send skips upload
5. Next: mock `/api/v1/convert` with empty issues for Convert&Send chain
   (`fix/e2e-convert-send-mock-clean-convert`).
