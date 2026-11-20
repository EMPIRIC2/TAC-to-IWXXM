"""Decoding catalog row and meta TypedDicts.

[Corpus: product §F9]
"""

from __future__ import annotations

from typing import TypedDict


class CatalogTokenMeta(TypedDict, total=False):
    """Additive YAML fields for one glossary token."""

    issue_type: str
    severity: str
    source_url: str
    source_attribution: str
    source_access: str
    source_locator: str
    conform_note: str


class CatalogEntry(TypedDict):
    """One Decoding catalog row."""

    id: str
    title: str
    summary: str
    tags: list[str]
    issue_type: str | None
    severity: str | None
    source_url: str | None
    source_attribution: str | None
    source_access: str | None
    source_locator: str | None
    conform_note: str | None


__all__ = ["CatalogEntry", "CatalogTokenMeta"]
