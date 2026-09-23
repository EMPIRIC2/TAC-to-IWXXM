"""Load the national convert product allowlist through Hydra.

Annex 3 is absent from the file, so every supported product stays allowed
for that profile. A listed profile converts only the products named there.
"""

from __future__ import annotations

from collections.abc import Sequence
from functools import cache
from pathlib import Path
from typing import cast

from hydra import compose, initialize_config_dir
from hydra.core.global_hydra import GlobalHydra
from omegaconf import OmegaConf

_CONF = Path(__file__).resolve().parent / "conf"


def compose_allowlist(overrides: Sequence[str] = ()) -> dict[str, frozenset[str]]:
    """
    Compose the convert allowlist, applying Hydra overrides when given.

    Parameters
    ----------
    overrides :
        Hydra override strings, such as ``profiles.au_bom=[METAR,TAF]``.

    Returns
    -------
    dict[str, frozenset[str]]
        Upper-case product codes for each gated emit key.

    Raises
    ------
    ValueError
        When the composed config is not a profile mapping.
    """
    if GlobalHydra.instance().is_initialized():
        GlobalHydra.instance().clear()
    with initialize_config_dir(version_base="1.3", config_dir=str(_CONF)):
        cfg = compose(config_name="convert_allowlist", overrides=list(overrides))
    raw_obj: object = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(raw_obj, dict):
        msg = "convert allowlist must be a mapping"
        raise ValueError(msg)
    raw = cast(dict[str, object], raw_obj)
    profiles_obj = raw.get("profiles")
    if not isinstance(profiles_obj, dict):
        msg = "convert allowlist profiles must be a mapping"
        raise ValueError(msg)
    profiles = cast(dict[object, object], profiles_obj)
    loaded: dict[str, frozenset[str]] = {}
    for key, products in profiles.items():
        if not isinstance(key, str) or not isinstance(products, list):
            msg = f"invalid allowlist row for {key!r}"
            raise ValueError(msg)
        codes = cast(list[object], products)
        loaded[key.strip().lower()] = frozenset(str(item).upper() for item in codes)
    return loaded


@cache
def load_convert_allowlist() -> dict[str, frozenset[str]]:
    """
    Return the packaged convert allowlist with no overrides.

    Returns
    -------
    dict[str, frozenset[str]]
        Upper-case product codes for each gated emit key.
    """
    return compose_allowlist()


def products_for(emit_key: str) -> frozenset[str] | None:
    """
    Return the product gate for ``emit_key``.

    Parameters
    ----------
    emit_key : str
        Semantic profile emit key, such as ``au_bom``.

    Returns
    -------
    frozenset[str] | None
        Allowed products, or ``None`` when the profile is not gated.
    """
    return load_convert_allowlist().get(emit_key.strip().lower())


def format_allowlist(loaded: dict[str, frozenset[str]]) -> str:
    """
    Render a composed allowlist as stable text.

    Parameters
    ----------
    loaded :
        Emit key to product codes.

    Returns
    -------
    str
        One line per profile, products sorted.
    """
    lines = [f"{key}: {', '.join(sorted(products))}" for key, products in sorted(loaded.items())]
    return "\n".join(lines)
