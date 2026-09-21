# Overlay cookbook (draft)

**Ticket:** [#1224](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1224)  
**Audience:** SDK embedders and deployers (file/env overlays)  
**Not for:** in-app YAML editing (retired — ADR-044)

[Corpus: tech-spec] [Corpus: adr/ADR-044] [Corpus: adr/ADR-045] [Corpus: adr/ADR-046]

## Shared header

Extension YAML uses:

```yaml
id: my-overlay
profiles: [annex3]          # required on overlays
extends: annex3-metar-quality  # exactly one builtin id
```

- Missing base → **fail closed** (builtin stays in force).
- Same payload id → replace that entry; new id → add; other builtins unchanged.

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
| `tac2iwxxm` | `TAC2IWXXM_CONVERT_IR_SOURCE` | `legacy` / `pack` / `auto` |

See also [config-spec.md](../config-spec.md) §F24/F9 deepen.

## Honesty

Read [product-engine-matrix.md](product-engine-matrix.md) before assuming a product is “fully YAML configured.” Convert **emit** remains Python this cycle.

## Examples (Build)

After Build gate: `packages/*/examples/overlays/` plus monorepo preflight:

```bash
# Planned entrypoint (TC-EVYEC-003)
make overlay-preflight
# or: bash scripts/overlays/preflight.sh path/to/overlay-dir
```

## HTTP

The API does **not** accept pack/policy YAML in request bodies. Mount overlay directories in the deploy environment instead.

## Glossary SoT

Official glossary home is **`tac-decoding`**. Prefer `TAC_DECODING_GLOSSARY_PATH`.
