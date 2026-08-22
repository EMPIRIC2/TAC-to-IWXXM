# ADR-036: Semantic vs Exchange Profiles + Canonical ID Migration

> **Status**: Accepted (EV-063 / #912 / #914)  
> **Date**: 2026-08-22  
> **Deciders**: User (EV-063 evolve intake)  
> **Related**: [ADR-013](ADR-013-tac2iwxxm-package-architecture.md), [ADR-030](ADR-030-dissemination-package-architecture.md), [ADR-021](ADR-021-byo-credentials-admin-removal.md), [ADR-029](ADR-029-dissemination-ssrf-allowlist.md)  
> **Issues**: [#912](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/912), [#914](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/914), [#1025](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1025) (alias cutover)

## Context

F6 today exposes a single flat `profile` enum (`annex3` | `iwxxm_us`) on convert/validate
([Corpus: api], [Corpus: product] F6). That conflates:

1. **Semantic profiles** — how TAC is parsed, normalized, and encoded to IWXXM (national
   extensions, RMK policy, unit/geo rules).
2. **Exchange profiles** — how converted products are **packaged** for regional AFS / ROBEX /
   RODEX routing (bulletin headers, filenames, COLLECT conventions) — not TAC grammar.

Epic [#912](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/912) requires multiple national
semantic profiles (`ICAO_2025`, `US_FAA_NWS`, `CA_ECCC`, …) and separate exchange overlays
(`GLOBAL_AFS`, `APAC_ROBEX`, …). Dissemination saved connections (F16–F19) already use the
word “profile” for a different concept (memory-only BYOC destinations) — must not merge.

Constraints from EV-063 intake:

- One ICAO/PANS-MET canonical IR + national overlays — not N independent converters.
- `iwxxmVersion` and extension XSD list are **independent** of semantic profile id.
- Breaking wire change is acceptable with ADR + deprecation window; alias removal tracked in #1025
  after **2026-10-31**.
- Must-not-break: annex3 / iwxxm_us golden behavior during alias window; F16–F19 credential /
  allowlist semantics unchanged.

## Decision

1. **Split profile kinds**
   - **Semantic profile** — TAC → canonical IR → IWXXM mapper (core + national extension).
   - **Exchange profile** — post-convert packaging for bulletin/filename/routing defaults
     (invoked on package/disseminate-prep paths; not on convert-only calls).

2. **Canonical semantic IDs** (initial set; extend via F36 / child issues)

   | Canonical ID | Purpose | Legacy alias (deprecation window) |
   |--------------|---------|-----------------------------------|
   | `ICAO_2025` | International baseline (Annex 3 Amd 82 + PANS-MET; IWXXM 2025-2) | `annex3` |
   | `US_FAA_NWS` | US differences + IWXXM-US | `iwxxm_us` |

   Additional national ids (`CA_ECCC`, `AU_BOM`, `NZ_CAA_MET`, …) are **F36** children of #912.

3. **Wire shape** (normative target — implement after Spec→Build gate)

   ```yaml
   conversion:
     semanticProfile: US_FAA_NWS
     iwxxmVersion: "2025-2"      # independent of semantic id
     extensions: [IWXXM_US_3]    # optional national extension tokens
   exchange:
     profile: GLOBAL_AFS         # default when packaging path invoked
   ```

   During transition, flat multipart `profile=` remains accepted and maps to
   `conversion.semanticProfile` via aliases. Config default may stay on legacy names until cutover
   (`PROFILE_WIRE_V2` feature flag — see env-contract).

4. **Validation contract** (align #925 later; minimum for F35)

   Stages exposed as structured multi-result validity where applicable:
   TAC lexical → profile semantic → cross-field → canonical → core XSD → extension XSD →
   Schematron → code lists → profile output rules → exchange validation.

   Unknown semantic or exchange profile id → **HTTP 400** (hard). Alias ids accepted only during
   the deprecation window with a deprecation signal (header and/or structured field).

5. **Exchange profile ≠ dissemination destination**

   Exchange profile selects packaging rules only. BYOC credentials, sink URIs, and
   `DISSEMINATION_EGRESS_ALLOWLIST` remain F16–F19 concerns (ADR-021/029/030). No persistence of
   secrets in profile definitions.

6. **Observability**

   Emit metrics for semantic profile id, exchange profile id (when used), and alias-use counters
   during deprecation. No PII in profile metric labels.

7. **Source catalog**

   Authoritative URLs and gaps for national/exchange profiles live under
   [Corpus: domain-profiles] (`docs/domain/profiles/`), fed by #913 mine ticket.

## Alternatives considered

| # | Alternative | Why rejected |
|---|-------------|--------------|
| 1 | Keep flat `profile` only | Cannot express exchange overlays; blocks #912 national matrix |
| 2 | One profile id encodes both semantic + exchange | Couples TAC grammar to AFTN/ROBEX routing; breaks F16 naming clarity |
| 3 | Indefinite `annex3` / `iwxxm_us` aliases | User chose dated cutover (#1025) for clarity and operator copy |
| 4 | N independent converters per country | Violates canonical IR + overlay architecture (#912) |
| 5 | Bake WIS2/AFTN destinations into semantic profiles | Epic non-goal; conflicts with BYOC memory-only model |

## Consequences

### Positive

- Clear separation for API, UI (#1024 light picker vs #933 editor), and library consumers.
- National profiles become data-driven overlays on one pipeline.
- Exchange packaging can evolve with #921 without re-parsing TAC.

### Negative / risks

- Dual wire acceptance during deprecation increases contract-test surface.
- UI and OpenAPI must stay aligned across alias + canonical ids.
- First national profiles (F36) depend on #913 catalog quality and #914 landing.

### Follow-ups

- **F35** (EV-063): ADR acceptance, api-contract delta, compat layer, metrics, #1025 schedule.
- **F36**: #919 US deepen, #916 CA_ECCC first P1, #921 exchange overlays, fixture layout
  `profiles/<id>/<product>/{valid,invalid,expected-*}`.
- **#1024**: Light operator picker (deferred unless Spec→Build pulls FE).
- Amend ADR-013 cross-reference when F35 Build completes (profile plugin path naming).

## References

- [feature-list.md §F35](../feature-list.md), [feature-list.md §F36](../feature-list.md)
- [api-contract.md §EV-063 proposed wire](../api-contract.md)
- [domain/profiles/README.md](../domain/profiles/README.md)
- Epic [#912](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/912), architecture [#914](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/914)
