# Evolve summary — S016 / EV-012

> Completed: 2026-07-20 (Phase 4 closed — D-S016-EV012-phase4-close-1)  
> Features: **F7** validation deepen only (status stays **Planned**)  
> Branch: `evolve/EV-012-manual-tac-input-modes` → PR [#746](https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/746) → `main` @ `37be5f8`  
> Deploy-smoke docs: PR [#747](https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/747)  
> Issue [#730](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/730) closed on cycle close  
> Orchestrator: 16-evolve  
> Routing: lean + 13 (00 → 16 → 01 → 02 → 10 → 13)

## Outcome

Validated Manual TAC Input modes (TAC / AHL bulletin / IWXXM COLLECT) per ADR-024 / #730:
Playwright TC-F7-007 T1–T6 + Vitest anchors green; FE toast on convert-time auto-switch and
gzip COLLECT classify-after-inflate; staging H0ci–H5 + authenticated AHL + COLLECT **501** UX
PASS on image `…-37be5f8`. F7 remains Planned; COLLECT member extract still out of scope.

## Stage trail

| Stage | Result |
|-------|--------|
| 00 / 16 | Session + Phase 0 intake; lean+13 routing |
| 01–02 | UJ-025 + TC-F7-007; 02 PASS (H6+UJ-025; T1–T6 hard) |
| 10 | Playwright T1–T6 + Vitest PASS (`7e052f4`) |
| 13 | Render deploy + H4–H5 + live workbench AHL/COLLECT PASS |

## Key decisions

- E12-1 — No new Fn; COLLECT stays 501; F7 Planned
- D-S016-EV012-route-1 — Lean + 13 (skip 03–09, 11–12)
- D-S016-EV012-13-path-A — Push/PR then smoke after merge/deploy
- D-S016-EV012-phase4-close-1 — Close EV-012/S016 after deploy approval

## Artifacts

Session reports under `docs/sessions/S016-manual-tac-input-modes/reports/`.  
Standing: `docs/evolve-report-EV-012.md`, `docs/CHANGELOG.md`, `docs/deploy-state.md`.
