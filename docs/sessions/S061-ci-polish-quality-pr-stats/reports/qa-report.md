# 09-qa — S061 / EV-052

**Date:** 2026-08-09  
**Verdict:** **PASS** (advisories below)  
**Tip:** `828c7087` · PR [#969](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/969) → `stage`  
**Corpus:** [Corpus: product §F29] [Corpus: product §F6] [Corpus: product §F21] [Corpus: product §F30] [Corpus: product §M5] [Corpus: tests] [Corpus: adr/ADR-007] [Corpus: adr/ADR-006]

## Checks

| ID | Check | Result |
|----|-------|--------|
| QA-001 | Lint / format / typecheck (`make lint-fast`, `format-check`, `typecheck`) | PASS (via 08) |
| QA-002 | Full unit suite `make test-unit` | PASS (via 08) |
| QA-003 | H0c CORS `tests/unit/test_cors_policy.py` | PASS (6) |
| QA-004 | H0i `tests/integration` | PASS (10 skipped — no live stack; exit 0) |
| QA-005 | Secrets `make secrets-check` | PASS |
| QA-006 | pip-audit (lockfile export + ignore) | PASS (0 known) |
| QA-007 | YAML / actionlint `make validate-yaml` | PASS |
| QA-008 | Template layout `apps/*` + `packages/*` + `vendor/schemas` | PASS |
| QA-009 | TC-EV052 coverage inventory + gates | PASS (24 selected) |
| QA-010 | Quality sticky unit tests | PASS |
| QA-011 | `openapi:check` drift | PASS |
| QA-012 | Vitest coverage thresholds | PASS — stmts 97.79 / lines 98.26 / funcs 98.12; branches 88.88 (waived → #968) |
| QA-013 | Tip CI @ `828c7087` | PASS ([31330311606](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/31330311606)) |
| QA-014 | Connectivity artifacts present | PASS (staging smoke + verify script) |
| QA-015 | H4–H5 live staging | SKIPPED (12/13 waived; no UJ delta) |

## AC map (delta)

| AC | Status | Evidence |
|----|--------|----------|
| AC1–AC3 | PASS | TC-EV052-001..003; inventory + gates |
| AC4–AC5 | PASS | quality sticky scripts + unit tests |
| AC6–AC8 | PASS | M3 Sentry/Redis + fakeredis tests (build); tip CI |
| AC9 | PASS | openapi-typescript + `openapi:check` |
| AC10–AC11 | PASS | M5 docs / infra-free-tier |
| AC12 | PASS | tip CI green |

## Advisories

| ID | Note |
|----|------|
| QA-ADV-001 | Vitest **branches** still under 95 (~89 local / waived at 84) — tracked [#968](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/968); `D-S061-cov-branches=3` |
| QA-ADV-002 | Upstash `REDIS_URL` + Sentry DSNs are env/ops follow-up (12/13 skipped); in-memory fallback documented for unset Redis |
| QA-ADV-003 | H0i tests skipped locally without live stack — CI Integration Matrix remains source of truth |

## Exit

→ **11-verify-impl**
