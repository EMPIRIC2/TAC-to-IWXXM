# BUG-2026-07-15-multiline-preview-span-offsets

| Field | Value |
|-------|-------|
| **Status** | resolved |
| **Feature** | F7 (soft-preview / Failed-TAC cue) |
| **Severity** | high |
| **Classification** | code bug |
| **Remediation path** | PR #716 / PRM-016 |
| **GitHub** | [PR #716 discussion](https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/716#discussion_r3588538655) |

## Error description

Soft-preview (`preview=true`) on multi-line `manual_text` merges per-entry `failed_spans` without shifting offsets into the full editor buffer. The workbench highlights the wrong line (e.g. failure on line 2 highlights line 1).

## Error logs

18-pr-review PRR-019 / Bugbot (local repro on tip `012c490`):

```
status 200
ok False
n_spans 1
{'start': 0, 'end': 37, 'code': 'PARSE_ERROR', ...}
  as buffer offsets: 'METAR KJFK ...'   # wrong — good line
  as line2-local: 'METAR XXXX ...'        # correct relative to entry
```

## Investigation

1. `split_manual_entries` splits buffer into one TAC per non-empty line.
2. `absorb_soft_preview` appends spans with entry-local `start`/`end`.
3. Frontend applies spans to the full `manual_text` document.
4. Root cause: missing per-entry base offset when merging spans / Layer 1–2 soft-fail copies.

## Repro test

| Path | Status |
|------|--------|
| `tests/bugs/test_bug_2026_07_15_multiline_preview_span_offsets.py` | red → green (PRM-016) |

## Interview record

AskQuestion UI unavailable; user invoked **19-address-pr-review** for PRR-019 blockers/advisories — treated as confirm of repro + root cause.

## Fix

Pass buffer offset into `absorb_soft_preview` / `record_preview_layer12_soft_fail` for manual entries.

## Prevention & countermeasures

Keep multi-line soft-preview regression test in `tests/bugs/`.
