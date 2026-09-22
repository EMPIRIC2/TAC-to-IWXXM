# tac-decoding

Decode Traditional Alphanumeric Code (TAC) aviation weather products into
ordered natural-language segments and a deterministic plain-language summary.
MIT licensed. No FastAPI or database dependencies.

## Install

```bash
pip install tac-decoding
```

Requires Python ≥ 3.12.

## Library

```python
from tac_decoding import decode_tac

result = decode_tac("METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005=", product="METAR")
print(result.summary)
for seg in result.segments:
    print(seg.code, seg.explanation)
```

## Catalog

```python
from tac_decoding import catalog_entries

for row in catalog_entries(limit=10):
    print(row["id"], row["summary"])
```

## Glossary overlay

Optional YAML via `TAC_DECODING_GLOSSARY_PATH` (or legacy
`TAC2IWXXM_DECODE_GLOSSARY_PATH`). **SoT** for the glossary is this package.

## Pack overlays

Optional directory of pack YAML via `TAC_DECODING_PACK_DIR` (ADR-045). See the
monorepo [Overlay cookbook](https://github.com/EMPIRIC2/TAC-to-IWXXM/blob/stage/docs/domain/overlays/overlay-cookbook.md),
`examples/overlays/`, and copy-paste `examples/starters/`.

Install smoke (from a git checkout after `pip install -e packages/tac-decoding`):

```bash
export TAC_DECODING_PACK_DIR=packages/tac-decoding/examples/starters
tac-decoding --check-overlay "$TAC_DECODING_PACK_DIR"
```

## Links

- Source: [EMPIRIC2/TAC-to-IWXXM](https://github.com/EMPIRIC2/TAC-to-IWXXM)
- Related: [`tac2iwxxm`](https://pypi.org/project/tac2iwxxm/), [`tac-validate`](https://pypi.org/project/tac-validate/)
