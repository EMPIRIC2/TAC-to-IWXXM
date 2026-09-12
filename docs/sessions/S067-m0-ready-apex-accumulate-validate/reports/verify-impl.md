# Verify implementation — 11-verify-impl (S067 / EV-057)

> Generated: 2026-08-16  
> Tip: `ffdd1961` (local, unpushed)  
> Corpus: [Corpus: product §F7] [Corpus: product §F30] [Corpus: tests] [Corpus: deploy]

## Inputs

| Source | Result |
|--------|--------|
| 08-verify-build | PASS (`verification-report.md`) |
| 09-qa | PASS delta (`qa-report.md`) |
| 10-e2e | PASS + T2 Playwright waive `D-S067-10-pw=1a` (`e2e-report.md`) |
| Live #948 | UJ-OPS-002 PASS on prod (`t1.2-apex-live-apply.md`) |

## Per-Fn / issue AC

### #948 / F30 — apex → app

| AC | Status | Evidence |
|----|--------|----------|
| HTTPS apex → `https://app.tac-to-iwxxm.com` 301 | **met** | live curl |
| Path + query preserved | **met** | `/foo?bar=1` |
| www included | **met** | TLS SAN + 301 |
| TLS on apex (+ www) | **met** | `metar-frontend-apex-tls` Ready |
| Deploy docs | **met** | `docs/deploy.md` redirect pod |

H4–H5 N/A (ops journey). Staging short-host YAML in-repo, **not applied**.

### #903 / F7.r — accumulate ZIP

| AC | Status | Evidence |
|----|--------|----------|
| N≥2 accumulate | **met** (T0) | vitest FileConverter EV-057 |
| Download all ZIP | **met** (T0) | same |
| Stem / custom name | **met** (T0) | `outputFilename.test.ts` |
| Clear + cap ≤200 | **met** (T0) | same |
| UJ-057 Playwright | **waived T2** | `D-S067-10-pw=1a`; H4–H5 at 13 |

### #838 / F7.s — validate existing IWXXM

| AC | Status | Evidence |
|----|--------|----------|
| Paste / upload validate-only | **met** (T0) | vitest EV-057 #838 |
| Structured fail | **met** (T0) | same |
| UJ-058 Playwright | **waived T2** | `D-S067-10-pw=1a`; H4–H5 at 13 |

## UI preview

Remind at 11 (`D-S067-ui-preview=3a`). Offered this turn. **Declined** — `D-S067-11-preview=2a` (reports/tests only).

## Feature approval

**Approved** `D-S067-11-ac=1a` — all three (#948 / #903 / #838). Next: **12-verify-deploy**.

## Connectivity waiver

Staging H4–H5 for UJ-057/058 deferred to 13 (`D-S067-10-pw=1a` + Standard 12/13).
Do not treat T0 as production browser proof.
