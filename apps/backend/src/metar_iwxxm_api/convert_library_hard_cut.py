"""Operator Convert hard-cut helpers (EV-bridge AC7 / AC10).

Legacy Form fields ``semantic_profile`` / ``profile`` / ``preset_id`` /
``overlay_id`` / ``exchange_profile`` are rejected on the operator Convert
HTTP surface. Engine profile is resolved only from ``conversion_library_id``.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import cast

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


def resolve_dissemination_transforms(
    dissemination_library_id: str,
    *,
    get_custom_dissemination_body: Callable[[str], dict[str, object] | None] | None = None,
) -> list[object]:
    """
    Load ordered Dissemination transform specs for a library id.

    First-party ``LIB.DISSEMINATION.*`` assets resolve from code. Custom UUIDs
    require ``get_custom_dissemination_body`` (authenticated service lookup that
    already enforced ``kind == \"dissemination\"``).

    Parameters
    ----------
    dissemination_library_id :
        Dissemination library asset id.
    get_custom_dissemination_body :
        Optional callback returning the asset ``body`` dict, or ``None``.

    Returns
    -------
    list[object]
        Transform entries from ``body.transforms`` (may be empty).

    Raises
    ------
    ValueError
        Unknown id or wrong kind.
    """
    token = (dissemination_library_id or "").strip()
    if not token:
        msg = "dissemination_library_id is required"
        raise ValueError(msg)

    first = get_first_party_library_asset(token)
    if first is not None:
        if first.kind != "dissemination":
            msg = "dissemination_library_id must reference a Dissemination library"
            raise ValueError(msg)
        raw_transforms = (first.body or {}).get("transforms", [])
        if not isinstance(raw_transforms, list):
            return []
        return cast(list[object], raw_transforms)

    if get_custom_dissemination_body is not None:
        body = get_custom_dissemination_body(token)
        if body is not None:
            raw_transforms = body.get("transforms", [])
            if not isinstance(raw_transforms, list):
                return []
            return cast(list[object], raw_transforms)

    msg = f"Unknown dissemination library id: {token}"
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


DRAFT_LIBRARY_CONVERT_DETAIL = (
    "This library is still a draft. Activate it on Profile builder before using it on Convert."
)


def assert_library_usable_on_convert(
    *,
    kind: str,
    expected_kind: str,
    access: str,
    status: str | None,
) -> None:
    """Reject draft custom libraries on Convert (operator-visible detail)."""
    if kind != expected_kind:
        labels = {
            "conversion": "Conversion",
            "tac_validation": "TAC validation",
            "iwxxm_validation": "IWXXM validation",
            "dissemination": "Dissemination",
            "decoding": "Decoding",
        }
        label = labels.get(expected_kind, expected_kind)
        if expected_kind == "conversion":
            msg = "conversion_library_id must reference a Conversion library"
        elif expected_kind == "dissemination":
            msg = "dissemination_library_id must reference a Dissemination library"
        else:
            msg = f"library id must reference a {label} library"
        raise ValueError(msg)
    lifecycle = status or ("activated" if access == "first_party" else "draft")
    if access == "custom" and lifecycle != "activated":
        raise ValueError(DRAFT_LIBRARY_CONVERT_DETAIL)
