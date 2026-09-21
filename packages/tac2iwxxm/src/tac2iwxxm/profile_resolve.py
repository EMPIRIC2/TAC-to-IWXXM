"""Map a conversion profile to TAC quality and IWXXM output policy ids (ADR-046 / #1216 M5).

Validators stay dumb loaders. This module only resolves document ids.
An optional ``TAC2IWXXM_PROFILE_DIR`` overlay layers policy ids onto one builtin
binding for the conversion profile ids in its header.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import cast

import yaml

from tac2iwxxm.profile_registry import resolve_semantic_profile

_ANNEX3_POLICIES = ("annex3-metar-quality", "annex3-iwxxm-output")
ENV_PROFILE_DIR = "TAC2IWXXM_PROFILE_DIR"

# National emit keys share the annex3 policy documents until a profile ships its own ids.
_POLICY_BY_EMIT: dict[str, tuple[str, str]] = {
    "annex3": _ANNEX3_POLICIES,
    "iwxxm_us": _ANNEX3_POLICIES,
    "ca_eccc": _ANNEX3_POLICIES,
    "au_bom": _ANNEX3_POLICIES,
    "nz_caa_met": _ANNEX3_POLICIES,
    "uk_metoffice": _ANNEX3_POLICIES,
    "br_decea": _ANNEX3_POLICIES,
    "kr_kma": _ANNEX3_POLICIES,
    "jp_jma": _ANNEX3_POLICIES,
    "in_imd": _ANNEX3_POLICIES,
    "hk_hko": _ANNEX3_POLICIES,
}


class ProfileResolveError(ValueError):
    """Conversion profile id is unknown or has no policy binding."""


@dataclass(frozen=True, slots=True)
class ResolvedValidationPolicies:
    """Policy document ids bound to one conversion profile."""

    canonical: str
    emit_key: str
    tac_quality_policy_id: str
    iwxxm_output_policy_id: str


@dataclass(frozen=True, slots=True)
class _ProfileOverlay:
    profiles: tuple[str, ...]
    extends: str
    tac_quality_policy_id: str | None
    iwxxm_output_policy_id: str | None


def _string_list(value: object, *, label: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value:
        msg = label
        raise ProfileResolveError(msg)
    out: list[str] = []
    for item in cast(list[object], value):
        if not isinstance(item, str) or not item.strip():
            msg = label
            raise ProfileResolveError(msg)
        out.append(item.strip())
    return tuple(out)


def _optional_id(value: object, *, field: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        msg = f"{field} must be a string when set"
        raise ProfileResolveError(msg)
    return value.strip()


def _load_profile_overlays() -> tuple[_ProfileOverlay, ...]:
    raw_dir = os.environ.get(ENV_PROFILE_DIR, "").strip()
    if not raw_dir:
        return ()
    directory = Path(raw_dir)
    if not directory.is_dir():
        msg = f"Profile directory is not a folder: {directory}"
        raise ProfileResolveError(msg)
    found: list[_ProfileOverlay] = []
    for path in sorted(directory.iterdir()):
        if path.suffix.lower() not in {".yaml", ".yml"}:
            continue
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            msg = f"{path.name} must be a mapping"
            raise ProfileResolveError(msg)
        mapping = cast(dict[str, object], data)
        extends_raw = mapping.get("extends")
        if isinstance(extends_raw, str):
            extends_values: object = [extends_raw]
        else:
            extends_values = extends_raw
        extends = _string_list(extends_values, label=f"{path.name} must extend one builtin")
        if len(extends) != 1 or extends[0] not in _POLICY_BY_EMIT:
            if len(extends) != 1:
                msg = f"{path.name} must extend one builtin"
            else:
                msg = f"{path.name} extends unknown builtin {extends[0]}"
            raise ProfileResolveError(msg)
        profiles = _string_list(mapping.get("profiles"), label=f"{path.name} needs a profiles list")
        found.append(
            _ProfileOverlay(
                profiles=profiles,
                extends=extends[0],
                tac_quality_policy_id=_optional_id(
                    mapping.get("tac_quality_policy_id"),
                    field="tac_quality_policy_id",
                ),
                iwxxm_output_policy_id=_optional_id(
                    mapping.get("iwxxm_output_policy_id"),
                    field="iwxxm_output_policy_id",
                ),
            )
        )
    return tuple(found)


def resolve_validation_policies(
    profile: str,
    *,
    tac_policy: str | None = None,
    iwxxm_policy: str | None = None,
) -> ResolvedValidationPolicies:
    """
    Resolve ``profile`` to TAC quality and IWXXM output policy ids.

    Parameters
    ----------
    profile :
        Canonical conversion profile id or legacy alias (``ICAO_2025``, ``annex3``).
    tac_policy :
        Optional override for the TAC quality policy id (CLI ``--policy``).
    iwxxm_policy :
        Optional override for the IWXXM output policy id (CLI ``--policy``).
    """
    resolved = resolve_semantic_profile(profile)
    if resolved is None:
        msg = f"unknown conversion profile {profile!r}"
        raise ProfileResolveError(msg)
    pair = _POLICY_BY_EMIT.get(resolved.emit_key)
    if pair is None:
        msg = f"no policy binding for profile {resolved.canonical!r}"
        raise ProfileResolveError(msg)
    tac_id, iwxxm_id = pair
    keys = {resolved.emit_key, resolved.canonical, profile.strip()}
    for overlay in _load_profile_overlays():
        if keys.isdisjoint(overlay.profiles):
            continue
        shares_annex3 = pair == _ANNEX3_POLICIES and overlay.extends == "annex3"
        if overlay.extends != resolved.emit_key and not shares_annex3:
            continue
        if overlay.tac_quality_policy_id:
            tac_id = overlay.tac_quality_policy_id
        if overlay.iwxxm_output_policy_id:
            iwxxm_id = overlay.iwxxm_output_policy_id
    tac_override = tac_policy.strip() if isinstance(tac_policy, str) and tac_policy.strip() else ""
    iwxxm_override = iwxxm_policy.strip() if isinstance(iwxxm_policy, str) and iwxxm_policy.strip() else ""
    return ResolvedValidationPolicies(
        canonical=resolved.canonical,
        emit_key=resolved.emit_key,
        tac_quality_policy_id=tac_override or tac_id,
        iwxxm_output_policy_id=iwxxm_override or iwxxm_id,
    )


__all__ = [
    "ENV_PROFILE_DIR",
    "ProfileResolveError",
    "ResolvedValidationPolicies",
    "resolve_validation_policies",
]
