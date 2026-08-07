# Evolve report — EV-040

**Session:** S048-workbench-lint-ux  
**Completed (impl):** 2026-08-06 · **Deploy tip:** awaiting merge of PR #893  
**Deepen:** F7 / F10 / F15  
**PR:** [#893](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/893) OPEN @ `861c5457`

## Shipped

- Workbench: one lint console line per issue; keep TAC input after convert; **New TAC** + action strip above selects; prefs slimmed to name + extension; official WMO AHL + Collect examples.
- Catalog: `PROVENANCE_MAP` → ISSUE_CATALOG / packaged JSON / `/lint-issue-catalog` source attribution.
- Lint FPs: RVR tendency `U|D|N`; AHL heading skipped for visibility scans.

## Verification

- Local + pre-push CI green; FE coverage fix for fixture exclusion.
- Live H1–H3 + H0c/H4/H5 PASS on current DOKS (pre-merge baseline).
- Post-merge: re-run H4–H5 after FE/API tip rolls.

## Artifacts

- `docs/sessions/S048-workbench-lint-ux/`
- `docs/context/workbench-lint-ux.md`
- `docs/decisions/evolve-decisions.md` §EV-040
