# ADR-018: F8 Render Worker + Template `static+api+worker` (Amends ADR-015)

> **Status**: Accepted  
> **Date**: 2026-07-12  
> **Deciders**: User (S008 04-tech-plan Q15–Q20)  
> **Stage**: 04-tech-plan  
> **Amends**: [ADR-015](ADR-015-validate-packages-bulletin-api-f7-f8.md) §Decision (7) “F8 not built this cycle”  
> **Related**: realtime-tac-ingest.md R7–R15; template-conformance  
> **Session**: S008-general-tac-iwxxm-converter

## Context

ADR-015 deferred F8 (near-RT ingest worker) and kept template `static+api`. S008 04-tech-plan
promotes **F8 into this build** and adds a new Render deployable. Convert/lint/validate HTTP
remain on the existing API (thin wrappers); no dedicated converter microservice.

## Decision

1. **Promote F8** to build-this-cycle (Q15c=B). Amend feature-list status accordingly.
2. **New deployable**: `apps/worker/` — Render **Background Worker** (Q19=A).
3. **Template**: `static+api` → **`static+api+worker`** (document in workflow-state + rules).
4. **Ingest v1**: HTTPS / object-prefix **poller** (Q16=A). AMHS/SWIM still out of scope.
5. **Store**: On Schematron pass, persist IWXXM + metadata to **Supabase** (Q17=A).
6. **Quarantine**: **Separate** quarantine table/bucket on lint/convert/Schematron fail (Q18=B);
   no publish.
7. **Auth for writers**: Worker uses Supabase **service role JWT** (Q20=C). Machine-ingest
   public auth and push sinks remain postponed.
8. **Non-goals unchanged**: F7 UI; push sinks; AMHS/SWIM; dedicated converter API (Q15b=B).

## Alternatives Considered

| # | Alternative | Why rejected |
|---|-------------|--------------|
| 1 | Dedicated converter API service | Duplicates existing API; rejected recommendation |
| 2 | Worker process in backend image only | User chose `apps/worker/` |
| 3 | Keep F8 Planned / no deployable | User Q15 + Q15c=B |
| 4 | Log-only quarantine | Incompatible with durable store goals |

## Consequences

- New Render service + secrets matrix rows; deploy.md topology update.
- Supabase migrations for ingest results + quarantine.
- plan-adherence / template-conformance must list `apps/worker/`.
- F6 non-goal “no new Render deployable” now means **no converter microservice**; F8 worker is
  the explicit exception (aligned with realtime brief R7).

## References

- D-S008-04-q15b, D-S008-04-q16q20
- I-S008-04-new-service (resolved)
- S008 execution-plan Phase 5–6
