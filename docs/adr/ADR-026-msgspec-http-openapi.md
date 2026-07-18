# ADR-026: msgspec on high-churn HTTP; pydantic for OpenAPI

> **Status**: Accepted  
> **Date**: 2026-07-18  
> **Deciders**: User (S014 / EV-010 E10-14, E10-15, E10-17, E10-18)  
> **Stage**: 01-requirements  
> **Related**: ADR-016 (amended); feature-list F11; api-contract high-churn routes  
> **Session**: S014-package-publish-validation / EV-010  
> **Issues**: #703

## Context

ADR-016 placed **msgspec** in packages and **pydantic** at FastAPI HTTP edges, with a
msgspec→pydantic mapping tax of unknown cost. User direction for EV-010: move high-churn
validation to msgspec for speed ([msgspec](https://msgspec.dev/why.html) decode+validate),
while keeping pydantic where OpenAPI / FastAPI schema integration matters
([pydantic](https://docs.pydantic.dev/latest/why/)). Breaking response shapes are allowed;
Render redeploy (12–13) is in scope.

## Decision

1. **High-churn routes use msgspec** for **response** encode and for **internal** Struct
   validation after request assembly:
   `POST /api/v1/convert`, `/convert-zip`, `/convert-bulletin`, `/validate`, `/lint-tac`,
   `/decode-tac`. Prefer reused `Encoder`/`Decoder` instances on hot paths.
2. **Multipart intake stays FastAPI** `Form`/`File` parsing (these routes are
   `multipart/form-data`, not JSON bodies). After fields are assembled, map into msgspec
   Structs for typed validation where useful — **do not** claim msgspec JSON-decode of the
   raw multipart body. Optional JSON body alternatives are out of scope unless a later
   decision adds them.
3. **Auth, work-sessions, airports, ICAO OPMET stats** stay on **pydantic** (lower traffic;
   OpenAPI stability).
4. **OpenAPI**: Keep publishing OpenAPI for the API. For msgspec-backed **response** models,
   maintain **thin pydantic alias models** and/or explicit JSON Schema export solely for schema
   generation — **do not dual-validate** at runtime (would erase the speed win).
5. **Frontend**: Update shared/OpenAPI-derived TS types in the **same cycle** as any
   breaking JSON **response** shape changes.
6. **Perf gates (E10-24)**: Soft benches during build; hard-fail at publish/cutover that
   msgspec response encode path is ≤ prior pydantic response mapping path on convert/validate
   fixtures.

## Alternatives Considered

| # | Alternative | Why rejected |
|---|-------------|--------------|
| 1 | Keep ADR-016 as-is (pydantic all HTTP) | User chose faster validation than pydantic on hot paths |
| 2 | msgspec on all `/api/v1/*` | Auth/admin OpenAPI stability preferred (E10-17=A) |
| 3 | Dual-run pydantic + msgspec | Defeats performance goal |
| 4 | Drop OpenAPI for migrated routes | User requires pydantic for OpenAPI integrations (E10-18) |
| 5 | JSON body alternatives for convert/validate this cycle | Deferred — multipart remains FE contract (02 S2.M1=A) |

## Consequences

- ADR-016 §HTTP boundary is **amended**: packages remain msgspec; selected HTTP routes are
  msgspec too; pydantic remains for OpenAPI + low-churn routes.
- Requires FE type updates and H4–H5 / operator smokes after deploy.
- Tech plan must pick FastAPI integration pattern (custom dependency vs raw body +
  `msgspec.json.decode`).

## References

- E10-14, E10-15, E10-17, E10-18; [evolve-decisions §EV-010](../decisions/evolve-decisions.md)
- https://msgspec.dev/why.html — validation during decode
- https://docs.pydantic.dev/latest/why/ — JSON Schema / ecosystem
