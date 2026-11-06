# UX-2026-10-29-live-iwxxm-expand

| Field | Value |
|-------|--------|
| Id | `UX-2026-10-29-live-iwxxm-expand` |
| Session | `UX-live-iwxxm-expand` (local session store) |
| Surface | Convert Results / Live IWXXM soft preview |
| Journeys touched | F10 workbench IWXXM preview (tests/docs only — not UI copy) |
| Status | closed |

## Desired change

Live IWXXM XML sits in a short fixed-height box (`max-h-80`) with unused space below
in the Results drawer. Operators want an expand control so the preview can use more
vertical space, and clearer interactivity on that pane.

Soft-wrap for long XML lines already exists (`wrapXml`, default on; “Wrap XML lines” in
layout settings). This tweak does not rework wrap — it adds expand/collapse height.

## Acceptance

- [x] Expand control visible on Live IWXXM pane (named button / `aria-expanded`)
- [x] Expanded state raises or removes the squat `max-h-80` clamp (taller preview)
- [x] Collapse restores the compact clamp
- [x] Soft-wrap path unchanged (pretty XML still copyable; no new highlighter deps)

## Must not break

- Convert primary path, Results drawer tabs/resize, soft-fail banner copy
- Download / copy of IWXXM XML
- Sibling ui-ux-tweaks (issue list, Issue details, EV scrub, Live decode NL) — touch only
  `IwxxmPreviewPane` (+ its test / operator-copy catalog) and docs

## Style-guide impact

Norm to append ([Corpus: ui-style]):

> Live IWXXM preview: offer Expand/Collapse so operators can grow the XML viewer past the default squat max-height; keep soft-wrap available for long lines.

Target section: Layout / density

## Regression test

| Field | Value |
|-------|--------|
| Kind | Vitest |
| Path | `apps/frontend/src/app/components/IwxxmPreviewPane.test.tsx` |
| Red date | 2026-10-29 |
| Green date | 2026-10-29 |

## Change log (investigation)

| When | Note |
|------|------|
| 2026-10-29 | Pane clamps with `max-h-80`; wrap already prop-driven. Expand kept local to pane to avoid FileConverter conflicts. |
| 2026-10-29 | Header Expand/Collapse toggles `max-h-80` ↔ `max-h-[min(70dvh,40rem)]`. Soft-wrap unchanged. |

## Fix

- `IwxxmPreviewPane.tsx` — local expanded state; ghost Expand/Collapse button with chevron; `data-expanded`
- `IwxxmPreviewPane.test.tsx` — expand control present; expanded drops squat clamp
- `operatorVisibleCopy.ts` — catalog Expand/Collapse labels for internal-doc-ref scan
- `docs/ui-style-guide.md` — Changelog of norms row

## Close checklist

- [x] Regression green
- [x] Style-guide changelog row added (if norm)
- [x] No planning ids in operator-facing strings
- [x] Session closed / HANDOFF written
