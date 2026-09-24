"""Offline profile-check summary and exit code (TC-LIVE-PROFILE). No network.

[Corpus: tests §TC-LIVE-PROFILE] [Corpus: product §F6]
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from tests.live.profile_check import (
    DEFAULT_SUMMARY,
    HTTP_TIMEOUT_SECONDS,
    REQUIRED_FEEDS,
    Bulletin,
    Finding,
    ProfileTarget,
    body_has_line,
    complete_vona,
    engine_check,
    extract_jma_advisory,
    first_marked_report,
    first_nonempty_line,
    first_sigmet_within_validity,
    indexed_files,
    latest_jma_text_href,
    load_semantic_profiles,
    matching_names,
    run_check,
)

_METAR = "METAR KDEN 231853Z 18010KT 10SM FEW050 22/08 A3012="
_TAF = "TAF KDEN 231720Z 2318/2424 18010KT P6SM FEW050="


def _profile(profile_id: str, *products: str) -> ProfileTarget:
    return ProfileTarget(
        profile_id=profile_id, emit_key=profile_id.lower(), products=products
    )


def _pass(_bulletin: Bulletin, _profile: ProfileTarget) -> list[Finding]:
    return []


def test_zero_exit_when_every_check_passes(tmp_path: Path) -> None:
    """A complete sample set with no findings exits 0 and writes JSON."""
    bulletins = [
        Bulletin(
            feed=feed, product=product, text=_METAR if product == "METAR" else _TAF
        )
        for feed, product in REQUIRED_FEEDS
    ]
    summary_path = tmp_path / "summary.json"
    code = run_check(
        bulletins,
        profiles=(
            _profile(
                "ICAO_2025",
                "METAR",
                "TAF",
                "SIGMET",
                "VAA",
                "SWXA",
                "AIRMET",
                "TCA",
                "VONA",
            ),
        ),
        check=_pass,
        summary_path=summary_path,
    )
    assert code == 0
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["ok"] is True
    assert payload["schema_parse_errors"] == []
    assert payload["document_errors"] == []


def test_schema_parse_is_separate_from_document_errors(tmp_path: Path) -> None:
    """SCHEMA_PARSE_ERROR is its own JSON field and still fails the command."""
    bulletins = [
        Bulletin(feed=feed, product=product, text=_METAR)
        for feed, product in REQUIRED_FEEDS
    ]

    def _split(bulletin: Bulletin, profile: ProfileTarget) -> list[Finding]:
        if bulletin.feed == "awc-metar" and profile.profile_id == "CA_ECCC":
            return [
                Finding(
                    check="schema",
                    code="SCHEMA_PARSE_ERROR",
                    message="xsd failed to compile",
                ),
                Finding(
                    check="schema",
                    code="XSD_VALIDATION_ERROR",
                    message="element not allowed",
                ),
            ]
        return []

    summary_path = tmp_path / "summary.json"
    code = run_check(
        bulletins,
        profiles=(
            _profile(
                "ICAO_2025",
                "METAR",
                "TAF",
                "SIGMET",
                "VAA",
                "SWXA",
                "AIRMET",
                "TCA",
                "VONA",
            ),
            _profile("CA_ECCC", "METAR"),
        ),
        check=_split,
        summary_path=summary_path,
    )
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert code == 1
    assert payload["schema_parse_errors"][0]["code"] == "SCHEMA_PARSE_ERROR"
    assert payload["document_errors"][0]["code"] == "XSD_VALIDATION_ERROR"
    assert "SCHEMA_PARSE_ERROR" not in {
        row["code"] for row in payload["document_errors"]
    }


def test_lint_warning_does_not_fail(tmp_path: Path) -> None:
    """Only lint errors fail. A warning stays in the summary and exits 0."""
    bulletins = [
        Bulletin(feed=feed, product=product, text=_METAR)
        for feed, product in REQUIRED_FEEDS
    ]

    def _warn(bulletin: Bulletin, _profile: ProfileTarget) -> list[Finding]:
        if bulletin.feed == "awc-taf":
            return [
                Finding(
                    check="lint",
                    code="STYLE",
                    message="warning only",
                    severity="warning",
                )
            ]
        return []

    code = run_check(
        bulletins,
        profiles=(
            _profile(
                "ICAO_2025",
                "METAR",
                "TAF",
                "SIGMET",
                "VAA",
                "SWXA",
                "AIRMET",
                "TCA",
                "VONA",
            ),
        ),
        check=_warn,
        summary_path=tmp_path / "summary.json",
    )
    assert code == 0


def test_missing_required_feed_fails(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A required feed that was not fetched fails the command."""
    bulletins = [
        Bulletin(feed=feed, product=product, text=_METAR)
        for feed, product in REQUIRED_FEEDS
        if feed != "jma-vaac"
    ]
    code = run_check(
        bulletins,
        profiles=(
            _profile(
                "ICAO_2025",
                "METAR",
                "TAF",
                "SIGMET",
                "VAA",
                "SWXA",
                "AIRMET",
                "TCA",
                "VONA",
            ),
        ),
        check=_pass,
        summary_path=tmp_path / "summary.json",
    )
    payload = json.loads((tmp_path / "summary.json").read_text(encoding="utf-8"))
    assert code == 1
    assert any(
        row["code"] == "MISSING_FEED" and row["feed"] == "jma-vaac"
        for row in payload["failures"]
    )
    assert "failure MISSING_FEED jma-vaac" in capsys.readouterr().out


def test_one_report_runs_under_each_profile_that_lists_the_product(
    tmp_path: Path,
) -> None:
    """One bulletin per feed is checked once per matching semantic profile."""
    seen: list[tuple[str, str]] = []

    def _record(bulletin: Bulletin, profile: ProfileTarget) -> list[Finding]:
        seen.append((bulletin.feed, profile.profile_id))
        return []

    bulletins = [
        Bulletin(feed=feed, product=product, text=_METAR)
        for feed, product in REQUIRED_FEEDS
    ]
    run_check(
        bulletins,
        profiles=(
            _profile("ICAO_2025", "METAR", "TAF", "SIGMET", "VAA"),
            _profile("JP_JMA", "VAA"),
            _profile("US_FAA_NWS", "METAR"),
        ),
        check=_record,
        summary_path=tmp_path / "summary.json",
    )
    assert ("jma-vaac", "ICAO_2025") in seen
    assert ("jma-vaac", "JP_JMA") in seen
    assert ("awc-metar", "US_FAA_NWS") in seen
    assert ("awc-metar", "JP_JMA") not in seen
    assert seen.count(("awc-metar", "ICAO_2025")) == 1


def test_load_semantic_profiles_skips_exchange_and_stubs() -> None:
    """Only implemented semantic profiles are targets. GLOBAL_AFS is exchange."""
    profiles = load_semantic_profiles()
    ids = {profile.profile_id for profile in profiles}
    assert "ICAO_2025" in ids
    assert "CA_ECCC" in ids
    assert "GLOBAL_AFS" not in ids
    assert "APAC_ROBEX" not in ids


def test_stdout_names_schema_parse_on_its_own_line(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    """Stdout prints schema-parse findings apart from document findings."""
    bulletins = [
        Bulletin(feed=feed, product=product, text=_METAR)
        for feed, product in REQUIRED_FEEDS
    ]

    def _parse(_bulletin: Bulletin, _profile: ProfileTarget) -> list[Finding]:
        return [
            Finding(check="schema", code="SCHEMA_PARSE_ERROR", message="compile failed")
        ]

    run_check(
        bulletins,
        profiles=(
            _profile(
                "CA_ECCC",
                "METAR",
                "TAF",
                "SIGMET",
                "VAA",
                "SWXA",
                "AIRMET",
                "TCA",
                "VONA",
            ),
        ),
        check=_parse,
        summary_path=tmp_path / "summary.json",
    )
    out = capsys.readouterr().out
    assert "SCHEMA_PARSE_ERROR" in out
    assert "schema-parse" in out.lower()


_LISTING = """
<table>
<tr><td><a href="older.txt">older.txt</a></td><td align="right">21-Mar-2026 01:00  </td></tr>
<tr><td><a href="newer.txt">newer.txt</a></td><td align="right">22-Mar-2026 01:00  </td></tr>
</table>
"""


def test_indexed_files_are_newest_first() -> None:
    rows = indexed_files(_LISTING)
    names = [name for _stamp, name in rows]
    assert names == ["newer.txt", "older.txt"]
    assert [name for _stamp, name in matching_names(rows, "new")] == ["newer.txt"]


def test_sigmet_chunk_keeps_the_matching_bulletin() -> None:
    body = (
        "Hazard: TS\nWSMX31 KNHC\nSIGMET ALPHA\n\nHazard: TURB\nCONVECTIVE SIGMET 1E\n"
    )
    assert first_marked_report(body, "CONVECTIVE SIGMET") == "CONVECTIVE SIGMET 1E"
    assert first_nonempty_line("\nMETAR KDEN 231853Z=\n") == "METAR KDEN 231853Z="


def test_international_sigmet_skips_an_overlong_validity() -> None:
    body = (
        "Hazard: TS\n"
        "WSFJ01 NFFN 231940\n"
        "NFFF SIGMET 05 VALID 231940/242340 NFFN-\n"
        "NFFF FIR EMBD TS\n"
        "Hazard: TURB\n"
        "WSCN31 ZGGG 231900\n"
        "ZGZU SIGMET 1 VALID 231900/232300 ZGGG-\n"
        "ZGZU FIR SEV TURB\n"
    )
    chosen = first_sigmet_within_validity(body)
    assert chosen is not None
    assert "ZGZU SIGMET" in chosen
    assert "NFFF" not in chosen


def test_international_sigmet_keeps_the_first_when_all_exceed_the_limit() -> None:
    body = (
        "Hazard: TS\n"
        "NFFF SIGMET 05 VALID 231940/242340 NFFN-\n"
        "NFFF FIR EMBD TS\n"
        "Hazard: TS\n"
        "NFFF SIGMET 06 VALID 231900/242300 NFFN-\n"
        "NFFF FIR SEV TURB\n"
    )
    chosen = first_sigmet_within_validity(body)
    assert chosen is not None
    assert chosen.startswith("NFFF SIGMET 05")


def test_vona_marker_is_a_whole_line() -> None:
    assert body_has_line("VONA\nVOLCANO: UNKNOWN\n", "VONA")
    assert not body_has_line("VOLCANO: SAKURAJIMA\n", "VONA")


def test_complete_vona_requires_the_observatory_line() -> None:
    truncated = "WMPA01 PHVO 230952\nVONA\nCURRENT COLOUR CODE:?ORANGE\n"
    complete = "WMNZ02 NZKL 171140\nVONA\nSVO: EARTH SCIENCES NEW ZEALAND\n"
    assert complete_vona(complete)
    assert not complete_vona(truncated)
    assert not complete_vona("WVJP31 RJTD 232037\nRJJJ SIGMET U06 VA ERUPTION\n")


def test_jma_page_extracts_advisory_text() -> None:
    index = (
        '<a href="TextData/2026/20260922_1_0100_Text.html">a</a>'
        '<a href="TextData/2026/20260923_1_0235_Text.html">b</a>'
    )
    assert latest_jma_text_href(index) == "TextData/2026/20260923_1_0235_Text.html"
    page = "<!-- VAA Text Start -->FVFE01 RJTD<br>VA ADVISORY<!-- VAA Text End -->"
    assert extract_jma_advisory(page) == "FVFE01 RJTD\nVA ADVISORY"


def test_timeout_and_summary_path_are_pinned() -> None:
    assert HTTP_TIMEOUT_SECONDS == 30.0
    assert Path("artifacts/live-profile/summary.json") == DEFAULT_SUMMARY


def test_annex3_metar_engine_check_has_no_error() -> None:
    bulletin = Bulletin(
        feed="awc-metar",
        product="METAR",
        text="METAR EGLL 231520Z 21008KT 9999 FEW030 12/08 Q1020 NOSIG=",
    )
    findings = engine_check(
        bulletin,
        ProfileTarget(profile_id="ICAO_2025", emit_key="annex3", products=("METAR",)),
    )
    assert [item for item in findings if item.severity == "error"] == []


def test_national_profile_does_not_report_missing_engine() -> None:
    """A profile with no lint or schema module is checked with the Annex 3 engine."""
    bulletin = Bulletin(
        feed="awc-metar",
        product="METAR",
        text="METAR EGLL 231520Z 21008KT 9999 FEW030 12/08 Q1020 NOSIG=",
    )
    findings = engine_check(
        bulletin,
        ProfileTarget(profile_id="AU_BOM", emit_key="au_bom", products=("METAR",)),
    )
    codes = {item.code for item in findings if item.severity == "error"}
    assert "LINT_ERROR" not in codes
    assert "INVALID_PROFILE" not in codes
    assert codes == set()


def test_canada_uses_annex3_when_national_lint_does_not_apply() -> None:
    """Canada lint does not cover SIGMET; the check uses Annex 3 rules."""
    bulletin = Bulletin(
        feed="awc-sigmet-intl",
        product="SIGMET",
        text=(
            "YUDD SIGMET 2 VALID 101200/101600 YUSO - YUDD FIR SEV TURB FCST "
            "WI N2700 E01700 - N2700 E02000 - N2500 E02000 - N2500 E01700 - "
            "N2700 E01700 FL250/370 MOV E 20KT NC="
        ),
    )
    findings = engine_check(
        bulletin,
        ProfileTarget(profile_id="CA_ECCC", emit_key="ca_eccc", products=("SIGMET",)),
    )
    messages = " ".join(item.message for item in findings)
    assert "not applicable" not in messages
    assert "UNSUPPORTED_PROFILE" not in {item.code for item in findings}
