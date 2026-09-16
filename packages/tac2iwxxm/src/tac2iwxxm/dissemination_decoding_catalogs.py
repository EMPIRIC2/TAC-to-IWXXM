"""Load mined Dissemination / Decoding catalogs (EVPYL Phase B / T-B3)."""

from __future__ import annotations

from functools import lru_cache
from importlib import resources
from typing import Any, cast

import yaml


def _load_yaml(name: str) -> dict[str, Any]:
    raw = resources.files("tac2iwxxm.data").joinpath(name).read_text(encoding="utf-8")
    data = yaml.safe_load(raw)
    if not isinstance(data, dict):
        raise ValueError(f"{name} is not a mapping")
    return cast(dict[str, Any], data)


@lru_cache(maxsize=1)
def load_dissemination_transforms() -> dict[str, Any]:
    """Return mined dissemination transform catalog."""
    data = _load_yaml("dissemination_transforms.yaml")
    if "transforms" not in data:
        raise ValueError("dissemination_transforms.yaml missing transforms")
    return data


@lru_cache(maxsize=1)
def load_decoding_library_entries() -> dict[str, Any]:
    """Return mined decoding library entries catalog."""
    data = _load_yaml("decoding_library_entries.yaml")
    if "entries" not in data:
        raise ValueError("decoding_library_entries.yaml missing entries")
    return data
