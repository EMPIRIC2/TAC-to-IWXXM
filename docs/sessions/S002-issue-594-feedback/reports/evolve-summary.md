# Evolve Summary — EV-003 / S002-issue-594-feedback

**Cycle**: EV-003  
**GitHub**: [#594](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/594)  
**Branch**: `fix/S002-issue-594-feedback`  
**Status**: Phase D complete; 11-verify-impl approved — ready for PR merge

## Scope delivered

| Item | Status | Notes |
|------|--------|-------|
| COR-after-time decode | Done | GIFTs grammar `METAR -> Type Cor? Ident ITime Cor? (NIL\|Report)` |
| COR-before-station regression | Done | Existing path unchanged |
| API `tac_input` echo | Done | Manual, multi-line manual, file, JSON convert paths |
| UI Source TAC panel | Done | Collapsible region above IWXXM XML per result |
| Per-line manual mapping | Done | Uses `tac_input` + line split fallback |

## Out of scope (confirmed)

- `=` terminator — reporter resolved; no change
- #555 auto-clear / error log preview
- Backend COR preprocessor (grammar fix sufficient)

## Tests added/updated

- `tests/bugs/test_bug_2026_06_22_issue_594_cor_after_time.py` (3 cases)
- `packages/gifts/tests/test_metar_encoding.py::test_cor_after_time`
- `apps/e2e/tac-file-conversion.e2e.spec.ts` — COR-after-time E2E
- `apps/frontend/src/app/components/FileConverter.test.tsx` — Source TAC display

## Spec deltas

- `docs/decisions/evolve-decisions.md` §EV-003
- `docs/guides/API.md`, `docs/api-contract.md` — `tac_input`
- `docs/test-plan.md` — TC-001b

## Next stages (routing plan)

- 08-verify-build — full CI parity
- 09-qa — COR matrix + traceability UX
- 10-e2e — delta E2E
- 11-verify-impl — acceptance signoff
- 12-verify-deploy — optional after merge
