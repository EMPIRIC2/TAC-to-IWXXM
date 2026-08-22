"""TC-EV063-008 — CA_ECCC stub fixture pack (EV-063 M8 / #916 started).

[Corpus: product §F36] [Corpus: domain-profiles §CA_ECCC] [Corpus: tests §TC-EV063]
"""

from __future__ import annotations

import json
from pathlib import Path

from metar_shared.xml_canonical import canonicalize_xml

from tac2iwxxm import convert

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "profiles" / "CA_ECCC"
MANIFEST_PATH = FIXTURES / "manifest.json"
IWXXM_VERSION = "2025-2"
PROFILE = "CA_ECCC"


def test_tc_ev063_008_ca_eccc_manifest_present() -> None:
    """CA_ECCC fixture layout exists under profiles/CA_ECCC/METAR/valid."""
    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    assert data.get("profile") == PROFILE
    case = data["cases"][0]
    assert (FIXTURES / case["tac"]).is_file()
    assert (FIXTURES / case["golden"]).is_file()


def test_tc_ev063_008_ca_eccc_metar_stub_convert() -> None:
    """CA_ECCC converts Canadian METAR via annex3 stub encoder."""
    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    case = data["cases"][0]
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    expected = (FIXTURES / case["golden"]).read_text(encoding="utf-8")

    result = convert(
        tac,
        product=case["product"],
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"failed: {result.issues!r}"
    assert result.semantic_profile == "ca_eccc"
    codes = {issue.code for issue in result.issues}
    assert "PROFILE_STUB" in codes
    assert canonicalize_xml(result.xml or "") == canonicalize_xml(expected)


def test_tc_ev063_008_ca_eccc_taf_unsupported() -> None:
    """Non-METAR/SPECI products fail closed until #916 expands scope."""
    tac = "TAF CYUL 231800Z 2319/2418 24010KT 9999 FEW240="
    result = convert(tac, product="TAF", profile=PROFILE, iwxxm_version=IWXXM_VERSION)
    assert not result.ok
    assert result.issues[0].code == "UNSUPPORTED_PROFILE"
