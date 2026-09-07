"""Catalog metadata helpers for Validation Issues Catalog (EV-062 / #1017).

Derives operator-facing ``issue_type``, ``source_access``, and ``source_locator``
without changing encode/validate engines. [Corpus: product §F15] [Corpus: api]
"""

from __future__ import annotations

from collections.abc import Iterable

ISSUE_TYPES = frozenset({"presence", "structure", "content", "consistency", "iwxxm_schema", "other"})
SOURCE_ACCESS = frozenset({"public", "paywall", "login", "semantic_only"})

_STRUCTURE_TAGS = frozenset({"parse_gate", "terminator", "ahl", "bulletin", "header", "body", "one_report"})
_CONSISTENCY_TAGS = frozenset({"exclusivity", "adjacency", "conflict"})
_PRESENCE_TAGS = frozenset({"modifier", "trend", "change", "nil", "cnl"})


def classify_issue_type(
    *,
    code: str,
    tags: Iterable[str] = (),
    family: str | None = None,
) -> str:
    """
    Return a closed-vocabulary issue type for a catalog row.

    Parameters
    ----------
    code :
        SCREAMING_SNAKE issue code.
    tags :
        Registry / catalog tags.
    family :
        ``lint`` or ``iwxxm`` when known.

    Returns
    -------
    str
        One of ``ISSUE_TYPES``.
    """
    if (family or "").lower() == "iwxxm":
        return "iwxxm_schema"
    tag_set = {t.lower() for t in tags}
    upper = code.upper()
    if upper.endswith("_PRESENT") or "PRESENT" in upper.split("_"):
        return "presence"
    if tag_set & _PRESENCE_TAGS and upper.endswith(("_REPORT",)):
        return "presence"
    if tag_set & _STRUCTURE_TAGS or upper in {
        "EMPTY_TAC",
        "INVALID_AHL",
        "MISSING_TERMINATOR",
        "UNKNOWN_PRODUCT",
        "MISSING_PRODUCT_KEYWORD",
    }:
        return "structure"
    if tag_set & _CONSISTENCY_TAGS or "WITH_" in upper or "EXCLUSIV" in upper:
        return "consistency"
    if upper.startswith("INVALID_") or upper.startswith("MISSING_"):
        return "content"
    if tag_set:
        return "content"
    return "other"


def source_access_for(
    *,
    source_url: str | None,
    raw_status: str | None,
    operator_status: str | None = None,
) -> str | None:
    """
    Map provenance status to operator ``source_access``.

    Parameters
    ----------
    source_url :
        Operator-visible or vendor URL.
    raw_status :
        Provenance map status (``paywall``, ``ok``, ``gap``, …).
    operator_status :
        Catalog operator status (``verified``, ``semantic_only``, …).

    Returns
    -------
    str | None
        One of ``SOURCE_ACCESS``, or None when unknown.
    """
    if raw_status == "paywall" or (source_url and "store.icao.int" in source_url):
        return "paywall"
    if operator_status == "semantic_only" or (source_url and source_url.startswith("vendor:")):
        return "semantic_only"
    if raw_status in {"gap", "N/A"}:
        return "semantic_only"
    if source_url and source_url.startswith(("http://", "https://")):
        return "public"
    return None


def source_locator_for(note: str | None) -> str | None:
    """
    Prefer provenance ``note`` as a section/table/page locator when present.

    Parameters
    ----------
    note :
        Free-text locus from PROVENANCE_MAP (no planning ids).

    Returns
    -------
    str | None
        Locator string, or None when unavailable.
    """
    if not note:
        return None
    text = note.strip()
    if not text:
        return None
    # Companion blurbs without a locus still count as unavailable for section cite.
    lower = text.lower()
    if lower.startswith("eur doc") and "annex 3 paywall companion" in lower:
        # Still a document cite - keep as locator text.
        return text
    return text


def human_source_cite(locator: str | None, *, paywall: bool = False) -> str:
    """
    Operator-facing sentence fragment for description footers.

    Parameters
    ----------
    locator :
        Section/table/page text, or None.
    paywall :
        When True, note purchase/access constraint plainly.

    Returns
    -------
    str
        Natural-language source line (no planning ids).
    """
    if locator:
        base = f"Source: {locator}."
        if paywall:
            return f"{base} Full normative text may require purchase."
        return base
    if paywall:
        return "Source section unavailable (normative text may require purchase)."
    return "Source section unavailable."


__all__ = [
    "ISSUE_TYPES",
    "SOURCE_ACCESS",
    "classify_issue_type",
    "human_source_cite",
    "source_access_for",
    "source_locator_for",
]
