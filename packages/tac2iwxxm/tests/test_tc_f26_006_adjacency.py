"""TC-F26-006 / F26 theme V2 — VAA ↔ VA SIGMET adjacency (S027 / EV-021 T1.3).

HARD guards from vaa-tca-theme-fixture-map.md:
- ``product=vaa`` never emits ``iwxxm:VolcanicAshSIGMET`` (advisory root only)
- VA SIGMET path never emits ``iwxxm:VolcanicAshAdvisory`` (F23 keepers)

Complements TC-F23-006 (SIGMET-family side). Always write “F26 theme V2”
(not F23 VA-SIGMET V2) — D-S027-EV021-s02m1-1. T1.4 hardens emit/product
guards if any assertion fails.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from tac_validate import lint
from tac_validate.issue_registry import by_code

from tac2iwxxm import convert

TAC_VALIDATE = Path(__file__).resolve().parents[2] / "tac-validate" / "tests" / "fixtures" / "accept"

_PROFILE = "annex3"
_VERSION = "2025-2"

# F26 theme V1 accept pack + baseline — each must keep VolcanicAshAdvisory under product=vaa.
_VAA_ACCEPT = (
    "vaa_basic.tac",
    "vaa_v1_volcano_unknown.tac",
    "vaa_v1_volcano_unnamed.tac",
    "vaa_v1_rmk_nil_fcst_no_va.tac",
    "vaa_v1_no_further.tac",
)

# F23 VA SIGMET accept fixtures — must never silent-swap to VAA advisory root.
_VA_SIGMET_ACCEPT = (
    "sigmet_v1_va_volcano.tac",
    "sigmet_v1_no_va_exp.tac",
)


def _read_accept(name: str) -> str:
    path = TAC_VALIDATE / name
    assert path.is_file(), f"missing fixture: {path}"
    return path.read_text(encoding="utf-8")


def _has_root(xml: str, local: str) -> bool:
    """True when ``xml`` opens with ``<iwxxm:{local} `` (avoids child-element false positives)."""
    return f"<iwxxm:{local} " in xml


def test_tc_f26_006_keyword_presence_for_auto_detect() -> None:
    """VA ADVISORY vs SIGMET+VA must not blur for auto-detect / product hint."""
    vaa = _read_accept("vaa_basic.tac")
    va_sig = _read_accept("sigmet_v1_va_volcano.tac")
    assert "VA ADVISORY" in vaa.upper()
    assert "SIGMET" not in vaa.upper().split("VA ADVISORY", 1)[0]
    assert "SIGMET" in va_sig.upper()
    assert "VA" in va_sig.upper()
    assert "VA ADVISORY" not in va_sig.upper()
    assert lint(vaa, product="SIGMET").ok is False
    assert lint(va_sig, product="VAA").ok is False


@pytest.mark.parametrize("fname", _VAA_ACCEPT)
def test_tc_f26_006_vaa_keeps_advisory_root(fname: str) -> None:
    """F26 theme V2: product=vaa → VolcanicAshAdvisory only (never VolcanicAshSIGMET)."""
    tac = _read_accept(fname)
    assert lint(tac, product="VAA").ok is True
    result = convert(tac, product="VAA", profile=_PROFILE, iwxxm_version=_VERSION)
    assert result.ok is True, fname
    assert result.product == "VAA"
    assert _has_root(result.xml, "VolcanicAshAdvisory")
    assert not _has_root(result.xml, "VolcanicAshSIGMET")
    assert not _has_root(result.xml, "SIGMET")
    assert not _has_root(result.xml, "TropicalCycloneSIGMET")
    assert "iwxxm:VolcanicAshSIGMET" not in result.xml


@pytest.mark.parametrize("fname", _VA_SIGMET_ACCEPT)
def test_tc_f26_006_va_sigmet_never_emits_advisory(fname: str) -> None:
    """F26 theme V2 complement: VA SIGMET path keeps VolcanicAshSIGMET (never Advisory)."""
    tac = _read_accept(fname)
    assert lint(tac, product="SIGMET").ok is True
    result = convert(tac, product="SIGMET", profile=_PROFILE, iwxxm_version=_VERSION)
    assert result.ok is True, fname
    assert result.product == "SIGMET"
    assert _has_root(result.xml, "VolcanicAshSIGMET")
    assert not _has_root(result.xml, "VolcanicAshAdvisory")
    assert "iwxxm:VolcanicAshAdvisory" not in result.xml
    assert not _has_root(result.xml, "SIGMET")


@pytest.mark.parametrize("fname", _VAA_ACCEPT)
def test_tc_f26_006_vaa_rejected_as_sigmet(fname: str) -> None:
    tac = _read_accept(fname)
    report = lint(tac, product="SIGMET")
    assert report.ok is False, fname
    assert "MISSING_PRODUCT_KEYWORD" in {i.code for i in report.issues}
    assert by_code("MISSING_PRODUCT_KEYWORD").severity == "error"
    bad = convert(tac, product="SIGMET", profile=_PROFILE, iwxxm_version=_VERSION)
    assert bad.ok is False, fname


@pytest.mark.parametrize("fname", _VA_SIGMET_ACCEPT + ("sigmet_basic.tac",))
def test_tc_f26_006_sigmet_rejected_as_vaa(fname: str) -> None:
    tac = _read_accept(fname)
    report = lint(tac, product="VAA")
    assert report.ok is False, fname
    assert "MISSING_PRODUCT_KEYWORD" in {i.code for i in report.issues}
    bad = convert(tac, product="VAA", profile=_PROFILE, iwxxm_version=_VERSION)
    assert bad.ok is False, fname


def test_tc_f26_006_bulletin_neighbors_no_silent_swap() -> None:
    """Paired VAA + VA SIGMET: wrong hint fails; correct hint preserves distinct roots."""
    vaa = _read_accept("vaa_basic.tac")
    va = _read_accept("sigmet_v1_va_volcano.tac")

    assert lint(vaa, product="SIGMET").ok is False
    assert lint(va, product="VAA").ok is False

    a = convert(vaa, product="VAA", profile=_PROFILE, iwxxm_version=_VERSION)
    v = convert(va, product="SIGMET", profile=_PROFILE, iwxxm_version=_VERSION)
    assert a.ok and _has_root(a.xml, "VolcanicAshAdvisory")
    assert not _has_root(a.xml, "VolcanicAshSIGMET")
    assert v.ok and _has_root(v.xml, "VolcanicAshSIGMET")
    assert not _has_root(v.xml, "VolcanicAshAdvisory")

    assert convert(vaa, product="SIGMET", profile=_PROFILE, iwxxm_version=_VERSION).ok is False
    assert convert(va, product="VAA", profile=_PROFILE, iwxxm_version=_VERSION).ok is False


def test_tc_f26_006_emit_rejects_forbidden_sigmet_root() -> None:
    """T1.4 hardening: emit_vaa_annex3 refuses IR claiming VolcanicAshSIGMET."""
    from tac2iwxxm.products.vaa_tca import parse_vaa
    from tac2iwxxm.profiles.annex3_products import emit_vaa_annex3

    ir = parse_vaa(_read_accept("vaa_basic.tac"), product="VAA")
    assert ir.get("iwxxm_root") == "VolcanicAshAdvisory"
    ir["iwxxm_root"] = "VolcanicAshSIGMET"
    with pytest.raises(ValueError, match="forbidden iwxxm_root"):
        emit_vaa_annex3(ir, iwxxm_version=_VERSION)
