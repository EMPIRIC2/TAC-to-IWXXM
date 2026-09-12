# Scoped context: DisseminationGateway (#927)

> **Status**: active  
> **Created**: 2026-09-03  
> **Session**: `EV-927-dissemination-gateway`  
> **Tickets**: [#927](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/927) · [#922](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/922)  
> **Corpus**: [Corpus: product] F16–F19 · [Corpus: adr] ADR-030, ADR-041

## Goal

Validate unified **DisseminationGateway** (validate/send/health) + **DisseminationPlan** (policy, retry, audit) over AFTN/AMHS/EDIS/WIS2box. Spike only.

## Recommendation

Extend `packages/dissemination` with gateway contract (ADR-041); optional future `dissemination/afs/` submodule — no new top-level package. Map `validate`→preflight, `send`→send; add `health()` sketch. DisseminationPlan documented; runtime deferred.

## Current adapters

| Sink | Module | validate | send | health |
|------|--------|----------|------|--------|
| DB (F16) | `db_preflight`, writer_contract | preflight ✅ | send ✅ | ❌ |
| WIS2 (F17) | `wis2.py` | preflight ✅ | publish ✅ | ❌ |
| EDIS (F18) | `edis.py` | preflight ✅ | SMTP submit ✅ | ❌ |
| AMHS/SWIM/AFS (F19) | `f19_stubs.py` | staging ✅ | staging ✅ | ❌ |

## Policy notes

- **EDIS (#928):** ASCII-only; AHL + TAC body — raw IWXXM XML is **not** AFTN-safe as-is
- **WIS2 (#929):** BYOC MQTT + dataset PUT; DMZ = browser→API→egress→operator broker
- **Plan/audit (#930):** `DeliveryReceipt` status enum; no BYOC secret persistence

## Out of scope

#909/#910/#911 features · #936 UI · live AFTN pathway
