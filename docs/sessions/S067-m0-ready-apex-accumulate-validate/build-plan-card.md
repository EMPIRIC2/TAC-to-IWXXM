# Build Plan Card — S067 / EV-057

> Updated: 2026-08-16 · Branch: `evolve/EV-057-m0-ready-apex-accumulate-validate`  
> Active: **07-build** — M1–M3 tasks complete in-repo; next **08-verify-build**

## Goal

Ship M0 Ready **#948** (apex → app), **#903** (accumulate ZIP ≤200), **#838** (validate-only)
to `stage` under Standard routing; promote later after re-approve.

## Done

- [x] M1 #948 sibling Ingress + deploy docs (live DNS/Ingress apply still operator-blocked)
- [x] M2 #903 accumulate + ZIP stem + UJ-057 spec
- [x] M3 #838 Validate IWXXM mode + UJ-058 spec; T3.1 no wire gap

## Next

08-verify-build → 09/10 → … Live #948 AC still needs Porkbun DNS + prod apply.
