# Build Plan Card — S067 / EV-057

> Updated: 2026-08-15 · Branch: `evolve/EV-057-m0-ready-apex-accumulate-validate`  
> Active: **07-build** — next **M1 / T1.1** (DNS/TLS verify for apex)

## Goal

Ship M0 Ready **#948** (apex → app), **#903** (accumulate ZIP ≤200), **#838** (validate-only)
to `stage` under Standard routing; promote later after re-approve.

## In scope (this batch — M1)

- [ ] T1.1 DNS/TLS verify for `tac-to-iwxxm.com` (+ `www`)
- [ ] T1.2 Sibling Ingress `metar-frontend-apex` + permanent-redirect
- [ ] T1.3–T1.4 deploy docs + ops smoke notes

## Out of scope

- #841 / #727 / #874; S056 ruleset-admin; auto-promote; new deps; batch disseminate

## Acceptance

- TC-EV057-948-*; UJ-OPS-002; `D-S067-948-impl` sibling Ingress

## Next

**07-build M1** (`D-S067-04-plan=1`; 05/06 skipped).
