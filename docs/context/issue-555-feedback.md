# Context — Initial Test Recommendations (GitHub #555)

> **Mode**: scoped | **Slug**: issue-555-feedback | **Generated**: 2026-06-23  
> **Feature / workflow**: Parent tester feedback — remaining UX gaps after S001 | **Status**: active

## Executive Summary

[GitHub #555](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/555) captures Kenneth's initial manual-input test feedback (2026-03-12). Four items were raised; **two were delivered in S001 / EV-001** ([#656](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/656)): explicit **Convert** and **Convert&Send** buttons plus send success/failure feedback (toasts + inline status). **Two items remain open**: (1) auto-clear or overwrite previous input/results without manual per-card dismissal, and (2) a previewable error log when conversion fails. The converter already clears manual text and the pending-file queue after a **successful** convert, but **accumulates** result cards across runs and exposes no structured log from API `errors` / `issues`.

## Resolution Log

| ID | Category | Decision |
|----|----------|----------|
| R1 | Ambiguity | **Replace Results panel** on each successful convert (not append); manual input + pending queue already clear on success |
| R2 | Decision | **In-app collapsible panel** from API `errors` / `issues` (no download-only path) |
| R3 | Scope | **Single evolve cycle** (EV-004 / S004) for #555 UX **and F5 work history** + S003 Supabase |
| R4 | Scope | **Confirmed** — items 1–2 from #555 already shipped in S001; do not re-implement |

## Scope & Constraints

**In scope (remaining #555 items)**

| # | Reporter ask | Gap today |
|---|--------------|-----------|
| 3 | Previous METAR input removed automatically or overwritten | Success path clears `manualInput` + `pendingFiles` ([Repo: FileConverter.tsx:L296-298]) but **appends** to `convertedFiles`; user removes result cards individually ([Repo: FileConverter.tsx:L464-466, L1022-1065]) |
| 4 | Log file previewable on errors | Backend returns `errors` + `issues` on `ConversionResponse` ([Repo: conversion.py:L117-124]); frontend ignores them ([Repo: FileConverter.tsx:L248-287]); only toast + brief `conversionStatus` banner |

**Already delivered (S001 / EV-001 — out of scope for S004)**

- Convert button — present (`convert-button` test id).
- Convert&Send — `handleConvertAndSend` with fixed upload defaults.
- Send confirmation — toasts; `DatabaseUploadDialog` inline success/error; `conversionStatus` `send_error` banner.

**Linked features**

- **F1** — METAR → IWXXM conversion UI (UX polish, no GIFTs change expected).

**Out of scope**

- REQ-016 migration rewrites.
- Backend conversion logic changes unless needed to surface existing `issues` (unlikely).
- Re-opening S001 button work.

## Environment / Topology

| Surface | Role | Notes |
|---------|------|-------|
| `apps/frontend` | Static UI | All changes target `FileConverter.tsx` (+ tests) |
| `apps/backend` | `POST /api/v1/convert` | Already returns `errors`, `issues`, per-result metadata |
| `apps/e2e` | Playwright | Extend UJ-001 flows for auto-clear + error log panel |

Browser wiring unchanged: frontend → API on `VITE_API_BASE_URL`; CORS per existing H4 gates.

## Existing Infrastructure

| Asset | Path | Relevance |
|-------|------|-----------|
| Convert / clear input on success | `apps/frontend/src/app/components/FileConverter.tsx` L296-298 | Partial auto-clear |
| Results accumulation | `FileConverter.tsx` L296, L464-466 | Append vs replace — core #555 gap |
| Manual Clear button | `FileConverter.tsx` L468-472 | Clears queue only, not results |
| Conversion status banner | `FileConverter.tsx` L916-972 | Single-line error message only |
| API response types | `apps/frontend/src/utils/api.ts` L40-60 | `errors`, `issues` typed but unused in UI |
| Backend issues schema | `apps/backend/src/schemas/conversion.py` | Structured `ConversionIssue` list |
| Conversion params UI | `FileConverter.tsx` L758-801 | `logLevel` / `onError` **not sent** to `convertMetarToIwxxm` |
| Parent context | `docs/context/convert-send-buttons.md` | S001 scope split (R3 excluded auto-clear + log) |
| Evolve log | `docs/evolve-decisions.md` EV-001 | Explicit deferral of #555 siblings |
| Prior session | `docs/sessions/S001-convert-send-buttons/` | Completed 2026-06-22 |

## Cross-Reference Matrix

| Source | Convert | Convert&Send | Send feedback | Auto-clear inputs/results | Error log preview |
|--------|---------|--------------|---------------|---------------------------|-------------------|
| Issue #555 | Requested | Requested | Requested | Requested | Requested |
| S001 / EV-001 | **Done** | **Done** | **Done** | Deferred | Deferred |
| Current UI | Done | Done | Done (toast + banner) | **Partial** (inputs on success only) | **Missing** |
| Backend API | N/A | N/A | N/A | N/A | **Data available** (`errors`, `issues`) |
| UJ-001 | Steps 4–5 | Steps 4–5 | Step 5 | Not specified | Not specified |

## Implementation Backlog

1. **R1 — Replace results on success** — Change `setConvertedFiles((prev) => [...newConvertedFiles, ...prev])` to assign latest batch only; keep existing success-path clear of `manualInput` + `pendingFiles`.
2. **Error log panel (R2)** — After convert (failure or partial success): collapsible panel listing `response.errors` and `response.issues`; persist until next convert.
3. **Wire partial failures** — When `response.failed > 0` but some results returned, show log panel + per-result status (today only checks `results` array length).
4. **Tests** — Unit: replace-vs-append results, log panel visibility; E2E: convert error fixture shows previewable log (UJ-001 delta).
5. **Docs delta (16-evolve)** — UJ-001 steps, `feature-list.md` F1 UX bullets, `test-plan.md` tier note.

## Data & Credentials

No new secrets. Error log content comes from authenticated convert API responses already available to logged-in users.

- **F5 / S004 merged**: Persisted user METAR work history — see [metar-work-history.md](metar-work-history.md); **same EV-004 cycle** as #555 UX.

## Unresolved Gaps

- **R1**: Resolved — replace Results on successful convert only.
- **R2**: Resolved — in-app panel only; no separate log file download required for MVP.
- **Conversion params drift**: UI exposes `logLevel` / `onError` but `callBackendConversion` omits them — out of #555 scope unless evolve expands.
- **Issue #555 still open** on GitHub (1/4 subtasks in issue UI); close criteria should reference S001 + S004 deliverables.

## Sources

- [GitHub #555](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/555) — `gh issue view 555` (2026-06-23)
- [GitHub #656](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/656) — child implementation issue (S001)
- [Context: convert-send-buttons R3](convert-send-buttons.md)
- [Docs: evolve-decisions.md EV-001](../evolve-decisions.md)
- [Repo: apps/frontend/src/app/components/FileConverter.tsx]
- [Repo: apps/frontend/src/utils/api.ts]
- [Repo: apps/backend/src/schemas/conversion.py]
