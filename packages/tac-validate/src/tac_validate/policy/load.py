"""TAC quality policy load + resolve (ADR-046 / #1216).

Draft lifecycle warns on unknown registry codes; activate fails closed.
"""

# ruff: noqa: F403, F405
# pyright: reportWildcardImportFromLibrary=false, reportConstantRedefinition=false, reportUnknownVariableType=false, reportUnknownParameterType=false, reportUnknownArgumentType=false, reportInvalidTypeForm=false, reportUnusedImport=false, reportPrivateUsage=false, reportGeneralTypeIssues=false
from __future__ import annotations

import os
from collections.abc import Mapping
from importlib import resources
from pathlib import Path
from typing import Any, cast

import yaml

from tac_validate.issue_registry import ISSUES, by_code, catalog_entries
from tac_validate.policy.models import *


def _as_str_list(value: object) -> tuple[str, ...]:
    """
    Internal helper ``_as_str_list``.

    Parameters
    ----------
    value : object
        Argument ``value``.

    Returns
    -------
    object
        Return value.
    """
    if value is None:
        return ()
    if not isinstance(value, list):
        msg = "expected a list of strings"
        raise PolicyError(msg)
    out: list[str] = []
    for item in cast(list[object], value):
        if not isinstance(item, str) or not item.strip():
            msg = "list entries must be non-empty strings"
            raise PolicyError(msg)
        out.append(item.strip())
    return tuple(out)


def _as_severity_map(value: object) -> dict[str, str]:
    """
    Internal helper ``_as_severity_map``.

    Parameters
    ----------
    value : object
        Argument ``value``.

    Returns
    -------
    object
        Return value.
    """
    if value is None:
        return {}
    if not isinstance(value, dict):
        msg = "severity must be a mapping"
        raise PolicyError(msg)
    out: dict[str, str] = {}
    for key, raw in cast(dict[object, object], value).items():
        if not isinstance(key, str) or not key.strip():
            msg = "severity keys must be non-empty strings"
            raise PolicyError(msg)
        if not isinstance(raw, str) or raw.strip() not in _SEVERITIES:
            msg = f"severity[{key!r}] must be one of {sorted(_SEVERITIES)}"
            raise PolicyError(msg)
        out[key.strip()] = raw.strip()
    return out


def _parse_document(data: Mapping[str, Any], *, source_path: str | None) -> PolicyDocument:
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
    product_raw = data.get("product")
    product: str | None
    if product_raw is None or product_raw == "":
        product = None
    elif isinstance(product_raw, str):
        product = product_raw.strip().lower()
    else:
        msg = "product must be a string when set"
        raise PolicyError(msg)
    return PolicyDocument(
        schema_version=schema_raw,
        id=pid.strip(),
        lifecycle=lifecycle,
        product=product,
        extends=_as_str_list(data.get("extends")),
        select=_as_str_list(data.get("select")),
        ignore=_as_str_list(data.get("ignore")),
        profiles=_as_str_list(data.get("profiles")),
        severity=_as_severity_map(data.get("severity")),
        preview=_as_str_list(data.get("preview")),
        detectors=_as_str_list(data.get("detectors")),
        source_path=source_path,
    )


def _load_yaml_mapping(text: str, *, source_path: str | None) -> PolicyDocument:
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


def load_policy(path: Path | str) -> PolicyDocument:
    """
    Load one TAC quality policy YAML file.

    Parameters
    ----------
    path : Path or str
        Filesystem path to a policy document.

    Returns
    -------
    PolicyDocument
        Parsed policy (not yet resolved / activated).

    """
    file_path = Path(path)
    return _load_yaml_mapping(
        file_path.read_text(encoding="utf-8"),
        source_path=str(file_path),
    )


def load_policy_catalog(profile: str | None = None) -> dict[str, PolicyDocument]:
    """
    Load builtin policies plus optional ``TAC_VALIDATE_POLICY_DIR`` overlays.

    An overlay with ``extends`` layers onto that builtin for the profile ids in
    its header. Omitting ``profile`` leaves those layers off. A new policy id
    with no ``extends`` is added for every profile.


    Parameters
    ----------
    profile : str or None, optional
        Profile id. By default ``None``.

    Returns
    -------
    dict[str, PolicyDocument]
        Load builtin policies plus optional ``TAC_VALIDATE_POLICY_DIR`` overlays.
    """
    catalog: dict[str, PolicyDocument] = {}
    policies_root = resources.files("tac_validate").joinpath("data", "policies")
    for entry in policies_root.iterdir():
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
                doc = load_policy(path)
                layered = _take_policy_overlay(doc, catalog, profile=profile)
                if layered is None:
                    continue
                catalog[layered.id] = layered
    return catalog


def _layer_policy(parent: PolicyDocument, child: PolicyDocument) -> PolicyDocument:
    """
    Internal helper ``_layer_policy``.

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
    select = child.select if child.select else parent.select
    ignore = tuple(dict.fromkeys((*parent.ignore, *child.ignore)))
    severity = dict(parent.severity)
    severity.update(dict(child.severity))
    preview = tuple(dict.fromkeys((*parent.preview, *child.preview)))
    detectors = child.detectors if child.detectors else parent.detectors
    return PolicyDocument(
        schema_version=parent.schema_version,
        id=parent.id,
        lifecycle=parent.lifecycle,
        product=child.product if child.product is not None else parent.product,
        extends=parent.extends,
        select=select,
        ignore=ignore,
        profiles=parent.profiles,
        severity=severity,
        preview=preview,
        detectors=detectors,
        source_path=parent.source_path,
    )


def _take_policy_overlay(
    doc: PolicyDocument,
    catalog: Mapping[str, PolicyDocument],
    *,
    profile: str | None,
) -> PolicyDocument | None:
    """
    Internal helper ``_take_policy_overlay``.

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
    return _layer_policy(catalog[parent_id], doc)


def _default_codes_for_product(product: str | None) -> frozenset[str]:
    """
    Internal helper ``_default_codes_for_product``.

    Parameters
    ----------
    product : object
        Argument ``product``.

    Returns
    -------
    object
        Return value.
    """
    if product is None:
        return frozenset(spec.code for spec in ISSUES)
    return frozenset(spec.code for spec in catalog_entries(product=product))


def _unknown(code: str) -> bool:
    """
    Internal helper ``_unknown``.

    Parameters
    ----------
    code : object
        Argument ``code``.

    Returns
    -------
    object
        Return value.
    """
    try:
        by_code(code)
    except KeyError:
        return True
    return False


def _chain_docs(
    doc: PolicyDocument,
    policies: Mapping[str, PolicyDocument],
) -> tuple[PolicyDocument, ...]:
    """
    Internal helper ``_chain_docs``.

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

    def depth_of(current: PolicyDocument, seen: frozenset[str]) -> int:
        """
        Return the ``extends`` depth of ``current``.

        Parameters
        ----------
        current : PolicyDocument
            Policy document to measure.
        seen : frozenset[str]
            Ancestor policy ids already visited.

        Returns
        -------
        int
            ``0`` when ``current`` has no parents, otherwise one more than the deepest parent.

        Raises
        ------
        PolicyCycleError
            When ``current.id`` is already in ``seen``.
        PolicyError
            When a parent id is missing from ``policies``.

        """
        if current.id in seen:
            msg = f"extends cycle involving {current.id!r}"
            raise PolicyCycleError(msg)
        if not current.extends:
            return 0
        depths: list[int] = []
        for parent_id in current.extends:
            parent = policies.get(parent_id)
            if parent is None:
                msg = f"unknown extends parent {parent_id!r}"
                raise PolicyError(msg)
            depths.append(depth_of(parent, seen | {current.id}))
        return 1 + max(depths)

    if depth_of(doc, frozenset()) > MAX_EXTENDS_DEPTH:
        msg = f"extends depth exceeds {MAX_EXTENDS_DEPTH}"
        raise PolicyDepthError(msg)

    def walk(current: PolicyDocument, stack: tuple[str, ...]) -> list[PolicyDocument]:
        # Cycles already rejected by depth_of; stack is for ordered ancestry only.
        """
        Return ancestors of ``current``, then ``current``.

        Parameters
        ----------
        current : PolicyDocument
            Policy document to expand.
        stack : tuple[str, ...]
            Ancestor ids already on this path.

        Returns
        -------
        list[PolicyDocument]
            Parents in extend order, with ``current`` last.

        """
        out: list[PolicyDocument] = []
        for parent_id in current.extends:
            parent = policies[parent_id]
            out.extend(walk(parent, (*stack, current.id)))
        out.append(current)
        return out

    return tuple(walk(doc, ()))


def _validate_code_refs(
    codes: set[str],
    *,
    lifecycle: PolicyLifecycle,
    activate: bool,
) -> tuple[str, ...]:
    """
    Internal helper ``_validate_code_refs``.

    Parameters
    ----------
    codes : object
        Argument ``codes``.
    lifecycle : object
        Argument ``lifecycle``.
    activate : object
        Argument ``activate``.

    Returns
    -------
    object
        Return value.
    """
    unknown = sorted(code for code in codes if _unknown(code))
    warnings = [f"unknown registry code {code!r}" for code in unknown]
    if unknown and (activate or lifecycle == "activated"):
        msg = "; ".join(warnings)
        raise PolicyActivationError(msg)
    return tuple(warnings)


__all__ = [
    "_as_severity_map",
    "_as_str_list",
    "_chain_docs",
    "_default_codes_for_product",
    "_layer_policy",
    "_load_yaml_mapping",
    "_parse_document",
    "_take_policy_overlay",
    "_unknown",
    "_validate_code_refs",
    "load_policy",
    "load_policy_catalog",
]
