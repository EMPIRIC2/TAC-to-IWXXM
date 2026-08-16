# 12-verify-deploy — S067 / EV-057

> Generated: 2026-08-16  
> **env_role**: staging (PR → `stage`); prod apex #948 already live  
> Corpus: [Corpus: deploy] [Corpus: adr/ADR-034] [Corpus: product §F30]

## Target

| Item | Value |
|------|--------|
| PR | https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/991 |
| Base | `stage` |
| Head | `evolve/EV-057-m0-ready-apex-accumulate-validate` @ `a730d7a3` |
| Staging cluster | `metar-iwxxm-staging` / `app.staging.tac-to-iwxxm.com` |
| Promote | **held** (`D-S067-promote=2b`) |

## Connectivity (ready for 13)

| Row | Status |
|-----|--------|
| H0c | PASS (08/09) |
| CORS origins | existing `app` / `app.staging` — no new convert CORS for #948 |
| `verify_connectivity.sh` | present |
| H4–H5 | **13** after staging CD |

## Notes

- #948 prod apply already done (not waiting on this PR for apex TLS).
- Staging short-host YAML in overlay; apply only if `staging.tac-to-iwxxm.com` A → `143.244.202.13`.
- Tip CI must be green on the PR before 13 (`D-S067-12-pr=1a`).
