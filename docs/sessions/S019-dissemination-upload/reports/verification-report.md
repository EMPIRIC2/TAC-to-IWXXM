# Verification Report

> Generated: 2026-07-21  
> Scope: S019 / EV-014 — **T6.4** `08-verify-build` (M6 after T6.3)  
> Branch: `cursor/s019-t64-verify-build-7820` (from `cursor/s019-t63-dissemination-e2e-8b16` @ `abf2580`)  
> Mode: evolve / delta (F16–F19)

## Summary

| Check | Status | Findings | Auto-Fixed | Tool |
|-------|--------|----------|------------|------|
| Lint | PASS | 0 | — | ruff + eslint |
| Format | PASS | 1 Prettier | 1 (UJ-027–030 e2e) | ruff format + prettier |
| Typecheck | PASS | 0 | — | basedpyright + tsc |
| Unit tests | PASS | see below | — | pytest / vitest |
| H0c CORS | PASS | 6/6 | — | `tests/unit/test_cors_policy.py` |
| Dissemination integration | PASS | 5 passed / 10 skipped (no Docker engines) | — | `make test-integration-dissemination` |
| Backend integration stack | SKIPPED (local) | needs `DATABASE_URL` secrets | — | CI green on #769 |
| Security (deps) | PASS | 0 known CVEs (ignore PYSEC-2026-1325 / QA-001) | — | pip-audit lockfile export |
| Secrets scan | PASS | no private keys / sk_live | — | ripgrep |
| Badge audit | PASS | gifts path removed (F6 cutover) | 1 | `.github/scripts/badge_audit.py` |
| Connectivity artifacts | PASS | CORS + smoke present; `scripts/deploy/verify_connectivity.sh` | — | connectivity-gates §08 |
| Performance | SKIPPED | no EV-014 perf thresholds | — | — |
| Data | SKIPPED | no staged weights | — | — |

**Overall: PASS**

## Unit suite counts (local)

| Package | Result |
|---------|--------|
| workspace / shared | PASS (prior run) |
| backend | **1243 passed** (needs `SUPABASE_URL` + `sb_publishable_*` key) |
| auth | 228 passed, 31 skipped |
| frontend | PASS (vitest + coverage) |
| tac2iwxxm | 170 passed, 10 skipped |
| iwxxm-validate | **76 passed**, 1 skipped — **95.96%** cov (requires `maturin develop`) |
| tac-validate | 296 passed |
| dissemination | 124 passed, 15 deselected |
| worker | 11 passed |
| bugs | 43 passed, 1 skipped |

## Auto-fixes (T6.4)

1. **Prettier** — `apps/e2e/uj027-030-dissemination-drawer.e2e.spec.ts` (T6.3 leftover).
2. **badge_audit** — drop `packages/gifts/README.md` (package removed at F6 cutover; `make ci` otherwise fails).

## Notes / environment

- Local backend unit tests require modern publishable key shape (`sb_publishable_*`); CI supplies secrets.
- `iwxxm-validate` coverage gate needs Rust extension built (`maturin develop`) — same as CI matrix.
- Full `tests/integration` + H0i stack not re-run locally (no `.env` / `DATABASE_URL`); **Test (integration)** green on PR [#769](https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/769).
- Upstream open PRs: #768 (M5), #769 (M5+T6.1+T6.2), #770 (T6.3) — this branch stacks on #770 tip.

## Connectivity (stage 08)

| Artifact | Present |
|----------|---------|
| `configure_cors` (backend) | yes |
| `tests/unit/test_cors_policy.py` | yes (6 passed) |
| `tests/smoke/test_staging_connectivity.py` | yes |
| `scripts/deploy/verify_connectivity.sh` | yes |

## Next

**T6.5** — 12-verify-deploy checklist (allowlist + Compose harness) per E14-08.
