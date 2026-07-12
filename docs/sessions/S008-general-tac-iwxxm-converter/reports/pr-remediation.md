# PR remediation report — PRM-012 / PRM-013

| Field | Value |
|-------|-------|
| **Linked reviews** | PRR-009…012 then PRR-013…016 |
| **Date** | 2026-07-12 |

## Fixed

| Finding | Commits |
|---------|---------|
| 🔴 convert-bulletin product/profile | #706 `cb7a42f` (+ cherry-picks) |
| 🟡 poller URL INFO log + https + job_id dedup | #708 `ccc156e` → #709 `95d3e3c` |
| 🟡 `source_url` tokens persisted to DB | #708 `5837b41` → #709 `a91f4cd` |

## Tests

- Bulletin bug repro + TC-F6-030 unit: green
- Worker tests: **11 passed**

## Deferred

- `/api/v1/convert` product HTTP — M8 / F6.e
- Durable DB unique/upsert on `job_id` — in-process dedup for staging

## Merge

**Not merged** — user merges manually in order #706 → #707 → #708 → #709.
