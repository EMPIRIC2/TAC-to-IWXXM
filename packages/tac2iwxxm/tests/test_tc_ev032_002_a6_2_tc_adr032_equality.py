"""TC-EV032-002 - #835 A6-2-TC ADR-032 equality (S040 / EV-032 T1.1).

Strict bar (E32-T2): ``canonicalize_xml(convert(annex3 A6-2-TC))`` must equal
vendor ``sigmet-A6-2-TC.xml`` under the default pin before catalog ``wmoPass``.

Marked ``ev032_smoke`` for path-filtered pre-commit canary (E32-T7 / T1.5).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from metar_shared.xml_canonical import canonicalize_xml

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "annex3_golden"
VENDOR_XML = Path(__file__).resolve().parents[3] / "vendor/schemas/iwxxm/2025-2/IWXXM/examples/sigmet-A6-2-TC.xml"
IWXXM_VERSION = "2025-2"
PROFILE = "annex3"


@pytest.mark.ev032_smoke
def test_tc_ev032_002_a6_2_tc_adr032_equality() -> None:
    """Convert annex3 A6-2-TC TAC → vendor XML under ADR-032 canonicalize."""
    from tac2iwxxm import convert

    tac = (FIXTURES / "sigmet_a6_2_tc.tac").read_text(encoding="utf-8")
    vendor = VENDOR_XML.read_text(encoding="utf-8")
    result = convert(tac, product="SIGMET", profile=PROFILE, iwxxm_version=IWXXM_VERSION)
    assert result.ok is True, result.issues
    assert result.xml is not None
    assert "TropicalCycloneSIGMET" in result.xml
    assert canonicalize_xml(result.xml) == canonicalize_xml(vendor)
