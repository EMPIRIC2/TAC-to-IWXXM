# 04-tech-plan report — S023 / EV-017 (draft pending approve)

**Date**: 2026-07-28  
**Status**: draft artifacts ready — awaiting plan approve (E17-25)

## Interview locks

| Batch | IDs | Result |
|-------|-----|--------|
| 1 Architecture | E17-12..15 | idb; reuse payload; sessionStorage migrate; slowapi |
| 2 Privacy/ops | E17-16..20 | GPC; localStorage prefs; single deploy; rate defaults; JSON export |
| 3 Milestones | E17-21..25 | 7 milestones; **delete packages/auth**; ADR-031; env rewrite; draft plan |

## Artifacts

| Path | Role |
|------|------|
| `docs/adr/ADR-031-public-app-indexeddb-history.md` | Proposed → Accept on approve |
| `docs/adr/ADR-020-*.md` | Marked Superseded |
| `docs/sessions/S023-public-app-privacy/reports/execution-plan.md` | M1–M7 / T1.1–T7.4 |
| `docs/env-contract.md` | Full F21 rewrite (C5 closed) |
| `docs/dependency-inventory.md` | idb + slowapi; auth package deleted |

## Next

AskQuestion: approve execution plan + ADR-031 → mark 04 completed → handoff **07-build** (05/06 skipped).
