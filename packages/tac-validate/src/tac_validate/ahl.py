"""WMO AHL bulletin detect / split for lint (EV-060 / #1001).

Heading is communications format; contained TAC reports lint as the selected product.
Does not import ``tac2iwxxm`` (package boundary).
"""

from __future__ import annotations

import re
from collections.abc import Callable

from tac_validate.issue_registry import issue_from
from tac_validate.models import Fix, Issue, LintReport

# TTAAii CCCC YYGGgg [BBB] — same shape as operator input-kind detect.
_LOOKS_LIKE_AHL = re.compile(
    r"^[A-Z]{4}\d{2}\s+[A-Z]{4}\s+\d{6}(?:\s+[A-Z]{1,3})?\s*$",
)
_AHL_LINE = re.compile(
    r"^(?P<tt>[A-Z]{2})(?P<aa>[A-Z]{2})(?P<ii>\d{2})\s+"
    r"(?P<cccc>[A-Z]{4})\s+(?P<yygggg>\d{6})"
    r"(?:\s+(?P<bbb>[A-Z]{1,3}))?\s*$"
)
_BBB_VALID = re.compile(r"^(?:AA|CC|RR)[A-X]$")
_KNOWN_TT: frozenset[str] = frozenset({"SA", "SP", "FC", "FT", "FK", "FN", "FV", "WA", "WS", "WC", "WV", "WM"})
_REPORT = re.compile(r".+?=", re.DOTALL)

LintReportFn = Callable[[str, str, str], LintReport]


def looks_like_ahl(text: str) -> bool:
    """Return True when the first non-empty line looks like a WMO AHL."""
    line = _first_nonempty_line(text)
    if line is None:
        return False
    stripped, _start, _end = line
    return _LOOKS_LIKE_AHL.fullmatch(stripped.upper()) is not None


def _first_nonempty_line(text: str) -> tuple[str, int, int] | None:
    offset = 0
    for line in text.splitlines(keepends=True):
        stripped = line.strip()
        if stripped:
            lead = len(line) - len(line.lstrip(" \t"))
            start = offset + lead
            end = start + len(stripped)
            return stripped, start, end
        offset += len(line)
    return None


def _remainder_start(text: str, heading_end: int) -> int:
    if heading_end < len(text) and text[heading_end : heading_end + 2] == "\r\n":
        return heading_end + 2
    if heading_end < len(text) and text[heading_end : heading_end + 1] in "\r\n":
        return heading_end + 1
    return heading_end


def _ahl_heading_ok(heading: str) -> bool:
    match = _AHL_LINE.fullmatch(heading.upper())
    if match is None:
        return False
    if match.group("tt") not in _KNOWN_TT:
        return False
    bbb = match.group("bbb")
    if bbb and not _BBB_VALID.fullmatch(bbb.upper()):
        return False
    return True


def _shift_issue(issue: Issue, delta: int) -> Issue:
    start = issue.start if issue.start is None else issue.start + delta
    end = issue.end if issue.end is None else issue.end + delta
    return Issue(
        severity=issue.severity,
        code=issue.code,
        message=issue.message,
        location=issue.location,
        start=start,
        end=end,
    )


def _shift_report(
    report: LintReport,
    delta: int,
) -> tuple[list[Issue], list[Fix]]:
    issues = [_shift_issue(i, delta) for i in report.issues]
    return issues, list(report.fixes)


def lint_ahl_bulletin(
    text: str,
    *,
    product: str,
    profile: str,
    lint_report: LintReportFn,
) -> LintReport:
    """
    Lint a WMO AHL bulletin: heading as COM, each contained TAC as ``product``.

    Parameters
    ----------
    text :
        Full bulletin including AHL line.
    product :
        TAC product for contained reports.
    profile :
        ``annex3`` or ``iwxxm_us``.
    lint_report :
        Inner lint for a single TAC report (must not re-enter AHL split).

    Returns
    -------
    LintReport
        Flattened issues with offsets relative to ``text``.
    """
    first = _first_nonempty_line(text)
    assert first is not None
    heading, h_start, h_end = first
    issues: list[Issue] = []
    fixes: list[Fix] = []

    heading_ok = _ahl_heading_ok(heading)
    if not heading_ok:
        issues.append(
            issue_from(
                "INVALID_AHL",
                location="bulletin",
                start=h_start,
                end=h_end,
            )
        )

    rest_start = _remainder_start(text, h_end)
    remainder = text[rest_start:]
    found = False
    for match in _REPORT.finditer(remainder):
        raw = match.group(0)
        lstrip = len(raw) - len(raw.lstrip())
        report_text = raw.strip()
        if not report_text:
            continue
        found = True
        delta = rest_start + match.start() + lstrip
        inner = lint_report(report_text, product, profile)
        shifted, inner_fixes = _shift_report(inner, delta)
        issues.extend(shifted)
        fixes.extend(inner_fixes)

    if heading_ok and not found:
        issues.append(
            issue_from(
                "INVALID_AHL",
                message="AHL bulletin contains no TAC reports",
                location="bulletin",
                start=h_start,
                end=h_end,
            )
        )

    ok = not any(i.severity == "error" for i in issues)
    return LintReport(ok=ok, product=product.upper(), issues=issues, fixes=fixes)
