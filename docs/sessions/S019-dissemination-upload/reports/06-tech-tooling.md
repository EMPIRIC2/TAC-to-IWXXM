# 06-tech-tooling — S019 / EV-014

**Status**: completed  
**Date**: 2026-07-21  
**Mode**: delta (T0.1 — coverage paths + CI Compose hooks)  
**Decision**: D-S019-EV014-Q36A-06 (Assumed approve all; cloud AQ waived)

## Deliverables

| Item | Path / action |
|------|----------------|
| Dissemination coverage runner | `scripts/ci/run_dissemination_coverage.sh` (skip until T1.1/T1.2; then ≥95%) |
| wis2box Compose harness runner | `scripts/ci/run_wis2box_harness.sh` (skip until T3.3 `wis2box:` service) |
| Compose overlay stub | `docker-compose.wis2box.yml` (empty services; E14-04 not Render) |
| Makefile | `test-unit-dissemination`, `coverage-dissemination`, `lint-dissemination`, `compose-wis2box-*`; wired into `test-unit` / `ci` |
| CI matrix | `ci-cd.yml` package `dissemination` + integration step for wis2box harness hook |
| Cursor rule | `.cursor/rules/optional/dissemination-coverage-compose.mdc` |
| Hooks | `feature_drift.py` + `scope_check.py` — `packages/dissemination`, compose overlay |
| Test plan | CI matrix row notes dissemination + wis2box hook |

## Connectivity verification (stage 06)

| Check | Result |
|-------|--------|
| `tests/unit/test_cors_policy.py` | present |
| `tests/smoke/test_staging_connectivity.py` | present (`@pytest.mark.live`) |
| `scripts/deploy/verify_connectivity.sh` | executable |
| `docs/deploy.md` §Runbook H4–H5 | present |
| New deps | **none** (T0.1 tooling only; package deps land in T1.2) |

## Smoke

```text
make test-unit-dissemination
→ [dissemination-coverage] skip — packages/dissemination not scaffolded yet …

make compose-wis2box-harness
→ [wis2box-harness] skip — no wis2box service yet …

echo '{"filePath":".../packages/dissemination/src/allowlist.py"}' \
  | python3 .cursor/hooks/feature_drift.py
→ F16–F19 — Dissemination sinks / writer-contract / SSRF (ADR-030)
```

## Out of scope this stage

- Scaffolding `packages/dissemination` (T1.1/T1.2) — **07-build**
- Real wis2box image/service (T3.3) — **07-build** M3
- Regenerating core lint/format/typecheck hooks (already present from greenfield 06)

## Phase B gate

- [x] Execution plan audited (05-verify-tech)
- [x] Consistency check passed (05)
- [x] Technical tooling installed (T0.1)
- → Ready for Phase B checkpoint → **07-build** (M1 T1.1)
