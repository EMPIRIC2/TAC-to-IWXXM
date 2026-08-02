"""TC-F6-030 T0: WMO AHL bulletin split → N TAC reports (UJ-011 / F6.bulletin).

Spec: docs/test-plan.md TC-F6-030; docs/api-contract.md convert-bulletin bulletin_meta;
docs/feature-list.md F6.bulletin; Q4=A (with/before F6.a).
"""

from __future__ import annotations

from pathlib import Path

import msgspec
import pytest

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _read(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def test_split_bulletin_exports_public_entrypoints() -> None:
    import tac2iwxxm

    assert callable(getattr(tac2iwxxm, "split_bulletin", None))
    assert getattr(tac2iwxxm, "BulletinMeta", None) is not None
    assert getattr(tac2iwxxm, "BulletinSplit", None) is not None
    assert getattr(tac2iwxxm, "BulletinSplitError", None) is not None


def test_bulletin_meta_and_split_are_msgspec_structs() -> None:
    from tac2iwxxm import BulletinMeta, BulletinSplit

    assert issubclass(BulletinMeta, msgspec.Struct)
    assert issubclass(BulletinSplit, msgspec.Struct)


def test_split_multi_report_metar_ahl_yields_n_reports() -> None:
    """Fixture yields expected report count (TC-F6-030 pass criterion)."""
    from tac2iwxxm import split_bulletin

    text = _read("metar_multi_ahl.txt")
    result = split_bulletin(text, product="METAR")

    assert result.meta.ahl == "SAUS31 KZNY 121200"
    assert result.meta.tt == "SA"
    assert result.meta.aa == "US"
    assert result.meta.cccc == "KZNY"
    assert result.meta.yygggg == "121200"
    assert result.meta.bbb is None
    assert result.meta.report_count == 2
    assert len(result.reports) == 2
    assert result.reports[0].startswith("METAR KJFK")
    assert result.reports[0].rstrip().endswith("=")
    assert result.reports[1].startswith("METAR KLGA")
    assert result.reports[1].rstrip().endswith("=")


def test_split_single_report_ahl_still_works() -> None:
    from tac2iwxxm import split_bulletin

    result = split_bulletin(_read("metar_single_ahl.txt"), product="METAR")
    assert result.meta.report_count == 1
    assert len(result.reports) == 1
    assert "KJFK" in result.reports[0]


def test_split_ahl_optional_bbb() -> None:
    from tac2iwxxm import split_bulletin

    result = split_bulletin(_read("metar_ahl_with_bbb.txt"), product="METAR")
    assert result.meta.ahl == "SAUS31 KZNY 121200 CCA"
    assert result.meta.bbb == "CCA"
    assert result.meta.report_count == 1


def test_split_empty_body_raises_empty_bulletin() -> None:
    from tac2iwxxm import BulletinSplitError, split_bulletin

    text = "SAUS31 KZNY 121200\n"
    with pytest.raises(BulletinSplitError) as exc_info:
        split_bulletin(text, product="METAR")
    assert exc_info.value.code == "empty_bulletin"


def test_split_missing_ahl_raises_bulletin_split_failed() -> None:
    from tac2iwxxm import BulletinSplitError, split_bulletin

    text = "METAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012=\n"
    with pytest.raises(BulletinSplitError) as exc_info:
        split_bulletin(text, product="METAR")
    assert exc_info.value.code == "bulletin_split_failed"


def test_split_speci_product_uses_sp_ahl() -> None:
    from tac2iwxxm import split_bulletin

    text = "SPUS31 KZNY 121230\nSPECI KJFK 121225Z 18015G25KT 3SM -RA BKN015 18/16 A2995=\n"
    result = split_bulletin(text, product="SPECI")
    assert result.meta.tt == "SP"
    assert result.meta.aa == "US"
    assert result.meta.report_count == 1
    assert result.reports[0].startswith("SPECI KJFK")


def test_split_unsupported_product_raises() -> None:
    from tac2iwxxm import BulletinSplitError, split_bulletin

    text = _read("metar_multi_ahl.txt")
    with pytest.raises(BulletinSplitError) as exc_info:
        split_bulletin(text, product="NOTAPRODUCT")
    assert exc_info.value.code == "bulletin_split_failed"


def test_split_swxa_fn_bulletin() -> None:
    """SWXA FN AHL + SWX ADVISORY body (EV-029 M11 / TC-F28-006)."""
    from tac2iwxxm import split_bulletin

    text = (Path(__file__).resolve().parent / "fixtures" / "swxa" / "swxa_ahl_normal.txt").read_text(encoding="utf-8")
    result = split_bulletin(text, product="SWXA")
    assert result.meta.tt == "FN"
    assert result.meta.report_count == 1
    assert result.reports[0].startswith("SWX ADVISORY")


def test_split_metar_product_ignores_speci_body() -> None:
    from tac2iwxxm import BulletinSplitError, split_bulletin

    text = "SAUS31 KZNY 121200\nSPECI KJFK 121225Z 18015G25KT 3SM -RA BKN015 18/16 A2995=\n"
    with pytest.raises(BulletinSplitError) as exc_info:
        split_bulletin(text, product="METAR")
    assert exc_info.value.code == "empty_bulletin"


def test_split_ignores_tac_before_ahl_header() -> None:
    """TAC before the AHL must not be treated as part of this bulletin (PR #704)."""
    from tac2iwxxm import split_bulletin

    text = (
        "METAR KORD 121151Z 27010KT 10SM FEW050 20/12 A3015=\n"
        "SAUS31 KZNY 121200\n"
        "METAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012=\n"
    )
    result = split_bulletin(text, product="METAR")
    assert result.meta.report_count == 1
    assert result.reports[0].startswith("METAR KJFK")
    assert "KORD" not in result.reports[0]
