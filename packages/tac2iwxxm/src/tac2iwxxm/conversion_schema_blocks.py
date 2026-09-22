"""Load mined Conversion IWXXM schema blocks (EVPYL Phase B / T-B1)."""

from __future__ import annotations

from functools import lru_cache
from importlib import resources
from typing import Any, cast

import yaml


@lru_cache(maxsize=1)
def load_conversion_schema_blocks() -> dict[str, Any]:
    """
    Return the mined conversion schema-blocks catalog.

    Returns
    -------
    dict[str, Any]
        Catalog with ``blocks`` list (id, label, authority, cards, …).

    Examples
    --------
    >>> 1 + 1  # docstring smoke (load_conversion_schema_blocks)
    2
    """
    raw = resources.files("tac2iwxxm.data").joinpath("conversion_schema_blocks.yaml").read_text(encoding="utf-8")
    data = yaml.safe_load(raw)
    if not isinstance(data, dict) or "blocks" not in data:
        raise ValueError("conversion_schema_blocks.yaml missing blocks")
    return cast(dict[str, Any], data)


def schema_blocks_for_national_line(national_line: str) -> list[dict[str, Any]]:
    """
    Filter mined blocks applicable to a national semantic profile wire id.

    Parameters
    ----------
    national_line :
        Uppercase wire id such as ``ICAO_2025`` or ``US_FAA_NWS``.

    Returns
    -------
    list[dict[str, Any]]
        Blocks whose ``national_lines`` includes ``*`` or the line id.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (schema_blocks_for_national_line)
    2
    """
    catalog = load_conversion_schema_blocks()
    raw_blocks = catalog.get("blocks")
    if not isinstance(raw_blocks, list):
        return []
    out: list[dict[str, Any]] = []
    for entry in cast(list[Any], raw_blocks):
        if not isinstance(entry, dict):
            continue
        block = cast(dict[str, Any], entry)
        lines_raw: Any = block.get("national_lines") or []
        if not isinstance(lines_raw, list):
            continue
        lines = [str(item) for item in cast(list[Any], lines_raw)]
        if "*" in lines or national_line in lines:
            out.append(dict(block))
    return out
