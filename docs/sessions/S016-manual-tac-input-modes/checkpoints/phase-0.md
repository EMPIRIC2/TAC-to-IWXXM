# Checkpoint — Phase 0 complete (S016 / EV-012)

**Date**: 2026-07-20  
**Decision**: D-S016-EV012-route-1 (lean + 13)

## Digest

- **Session**: S016-manual-tac-input-modes (feature)
- **Cycle**: EV-012 — Validate Manual TAC Input modes (#730)
- **Branch**: `evolve/EV-012-manual-tac-input-modes`
- **Fn**: F7 validation only (no new Fn; F7 stays Planned)
- **Routing**: 00 ✓ → 16 → **01** → 02 → 10 → 13

## Locked scope

| Item | Value |
|------|-------|
| Modes | TAC / AHL / COLLECT (ADR-024) |
| COLLECT | 501 placeholder UX (no extract) |
| Auto-switch | Required |
| Tests | Vitest + Playwright T1–T4 + live H4–H5/AHL/COLLECT |
| Deploy | 13-deploy-smoke after merge |

## Next

**01-requirements** (delta): `test-plan.md` / `user-journeys.md` rows for input-mode UJ +
acceptance checklist; link #730 matrix T1–T6.
