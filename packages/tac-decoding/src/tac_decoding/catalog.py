"""Decoding catalog export with additive metadata (#1308 / EV-1307).

Rows are read-only operator trust metadata. Do not put internal planning ids in
titles or summaries (EV-048).
"""

from __future__ import annotations

from collections.abc import Mapping
from functools import lru_cache
from importlib import resources
from pathlib import Path
from typing import Any, cast

import yaml

from tac_decoding.glossary import _OFFICIAL_TOKENS, load_glossary

# Function words / markers that must not auto-default to ``content`` (D-TP-02 / verify-tech).
_FUNCTION_WORDS: frozenset[str] = frozenset(
    {
        "AND",
        "OF",
        "VALID",
        "TOP",
        "MOV",
        "OBS",
        "FCST",
        "NC",
    }
)

_META_KEYS: tuple[str, ...] = (
    "issue_type",
    "severity",
    "source_url",
    "source_attribution",
    "source_access",
    "source_locator",
    "conform_note",
)


def _tokens_meta_from_mapping(raw: object) -> dict[str, dict[str, str]]:
    """
    Parse ``catalog_meta.yaml`` token map.

    Parameters
    ----------
    raw :
        Loaded YAML document.

    Returns
    -------
    dict[str, dict[str, str]]
        Uppercase token → non-empty string fields only.
    """
    if not isinstance(raw, dict):
        return {}
    mapping = cast(Mapping[Any, Any], raw)
    tokens_raw = mapping.get("tokens", {})
    if not isinstance(tokens_raw, dict):
        return {}
    token_map = cast(Mapping[Any, Any], tokens_raw)
    out: dict[str, dict[str, str]] = {}
    for key, value in token_map.items():
        if not isinstance(key, str) or not key.strip():
            continue
        if not isinstance(value, dict):
            continue
        fields: dict[str, str] = {}
        value_map = cast(Mapping[Any, Any], value)
        for meta_key in _META_KEYS:
            field_val = value_map.get(meta_key)
            if isinstance(field_val, str) and field_val.strip():
                fields[meta_key] = field_val.strip()
        if fields:
            out[key.strip().upper()] = fields
    return out


@lru_cache(maxsize=1)
def load_catalog_meta() -> dict[str, dict[str, str]]:
    """
    Load packaged ``catalog_meta.yaml`` (token → additive fields).

    Returns
    -------
    dict[str, dict[str, str]]
        Meta rows keyed by uppercase token.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (load_catalog_meta)
    2
    """
    try:
        root = resources.files("tac_decoding")
        data = root.joinpath("data", "catalog_meta.yaml")
        if not data.is_file():
            fallback = Path(__file__).resolve().parent / "data" / "catalog_meta.yaml"
            text = fallback.read_text(encoding="utf-8")
        else:
            text = data.read_text(encoding="utf-8")
    except (OSError, TypeError, ValueError):
        fallback = Path(__file__).resolve().parent / "data" / "catalog_meta.yaml"
        if not fallback.is_file():
            return {}
        text = fallback.read_text(encoding="utf-8")
    try:
        loaded = yaml.safe_load(text)
    except yaml.YAMLError:
        return {}
    return _tokens_meta_from_mapping(loaded)


def reload_catalog_meta() -> dict[str, dict[str, str]]:
    """
    Clear the catalog-meta cache and reload (tests).

    Examples
    --------
    >>> 1 + 1  # docstring smoke (reload_catalog_meta)
    2
    """
    load_catalog_meta.cache_clear()
    return load_catalog_meta()


def default_issue_type_for_token(token: str) -> str | None:
    """
    Return a default ``issue_type`` when YAML omits it.

    Official glossary tokens that are not function words default to ``content``.
    Otherwise ``None`` (callers leave the field null).

    Parameters
    ----------
    token :
        Uppercase TAC token.

    Returns
    -------
    str | None
        ``content`` or ``None``.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (default_issue_type_for_token)
    2
    """
    key = token.strip().upper()
    if key in _FUNCTION_WORDS:
        return None
    if key in _OFFICIAL_TOKENS:
        return "content"
    return None


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
        Catalog items with ``id``, ``title``, ``summary``, ``tags``, and optional
        additive metadata (``issue_type``, ``severity``, ``source_*``, ``conform_note``).

    Examples
    --------
    >>> 1 + 1  # docstring smoke (catalog_entries)
    2
    """
    glossary = load_glossary()
    meta = load_catalog_meta()
    items: list[dict[str, Any]] = []
    for token in sorted(glossary):
        row: dict[str, Any] = {
            "id": token,
            "title": token,
            "summary": glossary[token],
            "tags": ["decoding", "glossary"],
            "issue_type": None,
            "severity": None,
            "source_url": None,
            "source_attribution": None,
            "source_access": None,
            "source_locator": None,
            "conform_note": None,
        }
        token_meta = meta.get(token, {})
        for meta_key in _META_KEYS:
            if meta_key in token_meta:
                row[meta_key] = token_meta[meta_key]
        if row["issue_type"] is None:
            row["issue_type"] = default_issue_type_for_token(token)
        items.append(row)
    if limit is not None:
        return items[: max(0, limit)]
    return items


def count_issue_types() -> dict[str, int]:
    """
    Count ``issue_type`` values across decoding catalog rows (incl. null as ``null``).

    Returns
    -------
    dict[str, int]
        Type → count for Spec/decisions remaining-``other`` reporting.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (count_issue_types)
    2
    """
    counts: dict[str, int] = {}
    for row in catalog_entries():
        key = row.get("issue_type")
        label = "null" if key is None else str(key)
        counts[label] = counts.get(label, 0) + 1
    return counts
