# UI style guide

[Corpus: ui-style] [Corpus: product §F7] [Corpus: journeys]

This file records living norms for the operator user interface in `apps/frontend`.
Engineers and agents use this guide when they change screens, labels, or layout.

**Audience:** engineering. Operators do not read this file. Operator-visible strings
(labels, help, toasts, `aria-label`) must stay plain language. Do not put planning
ids (`EV-`, `UJ-`, `ADR-`, `docs/…`) into those strings.

**How norms grow:** the **ui-ux-tweak** orchestrator closes a tweak, then appends one
row under **Changelog of norms**. When two norms conflict, a consolidation pull
request may rewrite a section. Cite the UX log ids that the consolidation retires
or merges.

**Required artifacts (every ui-ux-tweak):**

1. UX log under local `docs/ui-ux-tweaks/` from `_template.md` (tree is gitignored)
2. Regression test (Vitest or Playwright)
3. Minimal frontend change plus a **Changelog of norms** row here that links that
   UX log id

Cite `[Corpus: ui-style]` when you apply these norms.

## Tokens / theme

- Prefer existing CSS variables and theme tokens under `apps/frontend/src/styles/` over one-off hex.
- Match surrounding surface density; avoid introducing a second visual system on a single screen.

## Layout / density

- One job per panel/section; prefer calm empty states over stacked chrome.
- Drawers and secondary actions should not compete with the primary convert path.
- Convert drop-zone chrome keeps Select files; do not show Mass Ingest beside it.
- Convert primary action strip (New TAC / Convert / Download latest): full-width three equal columns on `sm+` so Convert stays in the middle column. Do not left-pack unequal `min-w-*` widths.
- Convert TAC notes: no Groups chip strip under the editor; group selection lives in Decoder, not as horizontal chips above the notes summary.
- Convert empty state uses the same bordered converter chrome as the filled state (no marketing hero). Product type stays on the toolbar. Settings cog is rightmost; icon affordances use slow-fade hover cards.
- Operator footer is full-bleed across the bottom and collapsible to a right-edge reveal handle.
- Results Console does not show the conversion/validation log shell or lint issue catalog panel (status strip / error log may remain).
- Convert catalog Examples sit in a compact bar above the TAC editor — not inside the Settings product/profile panel.
- Results → Downloads is file management only; conversion XML and result assessment details belong on Results → IWXXM.
- Results drawer: title + Hide and the results tab strip stay pinned above the scrolling tab body (chrome outside the overflow scrollport).
- Results Decoder tab: pinned Live decode fills the drawer body height; scroll inside the panel (no squat max-height clamp).
- Results IWXXM preview fills the drawer body by default (no squat max-height); Expand may grow further; Collapse returns to fill.
- Collapsed Recent work is a sticky ~½″ vertical rail on the right spanning the workbench up to the primary action strip; expand restores the 280px panel and the main column reclaims width when collapsed.
- Live map station cards: product + station in a compact header, observation-time select (not Newer/Earlier pills), TAC collapsed by default, explicit Send to converter via the existing map→workbench handoff.
- Workbench Help / Preferences chrome and the User Preferences modal use dark outline controls (primary blue border, transparent fill); Preferences stays display-name + output-extension only (no validation knobs).

## Copy / tone

- Write operator copy in plain language. Do not use planning vocabulary in labels,
  help, toasts, or `aria-label`.
- Do not use feature, journey, or theme shorthand (`F26`, `UJ-…`, `theme V1`) on
  operator surfaces. Do not use vague filler (`stuff`). Keep articles (`a` / `an` /
  `the`).
- Prefer short, actionable empty-state and error text.
- Conversion / validation log Notes: when a coded issue has no `hint`, show a scrubbed catalog reason/consequence line (acronym gloss when the template provides it); never leave title+Code-only for catalogued codes.
- Live map / station minimap Leaflet corner credit must name OpenStreetMap contributors and the Open Database License (ODbL), with a link to the OSM copyright page, not a bare "© OpenStreetMap".
- Live map Results chrome shows the report provider in a muted visible line near the newest-observation status (Aviation Weather Center via existing notice copy); do not leave that credit screen-reader-only.

## Accessibility

- Visible focus; accessible names for icon-only controls.
- Do not rely on color alone for status.

## Motion

- Use motion for hierarchy/presence, not decoration. Prefer existing patterns when present.

## Test expectations

- **Vitest:** component/copy/class/`data-testid` invariants for local polish.
- **Playwright:** journey-visible layout or multi-step UX (cite journey id in the **test**, not in UI copy).

### Sample Vitest pattern (ui-ux-tweak)

```ts
// apps/frontend/src/…/Something.test.tsx
it("keeps the empty-state primary affordance visible", () => {
  render(<Something />);
  expect(screen.getByRole("button", { name: /convert/i })).toBeVisible();
  // Assert the calm invariant this tweak owns — must fail before the fix lands.
});
```

Record the test path and red/green dates on `docs/ui-ux-tweaks/UX-YYYY-MM-DD-*.md`.

## Changelog of norms

| Date | UX log | Norm (one line) |
|------|--------|-----------------|
| 2026-10-29 | [UX-2026-10-29-brand-tac-to-iwxxm](ui-ux-tweaks/UX-2026-10-29-brand-tac-to-iwxxm.md) | Login (and matching auth card) brand mark uses the product name **TAC-to-IWXXM** exactly; do not CSS-uppercase that mark. |
| 2026-10-29 | [UX-2026-10-29-center-button-text](ui-ux-tweaks/UX-2026-10-29-center-button-text.md) | Shared `Button` default size: fixed height + flex center; no vertical padding that fights the line box (labels/icons stay optically centered). |
| 2026-10-29 | [UX-2026-10-29-center-more-actions-buttons](ui-ux-tweaks/UX-2026-10-29-center-more-actions-buttons.md) | More actions (and other full-width Convert secondary buttons): keep shared `Button` flex center; do not override with `justify-start`. |
| 2026-10-29 | [UX-2026-10-29-convert-polish](ui-ux-tweaks/UX-2026-10-29-convert-polish.md) | Frame TAC INFO / severity feedback as notes on TAC input (not “lint failures” / “TAC lint: …”). |
| 2026-10-29 | [UX-2026-10-29-map-wrap-overlays](ui-ux-tweaks/UX-2026-10-29-map-wrap-overlays.md) | Live map overlays that must survive tile wrap paint at world-copy longitude offsets (−360 / 0 / +360). |
| 2026-10-29 | [UX-2026-10-29-issue-details-wrap-source-link](ui-ux-tweaks/UX-2026-10-29-issue-details-wrap-source-link.md) | Issue details: wrap long field values (no horizontal scroll); Source http(s) URLs are links (`target="_blank"`, `rel="noopener noreferrer"`), labels stay plain text. |
| 2026-10-29 | [UX-2026-10-29-tac-issue-severity](ui-ux-tweaks/UX-2026-10-29-tac-issue-severity.md) | TAC notes list: error rows use destructive text + semibold and a light destructive tint; Note / Warning stay default weight and no tint. |
| 2026-10-29 | [UX-2026-10-29-live-iwxxm-expand](ui-ux-tweaks/UX-2026-10-29-live-iwxxm-expand.md) | Live IWXXM preview: offer Expand/Collapse so operators can grow the XML viewer past the default squat max-height; keep soft-wrap available for long lines. |
| 2026-10-29 | [UX-2026-10-29-footer-links-horizontal](ui-ux-tweaks/UX-2026-10-29-footer-links-horizontal.md) | Public footer chrome links sit in one horizontal row (wrap allowed); keep the Beta badge with Feedback. |
| 2026-10-29 | [UX-2026-10-29-drop-groups-chips](ui-ux-tweaks/UX-2026-10-29-drop-groups-chips.md) | Convert TAC notes: no Groups chip strip under the editor; group selection lives in Decoder, not as horizontal chips above the notes summary. |
| 2026-10-29 | [UX-2026-10-29-convert-one-interface-examples](ui-ux-tweaks/UX-2026-10-29-convert-one-interface-examples.md) | Convert empty state: example chips sit in a bar above the TAC editor inside the main convert card; Other tasks sit in one tight row under that card — not a separate far strip. |
| 2026-10-29 | [UX-2026-10-29-drop-mass-ingest](ui-ux-tweaks/UX-2026-10-29-drop-mass-ingest.md) | Convert drop-zone chrome keeps Select files; do not show Mass Ingest beside it. |
| 2026-10-29 | [UX-2026-10-29-downloads-file-mgmt](ui-ux-tweaks/UX-2026-10-29-downloads-file-mgmt.md) | Results → Downloads is file management only (title, status chip, download/copy/remove). Conversion XML and assessment details belong on Results → IWXXM; picking a Downloads row focuses that file on IWXXM. |
| 2026-10-29 | [UX-2026-10-29-scrub-ev-operator-copy](ui-ux-tweaks/UX-2026-10-29-scrub-ev-operator-copy.md) | Lint issue list, Issue details, and tags show operator language only — never evolve ids, test ids, or ticket shorthand. |
| 2026-10-29 | [UX-2026-10-29-live-decode-phrases](ui-ux-tweaks/UX-2026-10-29-live-decode-phrases.md) | Live decode may group adjacent TAC tokens into natural-language phrase rows (joined Code, one Explanation); do not change the decode wire contract. |
| 2026-10-29 | [UX-2026-10-29-examples-bar-above-tac](ui-ux-tweaks/UX-2026-10-29-examples-bar-above-tac.md) | Convert catalog Examples sit in a compact bar above the TAC editor — not inside the Settings product/profile panel. |
| 2026-10-29 | [UX-2026-10-29-scrub-vague-jargon-operator-copy](ui-ux-tweaks/UX-2026-10-29-scrub-vague-jargon-operator-copy.md) | Operator copy stays concrete: no feature/journey/theme shorthand (`F26`, `UJ-…`, `theme V1`) and no vague filler (`stuff`); keep normal English articles. |
| 2026-10-30 | [UX-2026-10-30-console-log-enrichment](ui-ux-tweaks/UX-2026-10-30-console-log-enrichment.md) | Conversion / validation log Notes: when a coded issue has no `hint`, show a scrubbed catalog reason/consequence line (acronym gloss when the template provides it); never leave title+Code-only for catalogued codes. |
| 2026-10-30 | [UX-2026-10-30-map-data-attribution](ui-ux-tweaks/UX-2026-10-30-map-data-attribution.md) | Live map / station minimap Leaflet corner credit names OpenStreetMap contributors and ODbL (link OSM copyright page); not a bare "© OpenStreetMap". |
| 2026-10-30 | [UX-2026-10-30-convert-button-center](ui-ux-tweaks/UX-2026-10-30-convert-button-center.md) | Convert primary action strip: full-width three equal columns (New TAC \| Convert \| Download latest); Convert stays in the middle column. Do not left-pack unequal min-widths. |
| 2026-10-31 | [UX-2026-10-31-drop-console-chrome](ui-ux-tweaks/UX-2026-10-31-drop-console-chrome.md) | Operator log surfaces (conversion/validation log + Lint issue catalog) render inline — no collapsible "Console" shell/heading framing them. A **Clear log** affordance may remain as a small standalone control without a "Console" label. |
| 2026-11-02 | [UX-2026-11-02-cite-live-map-provider](ui-ux-tweaks/UX-2026-11-02-cite-live-map-provider.md) | Live map Results chrome shows Aviation Weather Center report credit in a muted visible line near newest-observation status; not screen-reader-only. |
| 2026-11-02 | [UX-2026-11-02-sticky-results-header](ui-ux-tweaks/UX-2026-11-02-sticky-results-header.md) | Results drawer: title + Hide and the results tab strip stay pinned above the scrolling tab body (chrome outside the overflow scrollport). |
| 2026-11-02 | [UX-2026-11-02-compact-map-result-card](ui-ux-tweaks/UX-2026-11-02-compact-map-result-card.md) | Live map station cards: product + station header, observation-time select (not Newer/Earlier pills), TAC collapsed by default, Send to converter via existing handoff. |
| 2026-11-02 | [UX-2026-11-02-preferences-visual](ui-ux-tweaks/UX-2026-11-02-preferences-visual.md) | Workbench Help / Preferences chrome and User Preferences modal: dark outline (primary blue border, transparent fill); Preferences stays display-name + output-extension only. |
| 2026-11-07 | [UX-2026-11-07-convert-chrome-polish](ui-ux-tweaks/UX-2026-11-07-convert-chrome-polish.md) | Convert empty state uses the same bordered converter chrome (no marketing hero); product type always on the toolbar; Settings cog rightmost with slow-fade hover cards; drop Results console + lint catalog panels; full-bleed collapsible footer; output-extension caret nudged left. |
| 2026-11-10 | [UX-2026-11-10-live-decode-drawer-fill](ui-ux-tweaks/UX-2026-11-10-live-decode-drawer-fill.md) | Results Decoder tab: pinned Live decode fills the drawer body height; scroll inside the panel (no squat max-height clamp). |
| 2026-11-10 | [UX-2026-11-10-recent-work-rail-results-fill](ui-ux-tweaks/UX-2026-11-10-recent-work-rail-results-fill.md) | Collapsed Recent work: sticky ~½″ vertical rail up to the primary action strip; Results IWXXM fills drawer by default (Expand grows further; Collapse returns to fill). |
