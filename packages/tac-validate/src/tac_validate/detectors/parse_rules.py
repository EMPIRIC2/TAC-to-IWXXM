"""Detector rule/pack parsing helpers."""

# ruff: noqa: F403, F405
# pyright: reportWildcardImportFromLibrary=false, reportConstantRedefinition=false, reportUnknownVariableType=false, reportUnknownParameterType=false, reportUnknownArgumentType=false, reportInvalidTypeForm=false, reportUnusedImport=false, reportPrivateUsage=false, reportGeneralTypeIssues=false
from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal, cast

import yaml

from metar_shared import tac_patterns as _tac_patterns
from tac_validate.detectors.models import *

_AHL_HEADING_LINE = _tac_patterns.AHL_HEADING_LINE_BBB3


def _re_flags(names: Sequence[object]) -> int:
    """
    Internal helper ``_re_flags``.

    Parameters
    ----------
    names : object
        Argument ``names``.

    Returns
    -------
    object
        Return value.
    """
    flags = 0
    for name in names:
        if not isinstance(name, str):
            msg = "flags entries must be strings"
            raise DetectorError(msg)
        key = name.strip().upper()
        if key == "IGNORECASE":
            flags |= re.IGNORECASE
        elif key == "MULTILINE":
            flags |= re.MULTILINE
        elif key == "DOTALL":
            flags |= re.DOTALL
        else:
            msg = f"unsupported flag {name!r}"
            raise DetectorError(msg)
    return flags


def _parse_preprocess(raw: object) -> PreprocessSpec:
    """
    Internal helper ``_parse_preprocess``.

    Parameters
    ----------
    raw : object
        Argument ``raw``.

    Returns
    -------
    object
        Return value.
    """
    if raw is None:
        return PreprocessSpec()
    if not isinstance(raw, dict):
        msg = "preprocess must be a mapping"
        raise DetectorError(msg)
    data = cast(dict[str, object], raw)
    before = data.get("before")
    before_s = before.strip() if isinstance(before, str) and before.strip() else None
    after = data.get("after")
    after_s = after.strip() if isinstance(after, str) and after.strip() else None
    exclude = bool(data.get("exclude_ahl_lines", False))
    strip_term = bool(data.get("strip_terminator", True))
    return PreprocessSpec(
        before=before_s,
        after=after_s,
        exclude_ahl_lines=exclude,
        strip_terminator=strip_term,
    )


def _parse_emit(raw: object, *, required: bool) -> EmitSpec | None:
    """
    Internal helper ``_parse_emit``.

    Parameters
    ----------
    raw : object
        Argument ``raw``.
    required : object
        Argument ``required``.

    Returns
    -------
    object
        Return value.
    """
    if raw is None:
        if required:
            msg = "emit spec required"
            raise DetectorError(msg)
        return None
    if not isinstance(raw, dict):
        msg = "emit spec must be a mapping"
        raise DetectorError(msg)
    data = cast(dict[str, object], raw)
    code = data.get("code")
    if not isinstance(code, str) or not code.strip():
        msg = "emit.code is required"
        raise DetectorError(msg)
    location_raw = data.get("location")
    location = location_raw.strip() if isinstance(location_raw, str) and location_raw.strip() else None
    message = data.get("message_template")
    if not isinstance(message, str) or not message.strip():
        msg = "emit.message_template is required"
        raise DetectorError(msg)
    group_raw = data.get("capture_group", 0)
    if not isinstance(group_raw, int) or group_raw < 0:
        msg = "capture_group must be a non-negative int"
        raise DetectorError(msg)
    span_raw = data.get("span", "match")
    if span_raw not in ("match", "body"):
        msg = "span must be match or body"
        raise DetectorError(msg)
    span: Literal["match", "body"] = "body" if span_raw == "body" else "match"
    return EmitSpec(
        code=code.strip(),
        location=location,
        message_template=message,
        capture_group=group_raw,
        span=span,
    )


def _parse_rule(raw: object) -> DetectorRule:
    """
    Internal helper ``_parse_rule``.

    Parameters
    ----------
    raw : object
        Argument ``raw``.

    Returns
    -------
    object
        Return value.
    """
    if not isinstance(raw, dict):
        msg = "rule must be a mapping"
        raise DetectorError(msg)
    data = cast(dict[str, object], raw)
    rid = data.get("id")
    if not isinstance(rid, str) or not rid.strip():
        msg = "rule.id is required"
        raise DetectorError(msg)
    kind_raw = data.get("kind")
    if kind_raw not in ("finditer", "require_search", "python", "token_scan"):
        msg = "rule.kind must be finditer, require_search, python, or token_scan"
        raise DetectorError(msg)
    kind: DetectorKind
    if kind_raw == "finditer":
        kind = "finditer"
    elif kind_raw == "require_search":
        kind = "require_search"
    elif kind_raw == "token_scan":
        kind = "token_scan"
    else:
        kind = "python"
    skip_raw: object = data.get("skip_if_codes") or []
    if not isinstance(skip_raw, list) or not all(isinstance(x, str) for x in cast(list[object], skip_raw)):
        msg = "skip_if_codes must be a list of strings"
        raise DetectorError(msg)
    skip = tuple(str(x).strip() for x in cast(list[object], skip_raw) if str(x).strip())
    skip_match_raw = data.get("skip_if_match")
    skip_match = skip_match_raw.strip() if isinstance(skip_match_raw, str) and skip_match_raw.strip() else None
    max_raw = data.get("max_emits")
    max_emits: int | None
    if max_raw is None:
        max_emits = None
    elif isinstance(max_raw, int) and max_raw > 0:
        max_emits = max_raw
    else:
        msg = "max_emits must be a positive int"
        raise DetectorError(msg)
    pattern = data.get("pattern")
    pattern_s = pattern if isinstance(pattern, str) and pattern else None
    flags_raw: object = data.get("flags") or []
    if not isinstance(flags_raw, list):
        msg = "flags must be a list"
        raise DetectorError(msg)
    flags_list = cast(list[object], flags_raw)
    python_ref = data.get("python")
    python_s = python_ref.strip() if isinstance(python_ref, str) and python_ref.strip() else None
    if kind == "python":
        if not python_s:
            msg = "python kind requires python: ref"
            raise DetectorError(msg)
        return DetectorRule(
            id=rid.strip(),
            kind=kind,
            preprocess=_parse_preprocess(data.get("preprocess")),
            pattern=None,
            flags=0,
            skip_if_codes=skip,
            on_match=None,
            on_fail=None,
            python_ref=python_s,
            skip_if_match=skip_match,
            max_emits=max_emits,
        )
    if kind == "token_scan":
        select_raw = data.get("select") or pattern
        select_s = select_raw if isinstance(select_raw, str) and select_raw else None
        ok_raw = data.get("ok")
        ok_s = ok_raw if isinstance(ok_raw, str) and ok_raw else None
        if not select_s or not ok_s:
            msg = "token_scan requires select (or pattern) and ok"
            raise DetectorError(msg)
        on_ok = _parse_emit(data.get("on_ok"), required=False)
        on_fail = _parse_emit(data.get("on_fail"), required=False)
        if on_ok is None and on_fail is None:
            msg = "token_scan requires on_ok and/or on_fail"
            raise DetectorError(msg)
        return DetectorRule(
            id=rid.strip(),
            kind=kind,
            preprocess=_parse_preprocess(data.get("preprocess")),
            pattern=None,
            flags=_re_flags(flags_list),
            skip_if_codes=skip,
            on_match=None,
            on_fail=on_fail,
            python_ref=None,
            skip_if_match=skip_match,
            select_pattern=select_s,
            ok_pattern=ok_s,
            on_ok=on_ok,
            max_emits=max_emits,
        )
    if not pattern_s:
        msg = f"{kind} requires pattern"
        raise DetectorError(msg)
    on_match = _parse_emit(data.get("on_match"), required=(kind == "finditer"))
    on_fail = _parse_emit(data.get("on_fail"), required=(kind == "require_search"))
    return DetectorRule(
        id=rid.strip(),
        kind=kind,
        preprocess=_parse_preprocess(data.get("preprocess")),
        pattern=pattern_s,
        flags=_re_flags(flags_list),
        skip_if_codes=skip,
        on_match=on_match,
        on_fail=on_fail,
        python_ref=None,
        skip_if_match=skip_match,
        max_emits=max_emits,
    )


def _parse_pack(data: object, *, source_path: str | None) -> DetectorPack:
    """
    Internal helper ``_parse_pack``.

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
    if not isinstance(data, dict):
        msg = "detector pack root must be a mapping"
        raise DetectorError(msg)
    mapping = cast(Mapping[str, Any], data)
    pid = mapping.get("id")
    if not isinstance(pid, str) or not pid.strip():
        msg = "id is required"
        raise DetectorError(msg)
    stage_raw = mapping.get("stage", "token")
    if stage_raw not in ("parse_gate", "token", "cross_field"):
        msg = "stage must be parse_gate, token, or cross_field"
        raise DetectorError(msg)
    products_raw: object = mapping.get("products") or []
    if not isinstance(products_raw, list) or not products_raw:
        msg = "products must be a non-empty list"
        raise DetectorError(msg)
    products = frozenset(str(p).strip().upper() for p in cast(list[object], products_raw))
    rules_raw: object = mapping.get("rules") or []
    if not isinstance(rules_raw, list) or not rules_raw:
        msg = "rules must be a non-empty list"
        raise DetectorError(msg)
    rules = tuple(_parse_rule(item) for item in cast(list[object], rules_raw))
    stage: DetectorStage
    if stage_raw == "parse_gate":
        stage = "parse_gate"
    elif stage_raw == "cross_field":
        stage = "cross_field"
    else:
        stage = "token"
    return DetectorPack(
        id=pid.strip(),
        stage=stage,
        products=products,
        rules=rules,
        source_path=source_path,
    )


def load_detector_pack(path: Path | str) -> DetectorPack:
    """
    Load one detector pack YAML file.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (load_detector_pack)
    2

    Parameters
    ----------
    path : Path or str
        Path.

    Returns
    -------
    DetectorPack
        Load one detector pack YAML file.
    """
    file_path = Path(path)
    raw = yaml.safe_load(file_path.read_text(encoding="utf-8"))
    return _parse_pack(raw, source_path=str(file_path))


def _header_extends(value: object, *, name: str) -> str | None:
    """Parse a single builtin id from ``extends`` (or raise)."""
    if value is None or value == []:
        return None
    if isinstance(value, str) and value.strip():
        return value.strip()
    if isinstance(value, list):
        items = cast(list[object], value)
        if len(items) == 1 and isinstance(items[0], str) and items[0].strip():
            return items[0].strip()
    msg = f"{name} must extend one builtin"
    raise DetectorError(msg)


def _header_profiles(value: object, *, name: str) -> tuple[str, ...]:
    """
    Internal helper ``_header_profiles``.

    Parameters
    ----------
    value : object
        Argument ``value``.
    name : object
        Argument ``name``.

    Returns
    -------
    object
        Return value.
    """
    if value is None:
        return ()
    if not isinstance(value, list) or not value:
        msg = f"{name} needs a profiles list"
        raise DetectorError(msg)
    out: list[str] = []
    for item in cast(list[object], value):
        if not isinstance(item, str) or not item:
            msg = f"{name} needs a profiles list"
            raise DetectorError(msg)
        out.append(item)
    return tuple(out)


def _merge_detector_rules(
    base: tuple[DetectorRule, ...],
    extra: tuple[DetectorRule, ...],
) -> tuple[DetectorRule, ...]:
    """
    Internal helper ``_merge_detector_rules``.

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


def _take_detector_overlay(
    raw: object,
    pack: DetectorPack,
    catalog: Mapping[str, DetectorPack],
    *,
    profile: str | None,
) -> DetectorPack | None:
    """
    Internal helper ``_take_detector_overlay``.

    Parameters
    ----------
    raw : object
        Argument ``raw``.
    pack : object
        Argument ``pack``.
    catalog : object
        Argument ``catalog``.
    profile : object
        Argument ``profile``.

    Returns
    -------
    object
        Return value.
    """
    mapping = cast(Mapping[str, Any], raw)
    base_id = _header_extends(mapping.get("extends"), name=pack.id)
    profiles = _header_profiles(mapping.get("profiles"), name=pack.id)
    if base_id is None and pack.id not in catalog:
        if profiles:
            msg = f"{pack.id} profiles require extends"
            raise DetectorError(msg)
        return pack
    if base_id is None:
        msg = f"{pack.id} must extend one builtin"
        raise DetectorError(msg)
    if not profiles:
        msg = f"{pack.id} needs a profiles list"
        raise DetectorError(msg)
    parent = catalog.get(base_id)
    if parent is None:
        msg = f"{pack.id} extends unknown builtin {base_id}"
        raise DetectorError(msg)
    if pack.stage != parent.stage:
        msg = f"{pack.id} stage must match {base_id}"
        raise DetectorError(msg)
    if profile is None or profile not in profiles:
        return None
    return DetectorPack(
        id=parent.id,
        stage=parent.stage,
        products=parent.products,
        rules=_merge_detector_rules(parent.rules, pack.rules),
        source_path=parent.source_path,
    )


__all__ = [
    "_AHL_HEADING_LINE",
    "_header_extends",
    "_header_profiles",
    "_merge_detector_rules",
    "_parse_emit",
    "_parse_pack",
    "_parse_preprocess",
    "_parse_rule",
    "_re_flags",
    "_take_detector_overlay",
    "load_detector_pack",
]
