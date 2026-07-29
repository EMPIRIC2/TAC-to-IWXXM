"""TC-F23-006 / V2 — SIGMET ↔ VA SIGMET ↔ VAA adjacency guards (S025 / EV-019 T3.3).

Never silent-swap roots or products under shared ``product=sigmet`` wire (E19-13):
VA TAC → ``iwxxm:VolcanicAshSIGMET``; general non-VA/TC → ``iwxxm:SIGMET``;
VAA advisory remains ``product=vaa`` / ``VolcanicAshAdvisory``. T3.4 greens root
selection if any assertion fails.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from tac_validate import lint
from tac_validate.issue_registry import by_code

from tac2iwxxm import convert

TAC_VALIDATE = Path(__file__).resolve().parents[2] / "tac-validate" / "tests" / "fixtures" / "accept"
ANNEX3 = Path(__file__).resolve().parent / "fixtures" / "annex3_golden"

_PROFILE = "annex3"
_VERSION = "2025-2"


def _read_accept(name: str) -> str:
    path = TAC_VALIDATE / name
    assert path.is_file(), f"missing fixture: {path}"
    return path.read_text(encoding="utf-8")


def test_tc_f23_006_keyword_presence_for_auto_detect() -> None:
    """TAC keywords are the auto-detect signal — SIGMET vs VA ADVISORY must not blur."""
    general = _read_accept("sigmet_basic.tac")
    va = _read_accept("sigmet_v1_va_volcano.tac")
    vaa = _read_accept("vaa_basic.tac")
    assert "SIGMET" in general.upper()
    assert "SIGMET" in va.upper()
    assert "VA" in va.upper()
    assert "VA ADVISORY" in vaa.upper()
    assert "SIGMET" not in vaa.upper().split("VA ADVISORY", 1)[0]
    # VAA-shaped text must not silent-pass under SIGMET product hint.
    assert lint(vaa, product="SIGMET").ok is False
    assert lint(general, product="VAA").ok is False


def _has_root(xml: str, local: str) -> bool:
    """True when ``xml`` opens with ``<iwxxm:{local} `` (avoids SIGMET* child false positives)."""
    return f"<iwxxm:{local} " in xml


@pytest.mark.parametrize(
    "fname",
    (
        "sigmet_basic.tac",
        "sigmet_a6_1a_ts.tac",
    ),
)
def test_tc_f23_006_general_sigmet_keeps_sigmet_root(fname: str) -> None:
    path = TAC_VALIDATE / fname if (TAC_VALIDATE / fname).is_file() else ANNEX3 / fname
    tac = path.read_text(encoding="utf-8")
    assert lint(tac, product="SIGMET").ok is True
    result = convert(tac, product="SIGMET", profile=_PROFILE, iwxxm_version=_VERSION)
    assert result.ok is True
    assert result.product == "SIGMET"
    assert _has_root(result.xml, "SIGMET")
    assert not _has_root(result.xml, "VolcanicAshSIGMET")
    assert "iwxxm:VolcanicAshAdvisory" not in result.xml
    assert not _has_root(result.xml, "TropicalCycloneSIGMET")


@pytest.mark.parametrize(
    "fname",
    (
        "sigmet_v1_va_volcano.tac",
        "sigmet_v1_no_va_exp.tac",
    ),
)
def test_tc_f23_006_va_sigmet_selects_volcanic_ash_root(fname: str) -> None:
    """VA phenomenon TAC under product=sigmet must content-select VolcanicAshSIGMET."""
    tac = _read_accept(fname)
    assert lint(tac, product="SIGMET").ok is True
    result = convert(tac, product="SIGMET", profile=_PROFILE, iwxxm_version=_VERSION)
    assert result.ok is True
    assert result.product == "SIGMET"
    assert _has_root(result.xml, "VolcanicAshSIGMET")
    assert not _has_root(result.xml, "SIGMET")
    assert "iwxxm:VolcanicAshAdvisory" not in result.xml
    assert not _has_root(result.xml, "TropicalCycloneSIGMET")


def test_tc_f23_006_vaa_keeps_advisory_root() -> None:
    tac = _read_accept("vaa_basic.tac")
    assert lint(tac, product="VAA").ok is True
    result = convert(tac, product="VAA", profile=_PROFILE, iwxxm_version=_VERSION)
    assert result.ok is True
    assert result.product == "VAA"
    assert _has_root(result.xml, "VolcanicAshAdvisory")
    assert not _has_root(result.xml, "VolcanicAshSIGMET")
    assert not _has_root(result.xml, "SIGMET")


def test_tc_f23_006_vaa_rejected_as_sigmet() -> None:
    tac = _read_accept("vaa_basic.tac")
    report = lint(tac, product="SIGMET")
    assert report.ok is False
    assert "MISSING_PRODUCT_KEYWORD" in {i.code for i in report.issues}
    assert by_code("MISSING_PRODUCT_KEYWORD").severity == "error"
    bad = convert(tac, product="SIGMET", profile=_PROFILE, iwxxm_version=_VERSION)
    assert bad.ok is False
    assert any(i.code == "PARSE_ERROR" for i in bad.issues)


def test_tc_f23_006_sigmet_rejected_as_vaa() -> None:
    for fname in ("sigmet_basic.tac", "sigmet_v1_va_volcano.tac"):
        tac = _read_accept(fname)
        report = lint(tac, product="VAA")
        assert report.ok is False, fname
        assert "MISSING_PRODUCT_KEYWORD" in {i.code for i in report.issues}
        bad = convert(tac, product="VAA", profile=_PROFILE, iwxxm_version=_VERSION)
        assert bad.ok is False, fname


def test_tc_f23_006_bulletin_neighbors_no_silent_swap() -> None:
    """Paired general + VA SIGMET + VAA: wrong hint fails; correct hint preserves root."""
    general = _read_accept("sigmet_basic.tac")
    va = _read_accept("sigmet_v1_va_volcano.tac")
    vaa = _read_accept("vaa_basic.tac")

    assert lint(general, product="VAA").ok is False
    assert lint(va, product="VAA").ok is False
    assert lint(vaa, product="SIGMET").ok is False

    g = convert(general, product="SIGMET", profile=_PROFILE, iwxxm_version=_VERSION)
    v = convert(va, product="SIGMET", profile=_PROFILE, iwxxm_version=_VERSION)
    a = convert(vaa, product="VAA", profile=_PROFILE, iwxxm_version=_VERSION)
    assert g.ok and _has_root(g.xml, "SIGMET") and not _has_root(g.xml, "VolcanicAshSIGMET")
    assert v.ok and _has_root(v.xml, "VolcanicAshSIGMET") and not _has_root(v.xml, "SIGMET")
    assert a.ok and _has_root(a.xml, "VolcanicAshAdvisory")

    assert convert(vaa, product="SIGMET", profile=_PROFILE, iwxxm_version=_VERSION).ok is False
    assert convert(general, product="VAA", profile=_PROFILE, iwxxm_version=_VERSION).ok is False
    assert convert(va, product="VAA", profile=_PROFILE, iwxxm_version=_VERSION).ok is False
