# Routing plan — S063 / EV-054

**Status:** approved (`D-S063-route=1`)  
**Preset:** **Standard** — not Auto-Lean (new operator UI tab + fixture metrics + H4–H5)

| Stage | Include? | Mode | Status | Notes |
|-------|----------|------|--------|-------|
| 00-context | yes | session | **completed** | `D-S063-route=1` / `D-S063-ui-preview=2` |
| 16-evolve | yes | orchestrate | **in_progress** | 13-deploy-smoke in_progress awaiting `D-S063-13`; PR #977 MERGED @ `4fd51e39`; CI/CD 31453072506 success; H0c/H1/H3/H4/H5 + UJ-056 PASS; #836 On stage |
| 01-requirements | yes | delta | **completed** | `D-S063-01-ac=1`; UJ-056; TC-EV054; shell-tab + unified diff |
| 02-verify-plan | yes | delta | **completed** | Gate A PASS `D-S063-gateA=2`; api-contract + 05 |
| 03-plan-tooling | no | — | skipped | No new Cursor rule expected |
| 04-tech-plan | yes | delta | **completed** | `D-S063-04-plan=1` — M1→M5 / 15 tasks |
| 05-verify-tech | yes | delta | **completed** | `D-S063-05=1` Gate B PASS |
| 06-tech-tooling | no | — | skipped | No new deps expected |
| 07-build | yes | delta | **completed** | M1–M5; UJ-056 Playwright; `make generate-quality-metrics` |
| 08-verify-build | yes | delta | **completed** | Gate C local PASS @ `7a1d1845`; report `reports/verification-report.md`; tip CI via PR→stage |
| 09-qa | yes | delta | **completed** | pass_with_advisories; `reports/qa-report.md`; tip `be9e3b07` |
| 10-e2e | yes | delta | **completed** | UJ-056 PASS local; `reports/e2e-report.md`; H4–H5 deferred 12/13; tip `be9e3b07` |
| 11-verify-impl | yes | delta | **completed** | PASS `D-S063-11=1`; `D-S063-ui-preview-11=1`; `D-S063-uj056=1`; `reports/verify-impl.md` |
| 12-verify-deploy | yes | delta | **completed** | `D-S063-12=1` approve checklist; `reports/deploy-checklist.md`; merge #977 → stage then 13 |
| 13-deploy-smoke | yes | delta | **in_progress** | Smoke PASS pending `D-S063-13`; PR #977 MERGED @ `4fd51e39`; CI/CD 31453072506 SUCCESS (Deploy stage + Staging smoke); H0c/H1/H3/H4/H5 + live UJ-056 PASS; `reports/deploy-smoke.md`; env_role staging |

## Recommended ordered stages

`00 → 16 → 01 → 02 → 04 → 05 → 07 → 08 → 09 → 10 → 11 → 12 → 13`

## Skip rationale

- **Not Auto-Lean:** new UI surface + corpus metrics model + connectivity smoke — needs
  04/07/08/09/10/11 (+ deploy 12/13), not Lean’s thin verify path alone.
- **Skip 03/06:** no new Cursor rules expected; new FE diff dep (if any) inventoried in 04/05.
- **Include 05:** Gate A option 2 requires public metrics HTTP API — tech verify after 04.
- **Include 10 + 12 + 13:** #836 AC requires H4–H5 or Playwright; UI ships to stage.

## Board

- Project [#7](https://github.com/orgs/EMPIRIC2/projects/7) — #836 **On stage** (already set); #959 **Done**
- Ready queue = 2 (`#948`, `#958`) — below 3–5; refill later

## Locked intake

| ID | Decision |
|----|----------|
| D-S063-route | **1** — Standard as drafted; branch from `stage@f2926ac8` |
| D-S063-ui-preview | **2** — No local UI preview |
| D-S063-gateA | **2** — PASS; public `GET /api/v1/quality-metrics*` required; 05 re-enabled |
| D-S063-04-plan | **1** — Approve execution plan as drafted; no npm `diff`; single corpus blob |
| D-S063-09-10-continue | **1** — Continue → 11-verify-impl (user: Continue) |
| D-S063-ui-preview-11 | **1** — Non-deployed preview at http://127.0.0.1:18000/ |
| D-S063-uj056 | **1** — Approve UJ-056; waive live T3 until 12/13 |
| D-S063-11 | **1** — Approve F7.q; finish 11; toward 12 |
| D-S063-12-path | **1** — Open PR → stage, then 12-verify-deploy (user) |
| D-S063-12 | **1** — Approve checklist; merge #977 → stage then 13 (user: recommended) |
