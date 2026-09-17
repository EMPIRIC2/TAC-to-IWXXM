"""Decoding trust-catalog export (ADR-044).

Rows are read-only operator trust metadata. Do not put internal planning ids in
titles or summaries (EV-048).
"""

from __future__ import annotations

from typing import Any

from tac_decoding.glossary import load_glossary


def catalog_entries(*, limit: int | None = None) -> list[dict[str, Any]]:
    """
    Export glossary tokens as Decoding catalog rows.

    Parameters
    ----------
    limit :
        Optional max rows (stable sorted by token). ``None`` = all.

    Returns
    -------
    list[dict[str, Any]]
        Catalog items with ``id``, ``title``, ``summary``, and ``tags``.
    """
    glossary = load_glossary()
    items = [
        {
            "id": token,
            "title": token,
            "summary": glossary[token],
            "tags": ["decoding", "glossary"],
        }
        for token in sorted(glossary)
    ]
    if limit is not None:
        return items[: max(0, limit)]
    return items
