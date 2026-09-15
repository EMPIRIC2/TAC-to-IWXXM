"""Operator Convert hard-cut helpers (EV-bridge AC7 / AC10).

Legacy Form fields ``semantic_profile`` / ``profile`` / ``preset_id`` /
``overlay_id`` / ``exchange_profile`` are rejected on the operator Convert
HTTP surface. Engine profile is resolved only from ``conversion_library_id``.
"""

from __future__ import annotations

from collections.abc import Callable

from tac2iwxxm.library_assets import (
    first_party_library_id,
    get_first_party_library_asset,
)
from tac2iwxxm.profile_registry import resolve_semantic_profile

DEFAULT_CONVERSION_LIBRARY_ID = first_party_library_id("conversion", "ICAO_2025")

_LEGACY_FIELD_NAMES = (
    "semantic_profile",
    "profile",
    "preset_id",
    "overlay_id",
    "exchange_profile",
)


def legacy_convert_fields_present(
    *,
    semantic_profile: str = "",
    profile: str = "",
    preset_id: str = "",
    overlay_id: str = "",
    exchange_profile: str = "",
) -> list[str]:
    """
    Return non-empty legacy Convert field names.

    Parameters
    ----------
    semantic_profile, profile, preset_id, overlay_id, exchange_profile :
        Raw Form / JSON values.

    Returns
    -------
    list[str]
        Operator-visible field names that were supplied.
    """
    values = {
        "semantic_profile": semantic_profile,
        "profile": profile,
        "preset_id": preset_id,
        "overlay_id": overlay_id,
        "exchange_profile": exchange_profile,
    }
    return [name for name in _LEGACY_FIELD_NAMES if (values.get(name) or "").strip()]


def legacy_convert_reject_detail(fields: list[str]) -> str:
    """Plain-language 422 detail for legacy Convert fields."""
    joined = ", ".join(fields)
    return (
        f"Legacy convert fields are no longer accepted: {joined}. "
        "Send conversion_library_id (and the other library ids) instead."
    )


def resolve_engine_profile_from_conversion_library(
    conversion_library_id: str,
    *,
    get_custom_engine_profile_id: Callable[[str], str | None] | None = None,
) -> tuple[str, str]:
    """
    Resolve ``(library_id, engine_profile_id)`` for Convert.

    Empty library id defaults to the ICAO Conversion first-party asset.
    Unknown ids raise ``ValueError``.

    Parameters
    ----------
    conversion_library_id :
        Library asset id from the Convert bar.
    get_custom_engine_profile_id :
        Optional lookup for custom (non first-party) assets; returns engine
        profile id or ``None``.

    Returns
    -------
    tuple[str, str]
        Canonical library id used and engine semantic profile wire id.
    """
    token = (conversion_library_id or "").strip() or DEFAULT_CONVERSION_LIBRARY_ID
    first = get_first_party_library_asset(token)
    if first is not None:
        if first.kind != "conversion":
            msg = "conversion_library_id must reference a Conversion library"
            raise ValueError(msg)
        return first.id, first.engine_profile_id

    if get_custom_engine_profile_id is not None:
        engine = get_custom_engine_profile_id(token)
        if engine:
            resolved = resolve_semantic_profile(str(engine))
            wire = resolved.canonical.upper() if resolved is not None else str(engine).strip().upper()
            return token, wire

    msg = f"Unknown conversion library id: {token}"
    raise ValueError(msg)


def library_id_for_semantic_or_alias(profile_or_alias: str) -> str:
    """
    Map a legacy semantic id / emit alias to a Conversion library id.

    Used by tests migrating off ``semantic_profile`` / ``profile``.
    """
    raw = (profile_or_alias or "").strip()
    if not raw:
        return DEFAULT_CONVERSION_LIBRARY_ID
    if raw.upper().startswith("LIB."):
        return raw
    resolved = resolve_semantic_profile(raw)
    if resolved is None:
        return DEFAULT_CONVERSION_LIBRARY_ID
    return first_party_library_id("conversion", resolved.canonical.upper())
