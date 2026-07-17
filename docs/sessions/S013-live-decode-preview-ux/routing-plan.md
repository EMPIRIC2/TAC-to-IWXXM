# Routing plan — S013-live-decode-preview-ux

| Stage | Required | Mode | Skip rationale |
|-------|----------|------|----------------|
| 00-context | yes | scoped (session open only) | Context covered by docs/context/f7-operator-ui.md + live code reading |
| 16-evolve | yes | orchestrator | — |
| 01-requirements | yes | delta | — |
| 02-verify-plan | yes | delta | — |
| 03-plan-tooling | no | — | Existing hooks/rules cover this scope; no new guardrails |
| 04-tech-plan | yes | delta | — |
| 05-verify-tech | yes | delta | — |
| 06-tech-tooling | no | — | Lint/typecheck/CI already wired; no new dependencies anticipated |
| 07-build | yes | full | — |
| 08-verify-build | yes | full | — |
| 09-qa | yes | full | — |
| 10-e2e | yes | full | — |
| 11-verify-impl | yes | full | — |
| 12-verify-deploy | yes | full | — |
| 13-deploy-smoke | yes | full | User approved full cycle including deploy + smokes |

## Approved

User approval recorded: 2026-07-16 (AskQuestion — routing "Approve routing as proposed";
Fn allocation F9 + F10 approved in the same batch).
