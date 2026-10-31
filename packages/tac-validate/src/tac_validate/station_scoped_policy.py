"""Lint policies keyed by station ICAO for end-of-TAF TX/TN (F20 / F36).

``UsMilitaryLintPolicy`` and ``LatAmTafLintPolicy`` extend
``StationScopedLintPolicy``. Wire ids stay in ``lint_profiles.yaml``; this
module maps stations and whether TX/TN after change groups is informational.

[Corpus: product §F20] [Corpus: product §F36] [Corpus: domain-profiles]
"""

from __future__ import annotations

from abc import ABC
from functools import cache


class StationScopedLintPolicy(ABC):
    """
    Base class for a lint profile tied to a fixed station list.

    Parameters
    ----------
    profile_id :
        Lint profile id (e.g. ``us_military``).
    stations :
        ICAO codes on this profile.
    accept_end_tx_tn :
        If True, TX/TN after change groups → ``TX_TN_PRESENT`` (info), not
        ``INVALID_TX_TN`` (error).
    """

    profile_id: str
    stations: frozenset[str]
    accept_end_tx_tn: bool = False

    def __init_subclass__(cls, **kwargs: object) -> None:
        """Require ``profile_id`` and ``stations`` on concrete subclasses."""
        super().__init_subclass__(**kwargs)
        required = ("profile_id", "stations")
        for name in required:
            if not hasattr(cls, name):
                msg = f"{cls.__name__} must define {name}"
                raise TypeError(msg)


class UsMilitaryLintPolicy(StationScopedLintPolicy):
    """US military TAF lint (QNH####INS + TX/TN after change groups)."""

    profile_id = "us_military"
    stations = frozenset({"KBIX", "KCVS", "KGRK", "KNID", "KNYL", "KPOE", "KSZL"})
    accept_end_tx_tn = True


class LatAmTafLintPolicy(StationScopedLintPolicy):
    """Latin America TAF lint (TX/TN after change groups)."""

    profile_id = "latam_taf"
    stations = frozenset({"SKBO", "SEQM", "SKBQ", "SVMI"})
    accept_end_tx_tn = True


@cache
def station_scoped_policies() -> tuple[StationScopedLintPolicy, ...]:
    """
    Return the registered station-list policies.

    Returns
    -------
    tuple[StationScopedLintPolicy, ...]
        Policies in registration order.
    """
    return (UsMilitaryLintPolicy(), LatAmTafLintPolicy())


@cache
def _station_to_profile() -> dict[str, str]:
    """Build ICAO → profile_id for every registered policy."""
    mapping: dict[str, str] = {}
    for policy in station_scoped_policies():
        for icao in policy.stations:
            key = icao.upper()
            if key in mapping and mapping[key] != policy.profile_id:
                msg = f"station {key} mapped to both {mapping[key]!r} and {policy.profile_id!r}"
                raise ValueError(msg)
            mapping[key] = policy.profile_id
    return mapping


@cache
def _end_tx_tn_profiles() -> frozenset[str]:
    """Profile ids that treat TX/TN after change groups as info."""
    return frozenset(p.profile_id for p in station_scoped_policies() if p.accept_end_tx_tn)


def resolve_profile_for_station(icao: str) -> str | None:
    """
    Return the lint profile id for an ICAO, if one is listed.

    Parameters
    ----------
    icao :
        Four-letter ICAO (case-insensitive).

    Returns
    -------
    str | None
        Profile id, or ``None`` if the station is not listed.
    """
    token = (icao or "").strip().upper()
    if not token:
        return None
    return _station_to_profile().get(token)


def accepts_end_tx_tn(profile: str) -> bool:
    """
    Return True if ``profile`` treats TX/TN after change groups as info.

    Parameters
    ----------
    profile :
        Lint profile id.

    Returns
    -------
    bool
        True when end TX/TN should be ``TX_TN_PRESENT``.
    """
    return profile.strip().lower() in _end_tx_tn_profiles()


__all__ = [
    "LatAmTafLintPolicy",
    "StationScopedLintPolicy",
    "UsMilitaryLintPolicy",
    "accepts_end_tx_tn",
    "resolve_profile_for_station",
    "station_scoped_policies",
]
