# tac-decoding

The **tac-decoding** package decodes Traditional Alphanumeric Code (TAC)
aviation weather products into ordered natural-language segments and a
deterministic plain-language summary.

The package is MIT licensed. The package has no FastAPI or database
dependencies.

## Install

```bash
pip install tac-decoding
```

You need Python 3.12 or newer.

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

You can point `TAC_DECODING_GLOSSARY_PATH` at optional glossary YAML. This
package is the source of truth for the decode glossary.

## Pack overlays

You can point `TAC_DECODING_PACK_DIR` at a directory of pack YAML files. See the
monorepo overlay cookbook and the package `examples/` tree for starter files.

## Links

- PyPI: [tac-decoding](https://pypi.org/project/tac-decoding/)
- Related: [tac2iwxxm](https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/Package-tac2iwxxm), [tac-validate](https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/Package-tac-validate)
