# Execution plan — S044 / EV-036 (Lean; no 04)

**Branch:** `evolve/EV-036-local-precommit-long-jobs`  
**Corpus:** `[Corpus: product]` M5 · `[Corpus: tests]` · `[Corpus: decisions]` EV-036

| ID | Status | Spec | Task |
|----|--------|------|------|
| T1 | **completed** | M5 AC1 / TC-EV036-001 | Husky pre-commit: fast + `validate-ci-medium`; Makefile targets |
| T2 | **completed** | M5 AC1 / TC-EV036-002 | Husky pre-push → `make ci`; no validate on push |
| T3 | **completed** | M5 AC3–4 / TC-EV036-003 | `ci-cd.yml`: drop validate + Compose; keep units/coverage; PR coverage comment; rewire `needs` |
| T4 | **completed** | TC-EV036-001..003 | Dense contract tests under `tests/` |
| T5 | **completed** | DEVELOPMENT / dependency-inventory | Ops + inventory docs |

Gate A amend (`D-S044-02-gate-a`): remote keeps unit matrix + coverage + PR comment.
