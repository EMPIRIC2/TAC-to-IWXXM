# 04-tech-plan — S071 / EV-061 (delta)

**Status:** **approved** `D-S071-04-plan=1a`  
**No new deps / no new ADR / no new CORS origins**  
**Corpus:** [Corpus: product §F2] [Corpus: product §F6] [Corpus: product §F7] [Corpus: api]
[Corpus: tests] [Corpus: deploy] [Corpus: decisions §EV-061]

## Artifacts

- [execution-plan.md](execution-plan.md)
- [../build-plan-card.md](../build-plan-card.md)
- Standing: `docs/test-plan.md` TC-EV061-* stubs; `docs/api-contract.md` EV-061 endpoint review

## Tech locks (intake A)

| ID | Choice |
|----|--------|
| D-S071-m-order | M1 #1011 → M2 #1012 → M3 #1010 → M4 #1013 → M5 #1014 → M6 #1015 |
| D-S071-deps | No new npm/PyPI |
| D-S071-adr | No new ADR |
| D-S071-api | Additive catalog + AHL + validate decode fields; no new catalog route |
| D-S071-cors | Unchanged |
| D-S071-ci | Restore lint/typecheck CI + full E2E as required on `stage`→`main` |

## Skip 05/06

No new dependencies. CI job names are workflow-only under M6 / 07.

## Next

Plan **approved** (`D-S071-04-plan=1a`). Dual Spec `verify-qa` + `uat` next. Spec→Build **closed** until gate AskQuestion.
