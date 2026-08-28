"""Exchange profile id registry (F36 / ADR-036 / EV-063).

Canonical exchange ids map to wire ids (``GLOBAL_AFS``, …). Packaging hooks
consume resolved ids - exchange profiles do not carry dissemination credentials.
"""

from __future__ import annotations

from dataclasses import dataclass

CANONICAL_GLOBAL_AFS = "global_afs"
CANONICAL_APAC_ROBEX = "apac_robex"
CANONICAL_EUR_RODEX = "eur_rodex"
CANONICAL_AFI = "afi"
CANONICAL_CAR_SAM = "car_sam"
DEFAULT_EXCHANGE_PROFILE_ID = "GLOBAL_AFS"

_CANONICAL_TO_WIRE: dict[str, str] = {
    CANONICAL_GLOBAL_AFS: DEFAULT_EXCHANGE_PROFILE_ID,
    CANONICAL_APAC_ROBEX: "APAC_ROBEX",
    CANONICAL_EUR_RODEX: "EUR_RODEX",
    CANONICAL_AFI: "AFI",
    CANONICAL_CAR_SAM: "CAR_SAM",
}

_KNOWN_WIRE_IDS: frozenset[str] = frozenset(_CANONICAL_TO_WIRE) | frozenset(_CANONICAL_TO_WIRE.values())


@dataclass(frozen=True, slots=True)
class ResolvedExchangeProfile:
    """Resolved exchange profile with canonical id and wire id."""

    canonical: str
    wire_id: str


def normalize_exchange_id(profile: str) -> str:
    """
    Normalize an exchange profile id for wire output.

    Parameters
    ----------
    profile :
        Exchange profile id (e.g. ``GLOBAL_AFS``).

    Returns
    -------
    str
        Uppercase id with hyphens as underscores.
    """
    return profile.strip().upper().replace("-", "_")


def normalize_exchange_id_key(profile: str) -> str:
    """Return lowercase registry lookup key for an exchange profile id."""
    return profile.strip().lower().replace("-", "_")


def resolve_exchange_profile(profile: str) -> ResolvedExchangeProfile | None:
    """
    Resolve an exchange profile id to canonical + wire id.

    Parameters
    ----------
    profile :
        Canonical or wire exchange profile id.

    Returns
    -------
    ResolvedExchangeProfile | None
        ``None`` when the id is unknown.
    """
    norm = normalize_exchange_id_key(profile)
    if norm in _CANONICAL_TO_WIRE:
        return ResolvedExchangeProfile(
            canonical=norm,
            wire_id=_CANONICAL_TO_WIRE[norm],
        )
    wire = normalize_exchange_id(profile)
    for canonical, wire_id in _CANONICAL_TO_WIRE.items():
        if wire == wire_id:
            return ResolvedExchangeProfile(canonical=canonical, wire_id=wire_id)
    return None


def known_exchange_profile_ids() -> frozenset[str]:
    """Return all accepted exchange profile wire ids."""
    return _KNOWN_WIRE_IDS


__all__ = [
    "CANONICAL_AFI",
    "CANONICAL_APAC_ROBEX",
    "CANONICAL_CAR_SAM",
    "CANONICAL_EUR_RODEX",
    "CANONICAL_GLOBAL_AFS",
    "DEFAULT_EXCHANGE_PROFILE_ID",
    "ResolvedExchangeProfile",
    "known_exchange_profile_ids",
    "normalize_exchange_id",
    "normalize_exchange_id_key",
    "resolve_exchange_profile",
]
