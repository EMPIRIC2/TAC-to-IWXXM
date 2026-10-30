# UI style guide

[Corpus: ui-style] [Corpus: product §F7] [Corpus: journeys]

Living norms for the operator UI (`apps/frontend`). Grown by the **ui-ux-tweak** orchestrator:
each closed tweak appends a row under **Changelog of norms**. Consolidation PRs may rewrite
sections when norms conflict—cite the UX log ids retired or merged.

**Required artifacts (every ui-ux-tweak):** (1) UX log under `docs/ui-ux-tweaks/` from
`_template.md`, (2) regression test (Vitest or Playwright), (3) minimal FE change plus a
**Changelog of norms** row here linking that UX log id. Cite `[Corpus: ui-style]`.

**Not for operators:** this file is engineering corpus. Do not put planning ids (`EV-`, `UJ-`,
`ADR-`, `docs/…`) into user-visible copy (see no-internal-doc-refs / EV-048).

## Tokens / theme

- Prefer existing CSS variables and theme tokens under `apps/frontend/src/styles/` over one-off hex.
- Match surrounding surface density; avoid introducing a second visual system on a single screen.

## Layout / density

- One job per panel/section; prefer calm empty states over stacked chrome.
- Drawers and secondary actions should not compete with the primary convert path.
- Convert drop-zone chrome keeps Select files; do not show Mass Ingest beside it.
- Convert TAC notes: no Groups chip strip under the editor; group selection lives in Decoder, not as horizontal chips above the notes summary.
- Convert empty state: example chips sit in a bar above the TAC editor inside the main convert card; Other tasks sit in one tight row under that card — not a separate far strip.
- Convert catalog Examples sit in a compact bar above the TAC editor — not inside the Settings product/profile panel.
- Results → Downloads is file management only; conversion XML and result assessment details belong on Results → IWXXM.

## Copy / tone

- Plain-language operator copy; no planning vocabulary in labels, help, toasts, or `aria-label`.
- No feature/journey/theme shorthand (`F26`, `UJ-…`, `theme V1`) and no vague filler (`stuff`) on operator surfaces; keep grammatical articles (`a` / `an` / `the`).
- Prefer short, actionable empty-state and error text.

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
