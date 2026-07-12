# ADR-015: Validate Packages, Bulletin API, and Deferred F7/F8

> **Status**: Accepted  
> **Date**: 2026-07-12  
> **Deciders**: User (S008 01-requirements AskQuestion Q1–Q54)  
> **Stage**: 01-requirements  
> **Related**: [ADR-013](ADR-013-tac2iwxxm-package-architecture.md), [ADR-014](ADR-014-tac2iwxxm-rust-gifts-removal.md), [ADR-009](ADR-009-live-test-harness.md)  
> **Context refs**: [Context: realtime-tac-ingest](../context/realtime-tac-ingest.md), session S008

## Context

S008 defined F6 (`packages/tac2iwxxm`) for seven-product TAC→IWXXM. A follow-on amend asked
for general TAC data entry, near-realtime ingest, and Schematron validation of IWXXM (and
clarified TAC is **not** Schematron-validated). Interview outcomes: package-first this cycle;
two new libraries; F7/F8 named Planned; Schematron on IWXXM only; bulletin split required;
dedicated bulletin HTTP endpoint; TAC lint HTTP endpoint; H7 live bulletin gate; auth/sinks
postponed; F5 remains METAR-only.

## Decision

1. **`packages/iwxxm-validate`** (MIT): XSD + Schematron engine; consumes `vendor/schemas/*`
   read-only; **no** FastAPI/Supabase. F2 backend route is a **thin wrapper**.
2. **`packages/tac-validate`** (MIT): TAC parse gate + shared business-rule pack for all seven
   product TAC forms; **no** Schematron; may use pydantic/msgspec (choose in 04).
3. **Unified pipeline** (library / future F7–F8): split → tac-validate → tac2iwxxm →
   iwxxm-validate.
4. **HTTP (this cycle)**:
   - `POST /api/v1/validate` → `iwxxm-validate` (shape unchanged).
   - `POST /api/v1/lint-tac` → `tac-validate` (new).
   - `POST /api/v1/convert` → **single-report** only.
   - `POST /api/v1/convert-bulletin` → AHL bulletin split + multi-result (schema in 04).
5. **F6.bulletin**: Bulletin split is a package acceptance criterion; phase with/before F6.a.
6. **F7** (multi-product operator entry/sessions): **Planned**; F5 unchanged; **not built**
   this cycle.
7. **F8** (near-RT ingest, store+push, quarantine, worker scale): **Planned**; **not built**
   this cycle. F6 non-goal “no new Render deployable” **unchanged**; F8 worker requires its
   own ADR when built.
8. **H7**: Dedicated live connectivity gate for bulletin path (UJ-011 / TC-LIVE-F6-030);
   extends live harness beyond H6 (see test-plan + connectivity-gates).
9. **Postponed**: Machine-ingest auth; push sinks; AMHS/SWIM adapters.

## Alternatives Considered

| # | Alternative | Why rejected |
|---|-------------|--------------|
| 1 | Schematron on TAC | User chose IWXXM-only Schematron; TAC uses rule pack |
| 2 | Validate packages inside tac2iwxxm only | User required separate IWXXM + TAC packages |
| 3 | Auto-detect bulletin on `/convert` | User chose explicit `/convert-bulletin` |
| 4 | Build F7/F8 this cycle | User chose package APIs + thin wrappers only |
| 5 | Amend F5 to multi-product | User chose new F7; leave F5 METAR-only |
| 6 | Fold live bulletin into H3 only | User chose dedicated **H7** |

## Consequences

- M1/M5/CI gain two workspace members; coverage gate applies.
- API surface grows by two routes; OpenAPI/shared types update in build.
- Template remains `static+api` until an F8 worker ADR.
- 04-tech-plan must define: bulletin multi-result schema; lint-tac content-type; AHL dialect
  fixtures; `make test-live-bulletin`.

## References

- [feature-list.md](../feature-list.md) F2, F6–F8
- [spec.md](../spec.md) unified pipeline
- [api-contract.md](../api-contract.md)
- [test-plan.md](../test-plan.md) TC-F6-030–033, H7
- [requirements-decisions.md](../decisions/requirements-decisions.md) RT-R1–R14
