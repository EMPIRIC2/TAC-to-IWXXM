# Deploy readiness — S024 / EV-018 (#785)

> Status: **PASS** — FE live; H4–H5 + H6′ 7/7  
> Tip merged: `2f552b9` on `main`  
> PR: [#791](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/791) **merged**  
> FE deploy: `dep-d9kkjj5bedkc73au0aeg` live  
> Decision: **D-S024-13-deploy-A**  
> Report: `reports/deploy-smoke.md`

## Preconditions

| Item | Status |
|------|--------|
| 08-verify-build | PASS |
| 10-e2e UJ-027–030 | PASS (7/7 local T0) |
| Backend / allowlist / CORS | unchanged |
| FE code | multi-select + queue + progress |

## Deploy path (after approval)

1. `git push -u origin HEAD`
2. Open PR → `main` (`[EV-018] F16 multi-file dissemination selection`)
3. Merge (user) → Render FE rebuild
4. `make test-live-connectivity` (H4–H5) + H6′ UJ-027–030 vs live FE (mocked or live BYOC per plan)

## Not required

- API image rebuild
- `DISSEMINATION_EGRESS_ALLOWLIST` change
- Supabase env changes
