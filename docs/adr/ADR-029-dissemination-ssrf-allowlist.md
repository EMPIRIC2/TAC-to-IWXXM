# ADR-029: Dissemination egress SSRF controls and required allowlist

> **Status**: Proposed (S019 / EV-014 Phase 0 → 01)  
> **Date**: 2026-07-21  
> **Deciders**: User (EV-014 Q11=A+B)  
> **Stage**: 01-requirements  
> **Related**: ADR-021 (amended for destination paste); feature-list F16–F19; #729  
> **Session**: S019-dissemination-upload / EV-014  
> **Decision id**: D-S019-EV014-Q11

## Context

EV-014 lets any authenticated user paste **one-shot** destination credentials (DB URI, WIS2,
EDIS SMTP, AMHS params) for backend-mediated dissemination. That creates SSRF and credential
leakage risk if the API opens arbitrary sockets.

## Decision

1. **Backend-only egress** — browser never opens DB/MQTT/SMTP sockets to user destinations.
2. **Memory-only credentials** — hold pasted secrets for the request (or short-lived handle);
   never persist to F5 sessions, logs, or config.
3. **Default deny** private/link-local/metadata ranges (IPv4 + IPv6) and common cloud metadata
   endpoints; **DNS rebinding guard** (resolve → validate IPs → connect only to those IPs).
4. **TLS preferred** for DB/MQTT/HTTP; timeouts and payload size limits on all egress.
5. **Secret redaction** in logs and error bodies; **rate limit** preflight/send per user.
6. **Required** deploy env `DISSEMINATION_EGRESS_ALLOWLIST` (host/CIDR list). **Empty allowlist
   ⇒ no user-URI / user-host egress** in that environment (fail closed). Staging may set an
   explicit list including the project wis2box harness.

## Alternatives Considered

| # | Alternative | Why rejected |
|---|-------------|--------------|
| 1 | Trust all authenticated users (any host) | Unacceptable SSRF surface |
| 2 | Optional allowlist only | User asked for max guard (Q11=A+B) |
| 3 | Browser-direct DB connections | Rejected (Q5=A); secrets + CORS/SQL in browser |

## Consequences

- Config/env-contract must document `DISSEMINATION_EGRESS_ALLOWLIST`.
- Preflight/send APIs return structured errors when allowlist/SSRF checks fail.
- Live BYOC demos require operator to populate allowlist for their destination hosts.
