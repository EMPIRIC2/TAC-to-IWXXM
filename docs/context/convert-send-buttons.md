# Context — Convert & Convert&Send Buttons

> **Mode**: scoped | **Slug**: convert-send-buttons | **Generated**: 2026-06-22  
> **Feature / workflow**: GitHub [#656](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/656) — dual convert/send UI | **Status**: active

## Executive Summary

Issue #656 requests two explicit actions in the main converter: **Convert** (format conversion only) and **Convert&Send** (convert then immediately send output). The codebase already implements **Convert** and a separate **Upload to Database** flow that requires a prior conversion and opens a configuration dialog. **Convert&Send is not implemented** — matching issue #555's note that it was "under development." Implementation is primarily frontend work in `FileConverter.tsx`, reusing the existing Supabase upload endpoint. Several behavioral details (upload defaults, button layout, scope of sibling #555 asks) need product decisions before build.

## Resolution Log

| ID | Category | Decision |
|----|----------|----------|
| R1 | Ambiguity | **Convert&Send uses fixed defaults** — `format: iwxxm`, `destination: primary`, `includeOriginal: false`; no upload dialog |
| R2 | Decision | **Keep all three buttons** — Convert, Convert&Send, Upload to Database |
| R3 | Scope | **#656 only** — buttons + send feedback; exclude #555 auto-clear and log preview |

## Scope & Constraints

**In scope (#656)**

- Convert-only button (may already satisfy requirement — verify UX/label placement).
- Convert&Send: chained convert → upload ("send").
- Send success/failure confirmation (toast and/or inline status).

**Linked features**

- **F1** — METAR → IWXXM conversion UI.
- Upload path is ancillary to F1 (Supabase edge function, not documented as separate Fn).

**Out of scope unless R3 expands**

- REQ-016 / migration non-goals: no unrelated rewrites.
- Backend `/api/v1/convert` unchanged unless evolve adds upload-prefs API (unlikely).

## Environment / Topology

| Surface | Role | Notes |
|---------|------|-------|
| `apps/frontend` | Static UI | Vite; calls backend for convert |
| Backend API | `POST /api/v1/convert` | Bearer auth; used by `convertMetarToIwxxm` |
| Supabase edge fn | `POST .../make-server-2e3cda33/database/upload` | "Send" destination; Bearer auth |

Browser wiring: frontend → API for convert; frontend → Supabase functions for upload (cross-origin). No CORS change expected for convert-only work; upload already used in production path.

## Existing Infrastructure

| Asset | Path | Relevance |
|-------|------|-----------|
| Convert handler | `apps/frontend/src/app/components/FileConverter.tsx` (`handleConvert`) | Core convert logic |
| Action buttons row | `FileConverter.tsx` ~L770–820 | Convert, Upload to Database, Download |
| Upload dialog | `apps/frontend/src/app/components/DatabaseUploadDialog.tsx` | Format/destination options; `handleUpload` |
| Upload API (client) | `DatabaseUploadDialog.tsx` L51–68 | POST with `{ files, options }` |
| Upload API (server) | `apps/frontend/supabase/functions/server/index.ts` L242–289 | Validates auth + options |
| User preferences | `UserPreferencesDialog.tsx` | Conversion params only — **no upload defaults** |
| Unit tests | `FileConverter.test.tsx`, `DatabaseUploadDialog.test.tsx` | Button states, upload mock |
| E2E | `apps/e2e/tac-file-upload-database.e2e.spec.ts` | Convert → open dialog → upload |
| Parent issue | GitHub #555 | Original tester feedback |

## Cross-Reference Matrix

| Source | Convert button | Convert&Send | Send = DB upload | Upload dialog required |
|--------|----------------|--------------|------------------|------------------------|
| Issue #656 | Required | Required | Implied ("send output") | Not specified |
| Issue #555 | Requested (under dev) | Requested (under dev) | Implied | Not specified |
| Current UI | **Present** ("Convert") | **Absent** | **Yes** (Upload to Database) | **Yes** (2-step) |
| E2E tests | Covered | Not covered | Covered (mocked upload) | Assumes dialog flow |

## Implementation Backlog

1. **Extract upload client** — Move fetch logic from `DatabaseUploadDialog` to shared util (e.g. `uploadConvertedFiles`) callable from Convert&Send and dialog.
2. **Add `handleConvertAndSend`** — After successful `handleConvert`, invoke upload with agreed defaults (R1).
3. **UI** — Add "Convert&Send" button next to Convert; disabled rules match Convert; loading states for combined operation.
4. **Feedback** — Surface send success/failure (#555 ask); distinguish convert failure vs send failure.
5. **Tests** — Unit: chained flow, error paths; E2E: optional one-click path with route mock.
6. **Docs delta (16-evolve)** — Extend UJ-001 steps; add test-plan tier note; optional feature-list bullet under F1.

## Data & Credentials

- Upload requires `accessToken` (Supabase JWT) — already passed to `FileConverter`.
- Default upload options today in dialog: `format: 'iwxxm'`, `destination: 'primary'`, `includeOriginal: false`.

## Unresolved Gaps

- **R1**: Without saved upload preferences, Convert&Send must pick defaults or still open the dialog (defeats "immediately sends").
- **R2**: Three buttons (Convert, Convert&Send, Upload) may clutter UI — product choice.
- **R3**: #555 also asks auto-clear inputs and error log preview — separate stories or same session?
- **Feature registry**: Database upload/send not listed as standalone feature in `feature-list.md`; evolve should document under F1 or new sub-capability.
- **No project `context-brief.md`** — scoped brief only; project-level brief unchanged.

## Sources

- [GitHub #656](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/656)
- [GitHub #555](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/555) — `gh issue view 555`
- [Repo: apps/frontend/src/app/components/FileConverter.tsx]
- [Repo: apps/frontend/src/app/components/DatabaseUploadDialog.tsx]
- [Repo: apps/e2e/tac-file-upload-database.e2e.spec.ts]
- [Docs: user-journeys.md §UJ-001]
