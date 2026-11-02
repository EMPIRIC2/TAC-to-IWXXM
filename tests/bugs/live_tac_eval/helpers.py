"""Shared helpers for live-tac-eval / downloads dump regressions.

[Corpus: product §F15] [Corpus: tests]
"""

from __future__ import annotations

from collections.abc import Iterable

from tac_validate.api import lint_with_profile

_PRODUCT_PREFIXES = ("METAR", "SPECI", "TAF")


def body_tac(raw: str) -> str:
    """Return the report line, stripping WMO abbreviated headings."""
    lines = [ln.strip() for ln in raw.replace("\r\n", "\n").split("\n") if ln.strip()]
    for ln in lines:
        upper = ln.upper()
        if upper.startswith(_PRODUCT_PREFIXES) or " SIGMET " in f" {upper} ":
            return ln
        # SIGMET body often starts with FIR designator (e.g. TTZP SIGMET …)
        if "SIGMET" in upper and not upper.startswith(("WS", "WC", "WV", "WA")):
            return ln
    return lines[-1] if lines else raw.strip()


def icao_from_tac(tac: str, *, default: str = "") -> str:
    """Best-effort ICAO from a METAR/SPECI/TAF body line."""
    tokens = body_tac(tac).split()
    if len(tokens) >= 2 and tokens[0].upper() in {"METAR", "SPECI", "TAF", "TAFAMD"}:
        station = tokens[1]
        if station.upper() in {"AMD", "COR"} and len(tokens) >= 3:
            station = tokens[2]
        if len(station) == 4 and station.isalpha():
            return station.upper()
    return default


def lint_annex3(tac: str, *, product: str, icao: str | None = None):
    """Lint body TAC under the annex3 profile used in the two-week dump."""
    body = body_tac(tac)
    station = icao or icao_from_tac(body) or None
    return lint_with_profile(body, product=product, profile="annex3", icao=station)


def issue_codes(report) -> set[str]:
    return {i.code for i in report.issues}


def issues_by_code(report) -> dict[str, list]:
    out: dict[str, list] = {}
    for issue in report.issues:
        out.setdefault(issue.code, []).append(issue)
    return out


def assert_has_code(report, code: str, *, severity: str | None = None) -> None:
    matched = [i for i in report.issues if i.code == code]
    assert matched, f"expected {code} in {[i.code for i in report.issues]}"
    if severity is not None:
        assert all(i.severity == severity for i in matched), (
            f"{code} severities={[i.severity for i in matched]} expected {severity}"
        )


def assert_absent_codes(report, codes: Iterable[str]) -> None:
    present = issue_codes(report)
    bad = set(codes) & present
    assert not bad, f"unexpected codes {bad} in {sorted(present)}"


def assert_no_error_severity(report) -> None:
    errors = [(i.code, i.severity) for i in report.issues if i.severity == "error"]
    assert not errors, f"unexpected error-severity issues: {errors}"
