"""Run every raw .tac / .xml under the Caribbean tester kit.

Guyana ``bulletin_report_*.tac`` files are IWXXM collect bulletins (XML) despite
the extension. [Corpus: product §F2] [Corpus: product §F6] [Corpus: tests]
"""

from __future__ import annotations

from pathlib import Path

import pytest
from iwxxm_validate.wellformed import run_wellformed_lxml
from tac2iwxxm.convert import convert

from .conftest import RAW, guess_product, is_xml_payload, strip_gts

_TAC_PATHS = sorted(RAW.rglob("*.tac"))
_XML_PATHS = sorted(RAW.rglob("*.xml"))


def test_raw_file_counts() -> None:
    assert len(_TAC_PATHS) == 15
    assert len(_XML_PATHS) >= 200


@pytest.mark.parametrize("path", _TAC_PATHS, ids=[p.name for p in _TAC_PATHS])
def test_raw_tac_path_converts_or_is_xml_bulletin(path: Path) -> None:
    text = path.read_text(encoding="utf-8", errors="replace")
    if is_xml_payload(text):
        issues = run_wellformed_lxml(text)
        assert issues == [], [issue.message for issue in issues]
        return
    body = strip_gts(text)
    product = guess_product(body)
    result = convert(body, product=product, bulletin_date="2026-10-08")
    assert result.ok is True
    assert result.xml is not None


@pytest.mark.parametrize(
    "path",
    _XML_PATHS,
    ids=[str(p.relative_to(RAW)).replace("/", "_")[:80] for p in _XML_PATHS],
)
def test_raw_xml_is_wellformed(path: Path) -> None:
    text = path.read_text(encoding="utf-8", errors="replace")
    issues = run_wellformed_lxml(text)
    assert issues == [], [issue.message for issue in issues]
