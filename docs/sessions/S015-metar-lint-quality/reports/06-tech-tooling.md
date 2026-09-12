# 06-tech-tooling — S015 / EV-011

**Status**: completed  
**Date**: 2026-07-19  
**Mode**: delta (T6.0 / E11-30 / E11-32)  
**Decision**: D-S015-EV011-06-start (user option 1)

## Deliverables

| Item | Path / action |
|------|----------------|
| Catalog regen | `scripts/tac-validate/regen_issue_catalog.py` + `make catalog-regen` / `catalog-check` |
| Stub catalog | `docs/domain/rules/ISSUE_CATALOG.md` + `.json` (empty until T1.2) |
| Literal check (warn) | `scripts/ci/check_issue_registry_literals.py` (`ISSUE_REGISTRY_GUARD_STRICT` for T2.2a) |
| Pre-commit | `.pre-commit-config.yaml` — `issue-registry-guard-warn` |
| Cursor hook | remains advisory exit 0 (docstring updated) |
| Fixture README | F15 layout + HARD R1–R8 + catalog tooling notes |
| Registry rule | warn→error timeline documented |

## Connectivity verification (stage 06)

| Check | Result |
|-------|--------|
| `tests/unit/test_cors_policy.py` | present |
| `scripts/deploy/verify_connectivity.sh` | executable |
| No new CORS/`VITE_*` knobs | per E11-26 |
| New deps | none |

## Out of scope this stage

- Registry module (T1.2) and drift pytest (T1.4) — 07-build M1
- Escalating guard to error — T2.2a

## Next

Phase B checkpoint → **B→C gate** → **07-build** (T1.1).
