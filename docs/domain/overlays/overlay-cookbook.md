# Overlay cookbook

**Ticket:** [#1226](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1226) (M1 DX) · baseline [#1224](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1224)  
**Audience:** SDK embedders and deployers (file/env overlays)  
**Not for:** in-app YAML editing (retired — ADR-044)

[Corpus: tech-spec] [Corpus: adr/ADR-044] [Corpus: adr/ADR-045] [Corpus: adr/ADR-046] [Corpus: adr/ADR-047] [Corpus: tests]

## Shared header

Extension YAML always needs `id` and `profiles`. **`extends` shape depends on the package** — do not copy one form for all four:

```yaml
# tac-decoding pack overlay (string parent pack id)
id: metar-demo
profiles: [annex3]
extends: metar
layout: token_stream
rules: []
```

```yaml
# tac-validate / iwxxm-validate policy overlay (exactly one parent in a list)
id: annex3-metar-quality-demo
profiles: [annex3]
extends: [annex3-metar-quality]
lifecycle: draft
# … product / pin / select / ignore per package schema
```

```yaml
# tac2iwxxm profile → policy binding (emit key; string or one-element list)
id: annex3-binding-demo
profiles: [annex3]
extends: annex3
```

- Missing or unknown base → **fail closed** (builtin stays in force).
- Same payload id → replace that entry; new id → add; other builtins unchanged.
- Load-tested demos: `packages/*/examples/overlays/{valid,invalid-bad-extends}/`.
- Copy-paste starters: `packages/*/examples/starters/`.

## Worked example (METAR across four packages)

From a git checkout of this monorepo:

```bash
# 1) Decode pack overlay
export TAC_DECODING_PACK_DIR=packages/tac-decoding/examples/starters
tac-decoding --check-overlay "$TAC_DECODING_PACK_DIR"

# 2) TAC quality policy overlay
export TAC_VALIDATE_POLICY_DIR=packages/tac-validate/examples/starters
tac-validate --check-overlay "$TAC_VALIDATE_POLICY_DIR"

# 3) IWXXM output policy overlay
export IWXXM_VALIDATE_POLICY_DIR=packages/iwxxm-validate/examples/starters
iwxxm-validate --check-overlay "$IWXXM_VALIDATE_POLICY_DIR"

# 4) Profile → policy binding overlay
export TAC2IWXXM_PROFILE_DIR=packages/tac2iwxxm/examples/starters
tac2iwxxm --check-overlay "$TAC2IWXXM_PROFILE_DIR"

# Or run every package example + starter tree:
make overlay-preflight
```

After preflight succeeds, point the same env vars at your own overlay directory in deploy
config (see [config-spec.md](../config-spec.md)). The HTTP API still does **not** accept
YAML bodies — mount directories on the server.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `extends unknown` / fail-closed | Typo in parent id, or wrong `extends` shape (string vs list) | Match the package header examples above; copy a starter |
| Overlay ignored | Env var not set in the process that loads the package | Export the env for that worker/API process; re-check with `--check-overlay` |
| Builtin disappeared | Replaced same `id` without intending to | Use a new `id` to add; only reuse `id` when replacing |
| CLI wants a TAC/XML path | Forgot `--check-overlay` | Pass `--check-overlay DIR` alone (no input file) |

## Env vars (canonical)

| Package | Env | Purpose |
|---------|-----|---------|
| `tac-decoding` | `TAC_DECODING_PACK_DIR` | Pack overlays |
| `tac-decoding` | `TAC_DECODING_GLOSSARY_PATH` | Glossary overlay (legacy: `TAC2IWXXM_DECODE_GLOSSARY_PATH`) |
| `tac-validate` | `TAC_VALIDATE_POLICY_DIR` | TAC quality policy overlays |
| `tac-validate` | `TAC_VALIDATE_DETECTOR_DIR` | Detector pack overlays |
| `tac-validate` | `TAC_VALIDATE_DETECTOR_MODE` | `detector` / `legacy` |
| `iwxxm-validate` | `IWXXM_VALIDATE_POLICY_DIR` | IWXXM output policy overlays |
| `tac2iwxxm` | `TAC2IWXXM_PROFILE_DIR` | Profile → policy binding overlays |
| `tac2iwxxm` | `TAC2IWXXM_EMIT_MAP_DIR` | Convert emit-map overlays (METAR/SPECI M3) |
| `tac2iwxxm` | `TAC2IWXXM_CONVERT_IR_SOURCE` | `legacy` / `pack` / `auto` |

See also [config-spec.md](../config-spec.md) §F24/F9 deepen.

## Honesty

Read [product-engine-matrix.md](product-engine-matrix.md) before assuming a product is
“fully YAML configured.” Program [#1226](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1226)
/ ADR-047: every core product cell (decode, TAC quality, detectors, IWXXM output policy,
convert pack-IR, convert emit) is rated **full**. Named Python residuals (detector hatches,
decode location enrichment, emit-map `plugin:` builders) remain documented and do **not**
block that rating — see residual epic [#1252](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1252).

## HTTP

The API does **not** accept pack/policy/emit-map YAML in request bodies. Mount overlay
directories in the deploy environment instead.

## Glossary SoT

Official glossary home is **`tac-decoding`**. Prefer `TAC_DECODING_GLOSSARY_PATH`.
