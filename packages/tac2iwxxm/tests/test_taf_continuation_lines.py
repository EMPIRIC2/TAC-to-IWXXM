"""A multi-line TAF stays one forecast, and AMD NOT SKED is not an amendment."""

from __future__ import annotations

from tac2iwxxm.taf_lines import join_taf_entries, join_taf_lines, starts_taf_report

from tac2iwxxm import convert

_MKJP = "TAF MKJP 081700Z 0818/0918 09012KT 9999 SCT018\nBECMG 0902/0904 14008KT\nTEMPO 0906/0912 4000 -SHRA BKN014="
_TRAILER = "TAF MKJP 081200Z 0812/0912 12010KT 9999 FEW020 AMD NOT SKED="
_REAL_AMD = "TAF AMD MKJP 081200Z 0812/0912 12010KT 9999 FEW020 AMD NOT SKED="


def test_three_line_mkjp_taf_is_one_forecast() -> None:
    result = convert(_MKJP, product="TAF", bulletin_date="2026-10-08")
    assert result.ok is True
    assert result.xml is not None
    assert result.xml.count("<iwxxm:TAF") == 1
    assert "BECMG" in result.xml or "BECOMING" in result.xml
    assert "TEMPO" in result.xml
    assert "PARSE_ERROR" not in [issue.code for issue in result.issues]


def test_continuation_lines_join_and_a_second_station_stays_separate() -> None:
    lines = [
        "TAF MKJP 081700Z 0818/0918 09012KT 9999 SCT018",
        "BECMG 0902/0904 14008KT",
        "TAF TNCM 081700Z 0818/0918 12010KT 9999 FEW020",
        "TEMPO 0906/0912 4000 -SHRA",
    ]
    joined = join_taf_lines(lines)
    assert len(joined) == 2
    assert joined[0].startswith("TAF MKJP")
    assert "BECMG 0902/0904 14008KT" in joined[0]
    assert joined[1].startswith("TAF TNCM")
    assert "TEMPO 0906/0912 4000 -SHRA" in joined[1]


def test_trailer_and_keywordless_header_and_blank_lines() -> None:
    assert starts_taf_report("MKJP 081200Z 0812/0912") is True
    assert starts_taf_report("TAF COR TNCM 081200Z") is True
    assert starts_taf_report("AMD NOT SKED") is False
    assert starts_taf_report("  ") is False
    joined = join_taf_lines(["", "TAF MKJP 081200Z 0812/0912 12010KT", "", "AMD NOT SKED"])
    assert joined == ["TAF MKJP 081200Z 0812/0912 12010KT AMD NOT SKED"]
    entries = join_taf_entries([("BECMG 0902/0904", 4), ("TAF MKJP 081200Z", 28), ("AMD NOT SKED", 48)])
    assert entries == [("BECMG 0902/0904", 4), ("TAF MKJP 081200Z AMD NOT SKED", 28)]


def test_amd_not_sked_does_not_set_amendment() -> None:
    result = convert(_TRAILER, product="TAF", bulletin_date="2026-10-08")
    assert result.ok is True
    assert result.xml is not None
    assert 'reportStatus="NORMAL"' in result.xml
    assert 'reportStatus="AMENDMENT"' not in result.xml


def test_real_amd_still_sets_amendment_when_the_trailer_is_also_present() -> None:
    result = convert(_REAL_AMD, product="TAF", bulletin_date="2026-10-08")
    assert result.ok is True
    assert result.xml is not None
    assert 'reportStatus="AMENDMENT"' in result.xml


def test_a_line_that_is_not_a_taf_still_fails_in_plain_language() -> None:
    result = convert("HELLO WORLD", product="TAF", bulletin_date="2026-10-08")
    assert result.ok is False
    assert any(issue.code == "PARSE_ERROR" and issue.message == "unable to parse TAF header" for issue in result.issues)
