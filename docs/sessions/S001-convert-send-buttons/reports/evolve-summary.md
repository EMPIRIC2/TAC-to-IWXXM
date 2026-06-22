# Evolve summary — S001 convert-send-buttons

**Cycle**: EV-001  
**GitHub**: [#656](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/656)  
**Status**: implementation complete (pending deploy verify)

## Delivered

- **Convert** — existing convert-only action retained.
- **Convert&Send** — one-click convert then upload with fixed defaults (`iwxxm` / `primary` / no original).
- **Upload to Database** — manual two-step flow with dialog retained.
- Shared `uploadConvertedFiles` client in `apps/frontend/src/utils/databaseUpload.ts`.
- Unit tests (`FileConverter`, `databaseUpload`) and E2E one-click path in `tac-file-upload-database.e2e.spec.ts`.

## Spec deltas

- `docs/evolve-decisions.md` — scope and R1–R3
- `docs/feature-list.md` — F1 UI actions
- `docs/user-journeys.md` — UJ-001 steps
- `docs/test-plan.md` — E2E module reference

## Out of scope (deferred)

- Auto-clear input (#555)
- In-app error log preview (#555)
