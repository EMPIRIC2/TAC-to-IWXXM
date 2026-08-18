# UAT report

- **Script:** `docs/sessions/S070-converter-operator-bugs/uat-script.md` §UAT-003
- **Cycle:** EV-060 / S070 — T4.2 (#1006) [Corpus: product §F31] [Corpus: journeys] [Corpus: tests §TC-EV060-1006-004]
- **Environment:** local non-deployed — frontend `http://localhost:18000`, API `http://localhost:18001` (not staging or production)
- **Mode:** uat Build (`D-S070-resume-m4`)
- **Overall:** **ACCEPTED** — product-owner sign-off 2026-08-18 (`D-S070-uat003=all-pass`)

## Results

| Scenario | Journey | Environment | Pass/fail | Notes | Signer |
|----------|---------|-------------|-----------|-------|--------|
| UAT-003 Register | UJ-003 | local :18000 | **pass** | Test account; no production PII | product owner |
| UAT-003 Login + reload persist | UJ-046 | local :18000 | **pass** | Reload still signed in | product owner |
| UAT-003 Logout | UJ-003 / F21 | local :18000 | **pass** | Sign out this device; Sign in returns | product owner |
| UAT-003 Guest convert | UJ-001 / F21 | local :18000 | **pass** | Convert without JWT | product owner |
| UAT-059 AHL | UJ-059 | local :18000 | **pass** | T2 + 11 journey approve | product owner |
| UAT-060 IWXXM product | UJ-060 | local :18000 | **pass** | T2 + 11 journey approve | product owner |
| UAT-061 Profile | UJ-061 | local :18000 | **pass** | T2 + 11 journey approve | product owner |
| UAT-062 Bulletin fields | UJ-062 | local :18000 | **pass** | T2 + 11 journey approve | product owner |
| UAT-063 log_level | UJ-063 | local T0+T2 | **pass** | T0 DEBUG>ERROR + redact; 11 checks-ok | product owner |
| UAT-059..063 | UJ-059..063 | local :18000 | **pass** | Accepted at 11-verify-impl (`D-S070-e2`) | product owner |

## Facilitated steps (operator)

1. Opened `http://localhost:18000` (guest converter; Sign in visible).
2. Register with test email + password + terms.
3. Login with verified test account.
4. Reload — still signed in.
5. Sign out from this device only — Sign in returned.
6. Guest convert of sample METAR — results without JWT.

Playwright covers TC-EV060-1006-001..003. This report is the human sign-off for TC-EV060-1006-004.
