"""T1.5 — tac-decoding does not import tac2iwxxm.

[Corpus: adr/ADR-045] [Corpus: tests]
"""

from __future__ import annotations

import ast
from pathlib import Path

import tac_decoding


def test_tac_decoding_has_no_tac2iwxxm_import() -> None:
    root = Path(tac_decoding.__file__).resolve().parent
    offenders: list[str] = []
    for path in sorted(root.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            modules: list[str] = []
            if isinstance(node, ast.Import):
                modules.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                modules.append(node.module)
            offenders.extend(f"{path.name}:{name}" for name in modules if name.split(".")[0] == "tac2iwxxm")
    assert offenders == []


def test_bulletin_split_is_injected() -> None:
    import tac_decoding.decode as decode_mod

    ahl = "SAXX99 YUDO 121200\nMETAR YUDO 121200Z 00000KT CAVOK 10/10 Q1000=\n"
    previous = decode_mod._bulletin_splitter
    decode_mod.set_bulletin_splitter(None)
    try:
        assert decode_mod._decode_bulletin(ahl, product="METAR") is None
        decode_mod.set_bulletin_splitter(lambda _tac, _product: None)
        assert decode_mod._decode_bulletin(ahl, product="METAR") is None
    finally:
        decode_mod.set_bulletin_splitter(previous)
