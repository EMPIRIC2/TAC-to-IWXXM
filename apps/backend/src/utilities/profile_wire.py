"""HTTP profile wire resolution (F35 / EV-063 / ADR-036).

Resolves multipart ``semantic_profile`` / ``exchange_profile`` and legacy ``profile``
into tac2iwxxm emit keys. Unknown ids fail closed with HTTP 400.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dissemination.exchange_registry import (
    DEFAULT_EXCHANGE_PROFILE_ID,
    resolve_exchange_profile,
)
from fastapi import HTTPException
from tac2iwxxm.profile_registry import resolve_semantic_profile

_LEGACY_DEFAULT_PROFILE = "annex3"
_WIRE_V2_DEFAULT_SEMANTIC = "ICAO_2025"


def _truthy_env(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def profile_wire_v2_enabled() -> bool:
    """Return whether nested semantic/exchange wire defaults are active."""
    return _truthy_env("PROFILE_WIRE_V2")


def default_semantic_profile() -> str:
    """Default semantic profile id for the active wire mode."""
    if profile_wire_v2_enabled():
        return os.getenv("DEFAULT_SEMANTIC_PROFILE", _WIRE_V2_DEFAULT_SEMANTIC).strip() or _WIRE_V2_DEFAULT_SEMANTIC
    return os.getenv("DEFAULT_SEMANTIC_PROFILE", _LEGACY_DEFAULT_PROFILE).strip() or _LEGACY_DEFAULT_PROFILE


def default_exchange_profile() -> str:
    """Default exchange profile id when packaging paths run."""
    return os.getenv("DEFAULT_EXCHANGE_PROFILE", DEFAULT_EXCHANGE_PROFILE_ID).strip() or DEFAULT_EXCHANGE_PROFILE_ID


def _clean(value: str | None) -> str:
    return (value or "").strip()


def _resolve_exchange_profile(raw: str | None, *, for_packaging: bool) -> str | None:
    cleaned = _clean(raw)
    if not cleaned:
        if for_packaging:
            return default_exchange_profile()
        return None
    resolved = resolve_exchange_profile(cleaned)
    if resolved is None:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "invalid_exchange_profile",
                "message": f"Unknown exchange profile {cleaned!r}",
            },
        )
    return resolved.wire_id


@dataclass(frozen=True, slots=True)
class WireProfileSelection:
    """Resolved profile wire fields for a single HTTP request."""

    emit_key: str
    semantic_canonical: str
    deprecated_alias_used: bool
    exchange_profile: str | None


def resolve_route_profiles(
    *,
    profile: str | None = None,
    semantic_profile: str | None = None,
    exchange_profile: str | None = None,
    for_packaging: bool = False,
) -> WireProfileSelection:
    """
    Resolve semantic and exchange profile multipart/JSON fields.

    Parameters
    ----------
    profile :
        Legacy flat profile field (deprecated alias path).
    semantic_profile :
        Canonical or alias semantic profile id.
    exchange_profile :
        Exchange packaging profile id (validated when provided).
    for_packaging :
        When ``True``, default to ``GLOBAL_AFS`` if exchange profile is omitted.

    Returns
    -------
    WireProfileSelection
        Emit key for tac2iwxxm / iwxxm-validate plus canonical semantic id.

    Raises
    ------
    HTTPException
        HTTP 400 when semantic or exchange profile id is unknown.
    """
    semantic_raw = _clean(semantic_profile)
    legacy_raw = _clean(profile)

    if semantic_raw:
        chosen = semantic_raw
    elif legacy_raw:
        chosen = legacy_raw
    else:
        chosen = default_semantic_profile()

    resolved = resolve_semantic_profile(chosen)
    if resolved is None:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "invalid_semantic_profile",
                "message": f"Unknown semantic profile {chosen!r}",
            },
        )

    exchange = _resolve_exchange_profile(exchange_profile, for_packaging=for_packaging)
    return WireProfileSelection(
        emit_key=resolved.emit_key,
        semantic_canonical=resolved.canonical,
        deprecated_alias_used=resolved.alias_used,
        exchange_profile=exchange,
    )


__all__ = [
    "WireProfileSelection",
    "default_exchange_profile",
    "default_semantic_profile",
    "profile_wire_v2_enabled",
    "resolve_route_profiles",
]
