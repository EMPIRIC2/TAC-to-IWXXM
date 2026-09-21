# Overlay cookbook (draft)

**Ticket:** [#1224](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1224)  
**Audience:** SDK embedders and deployers (file/env overlays)  
**Not for:** in-app YAML editing (retired — ADR-044)

[Corpus: tech-spec] [Corpus: adr/ADR-044] [Corpus: adr/ADR-045] [Corpus: adr/ADR-046]

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
- See package trees under `packages/*/examples/overlays/` for load-tested fixtures.

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

Package trees under `packages/*/examples/overlays/` plus monorepo preflight:

```bash
make overlay-preflight
# or: uv run python scripts/overlays/preflight.py --all-examples
# or: uv run python scripts/overlays/preflight.py --kind tac-policy --dir path/to/overlays
```

## HTTP

The API does **not** accept pack/policy YAML in request bodies. Mount overlay directories in the deploy environment instead.

## Glossary SoT

Official glossary home is **`tac-decoding`**. Prefer `TAC_DECODING_GLOSSARY_PATH`.
