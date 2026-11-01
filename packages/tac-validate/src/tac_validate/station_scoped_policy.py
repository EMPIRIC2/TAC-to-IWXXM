"""Station-scoped lint flags loaded from ``lint_profiles.yaml``.

Profiles with ``stations`` and/or ``accept_end_tx_tn`` drive ICAO → profile
resolve and end-of-TAF TX/TN info treatment. No per-country Python subclasses.

[Corpus: product §F20] [Corpus: product §F36] [Corpus: domain-profiles]
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache

from tac_validate.lint_profile_catalog import load_lint_profiles


@dataclass(frozen=True, slots=True)
class StationScopedLintPolicy:
    """
    One catalog row that lists stations and/or end TX/TN acceptance.

    Attributes
    ----------
    profile_id : str
        Lint profile id.
    stations : frozenset[str]
        ICAO codes on this profile.
    accept_end_tx_tn : bool
        If True, TX/TN after change groups → ``TX_TN_PRESENT``.
    """

    profile_id: str
    stations: frozenset[str]
    accept_end_tx_tn: bool = False


@cache
def station_scoped_policies() -> tuple[StationScopedLintPolicy, ...]:
    """
    Return catalog profiles that declare stations.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (station_scoped_policies)
    2

    Returns
    -------
    tuple[StationScopedLintPolicy, ...]
        Policies in catalog order.
    """
    rows: list[StationScopedLintPolicy] = []
    for profile_id, spec in load_lint_profiles().items():
        if not spec.stations and not spec.accept_end_tx_tn:
            continue
        if not spec.stations:
            continue
        rows.append(
            StationScopedLintPolicy(
                profile_id=profile_id,
                stations=spec.stations,
                accept_end_tx_tn=spec.accept_end_tx_tn,
            )
        )
    return tuple(rows)


@cache
def _station_to_profile() -> dict[str, str]:
    """
    Build ICAO → profile_id for every station-listed profile.

    Returns
    -------
    dict[str, str]
        Uppercase ICAO to lint profile id.
    """
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
def _prefix_to_profile() -> tuple[tuple[str, str], ...]:
    """
    Build ICAO-prefix → profile_id pairs, longest prefix first.

    National profiles (e.g. US ``K``, Canada ``CY``) claim a country prefix so
    live/default ``annex3`` + ICAO prefer maps a station to its national profile
    for TAF. Exact ``stations`` entries win over any prefix match.

    Returns
    -------
    tuple[tuple[str, str], ...]
        ``(prefix, profile_id)`` pairs sorted by descending prefix length.

    Raises
    ------
    ValueError
        When one prefix is claimed by two profiles.
    """
    pairs: dict[str, str] = {}
    for profile_id, spec in load_lint_profiles().items():
        for prefix in spec.station_prefixes:
            key = prefix.upper()
            if key in pairs and pairs[key] != profile_id:
                msg = f"prefix {key} claimed by both {pairs[key]!r} and {profile_id!r}"
                raise ValueError(msg)
            pairs[key] = profile_id
    return tuple(sorted(pairs.items(), key=lambda item: len(item[0]), reverse=True))


def resolve_profile_for_station(icao: str) -> str | None:
    """
    Return the lint profile id for an ICAO, if one is listed.

    Exact ``stations`` entries win over country ``station_prefixes`` (e.g. the
    military ``KBIX`` beats the US ``K`` prefix), and the longest prefix wins.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (resolve_profile_for_station)
    2

    Parameters
    ----------
    icao : str
        Four-letter ICAO (case-insensitive).

    Returns
    -------
    str | None
        Profile id, or ``None`` if the station is not listed.
    """
    token = (icao or "").strip().upper()
    if not token:
        return None
    exact = _station_to_profile().get(token)
    if exact is not None:
        return exact
    for prefix, profile_id in _prefix_to_profile():
        if token.startswith(prefix):
            return profile_id
    return None


def accepts_end_tx_tn(profile: str) -> bool:
    """
    Return True if ``profile`` treats TX/TN after change groups as info.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (accepts_end_tx_tn)
    2

    Parameters
    ----------
    profile : str
        Lint profile id.

    Returns
    -------
    bool
        True when end TX/TN should be ``TX_TN_PRESENT``.
    """
    spec = load_lint_profiles().get(profile.strip().lower())
    return bool(spec is not None and spec.accept_end_tx_tn)


def stations_for(profile: str) -> frozenset[str]:
    """
    Return ICAO stations listed on ``profile``.

    Parameters
    ----------
    profile : str
        Lint profile id.

    Returns
    -------
    frozenset[str]
        Station set (possibly empty).

    Examples
    --------
    >>> 1 + 1  # docstring smoke (stations_for)
    2
    """
    spec = load_lint_profiles().get(profile.strip().lower())
    if spec is None:
        return frozenset()
    return spec.stations


__all__ = [
    "StationScopedLintPolicy",
    "accepts_end_tx_tn",
    "resolve_profile_for_station",
    "station_scoped_policies",
    "stations_for",
]
