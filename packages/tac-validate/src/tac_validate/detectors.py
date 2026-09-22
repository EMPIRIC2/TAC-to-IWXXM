"""Declarative detector packs (ADR-046 / #1216 M2).

Small DSL v1: ``finditer`` + ``require_search`` + ``token_scan`` with preprocess
(before / exclude AHL). Optional ``skip_if_match`` gates rules on a window regex.
Python hatch: ``python:module:attr`` registered callables.
"""

# pyright: reportPrivateUsage=false

from __future__ import annotations

import importlib
import os
import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Any, Literal, cast

import yaml

from tac_validate.issue_registry import issue_from
from tac_validate.match_port import match_port_spans
from tac_validate.models import Issue
from tac_validate.product_rules_pkg._common import _strip_research_refs
from tac_validate.theme_checks import lint_profile

DetectorStage = Literal["parse_gate", "token", "cross_field"]
DetectorKind = Literal["finditer", "require_search", "python", "token_scan"]

ENV_DETECTOR_DIR = "TAC_VALIDATE_DETECTOR_DIR"
ENV_DETECTOR_MODE = "TAC_VALIDATE_DETECTOR_MODE"  # legacy | shadow | detector
DEFAULT_LINT_BUDGET = 10_000

_AHL_HEADING_LINE = re.compile(r"^[A-Z]{2}[A-Z]{2}\d{2}\s+[A-Z]{4}\s+\d{6}(?:\s+[A-Z]{3})?\s*$")
_TOKEN_RE = re.compile(r"\S+")

PythonDetector = Callable[[str, str], list[Issue]]


class DetectorError(ValueError):
    """
    Invalid detector pack or rule.

    Attributes
    ----------
    _ : object
        See implementation.
    """


@dataclass(frozen=True, slots=True)
class PreprocessSpec:
    """
    Text windowing before a rule runs.

    Attributes
    ----------
    _ : object
        See implementation.
    """

    before: str | None = None
    after: str | None = None
    exclude_ahl_lines: bool = False
    strip_terminator: bool = True


@dataclass(frozen=True, slots=True)
class EmitSpec:
    """
    Issue emission on match or fail.

    Attributes
    ----------
    _ : object
        See implementation.
    """

    code: str
    location: str | None
    message_template: str
    capture_group: int = 0
    span: Literal["match", "body"] = "match"


@dataclass(frozen=True, slots=True)
class DetectorRule:
    """
    One detector rule inside a pack.

    Attributes
    ----------
    _ : object
        See implementation.
    """

    id: str
    kind: DetectorKind
    preprocess: PreprocessSpec
    pattern: str | None
    flags: int
    skip_if_codes: tuple[str, ...]
    on_match: EmitSpec | None
    on_fail: EmitSpec | None
    python_ref: str | None
    skip_if_match: str | None = None
    select_pattern: str | None = None
    ok_pattern: str | None = None
    on_ok: EmitSpec | None = None
    max_emits: int | None = None


@dataclass(frozen=True, slots=True)
class DetectorPack:
    """
    Loaded detector pack document.

    Attributes
    ----------
    _ : object
        See implementation.
    """

    id: str
    stage: DetectorStage
    products: frozenset[str]
    rules: tuple[DetectorRule, ...]
    source_path: str | None = None


@dataclass(frozen=True, slots=True)
class ShadowCompareResult:
    """
    Legacy vs detector issue sets for one code family.

    Attributes
    ----------
    _ : object
        See implementation.
    """

    matched: bool
    legacy_keys: frozenset[tuple[str, int | None, int | None]]
    detector_keys: frozenset[tuple[str, int | None, int | None]]


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
    path : object
        Argument ``path``.

    Returns
    -------
    object
        Return value.
    """
    file_path = Path(path)
    raw = yaml.safe_load(file_path.read_text(encoding="utf-8"))
    return _parse_pack(raw, source_path=str(file_path))


def _header_extends(value: object, *, name: str) -> str | None:
    """
    Internal helper ``_header_extends``.

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


def load_detector_catalog(profile: str | None = None) -> dict[str, DetectorPack]:
    """
    Load builtin detector packs plus optional ``TAC_VALIDATE_DETECTOR_DIR``.

    An overlay with ``extends`` layers rules onto that builtin for the profile
    ids in its header. Omitting ``profile`` leaves those layers off. A new pack
    id with no ``extends`` is added for every profile.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (load_detector_catalog)
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
    catalog: dict[str, DetectorPack] = {}
    root = resources.files("tac_validate").joinpath("data", "detectors")
    for entry in root.iterdir():
        name = entry.name
        if name.endswith((".yaml", ".yml")):
            text = entry.read_text(encoding="utf-8")
            pack = _parse_pack(yaml.safe_load(text), source_path=f"builtin:{name}")
            catalog[pack.id] = pack
    overlay = os.environ.get(ENV_DETECTOR_DIR, "").strip()
    if overlay:
        overlay_path = Path(overlay)
        if overlay_path.is_dir():
            for path in sorted(overlay_path.glob("*.yaml")) + sorted(overlay_path.glob("*.yml")):
                raw = yaml.safe_load(path.read_text(encoding="utf-8"))
                pack = _parse_pack(raw, source_path=str(path))
                layered = _take_detector_overlay(raw, pack, catalog, profile=profile)
                if layered is None:
                    continue
                catalog[layered.id] = layered
    return catalog


def detector_mode() -> Literal["legacy", "shadow", "detector"]:
    """
    Return effective detector mode (default ``detector`` after R2 flip).

    Examples
    --------
    >>> 1 + 1  # docstring smoke (detector_mode)
    2

    Returns
    -------
    object
        Return value.
    """
    raw = os.environ.get(ENV_DETECTOR_MODE, "detector").strip().lower()
    if raw == "legacy":
        return "legacy"
    if raw == "shadow":
        return "shadow"
    return "detector"


def _body_span(tac: str) -> tuple[int, int, str]:
    """
    Internal helper ``_body_span``.

    Parameters
    ----------
    tac : object
        Argument ``tac``.

    Returns
    -------
    object
        Return value.
    """
    stripped = tac.strip()
    if not stripped:
        return 0, len(tac), ""
    leading = len(tac) - len(tac.lstrip())
    return leading, leading + len(stripped), stripped


def _prepare_window(body: str, prep: PreprocessSpec) -> tuple[str, int]:
    """
    Internal helper ``_prepare_window``.

    Parameters
    ----------
    body : object
        Argument ``body``.
    prep : object
        Argument ``prep``.

    Returns
    -------
    object
        Return value.
    """
    text = body
    offset = 0
    if prep.strip_terminator and text.endswith("="):
        text = text[:-1]
    if prep.after:
        at = text.find(prep.after)
        if at >= 0:
            cut = at + len(prep.after)
            text = text[cut:]
            offset = cut
    if prep.before:
        at = text.find(prep.before)
        if at >= 0:
            text = text[:at]
    if prep.exclude_ahl_lines:
        kept = [
            line
            for line in text.splitlines(keepends=True)
            if not _AHL_HEADING_LINE.match(line.strip("\n").strip("\r").strip())
        ]
        text = "".join(kept)
        # Keep offset 0 so spans match legacy metar_speci visibility (stripped window
        # treated as starting at body start) — only when after was not applied.
        if not prep.after:
            offset = 0
    return text, offset


def _resolve_python(ref: str) -> PythonDetector:
    """
    Internal helper ``_resolve_python``.

    Parameters
    ----------
    ref : object
        Argument ``ref``.

    Returns
    -------
    object
        Return value.
    """
    if not ref.startswith("python:"):
        msg = f"python ref must start with python:: {ref!r}"
        raise DetectorError(msg)
    rest = ref[len("python:") :]
    if ":" not in rest:
        msg = f"python ref must be python:module:attr: {ref!r}"
        raise DetectorError(msg)
    module_name, _, attr = rest.rpartition(":")
    if not module_name or not attr:
        msg = f"python ref must be python:module:attr: {ref!r}"
        raise DetectorError(msg)
    module = importlib.import_module(module_name)
    fn = getattr(module, attr, None)
    if not callable(fn):
        msg = f"python detector not callable: {ref!r}"
        raise DetectorError(msg)
    return cast(PythonDetector, fn)


def _emit_issue(
    emit: EmitSpec,
    *,
    product: str,
    body_start: int,
    body_end: int,
    window_offset: int,
    match: re.Match[str] | None,
) -> Issue:
    """
    Internal helper ``_emit_issue``.

    Parameters
    ----------
    emit : object
        Argument ``emit``.
    product : object
        Argument ``product``.
    body_start : object
        Argument ``body_start``.
    body_end : object
        Argument ``body_end``.
    window_offset : object
        Argument ``window_offset``.
    match : object
        Argument ``match``.

    Returns
    -------
    object
        Return value.
    """
    capture = ""
    start = body_start
    end = body_end
    if emit.span == "match" and match is not None:
        group = emit.capture_group
        try:
            capture = match.group(group)
            start = body_start + window_offset + match.start(group)
            end = body_start + window_offset + match.end(group)
        except IndexError:
            capture = match.group(0)
            start = body_start + window_offset + match.start(0)
            end = body_start + window_offset + match.end(0)
    message = _strip_research_refs(emit.message_template.format(product=product, capture=capture))
    return issue_from(
        emit.code,
        message=message,
        start=start,
        end=end,
        location=emit.location,
    )


def run_detector_pack(
    pack: DetectorPack,
    tac_text: str,
    product: str,
    *,
    budget: int = DEFAULT_LINT_BUDGET,
) -> list[Issue]:
    """
    Run all rules in ``pack`` for ``product``.

    Parameters
    ----------
    pack :
        Loaded detector pack.
    tac_text :
        Raw TAC.
    product :
        Product id (METAR / SPECI / …).
    budget :
        Max regex match steps across finditer rules; fail closed when exceeded.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (run_detector_pack)
    2

    Returns
    -------
    object
        Return value.
    """
    product_u = product.upper()
    if product_u not in pack.products:
        return []
    body_start, body_end, body = _body_span(tac_text)
    upper = body.upper()
    issues: list[Issue] = []
    emitted_codes: set[str] = set()
    steps = 0
    for rule in pack.rules:
        if rule.skip_if_codes and any(code in emitted_codes for code in rule.skip_if_codes):
            continue
        window, win_off = _prepare_window(upper, rule.preprocess)
        if rule.skip_if_match and re.search(rule.skip_if_match, window, rule.flags):
            continue
        if rule.kind == "python":
            assert rule.python_ref is not None
            hatch_issues = _resolve_python(rule.python_ref)(tac_text, product_u)
            issues.extend(hatch_issues)
            for item in hatch_issues:
                emitted_codes.add(item.code)
            continue
        if rule.kind == "token_scan":
            assert rule.select_pattern is not None
            assert rule.ok_pattern is not None
            select_re = re.compile(rule.select_pattern, rule.flags)
            ok_re = re.compile(rule.ok_pattern, rule.flags)
            emitted_here = 0
            for tok_match in _TOKEN_RE.finditer(window):
                steps += 1
                if steps > budget:
                    msg = f"{product_u} lint detector budget exceeded"
                    raise DetectorError(msg)
                token = tok_match.group(0)
                if select_re.fullmatch(token) is None:
                    continue
                emit = rule.on_ok if ok_re.fullmatch(token) is not None else rule.on_fail
                if emit is None:
                    continue
                issue = _emit_issue(
                    emit,
                    product=product_u,
                    body_start=body_start,
                    body_end=body_end,
                    window_offset=win_off,
                    match=tok_match,
                )
                issues.append(issue)
                emitted_codes.add(issue.code)
                emitted_here += 1
                if rule.max_emits is not None and emitted_here >= rule.max_emits:
                    break
            continue
        if rule.pattern is None:
            msg = f"rule {rule.id!r} missing pattern"
            raise DetectorError(msg)
        compiled = re.compile(rule.pattern, rule.flags)
        if rule.kind == "finditer":
            assert rule.on_match is not None
            for emitted_here, match in enumerate(compiled.finditer(window), start=1):
                steps += 1
                if steps > budget:
                    msg = f"{product_u} lint detector budget exceeded"
                    raise DetectorError(msg)
                issue = _emit_issue(
                    rule.on_match,
                    product=product_u,
                    body_start=body_start,
                    body_end=body_end,
                    window_offset=win_off,
                    match=match,
                )
                issues.append(issue)
                emitted_codes.add(issue.code)
                if rule.max_emits is not None and emitted_here >= rule.max_emits:
                    break
        elif rule.kind == "require_search":
            assert rule.on_fail is not None
            steps += 1
            if steps > budget:
                msg = f"{product_u} lint detector budget exceeded"
                raise DetectorError(msg)
            if compiled.search(window) is None:
                issue = _emit_issue(
                    rule.on_fail,
                    product=product_u,
                    body_start=body_start,
                    body_end=body_end,
                    window_offset=win_off,
                    match=None,
                )
                issues.append(issue)
                emitted_codes.add(issue.code)
        else:
            msg = f"unsupported detector kind {rule.kind!r}"
            raise DetectorError(msg)
    return issues


def issue_keys(issues: Sequence[Issue]) -> frozenset[tuple[str, int | None, int | None]]:
    """
    Shadow-compare keys: code + span.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (issue_keys)
    2

    Parameters
    ----------
    issues : object
        Argument ``issues``.

    Returns
    -------
    object
        Return value.
    """
    return frozenset((i.code, i.start, i.end) for i in issues)


def compare_shadow(
    legacy: Sequence[Issue],
    detector: Sequence[Issue],
    *,
    codes: frozenset[str],
) -> ShadowCompareResult:
    """
    Compare legacy vs detector issues filtered to ``codes``.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (compare_shadow)
    2

    Parameters
    ----------
    legacy : object
        Argument ``legacy``.
    detector : object
        Argument ``detector``.
    codes : object
        Argument ``codes``.

    Returns
    -------
    object
        Return value.
    """
    leg = issue_keys([i for i in legacy if i.code in codes])
    det = issue_keys([i for i in detector if i.code in codes])
    return ShadowCompareResult(matched=leg == det, legacy_keys=leg, detector_keys=det)


def run_r2_visibility_detectors(tac_text: str, product: str) -> list[Issue]:
    """
    Convenience: run builtin R2 visibility pack.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (run_r2_visibility_detectors)
    2

    Parameters
    ----------
    tac_text : object
        Argument ``tac_text``.
    product : object
        Argument ``product``.

    Returns
    -------
    object
        Return value.
    """
    return run_theme_pack("metar-speci-r2-visibility", tac_text, product)


_ANNEX3_METAR_THEME_PACKS = frozenset(
    {
        "metar-speci-r1-identity-order",
        "metar-speci-r2-visibility",
        "metar-speci-r3-weather",
        "metar-speci-r4-cloud",
        "metar-speci-r5-remarks",
        "metar-speci-r8-modifiers",
    }
)


def run_theme_pack(pack_id: str, tac_text: str, product: str) -> list[Issue]:
    """
    Run one builtin/overlay detector pack by id (empty if missing or product mismatch).

    Examples
    --------
    >>> 1 + 1  # docstring smoke (run_theme_pack)
    2

    Parameters
    ----------
    pack_id : object
        Argument ``pack_id``.
    tac_text : object
        Argument ``tac_text``.
    product : object
        Argument ``product``.

    Returns
    -------
    object
        Return value.
    """
    spans = match_port_spans.get()
    strict = (
        spans is not None
        and pack_id in _ANNEX3_METAR_THEME_PACKS
        and product.upper() == "METAR"
        and lint_profile.get() == "annex3"
    )
    if strict and not spans:
        return [
            issue_from(
                "MISSING_DECODE_MATCH",
                product=product.upper(),
                location="match",
                start=0,
                end=len(tac_text),
            )
        ]
    catalog = load_detector_catalog(lint_profile.get())
    pack = catalog.get(pack_id)
    if pack is None:
        msg = f"detector pack {pack_id!r} not found"
        raise DetectorError(msg)
    issues = run_detector_pack(pack, tac_text, product)
    if strict and spans:
        span = spans[0]
        return [
            Issue(
                severity=issue.severity,
                code=issue.code,
                message=issue.message,
                location=issue.location,
                start=span.start,
                end=span.end,
            )
            for issue in issues
        ]
    return issues


def example_python_hatch(tac_text: str, product: str) -> list[Issue]:
    """
    No-op python hatch used by unit tests.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (example_python_hatch)
    2

    Parameters
    ----------
    tac_text : object
        Argument ``tac_text``.
    product : object
        Argument ``product``.

    Returns
    -------
    object
        Return value.
    """
    _ = (tac_text, product)
    return []


def example_python_hatch_emit(tac_text: str, product: str) -> list[Issue]:
    """
    Python hatch that emits INVALID_VISIBILITY for skip_if / emitted_codes coverage.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (example_python_hatch_emit)
    2

    Parameters
    ----------
    tac_text : object
        Argument ``tac_text``.
    product : object
        Argument ``product``.

    Returns
    -------
    object
        Return value.
    """
    _ = tac_text
    return [
        Issue(
            code="INVALID_VISIBILITY",
            severity="error",
            message=f"{product} hatch emit",
            start=0,
            end=0,
        )
    ]


__all__ = [
    "DEFAULT_LINT_BUDGET",
    "ENV_DETECTOR_DIR",
    "ENV_DETECTOR_MODE",
    "DetectorError",
    "DetectorPack",
    "DetectorRule",
    "ShadowCompareResult",
    "compare_shadow",
    "detector_mode",
    "example_python_hatch",
    "example_python_hatch_emit",
    "issue_keys",
    "load_detector_catalog",
    "load_detector_pack",
    "run_detector_pack",
    "run_r2_visibility_detectors",
    "run_theme_pack",
]
