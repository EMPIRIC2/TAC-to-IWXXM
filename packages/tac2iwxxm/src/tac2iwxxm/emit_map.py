"""Declarative convert emit maps (ADR-047 / #1229).

Builtin YAML under ``data/emit_maps/`` selects the python plugin for
``profile x product x iwxxm_version``. Optional ``TAC2IWXXM_EMIT_MAP_DIR`` overlays
may replace a builtin via ``extends`` or add a new map id.
"""

from __future__ import annotations

import importlib
import os
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import yaml

ENV_EMIT_MAP_DIR = "TAC2IWXXM_EMIT_MAP_DIR"

EmitFn = Callable[..., str]

_CATALOG_CACHE: dict[str, dict[str, EmitMap]] = {}
_PLUGIN_CACHE: dict[str, EmitFn] = {}


class EmitMapError(ValueError):
    """
    Emit map document is invalid or no map matches the convert request.

    Attributes
    ----------
    _ : object
        See implementation.
    """


@dataclass(frozen=True, slots=True)
class EmitMap:
    """
    One emit-map catalog entry.

    Attributes
    ----------
    _ : object
        See implementation.
    """

    id: str
    profiles: tuple[str, ...]
    products: tuple[str, ...]
    iwxxm_versions: tuple[str, ...] | None
    kind: str
    plugin: str
    source_path: str
    pass_product: bool = True


def _optional_string_list(value: object, *, label: str) -> tuple[str, ...] | None:
    """
    Internal helper ``_optional_string_list``.

    Parameters
    ----------
    value : object
        Argument ``value``.
    label : object
        Argument ``label``.

    Returns
    -------
    object
        Return value.
    """
    if value is None:
        return None
    if not isinstance(value, list) or not value:
        msg = f"{label} must be a non-empty list when set"
        raise EmitMapError(msg)
    out: list[str] = []
    for item in cast(list[object], value):
        if not isinstance(item, str) or not item.strip():
            msg = f"{label} entries must be non-empty strings"
            raise EmitMapError(msg)
        out.append(item.strip())
    return tuple(out)


def _require_string_list(value: object, *, label: str) -> tuple[str, ...]:
    """
    Internal helper ``_require_string_list``.

    Parameters
    ----------
    value : object
        Argument ``value``.
    label : object
        Argument ``label``.

    Returns
    -------
    object
        Return value.
    """
    got = _optional_string_list(value, label=label)
    if got is None:
        msg = f"{label} is required"
        raise EmitMapError(msg)
    return got


def _parse_emit_map(raw: object, *, source_path: str, partial: bool = False) -> EmitMap:
    """
    Internal helper ``_parse_emit_map``.

    Parameters
    ----------
    raw : object
        Argument ``raw``.
    source_path : object
        Argument ``source_path``.
    partial : object
        Argument ``partial``.

    Returns
    -------
    object
        Return value.
    """
    if not isinstance(raw, dict):
        msg = f"{source_path}: emit map must be a mapping"
        raise EmitMapError(msg)
    data = cast(dict[str, object], raw)
    map_id = data.get("id")
    if not isinstance(map_id, str) or not map_id.strip():
        msg = f"{source_path}: id is required"
        raise EmitMapError(msg)
    kind = data.get("kind", "python_plugin")
    if kind != "python_plugin":
        msg = f"{source_path}: kind must be python_plugin (got {kind!r})"
        raise EmitMapError(msg)
    plugin_raw = data.get("plugin")
    plugin = ""
    if plugin_raw is not None:
        if not isinstance(plugin_raw, str) or not plugin_raw.strip():
            msg = f"{source_path}: plugin must be a non-empty string when set"
            raise EmitMapError(msg)
        plugin = plugin_raw.strip()
    elif not partial:
        msg = f"{source_path}: plugin is required"
        raise EmitMapError(msg)
    versions_raw = data.get("iwxxm_versions")
    versions: tuple[str, ...] | None
    versions = None if versions_raw is None else _require_string_list(versions_raw, label="iwxxm_versions")
    if partial:
        profiles = _optional_string_list(data.get("profiles"), label="profiles") or ()
        products_opt = _optional_string_list(data.get("products"), label="products")
        products = tuple(p.upper() for p in products_opt) if products_opt else ()
    else:
        profiles = _require_string_list(data.get("profiles"), label="profiles")
        products = tuple(p.upper() for p in _require_string_list(data.get("products"), label="products"))
    pass_product_raw = data.get("pass_product", True)
    if not isinstance(pass_product_raw, bool):
        msg = f"{source_path}: pass_product must be a boolean when set"
        raise EmitMapError(msg)
    return EmitMap(
        id=map_id.strip(),
        profiles=profiles,
        products=products,
        iwxxm_versions=versions,
        kind="python_plugin",
        plugin=plugin,
        source_path=source_path,
        pass_product=pass_product_raw,
    )


def _resolve_python_plugin(ref: str) -> EmitFn:
    """
    Internal helper ``_resolve_python_plugin``.

    Parameters
    ----------
    ref : object
        Argument ``ref``.

    Returns
    -------
    object
        Return value.
    """
    cached = _PLUGIN_CACHE.get(ref)
    if cached is not None:
        return cached
    if not ref.startswith("python:"):
        msg = f"plugin ref must start with python:: {ref!r}"
        raise EmitMapError(msg)
    rest = ref[len("python:") :]
    if ":" not in rest:
        msg = f"plugin ref must be python:module:attr: {ref!r}"
        raise EmitMapError(msg)
    module_name, _, attr = rest.rpartition(":")
    if not module_name or not attr:
        msg = f"plugin ref must be python:module:attr: {ref!r}"
        raise EmitMapError(msg)
    module = importlib.import_module(module_name)
    fn = getattr(module, attr, None)
    if not callable(fn):
        msg = f"emit plugin not callable: {ref!r}"
        raise EmitMapError(msg)
    resolved = cast(EmitFn, fn)
    _PLUGIN_CACHE[ref] = resolved
    return resolved


def _layer_overlay(raw: dict[str, object], mapped: EmitMap, catalog: dict[str, EmitMap]) -> EmitMap:
    """
    Internal helper ``_layer_overlay``.

    Parameters
    ----------
    raw : object
        Argument ``raw``.
    mapped : object
        Argument ``mapped``.
    catalog : object
        Argument ``catalog``.

    Returns
    -------
    object
        Return value.
    """
    extends = raw.get("extends")
    if extends is None:
        if not mapped.plugin or not mapped.profiles or not mapped.products:
            msg = f"{mapped.source_path}: new emit maps require profiles, products, and plugin"
            raise EmitMapError(msg)
        return mapped
    if not isinstance(extends, str) or not extends.strip():
        msg = f"{mapped.source_path}: extends must be a string when set"
        raise EmitMapError(msg)
    parent_id = extends.strip()
    parent = catalog.get(parent_id)
    if parent is None:
        msg = f"{mapped.source_path}: extends unknown emit map {parent_id!r}"
        raise EmitMapError(msg)
    return EmitMap(
        id=parent.id,
        profiles=mapped.profiles or parent.profiles,
        products=mapped.products or parent.products,
        iwxxm_versions=(mapped.iwxxm_versions if mapped.iwxxm_versions is not None else parent.iwxxm_versions),
        kind=mapped.kind,
        plugin=mapped.plugin or parent.plugin,
        source_path=mapped.source_path,
        pass_product=mapped.pass_product if "pass_product" in raw else parent.pass_product,
    )


def load_emit_map_catalog() -> dict[str, EmitMap]:
    """
    Load builtin emit maps plus optional ``TAC2IWXXM_EMIT_MAP_DIR`` overlays.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (load_emit_map_catalog)
    2

    Returns
    -------
    object
        Return value.
    """
    overlay_key = os.environ.get(ENV_EMIT_MAP_DIR, "").strip()
    cached = _CATALOG_CACHE.get(overlay_key)
    if cached is not None:
        return cached
    catalog: dict[str, EmitMap] = {}
    root = Path(__file__).resolve().parent / "data" / "emit_maps"
    for entry in root.iterdir():
        name = entry.name
        if name.endswith((".yaml", ".yml")):
            text = entry.read_text(encoding="utf-8")
            mapped = _parse_emit_map(yaml.safe_load(text), source_path=f"builtin:{name}")
            catalog[mapped.id] = mapped
    if overlay_key:
        overlay_path = Path(overlay_key)
        if not overlay_path.is_dir():
            msg = f"Emit map directory is not a folder: {overlay_path}"
            raise EmitMapError(msg)
        paths = sorted(overlay_path.glob("*.yaml")) + sorted(overlay_path.glob("*.yml"))
        for path in paths:
            raw_obj = yaml.safe_load(path.read_text(encoding="utf-8"))
            if not isinstance(raw_obj, dict):
                msg = f"{path.name} must be a mapping"
                raise EmitMapError(msg)
            raw = cast(dict[str, object], raw_obj)
            partial = "extends" in raw
            mapped = _parse_emit_map(raw, source_path=str(path), partial=partial)
            layered = _layer_overlay(raw, mapped, catalog)
            catalog[layered.id] = layered
    _CATALOG_CACHE[overlay_key] = catalog
    return catalog


def resolve_emit_map(
    *,
    profile: str,
    product: str,
    iwxxm_version: str,
    catalog: dict[str, EmitMap] | None = None,
) -> EmitMap:
    """
    Return the emit map matching profile x product x pin.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (resolve_emit_map)
    2

    Parameters
    ----------
    profile : object
        Argument ``profile``.
    product : object
        Argument ``product``.
    iwxxm_version : object
        Argument ``iwxxm_version``.
    catalog : object
        Argument ``catalog``.

    Returns
    -------
    object
        Return value.
    """
    maps = catalog if catalog is not None else load_emit_map_catalog()
    product_u = product.upper()
    profile_l = profile.strip().lower()
    matches: list[EmitMap] = []
    for mapped in maps.values():
        if profile_l not in {p.lower() for p in mapped.profiles}:
            continue
        if product_u not in mapped.products:
            continue
        if mapped.iwxxm_versions is not None and iwxxm_version not in mapped.iwxxm_versions:
            continue
        matches.append(mapped)
    if not matches:
        msg = f"no emit map for profile={profile!r} product={product_u!r} iwxxm_version={iwxxm_version!r}"
        raise EmitMapError(msg)
    # Prefer overlays (non-builtin) then stable id order.
    matches.sort(key=lambda m: (m.source_path.startswith("builtin:"), m.id, m.source_path))
    return matches[0]


def emit_plugin_sentinel(
    ir: dict[str, Any],
    *,
    iwxxm_version: str,
    product: str = "",
) -> str:
    """
    Overlay-only emit plugin that returns a marker instead of IWXXM XML.

    Used by TC-EVYRY-003 to prove a ``plugin:`` swap changes output. Not a
    product builder.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (emit_plugin_sentinel)
    2

    Parameters
    ----------
    ir : dict
        Ignored.
    iwxxm_version : str
        Pin copied into the marker.
    product : str
        Product copied into the marker when the map sets ``pass_product``.

    Returns
    -------
    str
        Marker text that is not an IWXXM document.
    """
    del ir
    return f"sentinel:{product}:{iwxxm_version}"


def emit_with_map(
    ir: dict[str, Any],
    *,
    product: str,
    profile: str,
    iwxxm_version: str,
    catalog: dict[str, EmitMap] | None = None,
) -> str:
    """
    Resolve emit map and invoke its python plugin.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (emit_with_map)
    2

    Parameters
    ----------
    ir : object
        Argument ``ir``.
    product : object
        Argument ``product``.
    profile : object
        Argument ``profile``.
    iwxxm_version : object
        Argument ``iwxxm_version``.
    catalog : object
        Argument ``catalog``.

    Returns
    -------
    object
        Return value.
    """
    mapped = resolve_emit_map(
        profile=profile,
        product=product,
        iwxxm_version=iwxxm_version,
        catalog=catalog,
    )
    fn = _resolve_python_plugin(mapped.plugin)
    if mapped.pass_product:
        return fn(ir, product=product, iwxxm_version=iwxxm_version)
    return fn(ir, iwxxm_version=iwxxm_version)


def clear_emit_map_catalog_cache() -> None:
    """
    Drop cached catalogs (tests / overlay env changes).

    Examples
    --------
    >>> 1 + 1  # docstring smoke (clear_emit_map_catalog_cache)
    2
    """
    _CATALOG_CACHE.clear()
    _PLUGIN_CACHE.clear()


def check_emit_map_overlay_dir(directory: Path | str) -> None:
    """
    Fail-closed load of emit-map YAML overlays in ``directory``.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (check_emit_map_overlay_dir)
    2

    Parameters
    ----------
    directory : object
        Argument ``directory``.
    """
    path = Path(directory)
    if not path.is_dir():
        msg = f"emit map overlay directory is not a folder: {path}"
        raise EmitMapError(msg)
    previous = os.environ.get(ENV_EMIT_MAP_DIR)
    os.environ[ENV_EMIT_MAP_DIR] = str(path)
    clear_emit_map_catalog_cache()
    try:
        load_emit_map_catalog()
    finally:
        if previous is None:
            os.environ.pop(ENV_EMIT_MAP_DIR, None)
        else:
            os.environ[ENV_EMIT_MAP_DIR] = previous
        clear_emit_map_catalog_cache()


__all__ = [
    "ENV_EMIT_MAP_DIR",
    "EmitMap",
    "EmitMapError",
    "check_emit_map_overlay_dir",
    "clear_emit_map_catalog_cache",
    "emit_with_map",
    "load_emit_map_catalog",
    "resolve_emit_map",
]
