"""IWXXM output policy load + resolve (ADR-046 / #1216 M4).

Select/ignore apply to Schematron assert ids only. XSD, well-formed, and
``SCHEMATRON_SKIPPED`` are engine behavior and are not a select surface.

"""

from __future__ import annotations

import os
from collections.abc import Mapping
from importlib import resources
from pathlib import Path
from typing import Any, cast

import yaml

from iwxxm_validate.inventory import InventoryError, load_assert_inventory
from iwxxm_validate.models import ValidationReport
from iwxxm_validate.models.policy import (
    OutputPolicyDocument,
    PolicyActivationError,
    PolicyError,
    PolicyLifecycle,
    ResolvedOutputPolicy,
)

ENV_POLICY_DIR = "IWXXM_VALIDATE_POLICY_DIR"

# Not selectable (D-VPL-D1..D3).
NON_SELECTABLE = frozenset({"XSD", "WELL_FORMED", "XML_SYNTAX_ERROR", "SCHEMATRON_SKIPPED"})


def _as_str_tuple(value: object, *, field: str) -> tuple[str, ...]:
    """
    Internal helper ``_as_str_tuple``.

    Parameters
    ----------
    value : object
        Argument ``value``.
    field : object
        Argument ``field``.


    Returns
    -------
    object
        Return value.
    """
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
    """
    Internal helper ``_parse_document``.

    Parameters
    ----------
    data : object
        Argument ``data``.
    source_path : object
        Argument ``source_path``.


    Returns
    -------
    object
        Return value.
    """
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
        profiles=_as_str_tuple(data.get("profiles"), field="profiles"),
        source_path=source_path,
    )


def _load_yaml_mapping(text: str, *, source_path: str | None) -> OutputPolicyDocument:
    """
    Internal helper ``_load_yaml_mapping``.

    Parameters
    ----------
    text : object
        Argument ``text``.
    source_path : object
        Argument ``source_path``.


    Returns
    -------
    object
        Return value.
    """
    raw = yaml.safe_load(text)
    if not isinstance(raw, dict):
        msg = "policy root must be a mapping"
        raise PolicyError(msg)
    return _parse_document(cast(Mapping[str, Any], raw), source_path=source_path)


def load_output_policy(path: Path | str) -> OutputPolicyDocument:
    """
    Load one IWXXM output policy YAML file.


    Parameters
    ----------
    path : Path or str
        Path.

    Returns
    -------
    OutputPolicyDocument
        Load one IWXXM output policy YAML file.
    """
    file_path = Path(path)
    return _load_yaml_mapping(file_path.read_text(encoding="utf-8"), source_path=str(file_path))


def _layer_output_policy(
    parent: OutputPolicyDocument,
    child: OutputPolicyDocument,
) -> OutputPolicyDocument:
    """
    Internal helper ``_layer_output_policy``.

    Parameters
    ----------
    parent : object
        Argument ``parent``.
    child : object
        Argument ``child``.


    Returns
    -------
    object
        Return value.
    """
    if child.pin != parent.pin:
        msg = f"{child.id} pin must match {parent.id}"
        raise PolicyError(msg)
    select = child.select if child.select else parent.select
    ignore = tuple(dict.fromkeys((*parent.ignore, *child.ignore)))
    return OutputPolicyDocument(
        schema_version=parent.schema_version,
        id=parent.id,
        lifecycle=parent.lifecycle,
        pin=parent.pin,
        extends=parent.extends,
        select=select,
        ignore=ignore,
        profiles=parent.profiles,
        source_path=parent.source_path,
    )


def _take_output_overlay(
    doc: OutputPolicyDocument,
    catalog: Mapping[str, OutputPolicyDocument],
    *,
    profile: str | None,
) -> OutputPolicyDocument | None:
    """
    Internal helper ``_take_output_overlay``.

    Parameters
    ----------
    doc : object
        Argument ``doc``.
    catalog : object
        Argument ``catalog``.
    profile : object
        Argument ``profile``.


    Returns
    -------
    object
        Return value.
    """
    if not doc.extends and doc.id not in catalog:
        if doc.profiles:
            msg = f"{doc.id} profiles require extends"
            raise PolicyError(msg)
        return doc
    if len(doc.extends) != 1:
        msg = f"{doc.id} must extend one builtin"
        raise PolicyError(msg)
    if not doc.profiles:
        msg = f"{doc.id} needs a profiles list"
        raise PolicyError(msg)
    parent_id = doc.extends[0]
    if parent_id not in catalog:
        msg = f"{doc.id} extends unknown builtin {parent_id}"
        raise PolicyError(msg)
    if profile is None or profile not in doc.profiles:
        return None
    return _layer_output_policy(catalog[parent_id], doc)


def load_output_policy_catalog(profile: str | None = None) -> dict[str, OutputPolicyDocument]:
    """
    Load builtin output policies plus optional ``IWXXM_VALIDATE_POLICY_DIR``.

    An overlay with ``extends`` layers onto that builtin for the profile ids in
    its header. Omitting ``profile`` leaves those layers off. A new policy id
    with no ``extends`` is added for every profile.


    Parameters
    ----------
    profile : str or None, optional
        Profile id. By default ``None``.

    Returns
    -------
    dict[str, OutputPolicyDocument]
        Load builtin output policies plus optional ``IWXXM_VALIDATE_POLICY_DIR``.
    """
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
                layered = _take_output_overlay(doc, catalog, profile=profile)
                if layered is None:
                    continue
                catalog[layered.id] = layered
    return catalog


def _merged_lists(
    doc: OutputPolicyDocument,
    policies: Mapping[str, OutputPolicyDocument],
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """
    Internal helper ``_merged_lists``.

    Parameters
    ----------
    doc : object
        Argument ``doc``.
    policies : object
        Argument ``policies``.


    Returns
    -------
    object
        Return value.
    """
    select: list[str] = []
    ignore: list[str] = []
    seen: set[str] = set()

    def walk(current: OutputPolicyDocument) -> None:
        """
        Fold ``current`` and its parents into ``select`` and ``ignore``.

        A non-empty ``select`` replaces the list gathered so far. ``ignore``
        entries are appended.

        Parameters
        ----------
        current : OutputPolicyDocument
            Policy document to fold in.

        Raises
        ------
        PolicyError
            When ``extends`` cycles or names an unknown parent.
        """
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
    doc : OutputPolicyDocument
        Policy to resolve.
    policies : Mapping[str, OutputPolicyDocument] or None, optional
        Catalog used for ``extends``. Defaults to the loaded catalog.
    inventory : frozenset[str] or None, optional
        Assert ids for ``doc.pin``. Defaults to the vendor pin inventory.
    activate : bool or None, optional
        When true (or lifecycle is activated), unknown ids fail closed. By default ``None``.


    Returns
    -------
    ResolvedOutputPolicy
        Resolve select/ignore against the pin assert inventory.
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


def apply_output_policy_to_report(
    report: ValidationReport,
    policy_id: str,
    *,
    profile: str | None = None,
) -> ValidationReport:
    """
    Drop disabled Schematron assert ids (compat re-export).

    Parameters
    ----------
    report : ValidationReport
        Report.
    policy_id : str
        Policy ID.
    profile : str or None, optional
        Profile id. By default ``None``.


    Returns
    -------
    ValidationReport
        Filtered report.
    """
    from iwxxm_validate.policy_apply import apply_output_policy_to_report as apply_fn

    return apply_fn(report, policy_id, profile=profile)


__all__ = [
    "ENV_POLICY_DIR",
    "NON_SELECTABLE",
    "OutputPolicyDocument",
    "PolicyActivationError",
    "PolicyError",
    "PolicyLifecycle",
    "ResolvedOutputPolicy",
    "apply_output_policy_to_report",
    "load_output_policy",
    "load_output_policy_catalog",
    "resolve_output_policy",
]
