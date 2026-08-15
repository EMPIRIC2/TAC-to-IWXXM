# Build Plan Card — S067 / EV-057

> Updated: 2026-08-15 · Branch: `evolve/EV-057-m0-ready-apex-accumulate-validate`  
> Active: **07-build** — **M1 repo complete**; next DNS cutover AskQuestion → **M2**

## Goal

Ship M0 Ready **#948** (apex → app), **#903** (accumulate ZIP ≤200), **#838** (validate-only)
to `stage` under Standard routing; promote later after re-approve.

## In scope (M1 — done in-repo)

- [x] T1.1 DNS/TLS verify — **gap**: Porkbun parking → `l.ink` (not LB)
- [x] T1.2 Sibling Ingress `metar-frontend-apex` + permanent-redirect
- [x] T1.3–T1.4 deploy.md + ops curl checklist

## Blocked for live #948 AC

DNS A/`www` must move to `168.144.12.70` before redirect works in production.

## Next

AskQuestion DNS cutover timing → then **M2 #903** (or pause).
