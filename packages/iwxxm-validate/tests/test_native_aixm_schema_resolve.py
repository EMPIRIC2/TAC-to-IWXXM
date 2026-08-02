"""Regression: native XSD must resolve AIXM 5.1.1 (not 5.1) for IWXXM imports.

PyPI 0.1.1 native wheels hit SCHEMA_PARSE_ERROR because VendorResolver basename
index preferred ``externalSchema/aero/aixm/5.1/`` over ``5.1.1/`` (and xmloxide
does not re-base nested includes). Fix lands in 0.1.2 (EV-028 / F13).
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
VENDOR_METAR = REPO_ROOT / "vendor" / "schemas" / "iwxxm" / "2023-1" / "IWXXM" / "examples" / "metar-A3-1.xml"
ANNEX3_METAR = REPO_ROOT / "packages" / "tac2iwxxm" / "tests" / "fixtures" / "annex3_golden" / "metar_basic.golden.xml"


def _rust_or_skip():
    from iwxxm_validate.native import rust_available, rust_module

    if not rust_available():
        pytest.skip("native iwxxm_validate._rust not built")
    mod = rust_module()
    assert mod is not None
    mod.clear_schema_caches()
    return mod


@pytest.mark.parametrize(
    ("xml_path", "iwxxm_version"),
    [
        (VENDOR_METAR, "2023-1"),
        (ANNEX3_METAR, "2023-1"),
        (ANNEX3_METAR, "2025-2"),
    ],
    ids=["vendor_2023-1", "annex3_2023-1", "annex3_2025-2"],
)
def test_native_xsd_resolves_aixm_5_1_1(xml_path: Path, iwxxm_version: str) -> None:
    """Native XSD parse must not load AIXM 5.1 for a 5.1.1 import."""
    _rust_or_skip()
    from iwxxm_validate import validate_iwxxm

    assert xml_path.is_file(), xml_path
    report = validate_iwxxm(
        xml_path.read_text(encoding="utf-8"),
        iwxxm_version=iwxxm_version,
        levels=("xsd",),
    )
    aixm_wrong_tree = [
        i
        for i in report.issues
        if i.code == "SCHEMA_PARSE_ERROR"
        and (
            "schema/5.1'" in i.message
            or "aero/schema/5.1'" in i.message
            or ("targetNamespace 'http://www.aixm.aero/schema/5.1'" in i.message and "5.1.1" in i.message)
        )
    ]
    assert not aixm_wrong_tree, aixm_wrong_tree
    assert report.ok, [(i.code, i.message) for i in report.issues]
