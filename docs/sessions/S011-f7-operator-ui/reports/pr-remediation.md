# PR Remediation — PRM-016 (19-address-pr-review)

> **Generated**: 2026-07-15  
> **Linked review**: PRR-019  
> **PR**: [#716](https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/716)

## Scope

Blockers then advisories from PRR-019 (user: bugs + blockers + advisories).

## Findings

| ID | Severity | Finding | Status | Commit |
|----|----------|---------|--------|--------|
| F1 | 🔴 | Multi-line soft-preview `failed_spans` offsets | fixed | see log |
| F2 | 🔴 | CI Validate / npm audit 410 | fixed | see log |
| F3 | 🟡 | Gzip decompress bomb | fixed | with F1 |
| F4 | 🟡 | Soft-preview SUCCESS logging/webhook | fixed | with F1 |
| F5 | 🟡 | Playwright T2 / H4–H5 on tip | deferred | host ports + disk; needs CI E2E + T6.4 deploy |

## Notes

AskQuestion UI unavailable; approaches assumed from PRR-019 + user scope.
