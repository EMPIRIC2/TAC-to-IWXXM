"""COLLECT / IWXXM read models.

[Corpus: product §F9]
"""

from __future__ import annotations

from dataclasses import dataclass


class CollectError(ValueError):
    """
    The text is not a readable COLLECT or IWXXM document.

    Attributes
    ----------
    args : tuple
        Arguments passed to the exception constructor.
    """


@dataclass(frozen=True, slots=True)
class CollectField:
    """
    One leaf XML field from an XML-only COLLECT walk.

    Attributes
    ----------
    name : str
        Local name of the leaf element.
    value : str
        Leaf text.
    path : str
        Local-name path from the root to the leaf.
    """

    name: str
    value: str
    path: str


@dataclass(frozen=True, slots=True)
class CollectRead:
    """
    Result of reading COLLECT or IWXXM XML without encoding.

    Attributes
    ----------
    mode : str
        Mode.
    bulletin_identifier : str | None
        Bulletin identifier.
    tac_reports : tuple[str, ...]
        TAC reports.
    fields : tuple[CollectField, ...]
        Fields.
    """

    mode: str
    bulletin_identifier: str | None
    tac_reports: tuple[str, ...]
    fields: tuple[CollectField, ...]


__all__ = ["CollectError", "CollectField", "CollectRead"]
