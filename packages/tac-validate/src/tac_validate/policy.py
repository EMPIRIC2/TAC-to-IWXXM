"""TAC quality policy load + resolve (ADR-046 / #1216).

Draft lifecycle warns on unknown registry codes; activate fails closed.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Any, Literal, cast

import yaml

from tac_validate.issue_registry import ISSUES, by_code, catalog_entries

PolicyLifecycle = Literal["draft", "activated"]

MAX_EXTENDS_DEPTH = 5
ENV_POLICY_DIR = "TAC_VALIDATE_POLICY_DIR"

_SEVERITIES = frozenset({"error", "warning", "info"})


class PolicyError(ValueError):
    """Base error for TAC quality policy documents."""


class PolicyActivationError(PolicyError):
    """Activated policy references unknown codes or invalid severity remaps."""


class PolicyCycleError(PolicyError):
    """``extends`` graph contains a cycle."""


class PolicyDepthError(PolicyError):
    """``extends`` chain exceeds ``MAX_EXTENDS_DEPTH``."""


@dataclass(frozen=True, slots=True)
class PolicyDocument:
    """One TAC quality policy YAML document."""

    schema_version: int
    id: str
    lifecycle: PolicyLifecycle
    product: str | None
    extends: tuple[str, ...]
    select: tuple[str, ...]
    ignore: tuple[str, ...]
    severity: Mapping[str, str]
    preview: tuple[str, ...]
    detectors: tuple[str, ...]
    source_path: str | None = None


@dataclass(frozen=True, slots=True)
class ResolvedPolicy:
    """Merged policy ready for lint runtime consumption."""

    id: str
    lifecycle: PolicyLifecycle
    product: str | None
    enabled_codes: frozenset[str]
    severity_overrides: Mapping[str, str]
    preview_codes: frozenset[str]
    detector_ids: tuple[str, ...]
    warnings: tuple[str, ...]
    can_activate: bool
    chain: tuple[str, ...]


def _as_str_list(value: object) -> tuple[str, ...]:
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
        severity=_as_severity_map(data.get("severity")),
        preview=_as_str_list(data.get("preview")),
        detectors=_as_str_list(data.get("detectors")),
        source_path=source_path,
    )


def _load_yaml_mapping(text: str, *, source_path: str | None) -> PolicyDocument:
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
    path :
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


def load_policy_catalog() -> dict[str, PolicyDocument]:
    """
    Load builtin policies plus optional ``TAC_VALIDATE_POLICY_DIR`` overlays.

    Later paths with the same ``id`` replace earlier ones (overlay wins).
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
                catalog[doc.id] = doc
    return catalog


def _default_codes_for_product(product: str | None) -> frozenset[str]:
    if product is None:
        return frozenset(spec.code for spec in ISSUES)
    return frozenset(spec.code for spec in catalog_entries(product=product))


def _unknown(code: str) -> bool:
    try:
        by_code(code)
    except KeyError:
        return True
    return False


def _chain_docs(
    doc: PolicyDocument,
    policies: Mapping[str, PolicyDocument],
) -> tuple[PolicyDocument, ...]:
    """Return base→child order with cycle and depth checks."""

    def depth_of(current: PolicyDocument, seen: frozenset[str]) -> int:
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
    unknown = sorted(code for code in codes if _unknown(code))
    warnings = [f"unknown registry code {code!r}" for code in unknown]
    if unknown and (activate or lifecycle == "activated"):
        msg = "; ".join(warnings)
        raise PolicyActivationError(msg)
    return tuple(warnings)


def resolve_policy(
    doc: PolicyDocument,
    *,
    policies: Mapping[str, PolicyDocument],
    activate: bool = False,
) -> ResolvedPolicy:
    """
    Merge ``extends`` and compute enabled codes.

    Parameters
    ----------
    doc :
        Leaf policy document.
    policies :
        Catalog keyed by policy id (must include ``doc`` and parents).
    activate :
        When True, treat as activation even if ``lifecycle`` is draft (fail closed).

    Returns
    -------
    ResolvedPolicy
        Merged view with warnings / activation status.
    """
    chain = _chain_docs(doc, policies)
    select: list[str] = []
    ignore: set[str] = set()
    severity: dict[str, str] = {}
    preview: set[str] = set()
    detectors: list[str] = []
    product = doc.product
    for item in chain:
        if item.product is not None:
            product = item.product
        if item.select:
            select = list(item.select)
        ignore |= set(item.ignore)
        severity.update(dict(item.severity))
        preview |= set(item.preview)
        if item.detectors:
            detectors = list(item.detectors)

    referenced = set(select) | ignore | set(severity) | preview
    warnings = list(
        _validate_code_refs(
            referenced,
            lifecycle=doc.lifecycle,
            activate=activate,
        )
    )

    defaults = _default_codes_for_product(product)
    enabled = set(select) if select else set(defaults) - preview
    enabled -= ignore
    enabled = {code for code in enabled if not _unknown(code)}

    can_activate = not any("unknown registry code" in w for w in warnings)

    return ResolvedPolicy(
        id=doc.id,
        lifecycle=doc.lifecycle,
        product=product,
        enabled_codes=frozenset(enabled),
        severity_overrides=dict(severity),
        preview_codes=frozenset(preview),
        detector_ids=tuple(detectors),
        warnings=tuple(warnings),
        can_activate=can_activate,
        chain=tuple(item.id for item in chain),
    )


__all__ = [
    "ENV_POLICY_DIR",
    "MAX_EXTENDS_DEPTH",
    "PolicyActivationError",
    "PolicyCycleError",
    "PolicyDepthError",
    "PolicyDocument",
    "PolicyError",
    "ResolvedPolicy",
    "load_policy",
    "load_policy_catalog",
    "resolve_policy",
]
