# Context — Issue #664 Custom Output Filename (Manual METAR Input)

> **Mode**: scoped | **Slug**: issue-664-output-filename | **Generated**: 2026-06-25  
> **Feature / workflow**: [GitHub #664](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/664) — allow custom output filename for manual METAR input | **Status**: active

## Executive Summary

Enhancement request ([#664](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/664)): when a user types a
METAR/SPECI manually and converts it, the downloaded IWXXM file is always named `manual_input.xml`
(`manual_input_1.xml`, `manual_input_2.xml`, … for multi-line input). Testers want to specify a custom
output filename before convert/download; if left blank, the default stays `manual_input`. The default
name originates in the backend (`apps/backend/src/api.py`, `manual_name = "manual_input[_N].txt"`) and
is surfaced to the browser as `ConversionResult.name`. The frontend derives the download name from that
value in `handleDownloadSingle` / `handleDownloadAll` (swapping the extension to `.xml`).

**Approved scope (user, 2026-06-25): frontend-only.** No API/backend contract change. Add an optional
"output filename" input near the manual TAC textarea; the frontend applies that base name to
manual-derived converted results (default `manual_input`), so single download, ZIP entry, and result
card label all use it. File-upload results keep their original filename.

## Resolution Log

| ID | Category | Decision |
|----|----------|----------|
| R1 | Decision | **Frontend-only** — name manual-derived downloads client-side; do not change `ConversionResult.name` or backend `manual_input` naming (preserves API contract; matches issue wording "downloaded files"). |
| R2 | Decision | **Default preserved** — blank input ⇒ `manual_input` (and `manual_input_N` per line); non-blank ⇒ user base name, sanitized. |
| R3 | Decision | **Scope to manual input only** — file uploads keep their uploaded filename; the custom name applies only to manual textarea results. |
| R4 | Ambiguity (assumed) | ⚠️ Assumed: multi-line manual input with a custom base name suffixes `_1`, `_2`, … to disambiguate, mirroring existing `manual_input_N` behavior. Confirm in 16-evolve if reporter expects a different scheme. |

## Scope & Constraints

**In scope (#664)**

| Item | Feature | Component | Priority |
|------|---------|-----------|----------|
| Optional output-filename input for manual TAC | F1 | `apps/frontend/.../FileConverter.tsx` | Medium — UX |
| Apply custom base name to manual-result download (single + ZIP) | F1 | `FileConverter.tsx` `handleDownloadSingle` / `handleDownloadAll` | Medium |
| Sanitize/validate filename (strip path chars, extension) | F1 | `FileConverter.tsx` (or small util) | Medium — safety |
| Blank ⇒ `manual_input` default | F1 | `FileConverter.tsx` | High — backward compat |

**Out of scope (unless user expands)**

- Backend `ConversionResult.name` / `manual_input` naming changes (R1).
- Renaming **file-upload** outputs (R3) — only manual input.
- Custom name for the batch ZIP archive name itself (`converted_files_<ts>.zip`) — not requested.
- F5 work-history row naming / persistence of the custom name (not in issue).
- REQ-016 unrelated rewrites.

**Linked issues**

- Parent tester feedback context: [#594](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/594) (input traceability — added `tac_input`), [#555](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/555).
- Recent converter UI work: [#656](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/656) / S001 (Convert & Convert&Send).

## Environment / Topology

No deploy topology change. Browser → `POST /api/v1/convert` request/response unchanged. Conversion and
download stay client-side; this is a pure UI/labeling change in the React frontend.

## Existing Infrastructure

| Asset | Path | Relevance |
|-------|------|-----------|
| Backend manual naming | `apps/backend/src/api.py` L1437–1440 | `manual_source = "manual_input_{i}"` (>1 entry) else `manual_input`; `manual_name = "{source}.txt"` |
| Backend batch/zip naming | `apps/backend/src/api.py` L2013–2023 | `manual_name = "manual_input_{i}.xml"` else `manual_input.xml` for ZIP route |
| ConversionResult schema | `apps/backend/src/schemas/conversion.py` L66–84 | `name` = output filename; `source`, `tac_input`, `content` |
| Manual textarea state | `apps/frontend/.../FileConverter.tsx` L104, L883–891 | `manualInput` state + `#manual-input` Textarea |
| Manual result mapping | `FileConverter.tsx` L370–392 | Splits `manualInput` by line; sets `name: result.name \|\| 'manual_input.txt'` |
| Converted file build | `FileConverter.tsx` L399–405 | `originalName = originalFile.name` → drives download name |
| Single download | `FileConverter.tsx` L578–589 | `a.download = file.originalName.replace(/\.(txt\|metar)$/i, '.xml')` |
| ZIP download | `FileConverter.tsx` L591–611 | `filename = file.originalName.replace(...)`; archive = `converted_files_<ts>.zip` |
| Converter snapshot (autosave/guest) | `FileConverter.tsx` L128–134, L253, L261 | `ConverterSnapshot` persists `manualInput`, `pendingFiles` — extend if custom name should survive reload |
| Frontend unit tests | `FileConverter.test.tsx`, `FileConverter.work-session.test.tsx` | Existing download + conversion coverage to extend |
| Converter E2E | `apps/e2e/tac-file-conversion.e2e.spec.ts` | Add custom-name download assertion |

## Cross-Reference Matrix

| Source | Default name today | Who sets it | Custom-name hook (planned) | Multi-line |
|--------|--------------------|-------------|----------------------------|------------|
| Issue #664 | `MANUAL_INPUT` (reporter wording) | — | user input pre-convert; blank ⇒ default | not specified |
| Backend `/api/v1/convert` | `manual_input[_N].txt` | `api.py` | unchanged (R1) | `_N` per line |
| Backend ZIP route | `manual_input[_N].xml` | `api.py` | unchanged (R1) | `_N` per line |
| Frontend download | `manual_input.xml` (from `originalName`) | `FileConverter.tsx` | override `originalName` for manual results | suffix `_N` (R4) |

## Implementation Backlog

1. **Output-filename input (R1/R2)** — Add an optional text field near the manual TAC textarea (e.g.
   "Output filename"), placeholder `manual_input`, with helper text that `.xml` is appended automatically.
   Disable/clear semantics consistent with `Clear` button and read-only (Finished) sessions.
2. **Sanitize base name** — Strip directory separators and illegal filename chars, drop any user-supplied
   extension, trim whitespace; empty after sanitize ⇒ fall back to `manual_input`. Consider a small pure
   helper for unit testing.
3. **Apply to manual results (R3)** — When mapping manual conversion results into `convertedFiles`, set
   `originalName` to `${baseName}.txt` (so the existing `.xml` swap yields `${baseName}.xml`). For multi-line
   manual input, suffix `_1`, `_2`, … (R4). Leave file-upload results untouched.
4. **Downloads** — Verify `handleDownloadSingle` and `handleDownloadAll` (ZIP entry) pick up the new name
   with no further change beyond step 3; result-card label / aria-label reflect the custom name.
5. **Persistence (optional)** — Decide whether the custom name is part of `ConverterSnapshot`
   (autosave + guest state). Default assumption: ephemeral (not persisted) unless user wants it saved.
6. **Tests** — Unit: sanitizer + manual-result naming (default and custom, single + multi-line). E2E:
   type manual TAC, set custom name, convert, assert downloaded filename. Frontend Vitest + Playwright.
7. **Docs** — Update `docs/feature-list.md` F1 UI actions note and `docs/user-journeys.md` if a journey
   step changes; link fix to #664 in evolve artifacts. No new feature ID (extends F1).

## Data & Credentials

No new credentials, datasets, or schema assets. Pure client-side UX change.

## Unresolved Gaps

- **Multi-line custom-name scheme (R4)** — ⚠️ Assumed `_1/_2` suffix; confirm with reporter/user in 16-evolve.
- **Persistence across reload** — whether custom name should survive autosave/guest snapshot (backlog #5).
- **ZIP archive name** — archive itself stays `converted_files_<ts>.zip`; confirm reporter does not also
  expect the archive named after the custom base.
- **Reporter wording vs code** — issue says `MANUAL_INPUT` (uppercase); actual default is lowercase
  `manual_input`. No behavior change implied; note in evolve to avoid confusion.

## Sources

- [GitHub #664](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/664) — issue body (2026-03-20), label `enhancement`
- [Repo: apps/backend/src/api.py](apps/backend/src/api.py) — manual naming L1437–1440, L2013–2023
- [Repo: apps/backend/src/schemas/conversion.py](apps/backend/src/schemas/conversion.py) — `ConversionResult.name`
- [Repo: apps/frontend/src/app/components/FileConverter.tsx](apps/frontend/src/app/components/FileConverter.tsx) — manual mapping L370–405, downloads L578–611
- [Repo: docs/feature-list.md](../feature-list.md) — F1 UI actions
- [Context: issue-594-feedback](issue-594-feedback.md) — prior manual-input traceability work
