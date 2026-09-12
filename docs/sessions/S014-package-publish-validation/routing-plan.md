# Routing plan — S014-package-publish-validation

| Stage | Required | Mode | Skip rationale |
|-------|----------|------|----------------|
| 00-context | yes | scoped | Session open + `docs/context/package-publish-validation.md` |
| 16-evolve | yes | orchestrator | — |
| 01-requirements | yes | delta | New Fn F11–F14; product/package contracts |
| 02-verify-plan | yes | delta | — |
| 03-plan-tooling | yes | delta | PyPI publish / release-tag guardrails |
| 04-tech-plan | yes | delta | Execution plan: benches → packages → PyPI CI → HTTP msgspec |
| 05-verify-tech | yes | delta | — |
| 06-tech-tooling | yes | delta | Rust crates, maturin, schema bundle, PyPI workflow, msgspec HTTP |
| 07-build | yes | full | — |
| 08-verify-build | yes | full | — |
| 09-qa | yes | full | — |
| 10-e2e | yes | full | Library/CLI + wheel smokes + browser if HTTP contract changes |
| 11-verify-impl | yes | full | Per-Fn sign-off |
| 12-verify-deploy | yes | full | PyPI trusted publishing + release tags **and** Render deploy checklist |
| 13-deploy-smoke | yes | full | **Included** per E10-15 (msgspec HTTP / faster validation than pydantic) |

## Approved

| Gate | Decision | Date |
|------|----------|------|
| Fn allocation | F11–F14 (12A) | 2026-07-18 |
| Must-ship | Everything (11B) | 2026-07-18 |
| Routing | 01–13 incl. 03/06; PyPI + Render | 2026-07-18 |
| HTTP msgspec | Breaking OK; leave pydantic for OpenAPI-only where still required (14A+15C) | 2026-07-18 |

**Amendment:** Intake E10-3/E10-13 “skip Render 13” superseded by E10-15 — move validation off pydantic to msgspec and redeploy.
