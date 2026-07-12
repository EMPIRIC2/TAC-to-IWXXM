# PR remediation — S008

## PRM-008 (PR #700) — brief

**Status:** completed 2026-07-12  
**PR:** https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/700 (`feat/S008-M1-scaffold` → evolve)  
**Summary:** 1 advisory fixed (`vendor_manifest` name-based HTTP/GitHub dispatch); head `789ea0b`; merged `369f028` under D-S008-PR700-19 anti-merge override.

---

# PR remediation — PRM-009 (PR #701)

**Skill:** 19-address-pr-review  
**PR:** https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/701  
**Branch:** `feat/S008-M2-validate` → `evolve/S008-general-tac-iwxxm-converter`  
**Date:** 2026-07-12  
**Status:** completed  
**Scope:** `blockers_then_advisories`  
**Head SHA:** `6ddec3a19969aa922e6d139abda932425d38fd4c`  
**CI:** green

## Scope

User waived AskQuestion gates and requested remediate → commit → push → merge (anti-merge override like D-S008-PR700-19 → **D-S008-PR701-19**).

| Severity | Count |
|----------|-------|
| Blockers (bug_risk) | 2 fixed |
| Advisories | 2 fixed, 1 wont_fix |

**Counts:** fixed 4, wont_fix 1, deferred 0

## Findings

| ID | Finding | Severity | Status | Commit |
|----|---------|----------|--------|--------|
| F-001 | `files` not declared with `File()` on `/lint-tac` | bug_risk | fixed | `f39560d` |
| F-002 | multipart vs urlencoded doc/guard mismatch → multipart-only (Q8=A) | advisory | fixed | `f39560d` |
| F-003 | `LintReport.fixes = []` shared mutable default | bug_risk | fixed | `f39560d` |
| F-004 | Extend `/validate` test for `profile` / `package_*` + OpenAPI `ValidateResponse` | advisory | fixed | `6ddec3a` |
| F-005 | Inline `vendor_manifest` helpers / `source_url` dispatch | advisory | **wont_fix** | — (keeps PRM-008 name-based HTTP dispatch) |

## CI / merge

- Sourcery review: pass  
- Merge: `8a0db0c` (user override of skill anti-merge; D-S008-PR701-19)


---

# PR remediation — PRM-010 (PR #704)

**Status:** completed 2026-07-12
**PR:** https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/704
**Head:** `dcd4791` → merge `2d9fb24`
**Scope:** blockers_then_advisories (D-S008-PR704-19)

| Finding | Severity | Status | Commit |
|---------|----------|--------|--------|
| TAC search after AHL only | bug_risk | fixed | `3175787` |
| UploadFile empty-file test | advisory | fixed | `4055b07` |
| Pydantic response models | advisory | fixed | `dcd4791` |
| AHL dialect abstraction | advisory | wont_fix (M5) | — |
