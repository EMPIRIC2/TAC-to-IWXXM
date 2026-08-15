# Build Plan Card — S067 / EV-057

> Updated: 2026-08-15 · Branch: `evolve/EV-057-m0-ready-apex-accumulate-validate`  
> Active: **04-tech-plan** — EP draft pending `D-S067-04-plan`

## Goal

Ship M0 Ready **#948** (apex → app), **#903** (accumulate ZIP ≤200), **#838** (validate-only)
to `stage` under Standard routing; promote later after re-approve.

## In scope (next after EP approval)

### M1 — #948
- [ ] T1.1 DNS/TLS verify
- [ ] T1.2 Sibling Ingress `metar-frontend-apex` + permanent-redirect
- [ ] T1.3–T1.4 deploy docs + ops smoke notes

### M2 — #903
- [ ] T2.1–T2.5 accumulate + ZIP stem + cap≤200 + Playwright

### M3 — #838
- [ ] T3.1–T3.5 validate mode + API reuse spike + Playwright

## Out of scope

- #841 / #727 / #874; S056 ruleset-admin; auto-promote; new deps; batch disseminate

## Acceptance

- TC-EV057-948 / 903 / 838 as in test-plan
- Gate A locks: cap≤200; sibling FE Ingress redirect

## Next

Approve EP (`D-S067-04-plan`) → **05 skipped** → **07-build M1** (or 05 if user re-enables).
