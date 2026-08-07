# Session brief — S051-output-filename-download-stale

| Field | Value |
|-------|-------|
| **Type** | hotfix |
| **Intent** | Fix #904 — after convert, Output filename field changes must apply to Download / ZIP member names (BUG-2026-08-07-output-filename-download-stale) |
| **Branch** | `fix/output-filename-download-stale` (pending create from `main@d6f6fa04`) |
| **Orchestrator** | 14-hotfix |
| **Bug report** | [docs/bug-reports/BUG-2026-08-07-output-filename-download-stale.md](../../bug-reports/BUG-2026-08-07-output-filename-download-stale.md) |
| **GitHub** | [#904](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/904) |
| **Remediation** | local-first (deploy only after explicit approval) |
| **Started** | 2026-08-07 |
| **Status** | in_progress |

## Routing

1. `14-hotfix` — full (**in_progress**)
2. `15-service-health` — optional after deploy (pending)

## Notes

Opened via workflow-state-manager after S050/EV-042 close. Related origin feature: #664 (S006 custom output filename).
