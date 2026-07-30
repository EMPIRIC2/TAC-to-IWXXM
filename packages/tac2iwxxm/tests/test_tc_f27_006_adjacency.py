"""TC-F27-006 / F27 theme T2 — TCA ↔ TC SIGMET adjacency (S027 / EV-021 T3.3).

HARD guards from vaa-tca-theme-fixture-map.md:
- ``product=tca`` never emits ``iwxxm:TropicalCycloneSIGMET`` (advisory root only)
- TC SIGMET quality (#738) is OOS this cycle — use general SIGMET keepers for
  cross-product rejection (never silent-swap TCA ↔ SIGMET)

Always write “F27 theme T2” (not F20 TAF T2) — D-S027-EV021-s02m1-1.
T3.4 hardens emit/product guards if any assertion fails.
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

# F27 theme T1 accept pack + baseline — each must keep TropicalCycloneAdvisory under product=tca.
_TCA_ACCEPT = (
    "tca_basic.tac",
    "tca_t1_unnamed.tac",
    "tca_t1_rmk_nil_no_msg.tac",
    "tca_t1_cb_nil.tac",
)

# General SIGMET accept — must never silent-swap to TCA advisory root (#738 OOS for TC SIGMET).
_SIGMET_ACCEPT = ("sigmet_basic.tac",)


def _read_accept(name: str) -> str:
    path = TAC_VALIDATE / name
    assert path.is_file(), f"missing fixture: {path}"
    return path.read_text(encoding="utf-8")


def _has_root(xml: str, local: str) -> bool:
    """True when ``xml`` opens with ``<iwxxm:{local} `` (avoids child-element false positives)."""
    return f"<iwxxm:{local} " in xml


def test_tc_f27_006_keyword_presence_for_auto_detect() -> None:
    """TC ADVISORY vs SIGMET must not blur for auto-detect / product hint."""
    tca = _read_accept("tca_basic.tac")
    sig = _read_accept("sigmet_basic.tac")
    assert "TC ADVISORY" in tca.upper()
    assert "SIGMET" not in tca.upper().split("TC ADVISORY", 1)[0]
    assert "SIGMET" in sig.upper()
    assert "TC ADVISORY" not in sig.upper()
    assert lint(tca, product="SIGMET").ok is False
    assert lint(sig, product="TCA").ok is False


@pytest.mark.parametrize("fname", _TCA_ACCEPT)
def test_tc_f27_006_tca_keeps_advisory_root(fname: str) -> None:
    """F27 theme T2: product=tca → TropicalCycloneAdvisory only (never TropicalCycloneSIGMET)."""
    tac = _read_accept(fname)
    assert lint(tac, product="TCA").ok is True
    result = convert(tac, product="TCA", profile=_PROFILE, iwxxm_version=_VERSION)
    assert result.ok is True, fname
    assert result.product == "TCA"
    assert _has_root(result.xml, "TropicalCycloneAdvisory")
    assert not _has_root(result.xml, "TropicalCycloneSIGMET")
    assert not _has_root(result.xml, "SIGMET")
    assert not _has_root(result.xml, "VolcanicAshSIGMET")
    assert not _has_root(result.xml, "VolcanicAshAdvisory")
    assert "iwxxm:TropicalCycloneSIGMET" not in result.xml


@pytest.mark.parametrize("fname", _SIGMET_ACCEPT)
def test_tc_f27_006_sigmet_never_emits_tca_advisory(fname: str) -> None:
    """F27 theme T2 complement: SIGMET path never emits TropicalCycloneAdvisory."""
    tac = _read_accept(fname)
    assert lint(tac, product="SIGMET").ok is True
    result = convert(tac, product="SIGMET", profile=_PROFILE, iwxxm_version=_VERSION)
    assert result.ok is True, fname
    assert result.product == "SIGMET"
    assert not _has_root(result.xml, "TropicalCycloneAdvisory")
    assert "iwxxm:TropicalCycloneAdvisory" not in result.xml


@pytest.mark.parametrize("fname", _TCA_ACCEPT)
def test_tc_f27_006_tca_rejected_as_sigmet(fname: str) -> None:
    tac = _read_accept(fname)
    report = lint(tac, product="SIGMET")
    assert report.ok is False, fname
    assert "MISSING_PRODUCT_KEYWORD" in {i.code for i in report.issues}
    assert by_code("MISSING_PRODUCT_KEYWORD").severity == "error"
    bad = convert(tac, product="SIGMET", profile=_PROFILE, iwxxm_version=_VERSION)
    assert bad.ok is False, fname


@pytest.mark.parametrize("fname", _SIGMET_ACCEPT)
def test_tc_f27_006_sigmet_rejected_as_tca(fname: str) -> None:
    tac = _read_accept(fname)
    report = lint(tac, product="TCA")
    assert report.ok is False, fname
    assert "MISSING_PRODUCT_KEYWORD" in {i.code for i in report.issues}
    bad = convert(tac, product="TCA", profile=_PROFILE, iwxxm_version=_VERSION)
    assert bad.ok is False, fname


def test_tc_f27_006_bulletin_neighbors_no_silent_swap() -> None:
    """Paired TCA + SIGMET: wrong hint fails; correct hint preserves distinct roots."""
    tca = _read_accept("tca_basic.tac")
    sig = _read_accept("sigmet_basic.tac")

    assert lint(tca, product="SIGMET").ok is False
    assert lint(sig, product="TCA").ok is False

    a = convert(tca, product="TCA", profile=_PROFILE, iwxxm_version=_VERSION)
    s = convert(sig, product="SIGMET", profile=_PROFILE, iwxxm_version=_VERSION)
    assert a.ok and _has_root(a.xml, "TropicalCycloneAdvisory")
    assert not _has_root(a.xml, "TropicalCycloneSIGMET")
    assert s.ok and not _has_root(s.xml, "TropicalCycloneAdvisory")

    assert convert(tca, product="SIGMET", profile=_PROFILE, iwxxm_version=_VERSION).ok is False
    assert convert(sig, product="TCA", profile=_PROFILE, iwxxm_version=_VERSION).ok is False


def test_tc_f27_006_emit_rejects_forbidden_sigmet_root() -> None:
    """T3.4 hardening: emit_tca_annex3 refuses IR claiming TropicalCycloneSIGMET."""
    from tac2iwxxm.products.vaa_tca import parse_tca
    from tac2iwxxm.profiles.annex3_products import emit_tca_annex3

    ir = parse_tca(_read_accept("tca_basic.tac"), product="TCA")
    assert ir.get("iwxxm_root") == "TropicalCycloneAdvisory"
    ir["iwxxm_root"] = "TropicalCycloneSIGMET"
    with pytest.raises(ValueError, match="forbidden iwxxm_root"):
        emit_tca_annex3(ir, iwxxm_version=_VERSION)
