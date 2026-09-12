# Scoped context: Dissemination ops + Gateway hooks (#936)

> **Status**: active  
> **Created**: 2026-09-03  
> **Session**: `EV-936-dissemination-ops-gateway-hooks`  
> **Tickets**: [#936](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/936) · absorbed [#935](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/935)/[#937](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/937) · contract [#927](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/927)  
> **Corpus**: [Corpus: product] F16–F19 / F7 · [Corpus: adr] ADR-030, ADR-041, ADR-040 · [Corpus: system-spec] · [Corpus: journeys] · [Corpus: tests]

## Goal

Implement **DisseminationGateway runtime hooks** (ADR-041 façade: `validate` / `send` / `health`) and the operator **#936** dissemination ops UI MVP: SQL mapping configurator, DisseminationPlan editor + delivery audit, gateway health console — complementing the restored destinations drawer (#898), not replacing one-shot send.

## Decisions (context interview 2026-09-03)

| ID | Decision |
|----|----------|
| D-EV936-C1 | **UI shape:** keep destinations drawer for one-shot preflight/send; add a **Dissemination ops** surface for plan/audit, SQL mapping, and gateway health |
| D-EV936-C2 | **Audit storage:** persist delivery audit on **product Postgres** (`DATABASE_URL`) with JWT-gated access (operator-scoped rows); redact at write — never store BYOC secrets or connection URIs. *(Amended from interview “Supabase RLS” shorthand — F30: no product PostgREST writes.)* |
| D-EV936-C3 | **Connectivity:** local FE+API + propose **H6′** smoke IDs; staging ack only if deploy-smoke later |
| D-EV936-C4 | Scale **standard**; gate stays closed until Spec band complete |

## In scope

- Thin `DisseminationGateway` registry in `packages/dissemination` over existing sinks (`gateway_kind`)
- `health()` connectivity-only probes (operator-safe `detail`)
- DisseminationPlan execute path + `DeliveryReceipt` / audit rows (ADR-041 fields)
- SQL MappingConfig configurator UI (ADR-040) — source vs sink modes
- Ops UI: plan editor (policy + destination multi-select), audit list/detail, gateway health
- Journey + H6′ smoke ID proposals when F16–F19 ops UI ships
- Feature-list / spec / journeys / test-plan / API deltas in Spec band

## Out of scope

- #933 ConversionProfile editor · #934 workflow builder · #938 pipeline inspector
- Live AFTN pathway (#909) / failover (#910) / wis2box buffer (#911) product features beyond façade hooks
- Credential paste; rendering secrets/URIs in audit UI
- Re-splitting #935/#937 without new AC
- New top-level `packages/afs` or `packages/gateways` (ADR-037 Option C / ADR-041)

## Current → target (runtime)

| Capability | Today | Target this evolve |
|------------|-------|--------------------|
| SinkAdapter preflight/send | ✅ drawer + API | Keep; Gateway façade dispatches to same |
| `health()` | ❌ | ✅ per gateway kind |
| DisseminationPlan runtime | Doc only (ADR-041) | ✅ execute + audit persist |
| SQL MappingConfig UI | Spike ADR-040 | ✅ configurator |
| Gateway health UI | ❌ | ✅ ops console |
| Audit UI | ❌ | ✅ list/detail (redacted) |

## Related standing docs

| Doc | Role |
|-----|------|
| [dissemination-gateway-927](dissemination-gateway-927.md) | Spike contract context |
| [sql-adapters-mapping-926](sql-adapters-mapping-926.md) | MappingConfig |
| [ADR-041](../adr/ADR-041-dissemination-gateway.md) | Gateway + Plan normative |
| [ADR-040](../adr/ADR-040-sql-adapters-mapping-config.md) | SQL mapping |
| [ADR-030](../adr/ADR-030-dissemination-package-architecture.md) | Package / egress |

## Must-not-break

- F16–F19 destinations drawer restore (#898) one-shot BYOC memory-only credentials
- `DISSEMINATION_EGRESS_ALLOWLIST` fail-closed egress (ADR-029/030)
- No internal doc refs on operator surfaces
- SinkAdapter HTTP v1 shapes for existing preflight/send

## Success (Spec band exit)

- Standing deltas drafted for product/system-spec/api/journeys/tests
- Tech plan for façade + Supabase audit + ops UI milestones
- Feasibility + documenting verify green; gate AskQuestion ready
