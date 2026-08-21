"""IWXXM product pass-through helpers (F7.t / EV-060 / #1003).

``product=iwxxm`` skips TAC→IWXXM convert. Input must be XML; TAC text yields
structured ``NOT_XML``. Well-formed XML may proceed to optional F2 validate.
"""

from __future__ import annotations

from dataclasses import dataclass
from xml.etree import ElementTree as ET

NOT_XML_CODE = "NOT_XML"
NOT_WELLFORMED_XML_CODE = "NOT_WELLFORMED_XML"


@dataclass(frozen=True)
class IwxxmLintIssue:
    """Minimal lint issue for pass-through XML checks."""

    severity: str
    code: str
    message: str
    location: str | None = None
    start: int | None = None
    end: int | None = None


@dataclass(frozen=True)
class IwxxmLintReport:
    """Lint report shape compatible with ``/lint-tac`` mapping."""

    ok: bool
    product: str
    issues: list[IwxxmLintIssue]


def looks_like_xml(text: str) -> bool:
    """Return True when trimmed text appears to be XML markup."""
    return text.lstrip().startswith("<")


def lint_iwxxm_pass_through(text: str) -> IwxxmLintReport:
    """
    Lint text under ``product=iwxxm``.

    Parameters
    ----------
    text :
        Operator paste or file contents.

    Returns
    -------
    IwxxmLintReport
        ``ok`` is False for empty, non-XML, or not well-formed input.
    """
    stripped = (text or "").strip()
    if not stripped:
        return IwxxmLintReport(
            ok=False,
            product="IWXXM",
            issues=[
                IwxxmLintIssue(
                    severity="error",
                    code=NOT_XML_CODE,
                    message="Expected IWXXM XML; input is empty",
                    location="body",
                )
            ],
        )
    if not looks_like_xml(stripped):
        return IwxxmLintReport(
            ok=False,
            product="IWXXM",
            issues=[
                IwxxmLintIssue(
                    severity="error",
                    code=NOT_XML_CODE,
                    message=("Expected IWXXM XML for product IWXXM; TAC text cannot be converted on this product"),
                    location="body",
                    start=0,
                    end=min(len(stripped), 64),
                )
            ],
        )
    try:
        ET.fromstring(stripped)
    except ET.ParseError as exc:
        return IwxxmLintReport(
            ok=False,
            product="IWXXM",
            issues=[
                IwxxmLintIssue(
                    severity="error",
                    code=NOT_WELLFORMED_XML_CODE,
                    message=f"IWXXM XML is not well-formed: {exc}",
                    location="body",
                )
            ],
        )
    return IwxxmLintReport(ok=True, product="IWXXM", issues=[])


__all__ = [
    "NOT_WELLFORMED_XML_CODE",
    "NOT_XML_CODE",
    "IwxxmLintIssue",
    "IwxxmLintReport",
    "lint_iwxxm_pass_through",
    "looks_like_xml",
]
