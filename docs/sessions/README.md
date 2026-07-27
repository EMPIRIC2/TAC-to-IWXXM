# Sessions index

Session-specific artifacts for bounded work units. Standing project docs remain in `docs/` root.

**Convention:** [sessions-reference.md](../../.cursor/skills/sessions-reference.md)  
**Routing:** [skill-routing.md](../skill-routing.md)

## Quick start

```
@00-context I want to <your goal>
```

00-context will:

1. Classify session type (`greenfield`, `feature`, `hotfix`, `integration`, `new_service`, `ops`, `process`)
2. Allocate the next id (`S001`, `S002`, …)
3. Create this folder with `session-brief.md` and `routing-plan.md`
4. Ask you to approve the routing plan
5. Set `active_session` in `workflow-state.yaml`

Then invoke stages from the approved plan (e.g. `@10-e2e`, `@16-evolve`).

## Index

| Session ID | Type | Status | Intent | Branch | Started | Completed |
|------------|------|--------|--------|--------|---------|-----------|
| [S001-convert-send-buttons](S001-convert-send-buttons/session-brief.md) | feature | completed | Convert & Convert&Send UI (#656) | feat/S001-convert-send-buttons | 2026-06-22 | 2026-06-22 |
| [S002-issue-594-feedback](S002-issue-594-feedback/session-brief.md) | hotfix | in_progress | COR handling + TAC traceability (#594) | fix/S002-issue-594-feedback | 2026-06-22 | — |
| [S003-supabase-keys-config](S003-supabase-keys-config/session-brief.md) | hotfix | paused | Supabase keys / config split | fix/supabase-service-key-leak | 2026-06-23 | — |
| [S004-issue-555-feedback](S004-issue-555-feedback/session-brief.md) | feature | completed | #555 UX + F5 work history | feat/S004-issue-555-feedback | 2026-06-23 | 2026-06-25 |
| [S005-issue-671-docker-db](S005-issue-671-docker-db/session-brief.md) | hotfix | completed | Docker Compose bundled Postgres (#671) | fix/S005-issue-671-docker-db | 2026-06-25 | 2026-06-25 |
| [S006-issue-664-output-filename](S006-issue-664-output-filename/session-brief.md) | feature | completed | Custom output filename for manual METAR (#664) | feat/S006-issue-664-output-filename | 2026-06-25 | 2026-07-12 |
| [S007-docs-minimize](S007-docs-minimize/session-brief.md) | process | completed | Minimize docs/ root; nest non-standing docs | docs/S007-docs-minimize | 2026-07-12 | 2026-07-12 |
| [S008-general-tac-iwxxm-converter](S008-general-tac-iwxxm-converter/session-brief.md) | feature | completed | General TAC→IWXXM + near-RT ingest (EV-006) | evolve/S008-general-tac-iwxxm-converter | 2026-07-12 | 2026-07-12 |
| [S009-result-card-dismiss](S009-result-card-dismiss/session-brief.md) | hotfix | completed | Results Card stays after Cancel/Remove | fix/S009-result-card-dismiss | 2026-07-12 | 2026-07-12 |
| [S010-issue-655-tac-traceability](S010-issue-655-tac-traceability/session-brief.md) | feature | completed | Source TAC on conversion results (#655) | evolve/EV-007-issue-655-tac-traceability | 2026-07-12 | 2026-07-13 |
| [S011-f7-operator-ui](S011-f7-operator-ui/session-brief.md) | feature | completed | F7 multi-product UI + workbench/decode/admin (#694/#702/#665/#666/#697); PR #716 merged | evolve/S011-f7-operator-ui | 2026-07-13 | 2026-07-19 |
| [S012-empty-bearer-lint-tac](S012-empty-bearer-lint-tac/session-brief.md) | hotfix | completed | Empty Bearer on lint-tac/decode-tac + lint UX issue details | fix/S012-empty-bearer-lint-tac | 2026-07-15 | 2026-07-15 |
| [S013-live-decode-preview-ux](S013-live-decode-preview-ux/session-brief.md) | feature | completed | Value-aware live decode + plain-language summary (F9); IWXXM preview pane + lint UX clarity (F10) — EV-009; PR #723 | evolve/S013-live-decode-preview-ux | 2026-07-16 | 2026-07-18 |
| [S014-package-publish-validation](S014-package-publish-validation/session-brief.md) | feature | completed | Validation stack perf + PyPI packages F11–F14 (#703/#698/#699/#693) — EV-010 | evolve/EV-010-package-publish-validation | 2026-07-18 | 2026-07-19 |
| [S015-metar-lint-quality](S015-metar-lint-quality/session-brief.md) | feature | completed | METAR lint issue registry + #732 quality — EV-011; F15 Done; PR #742 | evolve/EV-011-metar-lint-quality | 2026-07-19 | 2026-07-20 |
| [S016-manual-tac-input-modes](S016-manual-tac-input-modes/session-brief.md) | feature | paused | Validate Manual TAC Input modes (#730 / ADR-024) — EV-012 | evolve/EV-012-manual-tac-input-modes | 2026-07-20 | — (paused for S017) |
| [S017-skill-trim-retro](S017-skill-trim-retro/session-brief.md) | process | in_progress | Skill trim retrospective RET-001 | chore/S017-skill-trim-retro | 2026-07-20 | — |
| [S018-metar-remarks-667](S018-metar-remarks-667/session-brief.md) | feature | completed | Handle METAR remarks (#667) — EV-013 | evolve/EV-013-metar-remarks-667 | 2026-07-20 | 2026-07-20 |
| [S019-dissemination-upload](S019-dissemination-upload/session-brief.md) | feature | completed | Dissemination epic F16–F19 — EV-014; PR #772 | evolve/EV-014 / cursor/* | 2026-07-20 | 2026-07-21 |
| [S020-aerodrome-quality](S020-aerodrome-quality/session-brief.md) | feature | completed | F15 sequel — TAF+#735 + SPECI+#734 quality (F20) — EV-015; PR #778 | evolve/EV-015-aerodrome-quality | 2026-07-22 | 2026-07-22 |
| [S021-golden-examples-ui](S021-golden-examples-ui/session-brief.md) | feature | completed | F7.g golden examples (#780) — EV-016; PR #782; live H4–H5 → #781 | evolve/EV-016-golden-examples-ui | 2026-07-22 | 2026-07-27 |

## Active session

**None** — S021 / EV-016 closed (`D-S021-EV016-phase4-close`; live H4–H5 waived → #781).

Parked/other: see rows above (S016 paused; S017 process).

Last closed: **[S021-golden-examples-ui](S021-golden-examples-ui/session-brief.md)** — F7.g on `main` @ `c49f22b`; PR [#782](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/782); live smoke deferred to [#781](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/781).

## Folder layout

```
docs/sessions/SNNN-slug/
  session-brief.md      # intent, type, scope, links to standing docs
  routing-plan.md       # approved stage list + skip rationale
  reports/              # qa-report, e2e-report, verification-report, etc.
  checkpoints/          # optional phase gate digests
```

## Standing docs vs session reports

| Kind | Location |
|------|----------|
| Long-lived specs | `docs/spec.md`, `feature-list.md`, `test-plan.md`, `deploy.md`, … |
| Session outputs | `docs/sessions/{id}/reports/*.md` |
| Scoped discovery | `docs/context/{slug}.md` |

Pre-session reports at `docs/` root (e.g. `docs/reports/qa-report.md`) are historical; new work uses
session report paths.
