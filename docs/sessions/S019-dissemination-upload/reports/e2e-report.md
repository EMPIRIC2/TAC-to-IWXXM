# E2E Report — S019 / EV-014 (F16–F19 / UJ-027–030)

> Generated: 2026-07-21  
> Scope: UJ-027–030 dissemination drawer + sink paths  
> Evidence: T6.3 Playwright (`07-build-t63.md`); CI E2E Smoke on #772; mock BYOC close gate  
> Mode: evolve / Full routing (10-e2e bookkeeping)

## Journey matrix

| Journey / TC | Mechanism | T0 | T2 connectivity | T3 browser |
|--------------|-----------|----|-----------------|------------|
| UJ-027 / F16 drawer + DB preflight | Playwright + Vitest + API | PASS | PASS (H4–H5) | PASS (T6.3 6/6) |
| UJ-028 / F17 WIS2 | Playwright + harness/mocks | PASS | PASS (route + mock) | PASS (drawer sink) |
| UJ-029 / F18 EDIS | Playwright + SMTP mocks | PASS | PASS (mock) | PASS (drawer sink) |
| UJ-030 / F19 AMHS/SWIM/AFS | Playwright + staging stubs | PASS | PASS (stub) | PASS (drawer sink) |
| TC-F16 writer-contract | pytest + Testcontainers (CI) | PASS | — | — |
| TC-F17-001 harness | Compose wis2box (when Docker) | PASS (CI path) | — | — |
| TC-F17-002 live BYOC | Live destination | **Waived** | mock smoke | — |
| Mock BYOC close gate | `make test-mock-byoc-smoke` | PASS (134) | — | — |

## Results

- **Playwright UJ-027–030:** 6/6 green (T6.3; PR #770 stack → #771/#772)
- **CI E2E Smoke (Playwright):** pass on #772
- **Mock BYOC close-gate:** 134 passed (`packages/dissemination/tests/test_mock_byoc_close_gate.py`)

## Connectivity columns

| Column | Status |
|--------|--------|
| T0 in-process | PASS |
| T2 H4–H5 | PASS (T6.6 public smokes) |
| T3 live browser UJ | PASS (T6.3); live FE drawer confirmed post-#771 |
| Live destination BYOC | Waived (`D-S019-EV014-Q15-mock-waive`) |

**Overall: PASS** with mock-BYOC close-gate amendment.
