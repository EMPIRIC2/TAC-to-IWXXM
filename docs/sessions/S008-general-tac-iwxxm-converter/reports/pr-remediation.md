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

---

# PR remediation report — PRM-015 (PR #711)

| Field | Value |
|-------|-------|
| **Linked review** | PRR-018 |
| **Date** | 2026-07-12 |
| **Decision** | D-S008-evolve-main-18-19 |
| **Head SHA** | `79af006` |
| **Counts** | fixed=2, deferred=0, wont_fix=0 |

## Fixed

| Finding | Commit | Note |
|---------|--------|------|
| 🔴 B1 | `ecdeac5` | validate TAC auto-convert forwards profile |
| 🟡 A1 | `79af006` | bound uploads + `MAX_BULLETIN_REPORTS=100` |

## Merge

Squash-merge to `main` authorized when CI is green (user explicit; D-S008-evolve-main-18-19).

