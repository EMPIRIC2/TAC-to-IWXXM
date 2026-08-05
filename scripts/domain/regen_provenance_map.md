# Regen PROVENANCE_MAP

Machine SoT: `docs/domain/rules/PROVENANCE_MAP.json` (+ MD twin).

To regenerate catalog/dig linkage heuristics after ISSUE_CATALOG or mining dig changes,
re-run the generator used in S043/EV-035 (session agent) or extend rows manually and
keep JSON/MD in sync. CI: `make test-provenance-quality` (TC-EV035-001..006).

Do **not** invent sources for `gap` rows — raise tickets (#869–#872 / #846).
