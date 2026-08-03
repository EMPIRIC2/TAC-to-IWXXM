# Quality matrices — authoring guide (F29 / #831)

When you **add or change** a lint rule, convert encode theme, or Schematron-facing
validate assert that is in the METAR/SPECI pilot inventory, update the parameterized
matrices under `tests/quality_matrices/`. Silent empty slots fail the inventory gate
(TC-F29-004).

## Layout

```text
tests/quality_matrices/
  inventory/metar_speci_pilot.yml   # unified SoT (95 pilot rules)
  inventory_gate.py                 # CI gate helper
  loaders.py / runners.py
  testdata/
    lint/metar_speci/<CODE>.yml
    convert/metar_speci/<stem>.yml
    validate/metar_speci/<SCH_ID>.yml
```

Each rule file declares **20 slots**: buckets `happy` / `sad` / `edge_pass` /
`edge_fail` × case ids `01`..`05`.

## Definition of done (rule PR)

1. **Registry / native id** — lint codes in `tac-validate` issue registry; convert stems
   match annex3 themes; validate ids match vendor `METAR_SPECI.*` Schematron patterns.
2. **Inventory row** — add the id under the correct engine in
   `inventory/metar_speci_pilot.yml` (or expand product scope via evolve).
3. **Matrix file** — create/update `testdata/<engine>/metar_speci/<id>.yml` with all 20
   slots. Prefer `status: ready` with TAC + `expect`; otherwise
   `status: needs-fixture` + `meta.reason`, or `status: oos` + cite.
4. **Runners** — ready slots must pass via `run_rule_case` (lint / convert / validate).
5. **Checks** — `make test-quality-matrices-smoke` green; optionally
   `make test-quality-matrices-full`. Inventory gate must pass
   (`test_tc_f29_004_inventory_gate.py`).

## Slot status policy

| Status | Meaning |
|--------|---------|
| `ready` | Has TAC (or XML for validate); runner asserts `expect` |
| `needs-fixture` | Explicit gap; pytest skips; **counts** for the gate |
| `oos` | Out of scope with `meta.cite` / `reason`; pytest skips |

Never omit a slot. Never leave a bucket short of five case ids.

## Node ids

Failures name `{rule_id}/{bucket}/{case_id}` (TC-F29-005).

## CI

- PR / path smoke: `make test-quality-matrices-smoke` (excludes `@pytest.mark.quality_matrix`)
- Full pilot: `make test-quality-matrices-full` (optional / workflow_dispatch)

See session design notes: `docs/sessions/S037-quality-residuals-831/reports/t0.1-harness-design-note.md`
and `t0.2-unified-inventory-sketch.md`.
