# ADR-041: DisseminationGateway contract + DisseminationPlan (spike #927)

> **Status**: Accepted (EV-927 / #927)  
> **Date**: 2026-09-03  
> **Related**: [ADR-030](ADR-030-dissemination-package-architecture.md), [ADR-037](ADR-037-platform-logical-layers.md), [ADR-029](ADR-029-dissemination-ssrf-allowlist.md), [ADR-021](ADR-021-byo-credentials-admin-removal.md)  
> **Issues**: [#927](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/927), [#922](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/922)  
> **Absorbed:** #928 EDIS caution · #929 WIS2box BYOC/DMZ · #930 plan/audit

## Context

Spike [#927](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/927) asks for a **single DisseminationGateway** so AFTN, AMHS, EDIS, and WIS2box share `validate` / `send` / `health`, plus **DisseminationPlan** (policy, transform, retry, delivery audit).

[ADR-030](ADR-030-dissemination-package-architecture.md) shipped F16–F19 as **SinkAdapter** + protocol modules (`edis`, `wis2`, `f19_stubs`, `db_preflight`) with unified HTTP preflight/send. Gaps:

- No named **Gateway** facade or `health()`
- No **DisseminationPlan** / **DeliveryReceipt** / audit model
- AFS addressing/envelope not grouped (scattered: `edis` AHL, `packaging`, F19 stubs)
- #909/#910/#911 feature pathways need contract before implementation

## Decision

1. **Extend `packages/dissemination`** — do **not** create `packages/afs` or `packages/gateways` top-level packages (ADR-037 Option C). Optional future **logical submodule** `dissemination/afs/` for addressing/envelope helpers.

2. **Accept DisseminationGateway contract** (normative documentation):

   ```yaml
   DisseminationGateway:
     validate(message: DisseminationMessage) -> ValidationResult  # maps to preflight
     send(message: DisseminationMessage) -> DeliveryReceipt       # maps to send/publish/submit
     health() -> GatewayHealth                                    # new; connectivity-only
   ```

   **Implementation (Planned):** thin registry dispatching to existing sink functions by `gateway_kind` (`edis` | `wis2` | `amhs` | `swim` | `afs` | `db` | …).

3. **SinkAdapter remains** the drawer/backend dispatch Protocol; Gateway is the **epic #922 narrative facade** over the same adapters — not a second parallel interface in HTTP v1.

4. **DisseminationPlan** (documented; runtime deferred to #931 / #936):

   | Field group | Purpose |
   |-------------|---------|
   | `validityPolicy` | When message may be sent (valid-only, warn-ok, etc.) |
   | `transforms` | Exchange packaging refs (`exchange_profile`, COLLECT wrap) |
   | `retry` | Max attempts, backoff, idempotency key |
   | `audit` | Delivery status + timestamps — **no BYOC secrets** |

5. **DeliveryReceipt minimum fields:** `status` (`DELIVERED` | `FAILED` | `SKIPPED`), `gateway`, `detail`, `idempotency_key`, `attempt`, `completed_at`. Secrets never stored.

6. **GatewayHealth minimum fields:** `ok`, `gateway`, `connectivity_ok`, `detail` (operator-safe).

7. **EDIS / AFTN policy (#928):** Dissemination transport is **separate from IWXXM format**. Raw IWXXM XML is **not** AFTN/EDIS-safe as-is (binary/non-alphanumeric). EDIS path uses **ASCII AHL + TAC body** (`build_edis_message`). IWXXM-over-AFS requires explicit transform/bulletin policy — out of #927 spike code.

8. **WIS2box BYOC + DMZ (#929):** Topology: operator browser → backend API (allowlist) → egress to operator MQTT broker + dataset URL. Publisher emits **dataset PUT** then **WIS2 notification** (`build_wis2_notification`). No platform-hosted wis2box in prod (ADR-030 harness only).

9. **#909 / #910 / #936 unblocked** with contract shapes; feature implementation remains separate evolves.

## Gateway gap table (current → target)

| Gateway kind | validate today | send today | health | Plan/audit |
|--------------|----------------|------------|--------|------------|
| postgres/mysql/sqlserver/sqlite | `run_db_preflight` | backend send | Planned | Planned |
| wis2 | `wis2_preflight` | `wis2_publish` | Planned | Planned |
| edis | `edis_preflight` | EDIS SMTP | Planned | Planned |
| amhs/swim/afs | F19 staging | F19 staging | Planned | Planned |

## Alternatives considered

| # | Alternative | Why rejected |
|---|-------------|--------------|
| A | New `packages/afs` | ADR-037 — keep dissemination home |
| B | Replace SinkAdapter with Gateway only | Breaks shipped F16 drawer contract |
| C | Gateway doc + adapter retention | **Accepted** |
| D | Persist plan secrets | Violates ADR-021 |

## Consequences

### Positive

- Epic #922 Gateways layer has standing contract
- #928/#929/#930 absorbed into one ADR
- Clear EDIS alphanumeric / IWXXM separation for operators

### Negative / follow-ups

- `health()` and Plan runtime = new build cycles
- Live AFTN (#909) still distinct pathway — gateway contract does not imply live wire

## References

- [Context: dissemination-gateway-927](../context/dissemination-gateway-927.md)
- EV-927 session report `927-dissemination-gateway.md`
