# Evolve report — S016 Manual TAC Input modes (F7 validation)

- **Cycle**: EV-012
- **Session**: S016-manual-tac-input-modes
- **Status**: completed (Phase 4 closed — D-S016-EV012-phase4-close-1)
- **Scope**: Validate Manual TAC Input modes (TAC / AHL / COLLECT) under F7 / ADR-024 / #730;
  no new Fn; COLLECT remains HTTP 501 placeholder; F7 stays Planned
- **Stages run**: 00, 01, 02, 10, 13, 16 (lean + 13)
- **ADRs**: ADR-024 (consumed; no new ADR)
- **Deploy**: Render API + frontend-v4-web @ merge `37be5f8` (CI Deploy `29766213356`);
  smoke docs PR #747
- **GitHub issues**: #730 **closed**
- **Follow-ups** (non-blocking): fix H7 live harness form field `file`→`files` (pre-existing);
  optional COLLECT member extract (future Fn / evolve)

## Summary

EV-012 locked acceptance for UJ-025 / TC-F7-007 (T1–T6 hard), authored Playwright coverage,
and small FE fixes (convert-time auto-switch toast; classify COLLECT after `.gz` inflate).
Post-merge Render smokes confirmed H0c–H5, authenticated `convert-bulletin`, `ingest-collect`
501, and live workbench placeholder UX.

## Artifacts changed (high level)

- `apps/e2e/f7-manual-tac-input-modes.e2e.spec.ts` — TC-F7-007 suite
- `apps/frontend/.../FileConverter.tsx` — toast + gzip classify
- Docs: UJ-025, TC-F7-007, feature-list F7 note, session S016
- Session reports under `docs/sessions/S016-manual-tac-input-modes/`

## Verification

- 02-verify-plan: PASS
- 10-e2e: PASS (T1–T6 + Vitest)
- 13-deploy-smoke: PASS (H0ci–H5 + AHL + COLLECT 501 + live workbench)
