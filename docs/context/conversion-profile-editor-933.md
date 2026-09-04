# Scoped context: ConversionProfile editor (#933)

> **Status**: active  
> **Created**: 2026-09-03  
> **Session**: `EV-933-ui-conversionprofile-editor-rule-packs-executabl`  
> **Tickets**: [#933](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/933) · parent UI [#922](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/922) · profiles [#912](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/912)  
> **Milestone**: M1 — Profiles  
> **Corpus**: [Corpus: product] F6 / F7 / F15 · [Corpus: journeys] · [Corpus: adr/ADR-038] · [Corpus: adr/ADR-036] · [Corpus: api] · [Corpus: tests]

## Goal

Ship operator **and admin** UI for ConversionProfile: **rule-pack editor**, **contract inspector**, and **operator-scoped overlays** persisted server-side under a signed/trust model (ADR-038 amend required — intake choice 2).

## Intake lock (2026-09-03)

| Topic | Decision |
|-------|----------|
| Users | Operator **and** admin |
| Overlay trust | Signed / operator-scoped overlays **persisted server-side** (heavier than first-party-only); ADR-038 amend |
| Docs | product + journeys + api + tests + decisions (+ ADR-038 amend) |
| UI preview | Local non-deployed FE+API (`:18000` / `:18001`) |
| Scale / routing | **full** — verify-plan → tech-tooling; e2e + verify-deploy |

## Precursors

| Item | Role |
|------|------|
| [ADR-038](../adr/ADR-038-conversion-profile-contract.md) | Contract accepted; overlays deferred **to this cycle** |
| [ADR-036](../adr/ADR-036-semantic-vs-exchange-profiles.md) | Semantic vs exchange split; nested wire |
| #1024 / EV-093 | Light picker — **keep**; do not collapse |
| EV-936 / #898 | Dissemination drawer — must-not-break |
| #915 | Absorbed into #933 (rule-pack editor) |

## Seed surfaces

| Piece | Location |
|-------|----------|
| Semantic catalog helpers | `apps/frontend/src/utils/semanticProfile.ts` |
| Exchange helpers | `apps/frontend/src/utils/exchangeProfile.ts` |
| Workbench pickers | convert/package UI + Vitest F6.e |
| Contract map | ADR-038 + `docs/domain/profiles/catalog.yaml` |
| Lint registry | `packages/tac-validate` / ADR-028 |

## Hard boundaries

1. No credential paste / no destinations-as-secrets in profiles (ADR-021/029)
2. No browser-uploaded **unsigned** schema bundles (ADR-038)
3. Fail-closed unknown profile ids
4. Profile defaults ≠ deployment destinations
5. Spec→Build gate closed until documenting verify PASS
6. Overlay storage: **product Postgres** + JWT ownership (F30) — Supabase Auth identity only

## Build intent (gate closed)

FE editor + BE JWT APIs for rule-packs/overlays; Playwright H4–H5 UJ-072; PR → `stage`.
**Milestones:** M1 rule-pack + inspector → M2 signed overlays.

## Out of scope

Live AFTN/WIS2 routes in editor; #1051 marketplace; #1050 variants; full declarative runtime loader rewrite; collapsing #1024.
