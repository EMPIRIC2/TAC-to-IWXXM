"""HF-sigmet-quebec-header — US domestic WS SIGMET ``VALID UNTIL`` parse + split.

Operator paste with phonetic series (QUEBEC) and ``VALID UNTIL`` (no ICAO
``ddhhmm/ddhhmm`` period) previously failed convert with
``unable to parse SIGMET header`` and Live decode / heading paste with
``No TAC reports found after the abbreviated heading``.

[Corpus: product §F23] [Corpus: domain] [Corpus: tests]
[Corpus: evolve-auto/test-matrix.md]
"""

from __future__ import annotations

import pytest
from tac2iwxxm.bulletin import _is_kept_sigmet_report, split_bulletin
from tac2iwxxm.geometry.reference_point import UnknownVOR
from tac2iwxxm.heading_paste import HeadingPasteError, reports_for_convert
from tac2iwxxm.slot_builders.sigmet_airmet import parse_sigmet
from tac_validate import lint

from tac2iwxxm import BulletinSplitError, convert

# Hermetic VOR coords for the exact operator TAC (CI may lack OpenAIP / table rows).
_QUEBEC_VOR_STUB: dict[str, dict[str, float]] = {
    "MPV": {"lat": 44.085499, "lon": -72.449402},
    "BOS": {"lat": 42.357399, "lon": -70.989502},
    "PVD": {"lat": 41.7243, "lon": -71.429604},
    "HNK": {"lat": 42.063099, "lon": -75.316299},
    "MSS": {"lat": 44.936157, "lon": -74.844304},
    "ONP": {"lat": 44.575401, "lon": -124.061},
}


@pytest.fixture(autouse=True)
def _stub_quebec_vor_table(monkeypatch: pytest.MonkeyPatch) -> None:
    """Stub resolve_vor so success paths stay hermetic without live navaid sources."""

    def _resolve(vor_id: str, table: dict[str, dict[str, float]] | None = None) -> tuple[float, float]:
        lookup = table if table is not None else _QUEBEC_VOR_STUB
        row = lookup.get(vor_id.upper())
        if row is None:
            raise UnknownVOR(vor_id.upper())
        return float(row["lat"]), float(row["lon"])

    monkeypatch.setattr("tac2iwxxm.geometry.reference_point.resolve_vor", _resolve)

# Exact failing operator paste (HF repro).
_QUEBEC = """\
WSUS01 KKCI 270354
BOSQ WS 270354
SIGMET QUEBEC 5 VALID UNTIL 270754
NH VT MA RI CT NY PA AND CSTL WTRS
FROM 80NE MPV TO 20NNE BOS TO PVD TO 20SW HNK TO 50SW MSS TO 80NE
MPV
OCNL SEV TURB BLW 150. DUE TO STG LOW LVL WNDS AND STG UDDFS AND
LLWS. CONDS CONTG BYD 0754Z.
"""

# Same Quebec geometry; different series / optional trailing Z on VALID UNTIL.
_YANKEE = """\
WSUS06 KKCI 312208
SFOY WS 312208
SIGMET YANKEE 1 VALID UNTIL 010208
NH VT MA RI CT NY PA AND CSTL WTRS
FROM 80NE MPV TO 20NNE BOS TO PVD TO 20SW HNK TO 50SW MSS TO 80NE
MPV
OCNL SEV TURB BLW 150.
"""

_VICTOR_Z = """\
WSUS05 KKCI 030721
SLCV WS 030721
SIGMET VICTOR 1 VALID UNTIL 031121Z
NH VT MA RI CT NY PA AND CSTL WTRS
FROM 80NE MPV TO 20NNE BOS TO PVD TO 20SW HNK TO 50SW MSS TO 80NE
MPV
OCNL SEV TURB BLW 150.
"""

_NO_OFFICE = """\
WSUS01 KKCI 270354
SIGMET QUEBEC 5 VALID UNTIL 270754
NH VT MA RI CT NY PA AND CSTL WTRS
FROM 80NE MPV TO 20NNE BOS TO PVD TO 20SW HNK TO 50SW MSS TO 80NE
MPV
OCNL SEV TURB BLW 150.
"""

_ICAO = (
    "YUDD SIGMET 2 VALID 101200/101600 YUSO- "
    "YUDD SHANLON FIR/UIR OBSC TS FCST S OF N54 AND E OF W012 TOP FL390 MOV E 20KT WKN="
)

_MALFORMED = "SIGMET QUEBEC VALID UNTIL NOTIME NH FROM 80NE MPV OCNL SEV TURB BLW 150."

_MISSING_PHENOMENON = """\
WSUS01 KKCI 270354
BOSQ WS 270354
SIGMET QUEBEC 5 VALID UNTIL 270754
NH VT
FROM 80NE MPV TO 20NNE BOS TO PVD TO 20SW HNK TO 50SW MSS TO 80NE
MPV
CONDS CONTG BYD 0754Z.
"""


# --- Success paths (S) -----------------------------------------------------------------


def test_hf_quebec_parse_success() -> None:
    """S: exact Quebec TAC parses with series, period, SEV_TURB, BLW 150, polygon."""
    ir = parse_sigmet(_QUEBEC)
    assert ir["us_domestic_ws"] is True
    assert ir["fir"] == "BOSQ"
    assert ir["mwo"] == "KKCI"
    assert ir["sequence"] == 5
    assert ir["sequence_label"] == "QUEBEC 5"
    assert ir["phenomenon"] == "SEV_TURB"
    assert (ir["valid_from_day"], ir["valid_from_hour"], ir["valid_from_minute"]) == (27, 3, 54)
    assert (ir["valid_to_day"], ir["valid_to_hour"], ir["valid_to_minute"]) == (27, 7, 54)
    assert ir["top_fl"] == 150
    assert ir["top_qualifier"] == "BLW"
    assert ir["geometry"]["kind"] == "polygon"
    assert len(ir["geometry"]["reference_points"]) == 6


def test_hf_quebec_convert_success() -> None:
    """S: convert emits IWXXM without PARSE_ERROR for the exact failing paste."""
    result = convert(_QUEBEC, product="SIGMET")
    assert result.ok is True
    assert result.xml
    assert not any(i.code == "PARSE_ERROR" for i in result.issues)
    assert "SIGMET" in result.xml


@pytest.mark.parametrize(
    "tac",
    [_QUEBEC, _YANKEE, _VICTOR_Z, _NO_OFFICE],
    ids=["quebec", "yankee", "victor_z", "no_office"],
)
def test_hf_domestic_ws_variants_parse_convert(tac: str) -> None:
    """S: close variants (Z optional, other series, missing office line) succeed."""
    ir = parse_sigmet(tac)
    assert ir.get("us_domestic_ws") is True
    assert ir.get("phenomenon") == "SEV_TURB"
    result = convert(tac, product="SIGMET")
    assert result.ok is True, result.issues
    assert not any(i.code == "PARSE_ERROR" for i in result.issues)


def test_hf_quebec_bulletin_split_and_heading_paste() -> None:
    """S / read-query: split + heading paste find one report (Live decode path)."""
    split = split_bulletin(_QUEBEC, product="SIGMET")
    assert split.meta.report_count == 1
    assert "SIGMET QUEBEC 5 VALID UNTIL 270754" in split.reports[0]
    assert _is_kept_sigmet_report(split.reports[0]) is True
    pasted = reports_for_convert(_QUEBEC, "SIGMET")
    assert pasted is not None
    assert len(pasted.reports) == 1
    assert pasted.reports[0][0].startswith("WSUS01 KKCI 270354")


# --- Failure modes (F) -----------------------------------------------------------------


def test_hf_malformed_domestic_header_parse_error() -> None:
    """F: truly malformed VALID UNTIL header still raises unable to parse SIGMET header."""
    with pytest.raises(ValueError, match="unable to parse SIGMET header"):
        parse_sigmet(_MALFORMED)


def test_hf_missing_phenomenon_rejected() -> None:
    """F: domestic WS header with FROM ring but no phenomenon fails closed."""
    with pytest.raises(ValueError, match="missing phenomenon"):
        parse_sigmet(_MISSING_PHENOMENON)


def test_hf_heading_only_still_empty_bulletin() -> None:
    """F / read-query fault: AHL with no report body stays empty_bulletin."""
    with pytest.raises(BulletinSplitError) as exc:
        split_bulletin("WSUS01 KKCI 270354\n", product="SIGMET")
    assert exc.value.code == "empty_bulletin"
    with pytest.raises(HeadingPasteError) as exc2:
        reports_for_convert("WSUS01 KKCI 270354\n", "SIGMET")
    assert exc2.value.code == "empty_bulletin"


def test_hf_icao_sigmet_still_parses() -> None:
    """F-adjacent must-not-break: ICAO VALID period form is unchanged."""
    ir = parse_sigmet(_ICAO)
    assert ir.get("us_domestic_ws") is not True
    assert ir["phenomenon"] == "OBSC_TS"
    result = convert(_ICAO, product="SIGMET")
    assert result.ok is True


# --- Validation (V+ / V-) --------------------------------------------------------------


def test_hf_quebec_lint_validation_pass() -> None:
    """V+: tac-validate accepts the domestic WS shape (no MISSING_VALID)."""
    report = lint(_QUEBEC, product="SIGMET")
    codes = {i.code for i in report.issues}
    assert "MISSING_VALID" not in codes
    assert not any(i.severity == "error" for i in report.issues)


def test_hf_domestic_ws_missing_valid_until_lint_fail() -> None:
    """V-: domestic series without VALID UNTIL is rejected by lint."""
    tac = "WSUS01 KKCI 270354\nBOSQ WS 270354\nSIGMET QUEBEC 5\nNH FROM 80NE MPV OCNL SEV TURB."
    report = lint(tac, product="SIGMET")
    assert any(i.code == "MISSING_VALID" for i in report.issues)


def test_hf_convert_malformed_validation_fail() -> None:
    """V- / create+validation fail: convert surfaces PARSE_ERROR for bad header."""
    result = convert(_MALFORMED, product="SIGMET")
    assert result.ok is False or any(i.code in {"PARSE_ERROR", "TRANSLATION_FAILED"} for i in result.issues)
    assert any("unable to parse SIGMET header" in (i.message or "") for i in result.issues)
