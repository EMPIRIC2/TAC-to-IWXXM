"""TC-EV063-008 — CA_ECCC fixture pack registry (EV-063 M8 / #916).

EV-064 superseded the stub encoder; this module keeps the EV-063 manifest gate and
version fail-closed checks. Golden equality lives in ``test_tc_ev064_002_ca_eccc_goldens``.

[Corpus: product §F36] [Corpus: domain-profiles §CA_ECCC] [Corpus: tests §TC-EV063]
"""

from __future__ import annotations

import json
from pathlib import Path

from tac2iwxxm import convert

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "profiles" / "CA_ECCC"
MANIFEST_PATH = FIXTURES / "manifest.json"
CA_IWXXM_VERSION = "3.0.0"
PROFILE = "CA_ECCC"


def test_tc_ev063_008_ca_eccc_manifest_present() -> None:
    """CA_ECCC fixture layout exists under profiles/CA_ECCC/METAR/valid."""
    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    assert data.get("profile") == PROFILE
    case = data["cases"][0]
    assert (FIXTURES / case["tac"]).is_file()
    assert (FIXTURES / case["golden"]).is_file()


def test_tc_ev063_008_ca_eccc_requires_iwxxm_3_0_0() -> None:
    """CA_ECCC fails closed when iwxxm_version is not the MSC 3.0.0 line."""
    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    case = data["cases"][0]
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")

    result = convert(
        tac,
        product=case["product"],
        profile=PROFILE,
        iwxxm_version="2025-2",
    )
    assert not result.ok
    assert result.issues[0].code == "INVALID_IWXXM_VERSION"


def test_tc_ev063_008_ca_eccc_taf_requires_iwxxm_3_0_0() -> None:
    """TAF on CA_ECCC also pins iwxxm_version to 3.0.0 (EV-064 M4)."""
    tac = "TAF CYUL 231800Z 2319/2418 24010KT 9999 FEW240="
    result = convert(tac, product="TAF", profile=PROFILE, iwxxm_version="2025-2")
    assert not result.ok
    assert result.issues[0].code == "INVALID_IWXXM_VERSION"

    ok = convert(tac, product="TAF", profile=PROFILE, iwxxm_version=CA_IWXXM_VERSION)
    assert ok.ok, f"expected TAF convert: {ok.issues!r}"
