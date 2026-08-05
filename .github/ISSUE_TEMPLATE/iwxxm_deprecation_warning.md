---
name: IWXXM release-line deprecation warning
about: Track the 6-month warning window when a line leaves "previous" support
title: "[IWXXM] Deprecation warning — <VERSION> (6-month window)"
labels: ["documentation"]
---

## Context

A supported IWXXM line is moving from **previous** into the **6-month deprecation warning**
period per [VERSION_SUPPORT_POLICY](../../docs/domain/iwxxm/VERSION_SUPPORT_POLICY.md)
§Deprecation Process.

**Do not** use this template for routine latest/previous rotates that keep two supported
lines — only when a line is scheduled to become **unsupported**.

| Field | Value |
|-------|-------|
| Line entering warning | <!-- e.g. 2023-1 --> |
| New **latest** | <!-- e.g. 2027-1 --> |
| New **previous** | <!-- e.g. 2025-2 --> |
| Warning start (UTC) | <!-- YYYY-MM-DD --> |
| Planned drop (UTC, ~+6 months) | <!-- YYYY-MM-DD --> |
| Parent epic / adopt PR | <!-- link --> |

## Checklists

### Policy / engineering

- [ ] [VERSION_SUPPORT_POLICY](../../docs/domain/iwxxm/VERSION_SUPPORT_POLICY.md) table updated (or PR linked)
- [ ] [RELEASE_LINE_ADOPTABILITY](../../docs/domain/iwxxm/RELEASE_LINE_ADOPTABILITY.md) §Deprecate-old-line in progress
- [ ] CHANGELOG / deploy note drafted
- [ ] Operator handoff (#847 / staff guide) drafted

### Staff / ops ([RELEASE_LINE_STAFF_GUIDE](../../docs/domain/iwxxm/RELEASE_LINE_STAFF_GUIDE.md))

- [ ] Stakeholders told which line remains **previous** vs entering warning
- [ ] Partners given migrate-to-default guidance
- [ ] Workbench default smoke planned after deploy
- [ ] After drop: picker no longer offers the retired line; prefs migrate

## Notes

<!-- Comms, blockers, US (iwxxm-us) lag, golden CI impact -->

## References

- Epic / corpus: [#846](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/846) · template child [#855](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/855)
- [Corpus: tech-spec] · [Corpus: product] F4
