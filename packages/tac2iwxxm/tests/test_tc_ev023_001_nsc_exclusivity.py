"""TC-EV023-001 - NSC without layered cloud (S030 / EV-023 T1.1).

Positive: TAC ``NSC`` → empty/nil ``iwxxm:cloud`` with
``nothingOfOperationalSignificance`` and no ``CloudLayer``.
Negative: fixture XML that pairs that nilReason with layered cloud fails the
structural exclusivity check (XSD/SCH may soft-skip under SCHEMA_IMPORT_WARNING /
SCHEMATRON_SKIPPED for 2025-2).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
_FIXTURES = Path(__file__).resolve().parent / "fixtures"
_ANNEX3 = _FIXTURES / "annex3_golden"
_EV023 = _FIXTURES / "ev023"
_AMD79 = _REPO / "vendor" / "schemas" / "iwxxm-translation" / "Amd79-80-2023"

IWXXM_VERSION = "2025-2"
PROFILE = "annex3"
_NIL_NSC = "http://codes.wmo.int/common/nil/nothingOfOperationalSignificance"
_CLOUD_OPEN = re.compile(
    r"<iwxxm:cloud\b([^>]*)>(.*?)</iwxxm:cloud>",
    re.DOTALL,
)
_CLOUD_EMPTY = re.compile(r"<iwxxm:cloud\b([^>]*)/>")


def _nsc_cloud_blocks(xml: str) -> list[str]:
    """Return attribute blobs for cloud elements that carry the NSC nilReason."""
    blocks: list[str] = []
    for m in _CLOUD_EMPTY.finditer(xml):
        attrs = m.group(1)
        if _NIL_NSC in attrs:
            blocks.append(attrs)
    for m in _CLOUD_OPEN.finditer(xml):
        attrs, body = m.group(1), m.group(2)
        if _NIL_NSC in attrs:
            blocks.append(attrs + "\n" + body)
    return blocks


def assert_nsc_cloud_exclusive(xml: str) -> None:
    """
    Fail when an NSC nilReason cloud also contains layered cloud content.

    Parameters
    ----------
    xml : str
        IWXXM document text.
    """
    blocks = _nsc_cloud_blocks(xml)
    assert blocks, f"expected NSC nilReason cloud ({_NIL_NSC})"
    for block in blocks:
        assert "CloudLayer" not in block, "NSC nilReason cloud must not contain CloudLayer"
        assert "AerodromeCloud" not in block, "NSC nilReason cloud must not contain AerodromeCloud"


def _blocking_validate(xml: str) -> list:
    from iwxxm_validate import validate

    report = validate(
        xml,
        iwxxm_version=IWXXM_VERSION,
        profile=PROFILE,
        levels=("xsd", "schematron"),
    )
    return [i for i in report.issues if i.severity == "error" and i.code not in {"SCHEMATRON_SKIPPED"}]


@pytest.mark.parametrize(
    ("tac_path", "product"),
    [
        (_ANNEX3 / "speci_nsc.tac", "SPECI"),
        (_AMD79 / "metar" / "EFHK-290020Z.tac", "SPECI"),
    ],
    ids=["annex3_speci_nsc", "amd79_efhk_nsc"],
)
def test_tc_ev023_001_nsc_convert_no_layered_cloud(tac_path: Path, product: str) -> None:
    from tac2iwxxm import convert

    assert tac_path.is_file(), tac_path
    tac = tac_path.read_text(encoding="utf-8")
    assert "NSC" in tac
    result = convert(
        tac,
        product=product,
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"convert failed: {result.issues!r}"
    assert "CloudLayer" not in result.xml
    assert_nsc_cloud_exclusive(result.xml)
    blocking = _blocking_validate(result.xml)
    assert not blocking, f"M-xsd/M-sch blocking: {[(i.code, i.message) for i in blocking]}"


@pytest.mark.parametrize(
    "tac",
    [
        "SPECI KJFK 231751Z 18012KT 9999 NSC FEW015 15/07 Q1013=",
        "SPECI KJFK 231751Z 18012KT 9999 FEW015 NSC 15/07 Q1013=",
        "METAR KJFK 231751Z 18012KT 9999 NSC SCT020 15/07 Q1013=",
    ],
    ids=["nsc_then_few", "few_then_nsc", "metar_nsc_sct"],
)
def test_tc_ev023_001_nsc_cooccurrence_omits_layers(tac: str) -> None:
    """When TAC has both NSC and layered amounts, encode must keep NSC exclusivity."""
    from tac2iwxxm.products.metar_speci import parse_metar_speci

    from tac2iwxxm import convert

    product = "METAR" if tac.startswith("METAR") else "SPECI"
    ir = parse_metar_speci(tac, product=product)
    assert ir.get("nsc") is True
    assert ir.get("clouds") == []
    assert "cloud_amount" not in ir
    result = convert(
        tac,
        product=product,
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"convert failed: {result.issues!r}"
    assert "CloudLayer" not in result.xml
    assert_nsc_cloud_exclusive(result.xml)


def test_tc_ev023_001_negative_nsc_nil_with_layer_fixture() -> None:
    """Hand-built XML pairing NSC nilReason with CloudLayer fails exclusivity."""
    path = _EV023 / "nsc_nil_with_layer.negative.xml"
    xml = path.read_text(encoding="utf-8")
    assert _NIL_NSC in xml
    assert "CloudLayer" in xml
    with pytest.raises(AssertionError, match="must not contain CloudLayer"):
        assert_nsc_cloud_exclusive(xml)
    # Soft-skip environment: still invoke validate so CI records the path; do not
    # require hard XSD/SCH fail while SCHEMA_IMPORT_WARNING / SCHEMATRON_SKIPPED apply.
    _blocking_validate(xml)
