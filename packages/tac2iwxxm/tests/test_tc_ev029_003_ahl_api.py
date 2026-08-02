"""TC-EV029-003 T1.1: Shared AHL / BBB / T1T2 / filename API (UJ-043 / F6.bulletin).

Red fixtures for the M1 ``tac2iwxxm.bulletin`` surface in
``docs/sessions/S036-eight-family-ahl-rules-823/reports/mining/ahl-design-note.md`` §3/§6.
Canonical map: ``docs/domain/IWXXM_CONVERSION.md`` §AHL / bulletin (EV-029).
Implementation lands in T1.2.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

FIXTURES = Path(__file__).resolve().parent / "fixtures"
AHL_FIXTURES = FIXTURES / "ahl"

# TAC T1T2 → IWXXM T1T2 (eight families + SWXA); design-note §3.2 / IWXXM_CONVERSION.
_TAC_TO_IWXXM: tuple[tuple[str, str, str], ...] = (
    ("sa_metar.txt", "SA", "LA"),
    ("sp_speci.txt", "SP", "LP"),
    ("fc_taf_short.txt", "FC", "LC"),
    ("ft_taf_long.txt", "FT", "LT"),
    ("ws_sigmet.txt", "WS", "LS"),
    ("wv_va_sigmet.txt", "WV", "LV"),
    ("wc_tc_sigmet.txt", "WC", "LY"),
    ("wa_airmet.txt", "WA", "LW"),
    ("fv_vaa.txt", "FV", "LU"),
    ("fk_tca.txt", "FK", "LK"),
    ("fn_swxa.txt", "FN", "LN"),
)


def _read_ahl(name: str) -> str:
    return (AHL_FIXTURES / name).read_text(encoding="utf-8")


def test_ahl_api_public_exports() -> None:
    """M1 public surface must be importable from tac2iwxxm (design-note §3)."""
    import tac2iwxxm

    for name in (
        "parse_ahl",
        "format_ahl",
        "map_t1t2",
        "bbb_to_report_status",
        "iwxxm_filename",
        "AhlParts",
    ):
        assert getattr(tac2iwxxm, name, None) is not None, f"missing export: {name}"


@pytest.mark.parametrize(("fixture", "tac_tt", "iwxxm_tt"), _TAC_TO_IWXXM)
def test_parse_ahl_and_map_t1t2_for_each_tac_designator(fixture: str, tac_tt: str, iwxxm_tt: str) -> None:
    """Accept each TAC T1T2 minimal AHL line; map_t1t2 yields IWXXM L* (TC-EV029-003)."""
    from tac2iwxxm import map_t1t2, parse_ahl

    line = _read_ahl(fixture).strip()
    parts = parse_ahl(line)
    assert parts.tt == tac_tt
    assert parts.ii  # ii present on AhlParts (gap vs BulletinMeta today)
    assert len(parts.ii) == 2
    assert parts.cccc
    assert parts.yygggg == "121200" or parts.yygggg == "121230"
    assert parts.bbb is None
    assert map_t1t2(tac_tt) == iwxxm_tt
    assert parts.iwxxm_tt == iwxxm_tt


@pytest.mark.parametrize(
    ("fixture", "bbb", "status"),
    (
        ("sa_bbb_cca.txt", "CCA", "CORRECTION"),
        ("sa_bbb_aaa.txt", "AAA", "AMENDMENT"),
        ("sa_bbb_rra.txt", "RRA", "NORMAL"),
    ),
)
def test_bbb_prefix_families_map_to_report_status(fixture: str, bbb: str, status: str) -> None:
    """CCA→CORRECTION, AAA→AMENDMENT, RRA→NORMAL (absent/RRx)."""
    from tac2iwxxm import bbb_to_report_status, parse_ahl

    parts = parse_ahl(_read_ahl(fixture).strip())
    assert parts.bbb == bbb
    assert bbb_to_report_status(bbb) == status
    assert parts.report_status == status


def test_bbb_absent_is_normal() -> None:
    from tac2iwxxm import bbb_to_report_status, parse_ahl

    parts = parse_ahl(_read_ahl("sa_metar.txt").strip())
    assert parts.bbb is None
    assert bbb_to_report_status(None) == "NORMAL"
    assert parts.report_status == "NORMAL"


@pytest.mark.parametrize(
    "fixture",
    (
        "sa_bbb_invalid_acr.txt",  # GIFTs-broad [ACR]{2}[A-Z] would accept
        "sa_bbb_invalid_ccy.txt",  # third letter Y — outside A…X
        "sa_bbb_invalid_bare_a.txt",
    ),
)
def test_invalid_bbb_rejected(fixture: str) -> None:
    """Reject over-broad / out-of-family BBB (AHL page v1.0.1 prefixes)."""
    from tac2iwxxm import BulletinSplitError, parse_ahl

    with pytest.raises(BulletinSplitError) as exc_info:
        parse_ahl(_read_ahl(fixture).strip())
    assert exc_info.value.code in {"bulletin_split_failed", "invalid_bbb"}


@pytest.mark.parametrize("bbb", ("CCY", "AAZ", "RRY", "PAA", "YYY"))
def test_bbb_third_letter_y_z_and_non_families_rejected(bbb: str) -> None:
    """Y/Z third letter and non AA/CC/RR families are not reportStatus BBB (doc fixture)."""
    from tac2iwxxm import BulletinSplitError, bbb_to_report_status

    with pytest.raises((BulletinSplitError, ValueError)):
        bbb_to_report_status(bbb)


def test_iwxxm_filename_uses_mapped_t1t2_not_tac() -> None:
    """Filename segment uses IWXXM T1T2 (SA→LA), not TAC SA (design-note §3.4)."""
    from tac2iwxxm import iwxxm_filename, parse_ahl

    parts = parse_ahl(_read_ahl("sa_metar.txt").strip())
    issued = datetime(2026, 8, 1, 12, 15, 30, tzinfo=UTC)
    name = iwxxm_filename(parts, issued_at=issued, gzip=False)
    assert name.startswith("A_LA")
    assert not name.startswith("A_SA")
    assert "SAUS31KZNY121200" not in name  # TAC T1T2 must not appear as A_ segment
    assert "LAUS31KZNY121200" in name
    assert "_C_KZNY_20260801121530" in name
    assert name.endswith(".xml")


def test_iwxxm_filename_optional_bbb_and_gzip() -> None:
    from tac2iwxxm import iwxxm_filename, parse_ahl

    parts = parse_ahl(_read_ahl("sa_bbb_cca.txt").strip())
    issued = datetime(2026, 8, 1, 12, 15, 30, tzinfo=UTC)
    name = iwxxm_filename(parts, issued_at=issued, gzip=True)
    assert "LAUS31KZNY121200CCA" in name
    assert name.endswith(".xml.gz")


def test_format_ahl_round_trip() -> None:
    from tac2iwxxm import format_ahl, parse_ahl

    line = "SAUS31 KZNY 121200 CCA"
    parts = parse_ahl(line)
    assert format_ahl(parts) == line


def test_taf_ahl_body_split_succeeds_m4() -> None:
    """TAF AHL+body: AHL helpers OK; split_bulletin(product=TAF) lands in M4."""
    from tac2iwxxm import parse_ahl, split_bulletin

    text = _read_ahl("fc_taf_with_body.txt")
    ahl_line = text.splitlines()[0]
    parts = parse_ahl(ahl_line)
    assert parts.tt == "FC"
    assert parts.iwxxm_tt == "LC"

    split = split_bulletin(text, product="TAF")
    assert split.meta.tt == "FC"
    assert split.meta.report_count == 1
    assert split.reports[0].startswith("TAF ")


def test_unsupported_product_body_raises_clear_error() -> None:
    """TCA/SWXA still raise a clear split error until their milestones (M10/M11)."""
    from tac2iwxxm import BulletinSplitError, split_bulletin

    text = _read_ahl("fc_taf_with_body.txt")
    with pytest.raises(BulletinSplitError) as exc_info:
        split_bulletin(text, product="TCA")
    assert exc_info.value.code == "bulletin_split_failed"
    assert exc_info.value.message  # non-empty operator-facing detail


def test_metar_multi_ahl_regression_tc_f6_030() -> None:
    """METAR multi-report bulletin remains green (TC-F6-030)."""
    from tac2iwxxm import split_bulletin

    text = (FIXTURES / "metar_multi_ahl.txt").read_text(encoding="utf-8")
    result = split_bulletin(text, product="METAR")
    assert result.meta.ahl == "SAUS31 KZNY 121200"
    assert result.meta.report_count == 2
    assert len(result.reports) == 2
