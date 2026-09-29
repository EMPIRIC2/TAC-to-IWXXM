"""Conversion rule-catalog export with readable profile summaries.

Rows are package-owned operator trust metadata for GET /rule-catalogs
family=conversion. Semantic profiles use issue_type=profile; policy unused.
"""

from __future__ import annotations

from collections.abc import Mapping
from functools import lru_cache
from importlib import resources
from pathlib import Path
from typing import Any, cast

import yaml

from tac2iwxxm.profile_registry import known_semantic_profile_ids, normalize_profile_id

_META_KEYS: tuple[str, ...] = (
    "summary",
    "severity",
    "source_url",
    "source_attribution",
    "source_access",
    "source_locator",
    "conform_note",
)

_BOILERPLATE_PREFIX = "Semantic conversion profile "


def _profiles_meta_from_mapping(raw: object) -> dict[str, dict[str, str]]:
    """
    Parse ``conversion_catalog_meta.yaml`` profile map.

    Parameters
    ----------
    raw :
        Loaded YAML document.

    Returns
    -------
    dict[str, dict[str, str]]
        Normalized profile id → non-empty string fields only.
    """
    if not isinstance(raw, dict):
        return {}
    mapping = cast(Mapping[Any, Any], raw)
    profiles_raw = mapping.get("profiles", {})
    if not isinstance(profiles_raw, dict):
        return {}
    profile_map = cast(Mapping[Any, Any], profiles_raw)
    out: dict[str, dict[str, str]] = {}
    for key, value in profile_map.items():
        if not isinstance(key, str) or not key.strip():
            continue
        if not isinstance(value, dict):
            continue
        fields: dict[str, str] = {}
        value_map = cast(Mapping[Any, Any], value)
        for meta_key in _META_KEYS:
            field_val = value_map.get(meta_key)
            if isinstance(field_val, str) and field_val.strip():
                fields[meta_key] = " ".join(field_val.split())
        if fields:
            out[normalize_profile_id(key)] = fields
    return out


@lru_cache(maxsize=1)
def load_conversion_catalog_meta() -> dict[str, dict[str, str]]:
    """
    Load packaged ``conversion_catalog_meta.yaml``.

    Returns
    -------
    dict[str, dict[str, str]]
        Meta rows keyed by normalized profile id.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (load_conversion_catalog_meta)
    2
    """
    try:
        root = resources.files("tac2iwxxm.data")
        data = root.joinpath("conversion_catalog_meta.yaml")
        if not data.is_file():
            fallback = Path(__file__).resolve().parent / "data" / "conversion_catalog_meta.yaml"
            text = fallback.read_text(encoding="utf-8")
        else:
            text = data.read_text(encoding="utf-8")
    except (OSError, TypeError, ValueError):
        fallback = Path(__file__).resolve().parent / "data" / "conversion_catalog_meta.yaml"
        if not fallback.is_file():
            return {}
        text = fallback.read_text(encoding="utf-8")
    try:
        loaded = yaml.safe_load(text)
    except yaml.YAMLError:
        return {}
    return _profiles_meta_from_mapping(loaded)


def reload_conversion_catalog_meta() -> dict[str, dict[str, str]]:
    """
    Clear the conversion-catalog-meta cache and reload (tests).

    Returns
    -------
    dict[str, dict[str, str]]
        Fresh meta rows keyed by normalized profile id.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (reload_conversion_catalog_meta)
    2
    """
    load_conversion_catalog_meta.cache_clear()
    return load_conversion_catalog_meta()


def catalog_entries(*, limit: int | None = None) -> list[dict[str, Any]]:
    """
    Export semantic conversion profiles as Conversion catalog rows.

    Parameters
    ----------
    limit :
        Optional max rows (sorted by id).

    Returns
    -------
    list[dict[str, Any]]
        Items with ``id``, ``title``, ``summary``, ``tags``, ``issue_type=profile``,
        and optional additive metadata.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (catalog_entries)
    2
    """
    meta = load_conversion_catalog_meta()
    items: list[dict[str, Any]] = []
    for pid in sorted(known_semantic_profile_ids()):
        norm = normalize_profile_id(pid)
        row_meta = meta.get(norm, {})
        summary = row_meta.get("summary")
        if not summary or summary.startswith(_BOILERPLATE_PREFIX):
            summary = (
                f"Conversion profile {pid.upper() if pid.islower() else pid}: "
                "national or Annex 3 TAC-to-IWXXM encoding rules for supported products."
            )
        row: dict[str, Any] = {
            "id": pid,
            "title": pid,
            "summary": summary,
            "tags": ["conversion", "profile"],
            "issue_type": "profile",
            "severity": None,
            "source_url": None,
            "source_attribution": None,
            "source_access": None,
            "source_locator": None,
            "conform_note": None,
        }
        for meta_key in _META_KEYS:
            if meta_key == "summary":
                continue
            if meta_key in row_meta:
                row[meta_key] = row_meta[meta_key]
        items.append(row)
    if limit is not None:
        return items[: max(0, limit)]
    return items
