"""Report keyword overrides a mismatched form product.

[Corpus: product §F9] [Corpus: tests]
"""

from __future__ import annotations

from tac_decoding.decode import DecodeSegment, _build_summary, _fmt_wx, _sentence_from_segment, decode_tac

SPECI = (
    "SPECI YUDO 151115Z 05025G37KT 3000 1200NE +TSRA BKN005CB 25/22 Q1008 TEMPO TL1200 0600 BECMG AT1200 8000 NSW NSC="
)


def test_report_keyword_overrides_mismatched_product() -> None:
    result = decode_tac(SPECI, product="TCA")
    assert result.product == "SPECI"
    assert all("TCA token" not in seg.explanation for seg in result.segments)


def test_non_keyword_keeps_requested_product() -> None:
    result = decode_tac("YUDO 151115Z 05025KT", product="METAR")
    assert result.product == "METAR"


def test_blank_report_keeps_requested_product() -> None:
    result = decode_tac("\n\n", product="SPECI")
    assert result.product == "SPECI"


def test_tropical_cyclone_advisory_stays_tca() -> None:
    result = decode_tac("TC ADVISORY\nDTG: 20240930/1200Z", product="TCA")
    assert result.product == "TCA"


def test_summary_collapses_repeated_clauses() -> None:
    repeated = DecodeSegment(start=0, end=3, code="NSW", explanation="No significant weather")
    other = DecodeSegment(start=4, end=7, code="NSC", explanation="No significant cloud")
    blank = DecodeSegment(start=8, end=8, code="X", explanation="   ")
    summary = _build_summary("SPECI", [repeated, repeated, other, blank], [])
    assert summary.count("No significant weather") == 1
    assert "No significant cloud" in summary


class _EmptyWeather:
    def group(self, name: str) -> str | None:
        return {"int": None, "desc": None, "phen": ""}[name]


def test_empty_weather_phrase_names_the_group() -> None:
    assert _fmt_wx(_EmptyWeather(), forecast=False) == "Weather group"  # type: ignore[arg-type]


def test_named_station_sentence_keeps_the_place() -> None:
    named = DecodeSegment(
        start=0,
        end=4,
        code="KJFK",
        explanation="ICAO station location indicator — Test Field",
    )
    assert _sentence_from_segment(named) == "station Test Field (KJFK)"
