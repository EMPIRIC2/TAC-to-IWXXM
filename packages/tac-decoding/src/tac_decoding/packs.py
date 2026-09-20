"""TAC product packs. Structure lives in data; this module only loads it.

Unset ``TAC_DECODING_PACK_DIR`` uses the built-in packs. A directory overlay
adds or replaces packs. Unknown fields fail closed so a bad file cannot
silently drop the built-ins.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import cast

import yaml

from tac_decoding.locale import LocaleError, render_template

PACK_DIR_ENV = "TAC_DECODING_PACK_DIR"
_ALLOWED = frozenset({"id", "layout", "rules"})
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
    """A pack file or directory does not match the pack schema."""


@dataclass(frozen=True, slots=True)
class Rule:
    """One match rule. Token rules use ``patterns``; label rules use ``label``."""

    id: str
    explain: str
    patterns: tuple[re.Pattern[str], ...] = ()
    label: str = ""


@dataclass(frozen=True, slots=True)
class Pack:
    """One product pack: an id, a layout, and optional rules."""

    id: str
    layout: str
    rules: tuple[Rule, ...] = ()


def load_packs() -> tuple[Pack, ...]:
    """Return built-in packs, with ``TAC_DECODING_PACK_DIR`` applied on top."""
    merged = {pack_id: Pack(pack_id, layout) for pack_id, layout in _BUILTINS}
    if _BUILTIN_PACK_DIR.is_dir():
        for pack in _read_overlay(_BUILTIN_PACK_DIR):
            merged[pack.id] = pack
    raw = os.environ.get(PACK_DIR_ENV, "").strip()
    if not raw:
        return tuple(merged.values())
    for pack in _read_overlay(Path(raw)):
        merged[pack.id] = pack
    return tuple(merged.values())


def _read_overlay(directory: Path) -> tuple[Pack, ...]:
    if not directory.is_dir():
        msg = f"Pack directory is not a folder: {directory}"
        raise PackSchemaError(msg)
    found: list[Pack] = []
    for path in sorted(directory.iterdir()):
        if path.suffix.lower() not in _SUFFIXES:
            continue
        found.append(_read_file(path))
    return tuple(found)


def _read_file(path: Path) -> Pack:
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
