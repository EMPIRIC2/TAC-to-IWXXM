---
name: IWXXM release-line deprecation warning
about: Track the 6-month warning window when a line leaves "previous" support
title: "[IWXXM] Deprecation warning — <VERSION> (6-month window)"
labels: ["documentation"]
---

## Context

A supported IWXXM release line is moving from **previous** into the **6-month
deprecation warning** period. See
[VERSION_SUPPORT_POLICY](../../docs/domain/iwxxm/VERSION_SUPPORT_POLICY.md)
§Deprecation Process.

**Do not** use this template for routine latest/previous rotates that keep two
supported lines. Use this template only when a line is scheduled to become
**unsupported**.

| Field | Value |
|-------|-------|
| Line entering warning | <!-- e.g. 2023-1 --> |
| New **latest** line | <!-- e.g. 2027-1 --> |
| New **previous** line | <!-- e.g. 2025-2 --> |
| Warning start (UTC) | <!-- YYYY-MM-DD --> |
| Planned drop (UTC, about +6 months) | <!-- YYYY-MM-DD --> |
| Parent epic or adopt pull request | <!-- link --> |

## Checklists

### Policy and engineering

- [ ] [VERSION_SUPPORT_POLICY](../../docs/domain/iwxxm/VERSION_SUPPORT_POLICY.md) table updated (or pull request linked)
- [ ] [RELEASE_LINE_ADOPTABILITY](../../docs/domain/iwxxm/RELEASE_LINE_ADOPTABILITY.md) §Deprecate-old-line in progress
- [ ] CHANGELOG or deploy note drafted
- [ ] Operator handoff (issue #847 / staff guide) drafted

### Staff and operations ([RELEASE_LINE_STAFF_GUIDE](../../docs/domain/iwxxm/RELEASE_LINE_STAFF_GUIDE.md))

- [ ] Stakeholders told which line remains **previous** and which line enters warning
- [ ] Partners given migrate-to-default guidance
- [ ] Workbench default smoke test planned after deploy
- [ ] After drop: the version picker no longer offers the retired line; preferences migrate

## Notes

<!-- Communications, blockers, United States (iwxxm-us) lag, golden CI impact -->

## References

- Epic / corpus: [#846](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/846) · template child [#855](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/855)
- Standing design docs: tech-spec · product feature F4 (IWXXM version handling)
