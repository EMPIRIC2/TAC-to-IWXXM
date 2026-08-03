# Evolve summary — EV-030 / S037 (quality residuals #831 / #829 / #820)

> Date: 2026-08-03  
> Status: **completed** (`D-S037-13=1`)  
> Branch: `evolve/EV-030-quality-residuals-831` → **merged** [#832](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/832) (`8bd111c`)  
> Features: **F29** (new) + deepen F23 / F12 / F2 / F13 / F9 / F26 / F27

## Outcomes

| Issue | Result |
|-------|--------|
| [#831](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/831) | F29 harness shipped — close on T4.5 |
| [#829](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/829) | **Closed** — TC SIGMET lint + A6-2-TC `wmoReference`; child [#835](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/835) for equality/`wmoPass` |
| [#820](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/820) | **Closed** — VAA/TCA structured + AHL decode; official peers `residuals == []` |

## Milestones

| M | Scope | Result |
|---|-------|--------|
| M0 | Design / spike | Design note + RuleCase spike |
| M1 | F29 harness + METAR/SPECI pilot | `tests/quality_matrices/`; PR smoke |
| M2 | #829 TC SIGMET | Lint pack + catalog unlock |
| M3 | #820 VAA/TCA decode | Structured fields + AHL; empty residuals |
| M4 | Verify / deploy | 08–13; H1–H5 PASS live |

## Pipeline stages

| Stage | Result |
|-------|--------|
| 00–04 | Delta REQUIREMENTS + Gate A/B PASS |
| 07 | M0–M4 build (27 tasks) |
| 08 | M1–M3 verification reports PASS |
| 09/10 | QA + E2E T0 PASS; H4–H5 → 13 |
| 11/12 | Approved `D-S037-11/12=1` |
| 13 | Deploy smoke PASS (hook 500 → Render API redeploy) |

## Publishable versions

| Package | Version | Notes |
|---------|---------|-------|
| `tac2iwxxm` | **0.2.4** | Patch (`D-S037-semver-tac2iwxxm=2`); no PyPI tag this cycle |
| `tac-validate` | 0.1.1 | No bump (`D-S037-semver-none`) |

## Residuals / follow-ups

- [#835](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/835) — A6-2-TC ADR-032 equality → `wmoPass`
- Render deploy-hook 500 when passing `imgURL` — ops follow-up (images + REST redeploy OK)
- Optional PyPI tag `tac2iwxxm-v0.2.4` in a later ops cycle

## Live

- API: https://metar-to-iwxxm-api.onrender.com  
- FE: https://metar-to-iwxxm-frontend-v4-web.onrender.com  
- Image tag: `20260803151459-8bd111c`
