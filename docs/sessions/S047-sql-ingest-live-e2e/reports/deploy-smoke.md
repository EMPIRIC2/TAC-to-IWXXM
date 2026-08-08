# Deploy smoke — S047 / EV-039 (13-deploy-smoke)

> Date: 2026-08-08 (resume) · prior CLI path 2026-08-06  
> Status: **PENDING SIGN-OFF** — evidence green; awaiting `D-S047-13`  
> PR: [#891](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/891) **MERGED** @ `fea30aba`  
> Product tip at merge: `fea30abacf14a8d6106637c99d7cce8d7652dabf`  
> `env_role`: **live = prod** (sole DOKS)  
> Resume: `D-S047-resume=2` (2026-08-08) — finish 13 properly then close  
> Corpus: [Corpus: tests] [Corpus: tech-spec] [Corpus: product §F16]  
> **OOS:** Production SQL containers (F16-R9); LIVE SQL remains local/CI opt-in

## Sequence

| Step | Result | Notes |
|------|--------|-------|
| 12 strategy sign-off | PASS | `D-S047-12=1` |
| Tip CI on PR branch | BLOCKED (historical) | GHA `major_outage` — zero runs on PR head |
| Local `make ci` + CLI DOKS | PASS (2026-08-06) | tag `20260806224839-7df9f8f` @ tip `7df9f8f5` (`D-S047-13-cli=1`) |
| Merge #891 | PASS | `fea30aba` @ 2026-08-06T23:01:57Z |
| Post-merge CI + DOKS Deploy | PASS | [CI/CD Pipeline 31130303373](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/31130303373) **success** (Deploy job green) |
| Resume 13 (2026-08-08) | PASS evidence | Re-run H0c/H1/H4–H5 against current live |
| H0c CORS unit | PASS | 6/6 |
| H1 live API | PASS | `make test-live-api` — 20 passed, 1 skipped |
| H4 live CORS (incl. mass) | PASS | 3/3 preflight |
| H5 FE `config.json` | PASS | `api.baseUrl=https://api.tac-to-iwxxm.com` |

## Live stack (2026-08-08 re-verify)

| Deploy | Image |
|--------|-------|
| `metar-api` | `ghcr.io/empiric2/tac-to-iwxxm/backend:20260808004030-3502af2` |
| `metar-frontend` | `ghcr.io/empiric2/tac-to-iwxxm/frontend:20260808004030-3502af2` |
| `metar-worker` | `ghcr.io/empiric2/tac-to-iwxxm/worker:20260808004030-3502af2` |

EV-039 product code is on `main` via #891; live tip `3502af27` includes later S050/S051 work (DB destinations UI hidden in S050 — restore [#898](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/898)). Historical CLI tag `20260806224839-7df9f8f` was the EV-039 rollout during the GHA outage.

## H0c / H4–H5 evidence (2026-08-08)

```
Live API awake: https://api.tac-to-iwxxm.com
== H0c: CORS policy unit tests == … 6 passed
== H4: Live CORS preflight == … 3 passed
  (convert + work_sessions PATCH + ingest/mass POST)
== H5: Frontend runtime config check ==
OK: https://app.tac-to-iwxxm.com/config.json api.baseUrl=https://api.tac-to-iwxxm.com
Connectivity verification complete.
```

## H1 evidence (2026-08-08)

```
make test-live-api — 20 passed, 1 skipped in 8.93s
  health / versions / schema / airport / auth / convert / validate / CORS / perf
```

## Advisories

1. `.env` line 55 parse noise (`to: command not found`) during Makefile `source .env` — pre-existing; did not block smokes.
2. Operator DB dissemination destinations were later hidden by S050/EV-042; EV-039 harness (Compose + Playwright LIVE SQL) remains in-repo for local/CI opt-in.
3. Original tip-CI hard-stop on PR #891 was resolved post-merge (run 31130303373); closeout docs were drafted on unpushed `docs/EV-039-closeout` @ `c65726dd` and never landed — this resume lands them.

## Rollback

Prior DOKS/GHCR tag via `doks_rollout_images.sh` / previous Deploy run; no DB migrations this cycle.

## Sign-Off

- [x] Deploy strategy verified (12)
- [x] #891 merged + post-merge DOKS CD green (31130303373)
- [x] Historical CLI deploy + H1/H3/H4/H5 (2026-08-06)
- [x] Resume re-verify H0c + H1 + H4–H5 (2026-08-08)
- [ ] User approves 13 complete (`D-S047-13`) — then close S047 / EV-039
