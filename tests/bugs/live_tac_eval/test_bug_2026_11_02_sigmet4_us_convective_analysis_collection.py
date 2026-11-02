"""US convective SIGMET must emit analysisCollection (SIGMET.SIGMET-4).

Schematron SIGMET.SIGMET-4 requires ``iwxxm:analysisCollection`` on ordinary
OPERATIONAL reports. Convective (WST) emit used a bare ``iwxxm:analysis``
wrapper (~111 / ~8% of 30d IWXXM validate fails).

Product-rule fix in tac2iwxxm convective emit — not a severity soften.

[Corpus: product §F23 §F36] [Corpus: tests]
"""

from __future__ import annotations

import re
from pathlib import Path

from iwxxm_validate import validate_iwxxm
from tac2iwxxm.profiles.annex3_emit.sigmet import emit_convective_sigmet_annex3

from tac2iwxxm import convert

_FIXTURE_TAC = (
    Path(__file__).resolve().parents[3]
    / "packages/tac2iwxxm/tests/fixtures/profiles/US_FAA_NWS/SIGMET/valid/sigmet_conv_wst.tac"
)

_ANALYSIS_COLLECTION = re.compile(
    r"<iwxxm:analysisCollection>\s*"
    r"<iwxxm:analysisAndForecastPositionAnalysis\b[^>]*>\s*"
    r"<iwxxm:analysis>\s*"
    r"<iwxxm:SIGMETEvolvingConditionCollection\b",
    re.DOTALL,
)

_MIN_IR = {
    "product": "SIGMET",
    "fir": "MKCC",
    "mwo": "KKCI",
    "sequence": 0,
    "valid_from_day": 9,
    "valid_from_hour": 8,
    "valid_from_minute": 55,
    "valid_to_day": 9,
    "valid_to_hour": 10,
    "valid_to_minute": 55,
    "convective": True,
    "convective_tag": "11C",
    "geometry": {
        "kind": "polygon",
        "pos_list": "44.0 -96.0 41.0 -96.0 41.0 -98.0 44.0 -98.0 44.0 -96.0",
    },
}


def test_emit_convective_wraps_analysis_collection() -> None:
    xml = emit_convective_sigmet_annex3(_MIN_IR, iwxxm_version="2025-2")
    assert _ANALYSIS_COLLECTION.search(xml)
    assert xml.count("<iwxxm:analysisCollection>") == 1
    assert xml.count("</iwxxm:analysisCollection>") == 1


def test_us_convective_fixture_clears_sigmet4_with_validate_iwxxm() -> None:
    tac = _FIXTURE_TAC.read_text(encoding="utf-8")
    result = convert(tac, product="SIGMET", profile="iwxxm_us", iwxxm_version="2025-2")
    assert result.ok is True
    assert result.xml is not None
    assert _ANALYSIS_COLLECTION.search(result.xml)
    report = validate_iwxxm(result.xml, iwxxm_version="2025-2")
    sig4 = [
        issue
        for issue in report.issues
        if "SIGMET-4" in (getattr(issue, "code", "") + getattr(issue, "message", ""))
    ]
    assert not sig4, [(i.code, i.message[:160]) for i in sig4]
