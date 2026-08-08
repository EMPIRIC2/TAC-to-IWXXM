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
| [S051-output-filename-download-stale](S051-output-filename-download-stale/session-brief.md) | hotfix | in_progress | #904 output filename stale on Download; BUG-2026-08-07 | fix/output-filename-download-stale | 2026-08-07 | — |
| [S049-operator-sources-briefing](S049-operator-sources-briefing/session-brief.md) | feature | in_progress | Operator UI source-centric runbook + PPT pack; EV-041 Lean docs | evolve/EV-041-operator-sources-briefing | 2026-08-06 | — |
| [S048-workbench-lint-ux](S048-workbench-lint-ux/session-brief.md) | feature | completed | Workbench lint UX + prefs + official AHL/Collect + catalog source; EV-040; PR #893; #894 | evolve/EV-040-workbench-lint-ux | 2026-08-06 | 2026-08-06 |
| [S047-sql-ingest-live-e2e](S047-sql-ingest-live-e2e/session-brief.md) | feature | completed | F16 live local multi-DB SQL ingest Playwright + teardown; EV-039; PR #891; `D-S047-13=1` | docs/EV-039-closeout → main | 2026-08-06 | 2026-08-08 |
| [S046-iwxxm-corpus-residuals](S046-iwxxm-corpus-residuals/session-brief.md) | feature | completed | #846 residuals #849–#861; deepen F2/F4/F6/F7/F32; EV-038; PR #890 | main @ 619a7ac3 / DOKS 20260806144346-619a7ac | 2026-08-05 | 2026-08-06 |
| [S045-matrix-disposition-residuals](S045-matrix-disposition-residuals/session-brief.md) | feature | completed | #869/#870/#872 matrix dispositions; deepen F2/F6/F32; EV-037; PR #887 | evolve/EV-037-matrix-disposition-residuals | 2026-08-05 | 2026-08-05 |
| [S044-local-precommit-long-jobs](S044-local-precommit-long-jobs/session-brief.md) | feature | completed | Local long jobs on pre-commit + slim CI; deepen M5; EV-036; PR #875 | evolve/EV-036-local-precommit-long-jobs | 2026-08-05 | 2026-08-05 |
| [S043-rule-source-traceability](S043-rule-source-traceability/session-brief.md) | feature | completed | Rule↔source provenance deepen F6/F12/F15/F2; EV-035; deploy waived | evolve/EV-035-rule-source-traceability | 2026-08-05 | 2026-08-05 |
| [S042-doks-cd-rollout](S042-doks-cd-rollout/session-brief.md) | feature | completed | Automate DOKS CD rollout; EV-034; TC-F30-007 @ 20260805115809-d3f4bb9 | main @ d3f4bb95 | 2026-08-05 | 2026-08-05 |
| [S041-worker-poller-hardening](S041-worker-poller-hardening/session-brief.md) | feature | completed | F8 deepen INGEST_POLLER_URL hardening; EV-033 lean-close D-S041-1+3 | main (#865) | 2026-08-04 | 2026-08-05 |
| [S040-iwxxm-corpus-quality](S040-iwxxm-corpus-quality/session-brief.md) | feature | completed | #846 epic children shipped; F32 VONA; EV-032 closed (`D-S040-close`) | main @ #848 / live d3f4bb9 | 2026-08-04 | 2026-08-05 |
| [S037-quality-residuals-831](S037-quality-residuals-831/session-brief.md) | feature | completed | #831/#829/#820 closed; F29 Done; residual #835; EV-030 | evolve/EV-030-quality-residuals-831 | 2026-08-02 | 2026-08-03 |
| [S036-eight-family-ahl-rules-823](S036-eight-family-ahl-rules-823/session-brief.md) | feature | completed | #823 eight-family AHL/lint/convert/validate; EV-029; F28 Done; PR #828 | main (#828) | 2026-08-01 | 2026-08-02 |
| [S034-wmo-decode-residual-matrix](S034-wmo-decode-residual-matrix/session-brief.md) | feature | in_progress | #815 official WMO decode residual matrix; EV-027 | evolve/EV-027-wmo-decode-residual-matrix | 2026-07-31 | — |
| [S033-va-multi-location-equality](S033-va-multi-location-equality/session-brief.md) | feature | completed | #809 ADR-032 equality → wmoPass; EV-026; PR #817/#818 | evolve/EV-026-va-multi-location-equality | 2026-07-31 | 2026-07-31 |
| [S032-iwxxm-us-remarks-va](S032-iwxxm-us-remarks-va/session-brief.md) | feature | completed | iwxxm-us REMARKS + #809 soft; EV-025; PR #816 | evolve/EV-025-iwxxm-us-remarks-va | 2026-07-31 | 2026-07-31 |
| [S029-sigmet-decode-residuals](S029-sigmet-decode-residuals/session-brief.md) | feature | in_progress | F9 deepen — SIGMET/AIRMET decode residual A6-1a tokens; EV-022 | feat/EV-022-sigmet-decode-residuals | 2026-07-30 | — |
| [S028-sigmet-multiline-split](S028-sigmet-multiline-split/session-brief.md) | hotfix | completed | BUG-2026-07-30 SIGMET multiline split; PR #796 | fix/BUG-2026-07-30-sigmet-multiline-split | 2026-07-30 | 2026-07-30 |
| [S027-vaa-quality](S027-vaa-quality/session-brief.md) | feature | completed | VAA+TCA quality (#736/#737); F26/F27; PR #794 | evolve/EV-021-vaa-quality | 2026-07-29 | 2026-07-30 |
| [S026-airmet-quality-wmo-examples](S026-airmet-quality-wmo-examples/session-brief.md) | feature | completed | AIRMET + WMO METAR/SPECI/TAF parity (#731); F24/F25; PR #793 | evolve/EV-020-airmet-quality | 2026-07-29 | 2026-07-29 |
| [S025-sigmet-quality](S025-sigmet-quality/session-brief.md) | feature | completed | SIGMET family quality (#733/#739); F23; PR #792 merged | evolve/EV-019-sigmet-quality | 2026-07-29 | 2026-07-29 |
| [S024-dissemination-file-select](S024-dissemination-file-select/session-brief.md) | feature | completed | Multi-file export selection in dissemination portal (#785); PR #791 | evolve/EV-018-dissemination-file-select | 2026-07-28 | 2026-07-29 |
| [S023-public-app-privacy](S023-public-app-privacy/session-brief.md) | feature | completed | Public app + local history + privacy (#783); PR #790 open (do not auto-merge) | evolve/EV-017-public-app-privacy | 2026-07-27 | 2026-07-28 |
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
| [S022-rename-cutover](S022-rename-cutover/session-brief.md) | ops | completed | #781 EMPIRIC2 rename cutover (Render/GHCR) + live goldens; PyPI follow-up | infra/S022-rename-cutover | 2026-07-27 | 2026-07-27 |

## Active session

**[S051-output-filename-download-stale](S051-output-filename-download-stale/session-brief.md)** — hotfix / 14-hotfix  
Fix [#904](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/904): Output filename field changes after convert must apply to Download / ZIP member names.  
Branch: `fix/output-filename-download-stale` (pending create). Bug report: `docs/bug-reports/BUG-2026-08-07-output-filename-download-stale.md`.

Prior closed: **[S050-remove-db-tools-operator-throughput](S050-remove-db-tools-operator-throughput/session-brief.md)** (EV-042) — PR #899 @ e3d1c7c8.

Epic [#846](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/846) remains **OPEN** for residual children
(#869/#870/#872; #871 closeable). S040 remains suspended eligible to resume (do not auto-resume).

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
