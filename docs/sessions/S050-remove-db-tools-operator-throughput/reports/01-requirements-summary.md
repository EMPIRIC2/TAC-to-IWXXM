# 01-requirements summary — S050 / EV-042

**Date:** 2026-08-07  
**Mode:** delta  
**Corpus:** [Corpus: product §F7/F16–F19/F33], [Corpus: journeys], [Corpus: api],
[Corpus: tests], [Corpus: decisions §EV-042]

## Locked intake

| ID | Decision |
|----|----------|
| R1 | Caps ≤200 files / ≤5 MiB each / ≤50 MiB total unzipped |
| R2 | **Hide all** dissemination destinations (DB + WIS2/EDIS/AMHS/SWIM/AFS) |
| R3 | Auth for folder/zip mass path; guests keep small multi-file |
| R4 | Batch disseminate **N/A**; batch convert/validate only |

## Standing doc deltas written

- `feature-list.md` — F33 ACs; F7/F16–F19 deepen
- `user-journeys.md` — UJ-051..053; UJ-027–030 operator UI deferred note
- `test-plan.md` — UJ↔TC map + H4–H5
- `api-contract.md` — mass ingest planned route + dissemination UI-hide note
- `decisions/evolve-decisions.md` §EV-042

## Proposed ACs (confirm)

| AC | Criterion |
|----|-----------|
| AC1 | No operator Dissemination destinations / Convert&Send sink path |
| AC2 | Backend `/dissemination/*` retained for harness |
| AC3 | Queue + keyboard + batch convert/validate |
| AC4 | F33 auth + caps 200/5MiB/50MiB + sniff/zip-bomb + progress |
| AC5 | Guest small multi-file unchanged; mass path 401/403 without JWT |
| AC6 | UJ-051..053 + TC-F33-* + TC-EV042-* + H4–H5 |
| AC7 | #898 restore track covers **all** destinations |

## Next

User confirms ACs → complete 01 → 02-verify-plan Gate A.
