"""Offline WMO codes encode href policy (F6 / EV-023 TC-EV023-004).

Reads pin ``vendor/schemas/iwxxm/{version}/IWXXM/rule/*.rdf`` only — never
live codes.wmo.int HTML. Dual registers:

* ``iwxxm/AviationColourCode`` (2025-2 VONA / preferred colour set + UNASSIGNED)
* ``49-2/AviationColourCode`` (legacy NIL / NOT_GIVEN / UNKNOWN)
* ``common/nil`` and ``iwxxm/nil`` (same 11 concept notations; dual SCH paths)
"""

from __future__ import annotations

import os
import re
from functools import lru_cache
from pathlib import Path
from typing import Literal

_PACKAGE_DIR = Path(__file__).resolve().parent
_PACKAGE_ROOT = _PACKAGE_DIR.parents[1]
_DEFAULT_REPO_ROOT = _PACKAGE_ROOT.parents[1]

_CONCEPT_ABOUT = re.compile(r'<skos:Concept rdf:about="([^"]+)"')

ColourRegister = Literal["iwxxm", "49-2"]
NilFamily = Literal["common", "iwxxm"]

IWXXM_COLOUR_PREFIX = "http://codes.wmo.int/iwxxm/AviationColourCode/"
LEGACY_COLOUR_PREFIX = "http://codes.wmo.int/49-2/AviationColourCode/"
COMMON_NIL_PREFIX = "http://codes.wmo.int/common/nil/"
IWXXM_NIL_PREFIX = "http://codes.wmo.int/iwxxm/nil/"

# TAC / Annex 3 wording → iwxxm UNASSIGNED under 2025-2 (never invent 49-2 NIL href).
_UNASSIGNED_TOKENS = frozenset({"UNKNOWN", "NOT_GIVEN", "NOT GIVEN", "NIL", "UNASSIGNED"})

_RDF_FILES: dict[str, str] = {
    "iwxxm-colour": "codes.wmo.int-iwxxm-AviationColourCode.rdf",
    "49-2-colour": "codes.wmo.int-49-2-AviationColourCode.rdf",
    "common-nil": "codes.wmo.int-common-nil.rdf",
    "iwxxm-nil": "codes.wmo.int-iwxxm-nil.rdf",
}

_REGISTER_URI: dict[str, str] = {
    "iwxxm-colour": "http://codes.wmo.int/iwxxm/AviationColourCode",
    "49-2-colour": "http://codes.wmo.int/49-2/AviationColourCode",
    "common-nil": "http://codes.wmo.int/common/nil",
    "iwxxm-nil": "http://codes.wmo.int/iwxxm/nil",
}


def repo_root() -> Path:
    """
    Return monorepo root containing ``vendor/schemas``.

    Honours ``TAC2IWXXM_REPO_ROOT`` when set.
    """
    env = os.environ.get("TAC2IWXXM_REPO_ROOT")
    if env:
        return Path(env).resolve()
    return _DEFAULT_REPO_ROOT


def _rule_dir(iwxxm_version: str) -> Path:
    path = repo_root() / "vendor" / "schemas" / "iwxxm" / iwxxm_version / "IWXXM" / "rule"
    if not path.is_dir():
        raise FileNotFoundError(f"IWXXM rule/codelist directory not found: {path}")
    return path


def _rdf_concept_members(path: Path, *, register_uri: str) -> frozenset[str]:
    text = path.read_text(encoding="utf-8")
    prefix = register_uri.rstrip("/") + "/"
    out: set[str] = set()
    for about in _CONCEPT_ABOUT.findall(text):
        if about.startswith(prefix):
            out.add(about[len(prefix) :])
    if not out:
        raise ValueError(f"no skos:Concept members under {register_uri} in {path}")
    return frozenset(out)


@lru_cache(maxsize=32)
def load_aviation_colour_members(
    register: ColourRegister,
    *,
    iwxxm_version: str = "2025-2",
) -> frozenset[str]:
    """
    Load AviationColourCode member notations from offline SCH RDF.

    Parameters
    ----------
    register : {"iwxxm", "49-2"}
        Colour register family.
    iwxxm_version : str, optional
        Vendor pin line (default ``2025-2``).

    Returns
    -------
    frozenset[str]
        Concept notations (e.g. ``RED``, ``UNASSIGNED``).

    Raises
    ------
    FileNotFoundError
        When the pin RDF is missing.
    ValueError
        When ``register`` is unknown or RDF has no concepts.
    """
    key = "iwxxm-colour" if register == "iwxxm" else "49-2-colour" if register == "49-2" else ""
    if not key:
        raise ValueError(f"unknown colour register: {register!r}")
    path = _rule_dir(iwxxm_version) / _RDF_FILES[key]
    if not path.is_file():
        raise FileNotFoundError(path)
    return _rdf_concept_members(path, register_uri=_REGISTER_URI[key])


@lru_cache(maxsize=32)
def load_nil_members(
    family: NilFamily,
    *,
    iwxxm_version: str = "2025-2",
) -> frozenset[str]:
    """
    Load nilReason concept notations from offline SCH RDF.

    Parameters
    ----------
    family : {"common", "iwxxm"}
        Nil register family.
    iwxxm_version : str, optional
        Vendor pin line (default ``2025-2``).

    Returns
    -------
    frozenset[str]
        Nil concept notations (11 members per pin).
    """
    key = "common-nil" if family == "common" else "iwxxm-nil" if family == "iwxxm" else ""
    if not key:
        raise ValueError(f"unknown nil family: {family!r}")
    path = _rule_dir(iwxxm_version) / _RDF_FILES[key]
    if not path.is_file():
        raise FileNotFoundError(path)
    return _rdf_concept_members(path, register_uri=_REGISTER_URI[key])


def _normalize_colour_token(token: str) -> str:
    cleaned = " ".join(token.strip().upper().split())
    if cleaned == "NOT GIVEN":
        return "NOT_GIVEN"
    return cleaned.replace(" ", "_")


def aviation_colour_href(
    token: str,
    *,
    iwxxm_version: str = "2025-2",
    register: ColourRegister | None = None,
) -> str:
    """
    Map a TAC / registry colour token to a codes.wmo.int ``xlink:href``.

    For pin ``2025-2`` (default), prefer ``iwxxm/AviationColourCode``. Tokens
    ``UNKNOWN`` / ``NOT GIVEN`` / ``NIL`` map to ``UNASSIGNED`` — never to a
    invented ``49-2`` NIL colour href when targeting the iwxxm register.

    Parameters
    ----------
    token : str
        Colour token (e.g. ``RED``, ``NOT GIVEN``).
    iwxxm_version : str, optional
        Vendor pin line.
    register : {"iwxxm", "49-2"}, optional
        Override register; default ``iwxxm`` for ``2025-2``, else ``49-2``.

    Returns
    -------
    str
        Absolute colour concept URI.

    Raises
    ------
    ValueError
        When the resolved notation is not in the offline register.
    """
    reg: ColourRegister
    if register is not None:
        reg = register
    else:
        reg = "iwxxm" if iwxxm_version == "2025-2" else "49-2"

    normalized = _normalize_colour_token(token)
    if reg == "iwxxm" and normalized in _UNASSIGNED_TOKENS:
        notation = "UNASSIGNED"
    else:
        notation = normalized

    members = load_aviation_colour_members(reg, iwxxm_version=iwxxm_version)
    if notation not in members:
        raise ValueError(
            f"colour notation {notation!r} not in offline {reg}/AviationColourCode "
            f"for {iwxxm_version} (from token {token!r})"
        )
    prefix = IWXXM_COLOUR_PREFIX if reg == "iwxxm" else LEGACY_COLOUR_PREFIX
    return f"{prefix}{notation}"


def nil_reason_href(
    notation: str,
    *,
    family: NilFamily = "common",
    iwxxm_version: str = "2025-2",
) -> str:
    """
    Build a nilReason URI from the offline ``common/nil`` or ``iwxxm/nil`` RDF.

    Parameters
    ----------
    notation : str
        Nil concept notation (e.g. ``missing``, ``notObservable``).
    family : {"common", "iwxxm"}, optional
        Register family (default ``common`` for aerodrome Guidance nils).
    iwxxm_version : str, optional
        Vendor pin line.

    Returns
    -------
    str
        Absolute nilReason URI.

    Raises
    ------
    ValueError
        When ``notation`` is not a member of the offline register.
    """
    members = load_nil_members(family, iwxxm_version=iwxxm_version)
    if notation not in members:
        raise ValueError(f"nil notation {notation!r} not in offline {family}/nil for {iwxxm_version}")
    prefix = COMMON_NIL_PREFIX if family == "common" else IWXXM_NIL_PREFIX
    return f"{prefix}{notation}"


def clear_codelist_caches() -> None:
    """Clear cached RDF member loads (tests / after vendor sync)."""
    load_aviation_colour_members.cache_clear()
    load_nil_members.cache_clear()


__all__ = [
    "COMMON_NIL_PREFIX",
    "IWXXM_COLOUR_PREFIX",
    "IWXXM_NIL_PREFIX",
    "LEGACY_COLOUR_PREFIX",
    "aviation_colour_href",
    "clear_codelist_caches",
    "load_aviation_colour_members",
    "load_nil_members",
    "nil_reason_href",
    "repo_root",
]
