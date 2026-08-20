"""TC-EV061-1011 / TC-LIVE-F6-030 — live bulletin harness posts multipart ``files``.

[Corpus: api] [Corpus: tests §TC-LIVE-F6-030] #1011
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
HARNESS = ROOT / "tests" / "live" / "test_tc_live_f6_030_bulletin.py"


def _convert_bulletin_multipart_field_names(source: str) -> list[str]:
    """Return string keys of the ``files=`` dict on convert-bulletin POSTs."""
    tree = ast.parse(source)
    names: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        path = ""
        if isinstance(node.func, ast.Attribute) and node.func.attr == "post":
            args = node.args
            if args and isinstance(args[0], ast.JoinedStr):
                path = "".join(
                    part.value
                    for part in args[0].values
                    if isinstance(part, ast.Constant) and isinstance(part.value, str)
                )
            elif (
                args
                and isinstance(args[0], ast.Constant)
                and isinstance(args[0].value, str)
            ):
                path = args[0].value
        if "convert-bulletin" not in path:
            continue
        for kw in node.keywords:
            if kw.arg != "files" or not isinstance(kw.value, ast.Dict):
                continue
            for key in kw.value.keys:
                if isinstance(key, ast.Constant) and isinstance(key.value, str):
                    names.append(key.value)
    return names


@pytest.mark.unit
def test_tc_ev061_1011_live_harness_posts_multipart_files() -> None:
    """H7 harness must use API field ``files`` (plural), not ``file``."""
    assert HARNESS.is_file(), f"missing live harness: {HARNESS}"
    names = _convert_bulletin_multipart_field_names(HARNESS.read_text(encoding="utf-8"))
    assert names, f"no convert-bulletin multipart keys found in {HARNESS}"
    assert "files" in names, (
        f"live harness must post multipart field 'files'; found {names}"
    )
    assert "file" not in names, (
        f"stale multipart field 'file' in live harness; found {names}"
    )
