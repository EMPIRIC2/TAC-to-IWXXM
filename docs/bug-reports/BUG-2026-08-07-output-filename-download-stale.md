# BUG-2026-08-07 — Output filename change after convert ignored on Download

| Field | Value |
|-------|-------|
| **Status** | fixed (pending verify / PR) |
| **Feature** | F1 / F10 (workbench download UX); origin #664 |
| **Severity** | medium (wrong download name; XML correct) |
| **Classification** | domain / UI logic (not connectivity) |
| **GitHub** | https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/904 |
| **Session** | S051-output-filename-download-stale |
| **Remediation path** | local-first (deploy only after explicit approval) |
| **Branch** | `fix/output-filename-download-stale` |
| **PR** | https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/905 |

## Error description

After a successful manual-input conversion on the **production** operator workbench,
changing **Output filename (optional)** does not update the name used when downloading.
Download still uses the name captured at convert time. Live preview under the field
updates; download does not. XML content is correct. Likely present since custom
output filename (#664). [Corpus: product] F1/F10 · GitHub #904.

## Error logs

```
N/A — UI QoL; no server traceback. Symptom is downloaded filename vs current field.
```

## Investigation

| Time (UTC) | Note |
|------------|------|
| 2026-08-07 | Opened from `/14-hotfix` + #904; intent = new issue |
| 2026-08-07 | Session S051 opened; branch `fix/output-filename-download-stale` |
| 2026-08-07 | Confirmed in code: `handleDownloadSingle` / ZIP members use `file.originalName` only; ZIP *archive* name already uses live `outputFilename` |

### Hypotheses

1. **Primary:** On convert, `originalName` is set via `manualOutputName(outputFilename, …)` and never updated; download reads baked `originalName` → stale after rename. Preview uses live `sanitizeOutputFilename(outputFilename)`.
2. Upload/file-queue results incorrectly renamed — out of scope per #904 (manual only).

## Repro test

| Artifact | Path | Status |
|----------|------|--------|
| Vitest UI | `apps/frontend/src/test/bug-2026-08-07-output-filename-download-stale.test.tsx` | **RED** then **GREEN** (2026-08-07) |
| Pytest wiring | `tests/bugs/test_bug_2026_08_07_output_filename_download_stale.py` | **RED** then **GREEN** (2026-08-07) |

### Root cause (agreed)

Convert bakes `originalName` via `manualOutputName`; `handleDownloadSingle` / ZIP members
used only that baked name. Preview already used live `outputFilename`.

## Fix

1. Add `manualDownloadXmlName(base, index, total)` in `apps/frontend/src/utils/outputFilename.ts`.
2. Tag manual results with `liveOutputSlot: { index, total }` on convert.
3. `resolveDownloadXmlName` uses live `outputFilename` when `liveOutputSlot` is set; file
   uploads keep `originalName` → `.xml`.
4. Wire single Download + ZIP members through that resolver (archive name already live).

Files: `outputFilename.ts`, `outputFilename.test.ts`, `FileConverter.tsx`, bug Vitest +
pytest wiring, no card aria/label churn (download *attribute* is the contract).

## Interview record

- `hotfix_intent`: Report a new issue (option 1)
- AskQuestion tool unavailable; markdown options fallback
- Source link: GitHub #904
- Batch A: `symptom_type`=Wrong output; `where_seen`=Production (operator app); `when_started`=Since #664 (likely always)
- Batch B: `repro_frequency`=Every time; `repro_environment`=Both production and local
- Batch C: `user_severity`=Medium; `evidence_available`=Partial (#904); `already_tried`=Nothing
- `remediation_path`: Fix locally first — deploy only after approval
- `confirm_hotfix_plan`: Proceed
- Step 0.5: success=behavior; checks=full CI parity + main CI; monitoring=user watches prod
- `bug_repro_matches`: Yes — matches (Vitest: expected `second_name.xml`, got `first_name.xml`)
- `bug_root_cause`: Agree — proceed to fix
- `bug_verified`: Yes — verified

## Verification plan

| Item | Choice |
|------|--------|
| **Success criterion** | After convert, rename Output filename → Download (and ZIP members) use new sanitized name; XML unchanged |
| **Checks** | Full main CI parity (local) + `gh` CI on `main` after merge |
| **Monitoring** | User watches production after deploy |

### Verification log (local)

| Check | Result |
|-------|--------|
| Vitest bug repro + `outputFilename` + FileConverter | pass |
| Frontend `npm run lint` + full `npm test` (798 passed) | pass |
| `make test-bugs` (incl. this module) | 56 passed, 5 skipped |
| Ruff on new pytest | pass |
| PR branch / main CI (`gh`) | pending push/merge |

## Prevention & countermeasures

*(pending Phase 5)*

## Cursor rule

*(pending Phase 5.1)*
