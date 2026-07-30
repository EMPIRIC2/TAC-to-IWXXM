# BUG-2026-07-30 — SIGMET multi-line split → PARSE_ERROR

| Field | Value |
|-------|-------|
| **Status** | deployed — awaiting production_verified |
| **Feature** | F7 soft-preview / convert + F23 SIGMET quality (UI path) |
| **Severity** | high (WMO demo example fails in workbench) |
| **Classification** | code bug (product-aware entry split) |
| **Remediation path** | local-first — deploy only after explicit approval |
| **Session** | S028-sigmet-multiline-split |
| **Branch** | fix/BUG-2026-07-30-sigmet-multiline-split |
| **PR** | https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/796 **merged** `17c93bd` |

## Error description

Loading Examples catalog item **SIGMET WMO A6-1a-TS** (two-line TAC) shows:

- **Failed-TAC** `PARSE_ERROR` — `unable to parse SIGMET header`
- Soft-preview IWXXM with **nil geometry** and `intensityChange="NO_CHANGE"` (body not applied)
- Decode residuals for tokens that belong on the second line (`SHANLON FIR/UIR`, `S OF N54…`, `FL390`, …)

The same TAC converts cleanly via `tac2iwxxm.convert` when passed as **one** string. The failure is in the **HTTP convert / soft-preview** path that **line-splits** manual text.

## Error logs

User UI (production workbench, 2026-07-30):

```
Failed-TAC
PARSE_ERROR
unable to parse SIGMET header
Soft-preview only — not a Schematron-passed publish.

TAC:
YUDD SIGMET 2 VALID 101200/101600 YUSO-
YUDD SHANLON FIR/UIR OBSC TS FCST S OF N54 AND E OF W012 TOP FL390 MOV E 20KT WKN=
```

Live API probe (`POST /api/v1/convert`, product=SIGMET, profile=annex3):

```
successful=1 failed=1
issues: manual_input_2 — PARSE_ERROR: unable to parse SIGMET header
result0 tac_input: "YUDD SIGMET 2 VALID 101200/101600 YUSO-"   # line 1 only
preview failed_spans: [{start: 40, end: 122, code: PARSE_ERROR, message: unable to parse SIGMET header}]
preview XML: intensityChange="NO_CHANGE", geometry nilReason=missing (no posList)
```

Local library (same full buffer):

```
convert(..., product='SIGMET') → ok=True, issues=[], has posList
```

## Investigation

### Timeline

| When | Note |
|------|------|
| 2026-07-29 | F23 / S025 closed — library goldens + live smoke PASS (single-entry convert) |
| 2026-07-30 | User reports UI failure on catalog example `sigmet-A6-1a-TS` |
| 2026-07-30 | Live convert shows `manual_input_1` + `manual_input_2` split |

### Hypotheses

| # | Hypothesis | Result |
|---|------------|--------|
| H1 | SIGMET header regex broken for WMO A6-1a TAC | **Rejected** — full-buffer `convert()` succeeds |
| H2 | Wrong product sent (METAR/AIRMET) | **Partial** — console shows cross-product lint noise; live SIGMET still fails via split |
| H3 | `split_manual_entries` line-splits SIGMET; body line fails header parse | **Confirmed** — VAA/TCA already exempt; SIGMET/AIRMET still per-line |

### Root cause (provisional)

`apps/backend/src/api.py` `split_manual_entries` / `manual_entries_with_offsets` treat SIGMET/AIRMET like METAR (one entry per non-empty line). WMO SIGMET examples are **two lines** (`…YUSO-` then body `…=`). Line 1 soft-converts with empty body; line 2 raises `unable to parse SIGMET header`.

Mirror: `apps/frontend/src/utils/tacProduct.ts` `MULTILINE_TEMPLATE_PRODUCTS` = VAA/TCA only.

Related prior: BUG-2026-07-15 (span offsets for multi-line **METAR** batches) — different bug; same splitter.

## Repro test

| Path | Status |
|------|--------|
| `tests/bugs/test_bug_2026_07_30_sigmet_multiline_split.py` | **RED** 2026-07-30 → **GREEN** 2026-07-30 |

TDD iteration log:

1. Wrote split + soft-preview assertions for WMO A6-1a-TS — both fail as expected (line-split).
2. Extended multiline product set with SIGMET+AIRMET (BE+FE) — both green.

## Fix

- `apps/backend/src/api.py` — `_MULTILINE_TEMPLATE_PRODUCTS` includes `SIGMET`/`AIRMET` (with VAA/TCA).
- `apps/frontend/src/utils/tacProduct.ts` — mirror set + docs; `FileConverter` comment.
- Unit tests: backend helpers + FE `tacProduct.test.ts`.

## Interview record

| Step | Answer |
|------|--------|
| hotfix_intent | Report a new issue |
| symptom_type | Error / wrong soft-preview on WMO SIGMET example |
| where_seen | Production Render |
| when_started | Unknown / noticed after F23 (library OK; UI path broken) |
| repro_frequency | Every time |
| repro_environment | Production (live API confirmed); local library OK |
| user_severity | High — catalog demo fails |
| evidence_available | Yes — full UI paste + live API probe |
| already_tried | Nothing noted |
| remediation_path | Fix locally first — deploy only after I approve |
| confirm_hotfix_plan | Proceed |
| repro_test_matches_symptom | Yes |
| investigation_root_cause | Agree — line-split of SIGMET/AIRMET; proceed to fix |
| hotfix_commit_pr | Commit + push + open PR (#796) |
| hotfix_pr_merge | Approve merge — merged `17c93bd` |
| deploy_hotfix | Deploy via main CI Deploy (run 30566625055) — live soft-preview PASS (1 result, posList, WEAKEN) |

## Prevention & countermeasures

*(Phase 5)*

## Cursor rule

*(Phase 5.1)*
