# TC-F6-022 — Archived gifts Annex-3 goldens (post-delete)

`packages/gifts` was removed in T4.7 (ADR-014). Live gifts Annex-3 XML is no longer
generated in-tree.

**Canonical post-cutover goldens** (use these for M-parity / regression):

- `packages/tac2iwxxm/tests/fixtures/annex3_golden/` — TC-F6-020/021 METAR/SPECI annex3
- `packages/tac2iwxxm/tests/fixtures/iwxxm_us_golden/` — TC-F6-003 subset METAR/SPECI US

Historical migration goldens under `test-data/golden/` (TC-M003) remain as frozen
pre-cutover snapshots for reference only; TC-M003 itself is deprecated.
