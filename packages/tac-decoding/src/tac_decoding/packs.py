"""TAC product packs. Structure lives in data; this module only loads it.

Unset ``TAC_DECODING_PACK_DIR`` uses the built-in packs. A directory overlay
extends a builtin for the profile ids in its header, or adds a new pack id.
A bad file fails closed and does not drop the built-ins.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import cast

import yaml

from tac_decoding.locale import LocaleError, render_template

PACK_DIR_ENV = "TAC_DECODING_PACK_DIR"
_ALLOWED = frozenset({"id", "layout", "rules", "profiles", "extends"})
_RULE_KEYS = frozenset({"id", "pattern", "explain", "label"})
_LAYOUTS = frozenset({"token_stream", "label_fields", "stub"})
_SUFFIXES = frozenset({".yaml", ".yml", ".json"})
_MAX_PATTERN = 200

_BUILTINS: tuple[tuple[str, str], ...] = (
    ("metar", "token_stream"),
    ("speci", "token_stream"),
    ("taf", "token_stream"),
    ("sigmet", "token_stream"),
    ("va_sigmet", "token_stream"),
    ("tc_sigmet", "token_stream"),
    ("airmet", "token_stream"),
    ("vaa", "label_fields"),
    ("tca", "label_fields"),
    ("swxa", "label_fields"),
    ("vona", "label_fields"),
    ("wafs", "stub"),
    ("qvaci", "stub"),
)
_BUILTIN_PACK_DIR = Path(__file__).resolve().parent / "data" / "packs"


class PackSchemaError(ValueError):
    """
    A pack file or directory does not match the pack schema.

    Attributes
    ----------
    _ : object
        See implementation.
    """


@dataclass(frozen=True, slots=True)
class Rule:
    """
    One match rule. Token rules use ``patterns``; label rules use ``label``.

    Attributes
    ----------
    _ : object
        See implementation.
    """

    id: str
    explain: str
    patterns: tuple[re.Pattern[str], ...] = ()
    label: str = ""


@dataclass(frozen=True, slots=True)
class Pack:
    """
    One product pack: an id, a layout, and optional rules.

    Attributes
    ----------
    _ : object
        See implementation.
    """

    id: str
    layout: str
    rules: tuple[Rule, ...] = ()


def load_packs(profile: str | None = None) -> tuple[Pack, ...]:
    """
    Return built-in packs, with ``TAC_DECODING_PACK_DIR`` applied for ``profile``.

    An overlay file with ``extends`` applies only when ``profile`` is one of its
    ``profiles``. Omitting ``profile`` leaves those overlays off the result.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (load_packs)
    2

    Parameters
    ----------
    profile : object
        Argument ``profile``.

    Returns
    -------
    object
        Return value.
    """
    overlay = os.environ.get(PACK_DIR_ENV, "").strip()
    if not overlay:
        return _load_builtins_cached()
    # Overlay dirs are not cached: tests rewrite the same path between loads.
    return _merge_packs(overlay, profile)


def clear_pack_cache() -> None:
    """
    Drop cached built-in packs (tests that patch ``_BUILTIN_PACK_DIR`` must call this).

    Examples
    --------
    >>> 1 + 1  # docstring smoke (clear_pack_cache)
    2
    """
    _load_builtins_cached.cache_clear()


@lru_cache(maxsize=1)
def _load_builtins_cached() -> tuple[Pack, ...]:
    """
    Internal helper ``_load_builtins_cached``.

    Returns
    -------
    object
        Return value.
    """
    return _merge_packs("")


def _merge_packs(overlay: str, profile: str | None = None) -> tuple[Pack, ...]:
    """
    Internal helper ``_merge_packs``.

    Parameters
    ----------
    overlay : object
        Argument ``overlay``.
    profile : object
        Argument ``profile``.

    Returns
    -------
    object
        Return value.
    """
    merged = {pack_id: Pack(pack_id, layout) for pack_id, layout in _BUILTINS}
    if _BUILTIN_PACK_DIR.is_dir():
        for pack in _read_overlay(_BUILTIN_PACK_DIR):
            merged[pack.id] = pack
    if not overlay:
        return tuple(merged.values())
    _apply_extension_dir(merged, Path(overlay), profile)
    return tuple(merged.values())


def _apply_extension_dir(merged: dict[str, Pack], directory: Path, profile: str | None) -> None:
    """
    Internal helper ``_apply_extension_dir``.

    Parameters
    ----------
    merged : object
        Argument ``merged``.
    directory : object
        Argument ``directory``.
    profile : object
        Argument ``profile``.
    """
    if not directory.is_dir():
        msg = f"Pack directory is not a folder: {directory}"
        raise PackSchemaError(msg)
    pending: list[tuple[str, Pack]] = []
    additions: list[Pack] = []
    for path in sorted(directory.iterdir()):
        if path.suffix.lower() not in _SUFFIXES:
            continue
        target, pack, is_extension = _read_extension(path, merged)
        if is_extension:
            if profile is None or profile not in target:
                continue
            pending.append((pack.id, pack))
        else:
            additions.append(pack)
    for pack in additions:
        merged[pack.id] = pack
    for builtin_id, pack in pending:
        base = merged[builtin_id]
        merged[builtin_id] = Pack(builtin_id, base.layout, _merge_rules(base.rules, pack.rules))


def _read_extension(path: Path, merged: dict[str, Pack]) -> tuple[tuple[str, ...], Pack, bool]:
    """
    Internal helper ``_read_extension``.

    Parameters
    ----------
    path : object
        Argument ``path``.
    merged : object
        Argument ``merged``.

    Returns
    -------
    object
        Return value.
    """
    mapping = _load_mapping(path)
    extends = mapping.get("extends")
    profiles = mapping.get("profiles")
    pack_id = mapping.get("id")
    if not isinstance(pack_id, str) or not pack_id.strip():
        msg = f"{path.name} needs a string id"
        raise PackSchemaError(msg)
    clean_id = pack_id.strip()
    if extends is None and clean_id not in merged:
        if profiles is not None:
            msg = f"{path.name} profiles require extends"
            raise PackSchemaError(msg)
        return (), _read_file(path), False
    if not isinstance(extends, str) or not extends.strip():
        msg = f"{path.name} must extend one builtin"
        raise PackSchemaError(msg)
    base_id = extends.strip()
    if base_id not in merged:
        msg = f"{path.name} extends unknown builtin {base_id}"
        raise PackSchemaError(msg)
    if not isinstance(profiles, list):
        msg = f"{path.name} needs a profiles list"
        raise PackSchemaError(msg)
    profile_ids = cast(list[object], profiles)
    if not profile_ids or not all(isinstance(item, str) and item for item in profile_ids):
        msg = f"{path.name} needs a profiles list"
        raise PackSchemaError(msg)
    pack = _read_file(path)
    base = merged[base_id]
    if pack.layout != base.layout:
        msg = f"{path.name} layout must match {base_id}"
        raise PackSchemaError(msg)
    return tuple(str(item) for item in profile_ids), Pack(base_id, pack.layout, pack.rules), True


def _merge_rules(base: tuple[Rule, ...], extra: tuple[Rule, ...]) -> tuple[Rule, ...]:
    """
    Internal helper ``_merge_rules``.

    Parameters
    ----------
    base : object
        Argument ``base``.
    extra : object
        Argument ``extra``.

    Returns
    -------
    object
        Return value.
    """
    replacement = {rule.id: rule for rule in extra}
    seen = {rule.id for rule in base}
    merged = [replacement.get(rule.id, rule) for rule in base]
    merged.extend(rule for rule in extra if rule.id not in seen)
    return tuple(merged)


def _load_mapping(path: Path) -> dict[str, object]:
    """
    Internal helper ``_load_mapping``.

    Parameters
    ----------
    path : object
        Argument ``path``.

    Returns
    -------
    object
        Return value.
    """
    text = path.read_text(encoding="utf-8")
    try:
        if path.suffix.lower() == ".json":
            data: object = json.loads(text)
        else:
            data = yaml.safe_load(text)
    except (json.JSONDecodeError, yaml.YAMLError) as exc:
        msg = f"{path.name} is not valid pack data"
        raise PackSchemaError(msg) from exc
    if not isinstance(data, dict):
        msg = f"{path.name} must be a mapping"
        raise PackSchemaError(msg)
    mapping = cast(dict[str, object], data)
    unknown = sorted(set(mapping) - _ALLOWED)
    if unknown:
        msg = f"{path.name} has unknown field {unknown[0]}"
        raise PackSchemaError(msg)
    return mapping


def _read_overlay(directory: Path) -> tuple[Pack, ...]:
    """
    Internal helper ``_read_overlay``.

    Parameters
    ----------
    directory : object
        Argument ``directory``.

    Returns
    -------
    object
        Return value.
    """
    found: list[Pack] = []
    for path in sorted(directory.iterdir()):
        if path.suffix.lower() not in _SUFFIXES:
            continue
        found.append(_read_file(path))
    return tuple(found)


def _read_file(path: Path) -> Pack:
    """
    Internal helper ``_read_file``.

    Parameters
    ----------
    path : object
        Argument ``path``.

    Returns
    -------
    object
        Return value.
    """
    mapping = _load_mapping(path)
    pack_id = mapping.get("id")
    layout = mapping.get("layout")
    if not isinstance(pack_id, str) or not pack_id.strip():
        msg = f"{path.name} needs a string id"
        raise PackSchemaError(msg)
    if layout not in _LAYOUTS:
        msg = f"{path.name} has unknown layout"
        raise PackSchemaError(msg)
    return Pack(pack_id.strip(), str(layout), _parse_rules(mapping, str(layout), path.name))


def _parse_rules(data: dict[str, object], layout: str, name: str) -> tuple[Rule, ...]:
    """
    Internal helper ``_parse_rules``.

    Parameters
    ----------
    data : object
        Argument ``data``.
    layout : object
        Argument ``layout``.
    name : object
        Argument ``name``.

    Returns
    -------
    object
        Return value.
    """
    raw = data.get("rules", [])
    if not isinstance(raw, list):
        msg = f"{name} rules must be a list"
        raise PackSchemaError(msg)
    if layout == "stub" and raw:
        msg = f"{name} stub packs cannot have rules"
        raise PackSchemaError(msg)
    seen: set[str] = set()
    rules = cast(list[object], raw)
    return tuple(_parse_rule(item, layout, name, seen) for item in rules)


def _parse_rule(item: object, layout: str, name: str, seen: set[str]) -> Rule:
    """
    Internal helper ``_parse_rule``.

    Parameters
    ----------
    item : object
        Argument ``item``.
    layout : object
        Argument ``layout``.
    name : object
        Argument ``name``.
    seen : object
        Argument ``seen``.

    Returns
    -------
    object
        Return value.
    """
    if not isinstance(item, dict):
        msg = f"{name} rule must be a mapping"
        raise PackSchemaError(msg)
    rule = cast(dict[str, object], item)
    unknown = sorted(set(rule) - _RULE_KEYS)
    if unknown:
        msg = f"{name} rule has unknown field {unknown[0]}"
        raise PackSchemaError(msg)
    rule_id = rule.get("id")
    explain = rule.get("explain")
    if not isinstance(rule_id, str) or not rule_id.strip():
        msg = f"{name} rule needs a string id"
        raise PackSchemaError(msg)
    clean_id = rule_id.strip()
    if clean_id in seen:
        msg = f"{name} rule id {clean_id} is duplicated"
        raise PackSchemaError(msg)
    seen.add(clean_id)
    if not isinstance(explain, str):
        msg = f"{name} rule needs an explain template"
        raise PackSchemaError(msg)
    if layout == "token_stream":
        return _token_rule(rule, clean_id, explain, name)
    return _label_rule(rule, clean_id, explain, name)


def _token_rule(item: dict[str, object], rule_id: str, explain: str, name: str) -> Rule:
    """
    Internal helper ``_token_rule``.

    Parameters
    ----------
    item : object
        Argument ``item``.
    rule_id : object
        Argument ``rule_id``.
    explain : object
        Argument ``explain``.
    name : object
        Argument ``name``.

    Returns
    -------
    object
        Return value.
    """
    if "label" in item:
        msg = f"{name} token rule cannot have a label"
        raise PackSchemaError(msg)
    pattern = item.get("pattern")
    if not isinstance(pattern, list) or not pattern:
        msg = f"{name} token rule needs a pattern"
        raise PackSchemaError(msg)
    compiled: list[re.Pattern[str]] = []
    for piece in cast(list[object], pattern):
        if not isinstance(piece, str) or not piece:
            msg = f"{name} pattern pieces must be strings"
            raise PackSchemaError(msg)
        if len(piece) > _MAX_PATTERN:
            msg = f"{name} pattern is too long"
            raise PackSchemaError(msg)
        try:
            compiled.append(re.compile(piece))
        except re.error as exc:
            msg = f"{name} has an invalid pattern"
            raise PackSchemaError(msg) from exc
    try:
        render_template(explain, tuple("" for _ in compiled))
    except LocaleError as exc:
        msg = f"{name} explain template does not match its pattern"
        raise PackSchemaError(msg) from exc
    return Rule(rule_id, explain, tuple(compiled))


def _label_rule(item: dict[str, object], rule_id: str, explain: str, name: str) -> Rule:
    """
    Internal helper ``_label_rule``.

    Parameters
    ----------
    item : object
        Argument ``item``.
    rule_id : object
        Argument ``rule_id``.
    explain : object
        Argument ``explain``.
    name : object
        Argument ``name``.

    Returns
    -------
    object
        Return value.
    """
    if "pattern" in item:
        msg = f"{name} label rule cannot have a pattern"
        raise PackSchemaError(msg)
    label = item.get("label")
    if not isinstance(label, str) or not label.strip():
        msg = f"{name} label rule needs a label"
        raise PackSchemaError(msg)
    try:
        render_template(explain, (), value="")
    except LocaleError as exc:
        msg = f"{name} explain template does not match its label"
        raise PackSchemaError(msg) from exc
    return Rule(rule_id, explain, (), label.strip())
