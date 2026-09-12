# Build Plan Card — S053 / EV-044

> Updated: 2026-08-08

## Goal

Provision staging DOKS + Postgres under **Staging TAC-to-IWXXM**, point CD/DNS at it,
tear down shared-cluster staging ns.

## Out of scope

UI features; promote-policy changes; App Platform.

## Milestone batch (first 07 run)

1. T2.1 provision staging DOKS + assign project  
2. T2.2 provision staging PG + migrate schema  
3. T2.3 ingress + cert-manager + LB IP  
4. T2.4 apply staging overlay + secrets  
5. T3.1 set GH Env staging `KUBE_CONFIG`

## Later batch

T3.2 DNS → T4.1 smoke → T3.3 teardown → T4.2 promote check → T3.4 docs polish

## Acceptance mapping

| AC / TC | Tasks |
|---------|-------|
| TC-F30-008′ | T2.1, T2.2, T4.1 |
| TC-F30-009 | T3.2, T4.1 |
| TC-F30-010 | T3.1, T4.1 |
| TC-F30-012 | T4.2 |
| TC-F30-013 | T3.3 |

[Corpus: product §F30] [Corpus: adr/ADR-034] [Corpus: deploy]
