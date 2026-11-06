"""Coherent product behavior where Services asked for overlapping fixes.

Policies (single product truth):
- Soft preview never presents as publishable Valid.
- OUTPUT_VALIDATION_WARNING blocks publish/download.
- annex3 excludes RMK; iwxxm_us may retain remarks.
- GTS/AHL peels for METAR/SPECI/TAF; SIGMET uses bulletin split.
- SIGMET CNL → isCancelReport; DECR → WEAKEN.
- VRB wind keeps knot units.

[Corpus: product §F6] [Corpus: product §F7] [Corpus: product §F10] [Corpus: tests]
"""

from __future__ import annotations

from pathlib import Path

import pytest
from tac2iwxxm.convert import convert
from tac2iwxxm.heading_paste import HeadingPasteError, reports_for_convert

# Soft-preview honesty is also locked in IwxxmPreviewPane.test.tsx / resultCard.test.ts


def test_soft_preview_never_shows_valid_with_publishable_status() -> None:
    """Incomplete TAC soft preview must not look publishable."""
    bad = "METAR TKPK 232100Z VBR02KT 9999 FEW014CB 29/25 Q1013="
    soft = convert(bad, product="METAR", preview=True, bulletin_date="2026-10-23")
    assert soft.xml is not None
    assert soft.ok is False
    assert any("missing wind" in issue.message for issue in soft.issues)


def test_output_validation_warning_is_a_blocking_code_in_fe_module() -> None:
    text = Path("apps/frontend/src/utils/resultCard.ts").read_text(encoding="utf-8")
    assert "OUTPUT_VALIDATION_WARNING" in text
    assert "codeBlocksPublish" in text
    assert "PUBLISH_BLOCKING_CODES" in text


def test_annex3_excludes_rmk_while_iwxxm_us_may_retain() -> None:
    tac = "METAR TTPP 080700Z 00000KT 9000 VCSH FEW015 27/24 Q1013 NOSIG RMK VCSH S="
    annex = convert(tac, product="METAR", profile="annex3", bulletin_date="2026-10-08")
    assert annex.ok is True
    assert annex.xml is not None
    assert any(issue.code == "REMARKS_EXCLUDED" for issue in annex.issues)
    us = convert(tac, product="METAR", profile="iwxxm_us", bulletin_date="2026-10-08")
    assert us.ok is True
    assert us.xml is not None


def test_sigmet_cnl_and_decr_coexist_as_distinct_behaviors() -> None:
    cnl = (
        "TTZP SIGMET A4 VALID 141815/142145 TTPP- "
        "TTZP PIARCO FIR CNL SIGMET A3 141545/142145="
    )
    decr = (
        "SIGMET 3 VALID 251435/251835 TTPP- "
        "TTZP PIARCO FIR EMBD TS OBS AT 1410Z WI N1800 W05406 - N1800 W05039 - "
        "N1031 W05542 - N1316 W05936 - N1800 W05406 TOP ABV FL380 STNR DECR="
    )
    cancel = convert(cnl, product="SIGMET", bulletin_date="2026-10-14")
    weaken = convert(decr, product="SIGMET", bulletin_date="2026-10-25")
    assert cancel.ok is True
    assert cancel.xml is not None
    assert 'isCancelReport="true"' in cancel.xml
    assert weaken.ok is True
    assert weaken.xml is not None
    assert 'intensityChange="WEAKEN"' in weaken.xml
    assert 'isCancelReport="true"' not in weaken.xml


def test_vrb_knots_and_gts_strip_do_not_conflict() -> None:
    gts_vrb = "SAXX31 TNCM 081200\nMETAR TNCM 081200Z VRB03KT 9999 FEW020 28/24 Q1013="
    result = convert(gts_vrb, product="METAR", bulletin_date="2026-10-08")
    assert result.ok is True
    assert result.xml is not None
    assert '[kn_i]">3</iwxxm:meanWindSpeed>' in result.xml or "[kn_i]" in result.xml


def test_cor_keyword_does_not_bypass_missing_visibility() -> None:
    """N10: COR is accepted as a keyword; incomplete groups still fail closed."""
    tac = (
        "METAR COR MZBZ 261200Z VRB02KT FEW002 FEW010CB SCT020 25/25 A2990 Q1012 NOSIG="
    )
    result = convert(tac, product="METAR", bulletin_date="2026-10-26")
    assert any("missing visibility" in issue.message for issue in result.issues), (
        result.issues
    )


def test_ahl_product_letter_mismatch_is_invalid_heading() -> None:
    """Guyana screenshots: SA… AHL with SPECI product selection is INVALID_AHL."""
    pasted = "SAGY31 SYCJ 081200\nSPECI SYCJ 081200Z 14006KT 9999 FEW020 28/24 Q1013="
    with pytest.raises(HeadingPasteError) as caught:
        reports_for_convert(pasted, product="SPECI")
    assert caught.value.code == "INVALID_AHL"
