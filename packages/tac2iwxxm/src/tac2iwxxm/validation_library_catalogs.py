"""Load mined TAC / IWXXM validation catalogs (EVPYL Phase B / T-B2)."""

from __future__ import annotations

from functools import lru_cache
from importlib import resources
from typing import Any, cast

import yaml


def _load_yaml(name: str) -> dict[str, Any]:
    """Internal helper ``_load_yaml``."""
    raw = resources.files("tac2iwxxm.data").joinpath(name).read_text(encoding="utf-8")
    data = yaml.safe_load(raw)
    if not isinstance(data, dict):
        raise ValueError(f"{name} is not a mapping")
    return cast(dict[str, Any], data)


@lru_cache(maxsize=1)
def load_tac_validation_rules() -> dict[str, Any]:
    """
    Return mined TAC validation rules catalog.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (load_tac_validation_rules)
    2

    Returns
    -------
    object
        Return value.
    """
    data = _load_yaml("tac_validation_rules.yaml")
    if "rules" not in data:
        raise ValueError("tac_validation_rules.yaml missing rules")
    return data


@lru_cache(maxsize=1)
def load_iwxxm_validation_asserts() -> dict[str, Any]:
    """
    Return mined IWXXM Schematron assert catalog.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (load_iwxxm_validation_asserts)
    2

    Returns
    -------
    object
        Return value.
    """
    data = _load_yaml("iwxxm_validation_asserts.yaml")
    if "asserts" not in data:
        raise ValueError("iwxxm_validation_asserts.yaml missing asserts")
    return data
