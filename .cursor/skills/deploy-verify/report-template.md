# Deploy Report Template

Template for `docs/deploy-report.md`.

```markdown
# Deployment Report

> **Date**: [date]
> **App**: [modal app name]
> **Commit**: [hash]
> **Branch**: [branch]

## Deployment Status: SUCCESS / PARTIAL / FAILED

## Pre-Deploy Checks
| Check | Result | Notes |
|-------|--------|-------|
| Config validation | PASS/FAIL | ... |
| Dependencies | PASS/FAIL | ... |
| Secrets | PASS/FAIL | ... |

## Deployment
- **Mode**: ephemeral / deployed
- **URL**: [app URL]
- **Functions**: [N] deployed

## CI/CD
| Pipeline | Status | URL |
|----------|--------|-----|
| [workflow] | PASS/FAIL | [url] |

## Validation
| Test | Result | Metric | Threshold | Actual |
|------|--------|--------|-----------|--------|
| Smoke test | PASS/FAIL | response_time | < 5s | [actual] |
| [experiment] | PASS/FAIL | [metric] | [threshold] | [actual] |

## Changelog
- Generated: CHANGELOG.md
- Tag: v[version]-deploy
- Commits included: [N]

## Monitoring Baseline
| Metric | Value at Deploy |
|--------|----------------|
| Error rate | [X]% |
| Avg response time | [X]ms |
| Container count | [N] |

## Monitoring Checklist
- [ ] Check deploy dashboard daily for first week
- [ ] Verify error rate stays below [X]%
- [ ] Health-check workflow enabled (if created)

## Known Issues
- [any accepted deviations from spec]

## Release notes (optional)

Aggregate merged PRs / task commits since last tag or prior deploy into a short user-facing
summary, or point to `docs/CHANGELOG.md`.

## Rollback Command
`modal app stop [app-name]`
```
