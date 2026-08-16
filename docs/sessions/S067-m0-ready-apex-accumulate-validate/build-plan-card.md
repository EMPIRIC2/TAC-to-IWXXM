# Build Plan Card — S067 / EV-057

> Updated: 2026-08-16 · Branch: `evolve/EV-057-m0-ready-apex-accumulate-validate`  
> Active: **07-build** — **M2 #903** (accumulate + ZIP); next **M3 #838** after T2.5 green

## Goal

Ship M0 Ready **#948** (apex → app), **#903** (accumulate ZIP ≤200), **#838** (validate-only)
to `stage` under Standard routing; promote later after re-approve.

## In scope (M1 — done in-repo)

- [x] T1.1 DNS/TLS verify — **gap**: Porkbun parking → `l.ink` (not LB) — operator cutover pending
- [x] T1.2 Sibling Ingress `metar-frontend-apex` + permanent-redirect
- [x] T1.3–T1.4 deploy.md + ops curl checklist

## In scope (M2 — #903)

- [x] T2.1–T2.2 unit/helper tests (`outputFilename` + FileConverter accumulate)
- [x] T2.3–T2.4 FileConverter accumulate + ZIP stem naming
- [ ] T2.5 Playwright UJ-057 local smoke

## Next

Finish T2.5 → start **M3 #838** (validate-only). Live #948 AC still needs Porkbun DNS + prod Ingress apply.
