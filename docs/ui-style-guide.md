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

## Copy / tone

- Plain-language operator copy; no planning vocabulary in labels, help, toasts, or `aria-label`.
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
| 2026-10-29 | [UX-2026-10-29-convert-polish](ui-ux-tweaks/UX-2026-10-29-convert-polish.md) | Frame TAC INFO / severity feedback as notes on TAC input (not “lint failures” / “TAC lint: …”). |
| 2026-10-29 | [UX-2026-10-29-map-wrap-overlays](ui-ux-tweaks/UX-2026-10-29-map-wrap-overlays.md) | Live map overlays that must survive tile wrap paint at world-copy longitude offsets (−360 / 0 / +360). |
