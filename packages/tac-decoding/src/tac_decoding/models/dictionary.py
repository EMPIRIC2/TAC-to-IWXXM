"""Code-name dictionary row and meta TypedDicts.

[Corpus: product §F9]
"""

from __future__ import annotations

from typing import TypedDict


class DictionaryTokenFields(TypedDict, total=False):
    """Optional YAML overrides for one glossary token."""

    products: list[str]
    countries: list[str]
    wmo_amendment: str | None


class DictionaryEntry(TypedDict):
    """One code-name dictionary row for the operator UI."""

    id: str
    code: str
    meaning: str
    products: list[str]
    countries: list[str]
    wmo_amendment: str | None


class DictionaryFacets(TypedDict):
    """Facet value lists for dictionary filters."""

    products: list[str]
    countries: list[str]
    wmo_amendments: list[str]


__all__ = ["DictionaryEntry", "DictionaryFacets", "DictionaryTokenFields"]
