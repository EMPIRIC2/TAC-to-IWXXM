# Scoped Context Briefs

Feature- and workflow-specific context gathered via **00-context scoped mode**. These files
supplement (never replace) the project-level `docs/context-brief.md` when one exists.

**Sessions:** Scoped briefs are linked from `docs/sessions/SNNN-slug/session-brief.md` when
part of an active pipeline session. See [sessions/README.md](../sessions/README.md).

| Slug | Topic | Status | Created | Linked features |
|------|-------|--------|---------|-----------------|
| [platform-package-layout-923](platform-package-layout-923.md) | #923/#922 platform package layout gap matrix + Core→Dissemination milestone plan | active | 2026-09-03 | F6, F16–F19, ADR-030, EV-922 |
| [ev-098-ca-eccc-mining](ev-098-ca-eccc-mining.md) | CA_ECCC deep mine #1028–#1031 (datamart, MSC PDFs, MANOBS, MANAIR) via EV-097 handoff | active | 2026-09-02 | F36, EV-098 |
| [propagate-residuals-to-remarks](propagate-residuals-to-remarks.md) | #981 opt-in fold decode residuals into remarks/HRT + profile default + F7.q hooks (EV-981) | active | 2026-08-31 | F6, F9, F7.q |
| [ev-080-unit-coverage-100](ev-080-unit-coverage-100.md) | Strict 100% line+branch unit coverage (Py/TS/scripts); ADR-007 uplift (EV-080) | active | 2026-08-27 | ADR-007, F34, M5/CI |
| [wmo-aviation-registers-889](wmo-aviation-registers-889.md) | #889 codes.wmo.int aviation registers TAC present/cite/cover (S055/EV-046 Lean) | active | 2026-08-08 | F6, F12, F15, F20, F23, F24, F26, F27, F28, F32 |
| [iwxxm-corpus-residuals-846](iwxxm-corpus-residuals-846.md) | #846 residuals #849–#861 (S046/EV-038) | active | 2026-08-05 | F2, F4, F6, F7, F32 |
| [iwxxm-corpus-quality-846](iwxxm-corpus-quality-846.md) | #846/#835/#741/#808 official IWXXM corpus + WMO sources | active | 2026-08-04 | F32, F23, F4, F6, F2, S040/EV-032 |
| [platform-independence-842](platform-independence-842.md) | #842/#830/#712 Supabase strip + Render→DOKS | active | 2026-08-03 | F30?, F8, F21, S038/EV-031 |
| [quality-residuals-831](quality-residuals-831.md) | #831/#829/#820 rule matrices + TC deepen + VAA/TCA decode | active | 2026-08-02 | F29?, F23, F9, F26/F27, S037/EV-030 |
| [eight-family-ahl-rules-823](eight-family-ahl-rules-823.md) | #823 eight-family AHL/lint/convert/validate gap sweep | active | 2026-08-01 | F6+, F28?, S036/EV-029 |
| [sql-ingest-live-e2e](sql-ingest-live-e2e.md) | F16 live local multi-DB SQL ingest Playwright + teardown (S047/EV-039) | active | 2026-08-06 | F16, S047/EV-039 |
| [public-app-privacy](public-app-privacy.md) | Public app + IndexedDB history + privacy (#783) | active | 2026-07-27 | F5, F7, M4, S023/EV-017 |
| [convert-send-buttons](convert-send-buttons.md) | Convert & Convert&Send UI (GitHub #656) | active | 2026-06-22 | F1, UJ-001 |
| [live-e2e-integration](live-e2e-integration.md) | Live E2E and integration tests for Render | requirements-complete | 2026-06-22 | test-plan H3–H6, UJ-001–003 |
| [issue-594-feedback](issue-594-feedback.md) | COR handling + input traceability (GitHub #594) | active | 2026-06-22 | F1 |
| [supabase-keys-config](supabase-keys-config.md) | Supabase secret keys, minimal env, Render↔Supabase↔local sync, advisor remediation | active | 2026-06-23 | F3, M4 |
| [issue-555-feedback](issue-555-feedback.md) | Initial test UX — auto-clear inputs/results, error log preview (GitHub #555) | active | 2026-06-23 | F1, UJ-001 |
| [metar-work-history](metar-work-history.md) | User METAR work sessions Draft→WIP→Finished in Supabase (F5) | active | 2026-06-23 | F5, F1, M4 |
| [issue-671-docker-db](issue-671-docker-db.md) | Docker Compose backend cannot create DB tables — localhost:5432 connect refused (GitHub #671) | active | 2026-06-25 | M1, docker-compose |
| [issue-664-output-filename](issue-664-output-filename.md) | Custom output filename for manual METAR input (GitHub #664) | active | 2026-06-25 | F1, UJ-001 |
| [general-tac-iwxxm-converter](general-tac-iwxxm-converter.md) | Generalizable C/Cython TAC→IWXXM + IWXXM-US architecture | active | 2026-07-12 | F1, F2, F4, proposed Fn |
| [realtime-tac-ingest](realtime-tac-ingest.md) | Near-RT ingest design + `iwxxm-validate` / `tac-validate` packages; F7/F8 Planned | active | 2026-07-12 | F2, F6, F7, F8 |
| [issue-655-tac-traceability](issue-655-tac-traceability.md) | Source TAC display UX for conversion results (GitHub #655) | superseded | 2026-07-12 | F6, UJ-001 |
| [f7-operator-ui](f7-operator-ui.md) | F7 multi-product operator UI + workbench/decode/admin (#694/#702/#665/#666/#697) | active | 2026-07-13 | F7, F6, F5, M4 |
| [package-publish-validation](package-publish-validation.md) | PyPI packages + validation stack perf (#703/#698/#699/#693) | active | 2026-07-18 | F11–F14, S014/EV-010 |
| [metar-lint-quality](metar-lint-quality.md) | METAR lint issue registry + #732 quality (lint/validate/convert) | active | 2026-07-19 | F15, F6, F12, S015/EV-011 |
| [manual-tac-input-modes](manual-tac-input-modes.md) | Validate Manual TAC Input modes TAC/AHL/COLLECT (#730 / ADR-024) | active | 2026-07-20 | F7, S016/EV-012 |
| [aerodrome-quality](aerodrome-quality.md) | TAF + SPECI quality bar (#735/#734) | active | 2026-07-22 | F20, S020/EV-015 |
| [golden-examples-ui](golden-examples-ui.md) | Pre-loaded workbench golden examples (#780) | active | 2026-07-22 | F7, S021/EV-016 |
| [sigmet-quality](sigmet-quality.md) | General + VA SIGMET quality bars (#733/#739) | active | 2026-07-29 | F23, S025/EV-019 |
| [iwxxm-domain-mine](iwxxm-domain-mine.md) | WMO IWXXM/ tree + org refresh + IWXXM-US/MDL mine (#804/#807/#773) | active | 2026-07-30 | F6, F2, F4, F12, F13, F25, S031/EV-024 |
| [iwxxm-us-remarks-va](iwxxm-us-remarks-va.md) | iwxxm-us REMARKS encode (full dig ❌) + VA multi-location golden (#810–#812/#809) | completed | 2026-07-31 | F6, F12, F2, F13, F23, S032/EV-025 |
| [va-multi-location-809](va-multi-location-809.md) | #809 residual: soft-compare shipped; ADR-032 equality / wmoPass deferred | active | 2026-07-31 | F23, F6, F7.g, #809 post-#816 |

**Convention**: One brief per topic at `docs/context/<slug>.md`. Reference downstream as
`[Context: <slug> R#]`.
