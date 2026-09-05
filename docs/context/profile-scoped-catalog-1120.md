# Scoped context: Profile-scoped catalog + glanceable Profile summary (#1120)

> **Status**: active  
> **Created**: 2026-09-05  
> **Session**: `EV-1120-epic-profile-scoped-lint-validation-issues-catal`  
> **Tickets**: [#1120](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1120) · [#1121](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1121) · [#1122](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1122) · [#1123](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1123) · [#1145](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1145) · umbrella [#912](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/912)  
> **Corpus**: [Corpus: product] F7.w / F15 / F35 / F36 · [Corpus: api] lint-issue-catalog · [Corpus: domain-profiles] · [Corpus: journeys] UJ-072 · [Corpus: tests] · [Corpus: adr/ADR-028] · [Corpus: adr/ADR-036] · [Corpus: adr/ADR-038]

## Goal

1. Filter `GET /api/v1/lint-issue-catalog` by semantic (+ exchange when packaging) so national-only codes appear only under the right Profile.  
2. Make Profile the glanceable primary context: one composition on Conversion Profiles and a compact twin on the convert workbench.

## Intake lock (2026-09-05)

| Topic | Decision |
|-------|----------|
| Scope | Dual track: #1120 children **and** Profile glanceable summary UX |
| Primary job | Author & understand **and** operate & convert (shared mental model) |
| WxDecoder priority | One composition / glanceable summary only |
| Summary content | Name/id, ≤3 vs-ICAO deltas, products, IWXXM line, rule-pack + overlay counts |
| Summary surfaces | Profiles page hero **and** workbench Profile twin |
| UX ticket | New child under #1120 (not amend #933 body as sole vehicle) |
| Unknown catalog profile params | **400** fail-closed (`invalid_semantic_profile` style) |
| Hard outs | No marketplace, Learn/XP, soft-preview TAC, #996, dissemination creds, full national engines, full workbench redesign |
| Scale | full rollup; UX sibling standard depth |
| Routing | Approved full spec band; Build #1121 → #1122 → #1123 → glanceable UX |
| Gate | closed until documenting verify |

## Precursors

| Item | Role |
|------|------|
| EV-062 / #1017 | Validation issues catalog (F7.v) |
| EV-093 / #1024 | Light Profile picker — keep; deepen with twin summary |
| EV-933 / #933 | ConversionProfile editor (F7.w) — forms remain; hierarchy under summary |
| ADR-028 | Lint issue registry |
| ADR-036 | Semantic vs exchange |
| ADR-038 | ConversionProfile contract / overlays |
| #912 | Multi-national profiles umbrella |

## Seed surfaces

| Piece | Location |
|-------|----------|
| Catalog API | `GET /api/v1/lint-issue-catalog` — [Corpus: api] |
| Catalog panel / hooks | FE `useLintIssueCatalog` + workbench catalog tab |
| Profiles editor | `apps/frontend/src/app/components/ConversionProfilePage.tsx` |
| Profiles copy | `apps/frontend/src/utils/conversionProfilesCopy.ts` |
| Semantic helpers | `apps/frontend/src/utils/semanticProfile.ts` |
| Profiles catalog API | `GET /api/v1/profiles/catalog` (JWT) |

## Must-not-break

- Omit-param catalog behavior (current clients)  
- `product` / `family` / existing catalog filters  
- F21 unauthenticated catalog + convert  
- EV-048 operator-copy guards  
- Dissemination drawer / BYOC secrets  

## Inspiration (bounded)

[WxDecoder](https://wxdecoder.com/app/#get) — clarity via one composition; **not** Learn mode, share cards, or map this cycle.

## Phase A lock (requirements + draft-docs)

See `reports/requirements-report.md`. Follow-ons: #1146 (composable convert), #1147 (workflow authoring).

## Next

`spec-development/feasibility` → tech-plan → … (delta standing docs) → verify-plan → draft-docs …
