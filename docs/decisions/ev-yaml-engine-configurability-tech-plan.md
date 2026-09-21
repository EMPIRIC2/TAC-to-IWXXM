# Tech plan — EV-yaml-engine-configurability (#1224)

**Session:** `EV-yaml-engine-configurability`  
**Locked:** 2026-09-21 (recommended tech choices — user: proceed with recommendations)  
**Gate:** documenting → implementing **closed** until Spec verify + AskQuestion  

[Corpus: product §F2/F6/F9/F12/F15] [Corpus: adr/ADR-044] [Corpus: adr/ADR-045] [Corpus: adr/ADR-046] [Corpus: tech-spec] [Corpus: tests] [Corpus: decisions]

## Architecture (no new components)

Reuse existing package overlay loaders. Add:

| Artifact | Location |
|----------|----------|
| Honesty matrix | `docs/domain/overlays/product-engine-matrix.md` (already drafted) |
| Cookbook | `docs/domain/overlays/overlay-cookbook.md` (already drafted) |
| Example overlays | `packages/{tac-decoding,tac-validate,iwxxm-validate,tac2iwxxm}/examples/overlays/` |
| Preflight | `scripts/overlays/preflight.py` (+ `make overlay-preflight`) |
| Thin CLI hooks | `--check-overlay DIR` on each package CLI (optional thin wrapper calling shared logic) |
| Tests | `tests/` or package tests for TC-EVYEC-001..005 |

**No** new apps/, no FE, no HTTP fields, no new ADR, no new third-party deps (PyYAML already allowed).

## Connectivity

**N/A** — H4–H5 not in scope (D-EVYEC-07). No CORS/VITE tasks.

## Deployment

Optional document note only: mount overlay dirs via env on API/worker images. No Render secret required. No staging-secrets-matrix rows beyond existing optional envs in config-spec.

## Data

None (no DB/schema).

## Preflight design (recommended)

1. **Shared checker** in `scripts/overlays/preflight.py`:
   - Discover `*.yaml` / `*.yml` in one or more dirs
   - For each engine family (detect via path hint or `--kind` flag): validate header `id`, `extends` (exactly one when profiles set), parent exists in builtin catalog for that kind
   - Exit `0` ok / `1` fail-closed with plain stderr messages
2. **Makefile:** `overlay-preflight` → `uv run python scripts/overlays/preflight.py …`
3. **CLI hooks:** each package CLI gains `--check-overlay DIR` that sets the appropriate env or calls package load APIs in dry-run mode (prefer calling existing `load_*_catalog` / `load_packs` with a temp env)

## Example overlay trees (minimal)

Each package ships:

```
examples/overlays/
  README.md                 # points to cookbook
  valid/                    # one minimal extends overlay
  invalid-bad-extends/      # unknown parent — preflight must fail
```

## README / PyPI

Each of four READMEs: env table row + link to `docs/domain/overlays/overlay-cookbook.md` (relative from monorepo; PyPI README short pointer to GitHub path).

## Glossary SoT

Document in cookbook + tac2iwxxm README shim note; no file delete this cycle unless tech-plan Build discovers zero consumers (prefer docs-only).

## Test mapping

| TC | Implementation sketch |
|----|----------------------|
| TC-EVYEC-001 | Assert matrix markdown exists + required product headers / cell vocabulary |
| TC-EVYEC-002 | Grep/README fixture: each package README mentions its env + cookbook path |
| TC-EVYEC-003 | Invoke preflight on valid/ + invalid-bad-extends/ fixtures |
| TC-EVYEC-004 | OpenAPI schema / contract test: no body properties matching pack/policy YAML upload |
| TC-EVYEC-005 | Assert cookbook/config-spec contains glossary SoT sentence |

## Build Plan Card

### Goal
Ship honesty matrix, overlay cookbook + examples, fail-closed preflight, and README/config docs so SDK/deployers can use YAML overlays without over-claiming coverage.

### Out of scope
ADR-044 authoring UI · HTTP policy YAML · Schematron-as-YAML · #1222 · convert-emit YAML · detector YAML deepen

### In-scope task IDs (TDD order)

| ID | Task | Spec source | Depends |
|----|------|-------------|---------|
| T1 | Lock matrix vocabulary + presence test (TC-EVYEC-001) | feature-list #1224 AC1; test-plan TC-EVYEC-001 | — |
| T2 | Add `examples/overlays/{valid,invalid-*}` ×4 packages | cookbook; D-EVYEC-04 | — |
| T3 | Implement `scripts/overlays/preflight.py` + `make overlay-preflight` (TC-EVYEC-003) | D-EVYEC-04 | T2 |
| T4 | Thin `--check-overlay` CLI hooks (optional if T3 covers) | D-EVYEC-04 | T3 |
| T5 | Update four package READMEs + cookbook links (TC-EVYEC-002) | AC2 | T2 |
| T6 | Glossary SoT docs (TC-EVYEC-005) | D-EVYEC-06 | — |
| T7 | OpenAPI / contract no-injection lock (TC-EVYEC-004) | api-contract #1224 | — |
| T8 | Wire CI or `validate-fast` optional target for overlay-preflight | tests | T3 |

### Branch
`evolve/EV-yaml-engine-configurability` from `stage` (after gate opens)

### PR target
`--base stage`

## Milestone summary

| M | Scope |
|---|--------|
| M1 | Matrix CI lock + glossary SoT docs |
| M2 | Example overlays |
| M3 | Preflight + Makefile (+ CLI hooks) |
| M4 | README ×4 + cookbook polish |
| M5 | TC-EVYEC-004 OpenAPI lock + CI wire |

## Decisions (tech)

| ID | Choice |
|----|--------|
| TP-EVYEC-01 | Shared Python preflight script (not four duplicated parsers) |
| TP-EVYEC-02 | Examples live under each package (ship with sdist/wheel optional — monorepo path sufficient for CI) |
| TP-EVYEC-03 | No new dependencies |
| TP-EVYEC-04 | No new ADR |
| TP-EVYEC-05 | H4–H5 / connectivity tasks waived (N/A) |
| TP-EVYEC-06 | Evidence-upgrade matrix cells in Build only where cheap; draft cells OK for T1 presence lock |
