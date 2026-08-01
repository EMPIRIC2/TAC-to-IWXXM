# 04-tech-plan — EV-028 / S035

**Date**: 2026-08-01  
**Mode**: delta / general ops  
**Connectivity**: N/A (no browser UI)

## Toolchain baseline (unchanged)

- Python packages + hatch/maturin via existing `pypi-publish.yml`
- GitHub Actions OIDC; no new deps
- Codecov removal only — coverage XML/HTML artifacts remain in CI

## Decisions (defaults — confirm at Gate B)

| ID | Topic | Recommendation |
|----|-------|----------------|
| E28-T1 | Task order | M0 Codecov → M1 READMEs → M2 bump + publisher → M3 verify/tags |
| E28-T2 | Tag timing | Merge PR to `main` first, then push three version tags on `main` tip (avoids publishing from unmerged branch) |
| E28-T3 | New deps | None |
| E28-T4 | Trusted Publisher | User/operator configures on pypi.org before T3.3; agent supplies exact field table + verifies Environment `pypi` |

## Artifacts

- `reports/execution-plan.md` — M0–M3 draft
- UJ-023 amended (E28-S2.1 / 9a)

## Gate B

Pending user approve execution plan → **07-build** @ T0.1.
