# PR remediation report — PRM-012 (19-address-pr-review)

| Field | Value |
|-------|-------|
| **Linked review** | PRR-009…PRR-012 |
| **Scope** | Blockers then advisories (waived AskQuestion: D-S008-PR706-709-19) |
| **Date** | 2026-07-12 |

## Fixed

| ID | Finding | Commits |
|----|---------|---------|
| 🔴 #706 | convert-bulletin product/profile | `cb7a42f` → M5 `c5f91dc` → M6 `00062e4` → M7 `61eef2c` |
| 🟡 #708 | URL log + https + job_id dedup | M6 `ccc156e` → M7 `95d3e3c` |

## Tests

- `apps/backend/tests/unit/test_bug_2026_07_12_convert_bulletin_product_profile.py` — green
- `apps/worker/tests` — 10 passed

## Deferred / won't-fix

- `/api/v1/convert` full product HTTP wiring — M8 / F6.e (documented on #707)
- Persistent DB unique/upsert on `job_id` — in-process dedup sufficient for staging fixture

## Next

Re-run 18-pr-review optional; merge still requires explicit user approval (never auto-merge).
