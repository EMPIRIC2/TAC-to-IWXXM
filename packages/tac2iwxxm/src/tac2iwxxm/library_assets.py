"""Five Libraries asset catalog (EV-bridge-ux-canvas-align).

First-party defaults are seeded per national semantic profile line x library kind.
Custom assets are persisted by the API; builtins are immutable (fork-on-edit).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, cast

from tac2iwxxm.conversion_templates import (
    FIRST_PARTY_TEMPLATES,
    ConversionTemplate,
    list_first_party_templates,
)
from tac2iwxxm.profile_registry import canonical_semantic_profile_wire_ids

LibraryKind = Literal[
    "conversion",
    "tac_validation",
    "iwxxm_validation",
    "dissemination",
    "decoding",
]

LIBRARY_KINDS: tuple[LibraryKind, ...] = (
    "conversion",
    "tac_validation",
    "iwxxm_validation",
    "dissemination",
    "decoding",
)

Access = Literal["first_party", "custom"]


def canonical_national_line_ids() -> tuple[str, ...]:
    """
    Return wire-form national semantic profile ids (uppercase).

    Returns
    -------
    tuple[str, ...]
        Sorted OpenAPI-style ids such as ``ICAO_2025``.
    """
    return canonical_semantic_profile_wire_ids()


@dataclass(frozen=True, slots=True)
class LibraryAsset:
    """One first-party or custom library asset."""

    id: str
    kind: LibraryKind
    name: str
    access: Access
    engine_profile_id: str
    attached_national_line: str
    body: dict[str, Any]
    fork_of: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize for JSON / API responses."""
        return {
            "id": self.id,
            "kind": self.kind,
            "name": self.name,
            "access": self.access,
            "engine_profile_id": self.engine_profile_id,
            "attached_national_line": self.attached_national_line,
            "body": dict(self.body),
            "fork_of": self.fork_of,
        }


def _kind_label(kind: LibraryKind) -> str:
    return {
        "conversion": "Conversion",
        "tac_validation": "TAC validation",
        "iwxxm_validation": "IWXXM validation",
        "dissemination": "Dissemination",
        "decoding": "Decoding",
    }[kind]


def _seed_body(kind: LibraryKind, national_line: str) -> dict[str, Any]:
    """Build a minimal first-party body for the kind."""
    if kind == "conversion":
        from tac2iwxxm.conversion_schema_blocks import schema_blocks_for_national_line

        templates = [t.to_dict() for t in list_first_party_templates()]
        return {
            "rules": templates,
            "schema_blocks": schema_blocks_for_national_line(national_line),
            "note": "TAC groups must match an associated conversion rule (AC11).",
        }
    if kind == "tac_validation":
        from tac2iwxxm.validation_library_catalogs import load_tac_validation_rules

        catalog = load_tac_validation_rules()
        return {
            "rules": list(catalog.get("rules") or []),
            "product_scope": "METAR",
            "national_line": national_line,
        }
    if kind == "iwxxm_validation":
        from tac2iwxxm.validation_library_catalogs import load_iwxxm_validation_asserts

        catalog = load_iwxxm_validation_asserts()
        return {
            "rules": list(catalog.get("asserts") or []),
            "schematron": True,
            "national_line": national_line,
        }
    if kind == "dissemination":
        return {
            "annotations": [],
            "transforms": [
                {"id": "envelope", "type": "envelope"},
                {"id": "topic_filename", "type": "topic_filename"},
                {"id": "bulletin_rewrap", "type": "bulletin_rewrap"},
                {"id": "checksum", "type": "checksum"},
            ],
            "national_line": national_line,
        }
    # Decoding: seed from F9 glossary / decode_tac catalog (AC9).
    from tac2iwxxm.glossary import load_glossary

    glossary = load_glossary()
    entries = [
        {
            "token": token,
            "explanation": meaning,
            "source": "decode_tac",
        }
        for token, meaning in sorted(glossary.items())
    ]
    return {
        "entries": entries,
        "seed": "decode_tac",
        "national_line": national_line,
    }


def first_party_library_id(kind: LibraryKind, national_line: str) -> str:
    """
    Stable first-party id for a kind x national line.

    Parameters
    ----------
    kind :
        Library kind.
    national_line :
        Uppercase wire id (e.g. ``ICAO_2025``).

    Returns
    -------
    str
        Id such as ``LIB.CONVERSION.ICAO_2025``.
    """
    kind_token = kind.upper()
    return f"LIB.{kind_token}.{national_line}"


def list_first_party_library_assets() -> tuple[LibraryAsset, ...]:
    """
    Seed five library defaults for every known national semantic profile.

    Returns
    -------
    tuple[LibraryAsset, ...]
        Immutable first-party catalog (5 kinds per national line).
    """
    return tuple(
        LibraryAsset(
            id=first_party_library_id(kind, national),
            kind=kind,
            name=f"{_kind_label(kind)} · {national}",
            access="first_party",
            engine_profile_id=national,
            attached_national_line=national,
            body=_seed_body(kind, national),
        )
        for national in canonical_national_line_ids()
        for kind in LIBRARY_KINDS
    )


def get_first_party_library_asset(asset_id: str) -> LibraryAsset | None:
    """
    Look up a first-party library asset by id.

    Parameters
    ----------
    asset_id :
        Stable ``LIB.*`` id.

    Returns
    -------
    LibraryAsset | None
        Matching asset, or ``None``.
    """
    for asset in list_first_party_library_assets():
        if asset.id == asset_id:
            return asset
    return None


def fork_first_party_library(
    asset_id: str,
    *,
    new_id: str,
    name: str | None = None,
) -> LibraryAsset:
    """
    Fork a first-party library asset to a custom copy (immutable source).

    Parameters
    ----------
    asset_id :
        First-party id to fork.
    new_id :
        Id for the custom fork.
    name :
        Optional display name; defaults to ``"{name} (fork)"``.

    Returns
    -------
    LibraryAsset
        Custom asset with ``fork_of`` set.

    Raises
    ------
    KeyError
        When ``asset_id`` is unknown.
    ValueError
        When attempting to fork a non-first-party id shape incorrectly.
    """
    base = get_first_party_library_asset(asset_id)
    if base is None:
        msg = f"unknown first-party library asset: {asset_id}"
        raise KeyError(msg)
    return LibraryAsset(
        id=new_id,
        kind=base.kind,
        name=name or f"{base.name} (fork)",
        access="custom",
        engine_profile_id=base.engine_profile_id,
        attached_national_line=base.attached_national_line,
        body=dict(base.body),
        fork_of=base.id,
    )


def assert_first_party_immutable(asset: LibraryAsset, *, mutating: bool) -> None:
    """
    Fail closed when mutating or deleting a first-party asset.

    Parameters
    ----------
    asset :
        Asset under consideration.
    mutating :
        ``True`` for update/delete of the builtin itself.

    Raises
    ------
    PermissionError
        When ``mutating`` and ``access`` is ``first_party``.
    """
    if mutating and asset.access == "first_party":
        msg = "first-party library defaults cannot be mutated or deleted; fork instead"
        raise PermissionError(msg)


def conversion_rules_for_asset(asset: LibraryAsset) -> tuple[ConversionTemplate, ...]:
    """
    Return ConversionTemplate rules embedded in a conversion library asset.

    Parameters
    ----------
    asset :
        Conversion-kind library asset.

    Returns
    -------
    tuple[ConversionTemplate, ...]
        Parsed rules; empty for non-conversion kinds.
    """
    if asset.kind != "conversion":
        return ()
    from tac2iwxxm.conversion_templates import template_from_dict

    rules_raw = asset.body.get("rules")
    if not isinstance(rules_raw, list):
        return ()
    raw_items = cast(list[Any], rules_raw)
    typed_dicts = [cast(dict[str, Any], item) for item in raw_items if isinstance(item, dict)]
    return tuple(template_from_dict(item) for item in typed_dicts)


def require_rule_for_group(
    asset: LibraryAsset,
    *,
    focus_group: str,
) -> ConversionTemplate:
    """
    Resolve the Conversion rule that matches a TAC group (AC11).

    Parameters
    ----------
    asset :
        Conversion library asset.
    focus_group :
        TAC group token (e.g. ``18012G20KT``).

    Returns
    -------
    ConversionTemplate
        Matching rule.

    Raises
    ------
    ValueError
        When kind is not conversion or no rule matches (fail closed).
    """
    from tac2iwxxm.conversion_templates import preview_bridge

    if asset.kind != "conversion":
        msg = "rule association requires a conversion library asset"
        raise ValueError(msg)
    rules = conversion_rules_for_asset(asset)
    if not rules:
        # Fall back to global first-party templates for seed bodies
        rules = tuple(FIRST_PARTY_TEMPLATES.values())
    for rule in rules:
        preview = preview_bridge(rule, focus_group=focus_group)
        if preview.matched:
            return rule
    msg = f"no conversion rule associated for TAC group: {focus_group!r}"
    raise ValueError(msg)


__all__ = [
    "LIBRARY_KINDS",
    "Access",
    "LibraryAsset",
    "LibraryKind",
    "assert_first_party_immutable",
    "canonical_national_line_ids",
    "conversion_rules_for_asset",
    "first_party_library_id",
    "fork_first_party_library",
    "get_first_party_library_asset",
    "list_first_party_library_assets",
    "require_rule_for_group",
]
