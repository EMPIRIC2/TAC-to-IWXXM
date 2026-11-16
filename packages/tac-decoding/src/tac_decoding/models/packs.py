"""Pack and rule dataclasses.

[Corpus: product §F9]
"""

from __future__ import annotations

import re
from dataclasses import dataclass


class PackSchemaError(ValueError):
    """
    A pack file or directory does not match the pack schema.

    Attributes
    ----------
    args : tuple
        Arguments passed to the exception constructor.
    """


@dataclass(frozen=True, slots=True)
class Rule:
    """
    One match rule. Token rules use ``patterns``; label rules use ``label``.

    Attributes
    ----------
    id : str
        ID.
    explain : str
        Explain.
    patterns : tuple[re.Pattern[str], ...]
        Patterns.
    label : str
        Label. Default ``''``.
    """

    id: str
    explain: str
    patterns: tuple[re.Pattern[str], ...] = ()
    label: str = ""


@dataclass(frozen=True, slots=True)
class Pack:
    """
    One product pack: an id, a layout, and optional rules.

    Attributes
    ----------
    id : str
        ID.
    layout : str
        Layout.
    rules : tuple[Rule, ...]
        Rules.
    """

    id: str
    layout: str
    rules: tuple[Rule, ...] = ()


__all__ = ["Pack", "PackSchemaError", "Rule"]
