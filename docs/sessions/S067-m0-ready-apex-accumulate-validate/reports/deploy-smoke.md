# Deploy smoke — S067 / EV-057 (13-deploy-smoke)

> Date: 2026-08-16  
> Status: **COMPLETE** — `D-S067-13=1a` (promote deferred)  
> PR pack: [#991](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/991) + follow-up [#992](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/992) **MERGED** → `stage`  
> Stage tip: `3af364fb` (aria-label fix) · prior pack `d7022f1f`  
> `env_role`: **staging** (`api|app.staging.tac-to-iwxxm.com`; cluster `metar-iwxxm-staging`)  
> CD: [31966102210](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/31966102210) (#991) + [31967444673](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/31967444673) (#992) — Deploy + Staging smoke **success**  
> Decisions: `D-S067-13-start/scope/depth=1a`; `D-S067-13-uj058=1a`  
> Corpus: [Corpus: tests] [Corpus: deploy] [Corpus: adr/ADR-034] [Corpus: product §F7] [Corpus: product §F30]  
> Board: #948 / #903 / #838 → **On stage** (promote held)

## Sequence

| Step | Result | Notes |
|------|--------|-------|
| 12 strategy sign-off | PASS | `D-S067-12-*` recommended |
| Merge #991 → `stage` | PASS | merge `d7022f1f` |
| Stage CI + Deploy (stage) | PASS | run 31966102210 |
| Staging smoke (CI) | PASS | health + FE + CORS |
| H0c CORS unit | PASS | 6/6 |
| H1 live API (staging) | PASS | 13 passed, 8 skipped |
| H2 / Staging health | PASS | API + FE + `config.json` |
| H3 convert journey | PASS | form `POST /api/v1/convert` → IWXXM |
| H4 live CORS | PASS | 3/3 |
| H5 FE `config.json` | PASS | staging API baseUrl |
| Live UJ-057 | PASS | accumulate ZIP |
| Live UJ-058 (first) | FAIL | stale CodeMirror aria-label |
| Fix #992 TacEditor sync | PASS | `setAttribute('aria-label', …)` on mode change |
| Merge #992 → `stage` | PASS | merge `3af364fb`; CD 31967444673 |
| Live UJ-057 re-check | PASS | 1/1 |
| Live UJ-058 re-check | PASS | 2/2 (~5.6s) |

## H4–H5 evidence

```
Live API awake: https://api.staging.tac-to-iwxxm.com
== H0c: CORS policy unit tests == … 6 passed
== H4: Live CORS preflight == … 3 passed
== H5: Frontend runtime config check ==
OK: https://app.staging.tac-to-iwxxm.com/config.json api.baseUrl=https://api.staging.tac-to-iwxxm.com
Connectivity verification complete.
```

## Live Playwright (post-#992)

```
[chromium] uj057 … Clear empties — passed
[chromium] uj058 … structured fail — passed
[chromium] uj058 … report panel — passed
3 passed (5.6s)
```

## Rollback

Prior staging GHCR/`stage-latest` predecessor via Deploy job; no DB migrations.

## Promote (deferred)

`D-S067-promote=2b` — promote `stage`→`main` only after separate re-approve. **Not** opened this turn.

## Sign-Off

- [x] Deploy strategy verified (12)
- [x] #991 + #992 merged + Staging Deploy + Staging smoke green
- [x] H0c + H1–H5 on staging
- [x] Live UJ-057 + UJ-058 PASS
- [x] User approves 13 complete (`D-S067-13=1a`) — promote still deferred (`D-S067-promote=2b`)
