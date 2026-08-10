# T2.1 triage — uncovered branches after first EV-053 batch

**Date:** 2026-08-10  
**After:** 10 EV-053 FileConverter tests @ tip (pre-commit batch)

## Aggregate

| Metric | Pct | Gate |
|--------|-----|------|
| Statements | 95.73% | PASS |
| Lines | 96.37% | PASS |
| Functions | 97.16% | PASS |
| Branches | 86.97% | FAIL (need 95) |

## FileConverter

| Metric | Pct | AC5 |
|--------|-----|-----|
| Branches | 81.03% (440/543) | FAIL — 103 arms left |
| Statements | 89.66% | — |
| Functions | 92.75% | — |

## Math for aggregate branches ≥95

Need ~163 more branch hits globally. Covering **all** remaining FC arms (+103) only reaches ~92% aggregate — must also fill other files (notably `localWorkSessionStore`, `api.ts`, `DisseminationDrawer`, `MyMetarsPage`, …).

## Next fill targets (priority)

1. Remaining FileConverter (EndpointNotImplemented L721, mass ingest L847+, prefs L340+, logout false arm L311)
2. `utils/localWorkSessionStore.ts` (~18 miss)
3. `utils/api.ts` (~18 miss)
4. `DisseminationDrawer.tsx` (~14 miss)
5. `MyMetarsPage.tsx` / prefs / golden select

## Corpus

[Corpus: tests] [Corpus: decisions §EV-053]
