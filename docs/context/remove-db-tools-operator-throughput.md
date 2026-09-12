# Context — remove DB tools + operator throughput

**Session:** S050-remove-db-tools-operator-throughput  
**Cycle:** EV-042  
**Issues:** [#897](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/897), [#898](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/898)  
**Corpus:** [Corpus: product §F16], [Corpus: product §F7], [Corpus: system-spec],
[Corpus: adr/ADR-021], [Corpus: adr/ADR-029], [Corpus: adr/ADR-030], [Corpus: tests]

## Locked decisions (Phase 0 complete)

| ID | Decision |
|----|----------|
| D-S050-ev041 | Merged PR #895 @ `fa5b2140`; closed S049 / EV-041 |
| D-S050-db-scope | Remove **drawer** DB sinks only; keep F17–F19; leave `DatabaseUploadDialog` |
| D-S050-cycle-scope | Ship **all three**: remove DB + churn UX + secure mass file/folder ingest |
| D-S050-churn | Queue+keyboard **and** batch convert/validate/disseminate |
| D-S050-mass-shape | Multi-file + folder/zip; progress; per-file errors |
| D-S050-mass-sec | Auth-gated + caps + MIME/binary reject + **content sniff / zip-bomb** guards |
| D-S050-db-api | **UI hide only** (API remains for tests/harness) |
| D-S050-preset | **Standard** |
| D-S050-improvements | Keyboard shortcuts; mass progress toast; default sink WIS2/last non-DB; keep multi-select |
| D-S050-ui-preview | Non-deployed local `http://localhost:18000` |

## Code touchpoints (expected)

| Area | Path | Notes |
|------|------|-------|
| Drawer sinks | `apps/frontend/src/utils/dissemination.ts` (`DB_SINK_TYPES`) | Hide/remove from UI chooser |
| Drawer UI | `apps/frontend/src/app/components/DisseminationDrawer.tsx` | Default sink ≠ postgres |
| Backend sinks | `packages/dissemination/`, `apps/backend` dissemination routes | Soft-disable vs leave API — open |
| File convert | `apps/frontend/src/app/components/FileConverter.tsx` | Existing multi-file upload; deepen for folder/mass |
| Tests | drawer + dissemination + Playwright H4–H5 / H6′ | Update for no DB sinks; mass-ingest journeys |

## Related open issues

- #843 Dissemination deepen epic (parent umbrella)
- #896 Customer DB connector spike (feeds #898, not this cycle)
- #795 Drawer connection-first checks (may pause while DB sinks removed)
- #840 Operator workbench deepen (churn UX may overlap)

## Phase 1 proposal (pending proceed gate)

| Fn | Role |
|----|------|
| F16 deepen | Hide drawer DB sinks; default non-DB sink |
| F7 deepen | Queue/keyboard + batch actions + improvements pack |
| **F33** (new) | Secure mass file/folder ingest (auth, caps, sniff/zip-bomb) |

## Next AskQuestion

Proceed gate → allocate Fn(s) + impact analysis
