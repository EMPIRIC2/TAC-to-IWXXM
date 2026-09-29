# Decisions — EV-1159 SIGMET example validate visibility

Session: EV-1159-sigmet-example-validate. Ticket: #1159. Date: 2026-09-29.

[Corpus: product §F7] [Corpus: decisions]

| ID | Decision |
|----|----------|
| D1 | Scale **standard**. Spec→Build gate **closed** until documenting verify. |
| D2 | Deepen F7.g / F23 / F25. No new feature id. F7 stays Implemented. |
| D3 | Prefer display + example quality over weakening validation. |
| D4 | Primary documenting hypothesis: convert emits one `OUTPUT_VALIDATION_WARNING` and parks details in statistics `validation_errors`, not `issues[]`. Confirm vs orchestrator false positives and validate-mode handoff in Build. |
| D5 | UI in scope; non-deployed local preview deferred to Build open. |
| D6 | H4–H5 only if FE contract or validate UX changes require live connectivity; Vitest/backend unit are the default regression bar. |
| D7 | No new CORPUS member. Context brief under `docs/context/`. |
| D8 | Memory Neo4j unavailable — fail-open. |
| D9 | PR `--base stage`. No `stage`→`main`. Do not touch PR #1269. |
