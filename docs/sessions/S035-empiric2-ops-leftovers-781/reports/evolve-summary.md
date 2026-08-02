# Evolve summary — S035 / EV-028

**Status**: completed  
**PR**: [#824](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/824) merged @ `70312dd`  
**Issue**: [#781](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/781) closed  
**Report**: `docs/evolve-report-EV-028.md`

## Acceptance

1. Codecov purged from CI/docs/secrets — PASS (T0.*, T3.1/T3.2)
2. Trusted Publishers → EMPIRIC2 — PASS (T2.2/T2.3)
3. OIDC `0.1.1` ×3 + `iwxxm-validate==0.1.2` + install smoke — PASS (T3.3/T3.3b/T3.4)
4. Consumer landings without required ADR/Fn/E10 — PASS (T1.*, T3.2)
5. #781 closable — PASS (merged #824)

## Stage outcomes

| Stage | Outcome |
|-------|---------|
| 07-build | M0–M3 complete including T3.5 merge |
| 08-verify-build | T3.1 PASS |
| 10-e2e | T3.2 packaging smoke PASS |
| 13-deploy-smoke | PASS via tag publish + clean-venv smoke |
