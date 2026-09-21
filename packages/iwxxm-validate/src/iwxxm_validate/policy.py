"""IWXXM output policy load + resolve (ADR-046 / #1216 M4).

Select/ignore apply to Schematron assert ids only. XSD, well-formed, and
``SCHEMATRON_SKIPPED`` are engine behavior and are not a select surface.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Any, Literal, cast

import yaml

from iwxxm_validate.inventory import InventoryError, load_assert_inventory

PolicyLifecycle = Literal["draft", "activated"]
ENV_POLICY_DIR = "IWXXM_VALIDATE_POLICY_DIR"

# Not selectable (D-VPL-D1..D3).
NON_SELECTABLE = frozenset({"XSD", "WELL_FORMED", "XML_SYNTAX_ERROR", "SCHEMATRON_SKIPPED"})


class PolicyError(ValueError):
    """Invalid IWXXM output policy document."""


class PolicyActivationError(PolicyError):
    """Activated policy references unknown or non-selectable assert ids."""


@dataclass(frozen=True, slots=True)
class OutputPolicyDocument:
    """One IWXXM output policy YAML document."""

    schema_version: int
    id: str
    lifecycle: PolicyLifecycle
    pin: str
    extends: tuple[str, ...]
    select: tuple[str, ...]
    ignore: tuple[str, ...]
    source_path: str | None = None


@dataclass(frozen=True, slots=True)
class ResolvedOutputPolicy:
    """Enabled Schematron assert ids after select/ignore against a pin inventory."""

    id: str
    pin: str
    lifecycle: PolicyLifecycle
    enabled: frozenset[str]
    warnings: tuple[str, ...]


def _as_str_tuple(value: object, *, field: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        msg = f"{field} must be a list of strings"
        raise PolicyError(msg)
    out: list[str] = []
    for item in cast(list[object], value):
        if not isinstance(item, str) or not item.strip():
            msg = f"{field} entries must be non-empty strings"
            raise PolicyError(msg)
        out.append(item.strip())
    return tuple(out)


def _parse_document(data: Mapping[str, Any], *, source_path: str | None) -> OutputPolicyDocument:
    schema_raw = data.get("schema_version", 1)
    if not isinstance(schema_raw, int) or schema_raw < 1:
        msg = "schema_version must be a positive integer"
        raise PolicyError(msg)
    pid = data.get("id")
    if not isinstance(pid, str) or not pid.strip():
        msg = "id is required"
        raise PolicyError(msg)
    life_raw = data.get("lifecycle", "draft")
    if life_raw not in ("draft", "activated"):
        msg = "lifecycle must be draft or activated"
        raise PolicyError(msg)
    lifecycle: PolicyLifecycle = "activated" if life_raw == "activated" else "draft"
    pin_raw = data.get("pin")
    if not isinstance(pin_raw, str) or not pin_raw.strip():
        msg = "pin is required"
        raise PolicyError(msg)
    return OutputPolicyDocument(
        schema_version=schema_raw,
        id=pid.strip(),
        lifecycle=lifecycle,
        pin=pin_raw.strip(),
        extends=_as_str_tuple(data.get("extends"), field="extends"),
        select=_as_str_tuple(data.get("select"), field="select"),
        ignore=_as_str_tuple(data.get("ignore"), field="ignore"),
        source_path=source_path,
    )


def _load_yaml_mapping(text: str, *, source_path: str | None) -> OutputPolicyDocument:
    raw = yaml.safe_load(text)
    if not isinstance(raw, dict):
        msg = "policy root must be a mapping"
        raise PolicyError(msg)
    return _parse_document(cast(Mapping[str, Any], raw), source_path=source_path)


def load_output_policy(path: Path | str) -> OutputPolicyDocument:
    """Load one IWXXM output policy YAML file."""
    file_path = Path(path)
    return _load_yaml_mapping(file_path.read_text(encoding="utf-8"), source_path=str(file_path))


def load_output_policy_catalog() -> dict[str, OutputPolicyDocument]:
    """Load builtin output policies plus optional ``IWXXM_VALIDATE_POLICY_DIR``."""
    catalog: dict[str, OutputPolicyDocument] = {}
    root = resources.files("iwxxm_validate").joinpath("data", "policies")
    for entry in root.iterdir():
        name = entry.name
        if name.endswith((".yaml", ".yml")):
            text = entry.read_text(encoding="utf-8")
            doc = _load_yaml_mapping(text, source_path=f"builtin:{name}")
            catalog[doc.id] = doc
    overlay = os.environ.get(ENV_POLICY_DIR, "").strip()
    if overlay:
        overlay_path = Path(overlay)
        if overlay_path.is_dir():
            for path in sorted(overlay_path.glob("*.yaml")) + sorted(overlay_path.glob("*.yml")):
                doc = load_output_policy(path)
                catalog[doc.id] = doc
    return catalog


def _merged_lists(
    doc: OutputPolicyDocument,
    policies: Mapping[str, OutputPolicyDocument],
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    select: list[str] = []
    ignore: list[str] = []
    seen: set[str] = set()

    def walk(current: OutputPolicyDocument) -> None:
        if current.id in seen:
            msg = f"extends cycle involving {current.id!r}"
            raise PolicyError(msg)
        seen.add(current.id)
        for parent_id in current.extends:
            parent = policies.get(parent_id)
            if parent is None:
                msg = f"unknown extends parent {parent_id!r}"
                raise PolicyError(msg)
            walk(parent)
        if current.select:
            select.clear()
            select.extend(current.select)
        ignore.extend(current.ignore)

    walk(doc)
    return tuple(select), tuple(dict.fromkeys(ignore))


def resolve_output_policy(
    doc: OutputPolicyDocument,
    *,
    policies: Mapping[str, OutputPolicyDocument] | None = None,
    inventory: frozenset[str] | None = None,
    activate: bool | None = None,
) -> ResolvedOutputPolicy:
    """
    Resolve select/ignore against the pin assert inventory.

    Parameters
    ----------
    doc :
        Policy to resolve.
    policies :
        Catalog used for ``extends``. Defaults to the loaded catalog.
    inventory :
        Assert ids for ``doc.pin``. Defaults to the vendor pin inventory.
    activate :
        When true (or lifecycle is activated), unknown ids fail closed.
    """
    catalog = policies if policies is not None else load_output_policy_catalog()
    select, ignore = _merged_lists(doc, catalog)
    refs = set(select) | set(ignore)
    blocked = sorted(code for code in refs if code in NON_SELECTABLE)
    if blocked:
        msg = "not selectable: " + ", ".join(blocked)
        raise PolicyActivationError(msg)
    try:
        known = inventory if inventory is not None else load_assert_inventory(doc.pin)
    except InventoryError as exc:
        raise PolicyError(str(exc)) from exc
    unknown = sorted(code for code in refs if code not in known)
    warnings = tuple(f"unknown assert id {code!r}" for code in unknown)
    fail_closed = doc.lifecycle == "activated" if activate is None else activate
    if unknown and fail_closed:
        raise PolicyActivationError("; ".join(warnings))
    base = set(select) if select else set(known)
    enabled = frozenset(code for code in base if code in known and code not in set(ignore))
    return ResolvedOutputPolicy(
        id=doc.id,
        pin=doc.pin,
        lifecycle=doc.lifecycle,
        enabled=enabled,
        warnings=warnings if not fail_closed else (),
    )


__all__ = [
    "ENV_POLICY_DIR",
    "NON_SELECTABLE",
    "OutputPolicyDocument",
    "PolicyActivationError",
    "PolicyError",
    "ResolvedOutputPolicy",
    "load_output_policy",
    "load_output_policy_catalog",
    "resolve_output_policy",
]
