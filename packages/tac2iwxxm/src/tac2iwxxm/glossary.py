"""Extensible decode glossary — official tables + YAML overrides (F9 / ADR-032).

Merge order: official/near-official meanings first, then YAML overlay
(``decode_glossary.yaml`` / ``TAC2IWXXM_DECODE_GLOSSARY_PATH`` wins on conflict).
Optional location-name resolver (OpenAIP/F3) soft-fails to ICAO designator.
"""

from __future__ import annotations

import os
from collections.abc import Callable, Mapping
from functools import lru_cache
from importlib import resources
from pathlib import Path
from typing import Any, cast

import yaml


def _tokens_from_mapping(raw: object) -> dict[str, str]:
    if not isinstance(raw, dict):
        return {}
    mapping = cast(Mapping[Any, Any], raw)
    tokens_raw = mapping.get("tokens", mapping)
    if not isinstance(tokens_raw, dict):
        return {}
    token_map = cast(Mapping[Any, Any], tokens_raw)
    out: dict[str, str] = {}
    for key, value in token_map.items():
        if isinstance(key, str) and isinstance(value, str) and key.strip() and value.strip():
            out[key.strip().upper()] = value.strip()
    return out


# Official / near-official abbreviations (WMO codes / Annex 3 / EUR App A cites —
# short meanings only; no copyrighted prose). Keys are uppercase TAC tokens.
_OFFICIAL_TOKENS: dict[str, str] = {
    # Spatial / intensity (SIGMET / AIRMET)
    "OBSC": "obscured",
    "EMBD": "embedded",
    "FRQ": "frequent",
    "SQL": "squall line",
    "ISOL": "isolated",
    "OCNL": "occasional",
    "SEV": "severe",
    "MOD": "moderate",
    "HVY": "heavy",
    "VALID": "validity period marker",
    "OF": "of",
    "AND": "and",
    "FIR/UIR": "flight information region / upper information region",
    # Hazards
    "TS": "thunderstorm",
    "TSGR": "thunderstorm with hail",
    "ICE": "icing",
    "TURB": "turbulence",
    "MTW": "mountain wave",
    "DS": "duststorm",
    "SS": "sandstorm",
    "VA": "volcanic ash",
    "TC": "tropical cyclone",
    "GR": "hail",
    "FZRA": "freezing rain",
    "RDOACT": "radioactive",
    "CLD": "cloud",
    "CB": "cumulonimbus",
    "TCU": "towering cumulus",
    # Movement / intensity change
    "STNR": "stationary",
    "WKN": "weakening",
    "INTSF": "intensifying",
    "NC": "no change",
    "MOV": "moving",
    # Observation / forecast markers
    "OBS": "observed",
    "FCST": "forecast",
    "TOP": "top",
    "ABV": "above",
    "BLW": "below",
    "FL": "flight level",
    "FIR": "flight information region",
    "UIR": "upper flight information region",
    "CNL": "cancel",
    # Advisory keywords
    "ADVISORY": "advisory",
    "VAA": "volcanic ash advisory",
    "TCA": "tropical cyclone advisory",
    "DTG": "date-time group",
    "VOLCANO": "volcano",
    "PSN": "position",
    "AREA": "area",
    "SUMMIT": "summit",
    "VAAC": "volcanic ash advisory centre",
    "TCAC": "tropical cyclone advisory centre",
}

_ENV_PATH = "TAC2IWXXM_DECODE_GLOSSARY_PATH"

LocationNameResolver = Callable[[str], str | None]

_location_name_resolver: LocationNameResolver | None = None


def set_location_name_resolver(resolver: LocationNameResolver | None) -> None:
    """
    Install an optional OpenAIP/F3-style ICAO→name lookup for decode.

    Parameters
    ----------
    resolver :
        Callable returning a place name for an ICAO designator, or ``None`` on
        miss. ``None`` clears the resolver (designator-only explanations).
    """
    global _location_name_resolver
    _location_name_resolver = resolver


def resolve_location_name(icao: str) -> str | None:
    """
    Resolve an ICAO designator via the installed location resolver.

    Returns
    -------
    str | None
        Place name when resolvable; ``None`` on miss or when no resolver is set.
        Never raises on lookup failure.
    """
    if _location_name_resolver is None:
        return None
    try:
        return _location_name_resolver(icao.upper())
    except Exception:
        return None


def _packaged_overlay_tokens() -> dict[str, str]:
    """Load packaged ``decode_glossary.yaml`` tokens (empty if absent)."""
    try:
        root = resources.files("tac2iwxxm")
        data = root.joinpath("data", "decode_glossary.yaml")
        if not data.is_file():
            # Editable installs may expose a real path.
            fallback = Path(__file__).resolve().parent / "data" / "decode_glossary.yaml"
            return _load_yaml_tokens(fallback)
        return _tokens_from_mapping(yaml.safe_load(data.read_text(encoding="utf-8")))
    except (FileNotFoundError, ModuleNotFoundError, TypeError, AttributeError, OSError):
        fallback = Path(__file__).resolve().parent / "data" / "decode_glossary.yaml"
        return _load_yaml_tokens(fallback)


def _load_yaml_tokens(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    return _tokens_from_mapping(yaml.safe_load(path.read_text(encoding="utf-8")))


def _merge_tables(official: dict[str, str], overlay: dict[str, str]) -> dict[str, str]:
    merged = dict(official)
    merged.update(overlay)
    return merged


@lru_cache(maxsize=1)
def load_glossary() -> dict[str, str]:
    """
    Load official token meanings merged with packaged + env YAML overlays.

    Returns
    -------
    dict[str, str]
        Uppercase token → English meaning. Env path overrides packaged YAML keys.
    """
    overlay: dict[str, str] = {}
    overlay.update(_packaged_overlay_tokens())
    env_path = os.environ.get(_ENV_PATH, "").strip()
    if env_path:
        overlay.update(_load_yaml_tokens(Path(env_path)))
    return _merge_tables(_OFFICIAL_TOKENS, overlay)


def reload_glossary() -> dict[str, str]:
    """Clear the glossary cache and reload (tests / hot reload)."""
    load_glossary.cache_clear()
    return load_glossary()


def meaning_for(token: str) -> str:
    """
    Return the glossary meaning for ``token``.

    Parameters
    ----------
    token :
        TAC token (case-insensitive).

    Returns
    -------
    str
        English meaning, or empty string if unknown.
    """
    return load_glossary().get(token.upper(), "")


def explain_glossary_token(token: str, *, fallback: str | None = None) -> str | None:
    """
    Build an explanation from the glossary, falling back to ``fallback``.

    Parameters
    ----------
    token :
        TAC token.
    fallback :
        Category-style label when the token is not in the glossary.

    Returns
    -------
    str | None
        Capitalized meaning or fallback; ``None`` if both missing.
    """
    meaning = meaning_for(token)
    if meaning:
        return meaning[0].upper() + meaning[1:] if meaning else meaning
    return fallback


__all__ = [
    "load_glossary",
    "meaning_for",
    "explain_glossary_token",
    "reload_glossary",
    "resolve_location_name",
    "set_location_name_resolver",
]
