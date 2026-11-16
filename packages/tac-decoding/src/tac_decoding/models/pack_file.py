"""Typed views of pack YAML/JSON documents.

[Corpus: product §F9]
"""

from __future__ import annotations

from typing import TypedDict


class PackRuleMapping(TypedDict, total=False):
    """One rule object inside a pack file."""

    id: str
    pattern: object
    explain: str
    label: str


class PackFileMapping(TypedDict, total=False):
    """Top-level pack document keys."""

    id: str
    layout: str
    rules: list[object]
    profiles: list[object]
    extends: str


__all__ = ["PackFileMapping", "PackRuleMapping"]
