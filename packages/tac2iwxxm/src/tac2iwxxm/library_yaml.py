"""Library YAML schema + regex diagnostics (EVPYL Phase C).

Fail = does not compile, or required sample has no match.
Warn = compiles but looks risky (nested quantifiers, unused groups).
Activate requires zero Fail; Draft may include Fail.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Literal, cast

import yaml

from tac2iwxxm.library_assets import LIBRARY_KINDS, LibraryKind
from tac2iwxxm.numeric_checks import evaluate_numeric_check, validate_numeric_check_shape

LibraryLifecycle = Literal["draft", "activated"]
RegexSeverity = Literal["ok", "warn", "fail"]

_NESTED_QUANTIFIER = re.compile(r"[+*][?+]|\{\d+,\}\+|\{0,")
_URI_OR_SECRET = re.compile(
    r"(password|secret|token|credential|api[_-]?key|https?://|sftp://|amqps?://)",
    re.IGNORECASE,
)


@dataclass(frozen=True, slots=True)
class CaptureSummary:
    """
    One named or positional capture from a compiled pattern.

    Attributes
    ----------
    _ : object
        See implementation.
    """

    index: int
    name: str


@dataclass(frozen=True, slots=True)
class RegexDiagnostic:
    """
    Compile result for one pattern in a library YAML document.

    Attributes
    ----------
    _ : object
        See implementation.
    """

    path: str
    pattern: str
    severity: RegexSeverity
    message: str
    captures: tuple[CaptureSummary, ...] = ()
    sample_matched: bool | None = None


@dataclass(frozen=True, slots=True)
class LibraryYamlReport:
    """
    Strict YAML parse + regex diagnostics for one library asset.

    Attributes
    ----------
    _ : object
        See implementation.
    """

    valid_yaml: bool
    yaml_error: str | None
    kind: LibraryKind | None
    name: str | None
    lifecycle: LibraryLifecycle
    diagnostics: tuple[RegexDiagnostic, ...]
    fail_count: int
    warn_count: int
    can_activate: bool
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize for JSON / API responses.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (to_dict)
        2

        Returns
        -------
        object
            Return value.
        """
        return {
            "valid_yaml": self.valid_yaml,
            "yaml_error": self.yaml_error,
            "kind": self.kind,
            "name": self.name,
            "lifecycle": self.lifecycle,
            "fail_count": self.fail_count,
            "warn_count": self.warn_count,
            "can_activate": self.can_activate,
            "data": dict(self.data),
            "diagnostics": [
                {
                    "path": item.path,
                    "pattern": item.pattern,
                    "severity": item.severity,
                    "message": item.message,
                    "captures": [{"index": c.index, "name": c.name} for c in item.captures],
                    "sample_matched": item.sample_matched,
                }
                for item in self.diagnostics
            ],
        }


def _as_str(value: object) -> str | None:
    """
    Internal helper ``_as_str``.

    Parameters
    ----------
    value : object
        Argument ``value``.

    Returns
    -------
    object
        Return value.
    """
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _as_mapping(value: object) -> dict[str, Any]:
    """
    Internal helper ``_as_mapping``.

    Parameters
    ----------
    value : object
        Argument ``value``.

    Returns
    -------
    object
        Return value.
    """
    if not isinstance(value, dict):
        return {}
    mapped: dict[str, Any] = {}
    for key, item in cast(dict[object, object], value).items():
        mapped[str(key)] = item
    return mapped


def _as_list(value: object) -> list[object]:
    """
    Internal helper ``_as_list``.

    Parameters
    ----------
    value : object
        Argument ``value``.

    Returns
    -------
    object
        Return value.
    """
    if not isinstance(value, list):
        return []
    return list(cast(list[object], value))


def _extract_patterns(kind: LibraryKind, data: dict[str, Any]) -> list[tuple[str, str, str | None]]:
    """
    Internal helper ``_extract_patterns``.

    Parameters
    ----------
    kind : object
        Argument ``kind``.
    data : object
        Argument ``data``.

    Returns
    -------
    object
        Return value.
    """
    found: list[tuple[str, str, str | None]] = []
    rows: list[object]
    key: str
    if kind == "tac_validation":
        rows = _as_list(data.get("rules"))
        key = "rules"
        fields = ("pattern", "regex")
    elif kind == "iwxxm_validation":
        rows = _as_list(data.get("custom_rules"))
        if not rows:
            rows = _as_list(data.get("rules"))
        key = "custom_rules"
        fields = ("regex", "pattern")
    elif kind == "decoding":
        rows = _as_list(data.get("entries"))
        key = "entries"
        fields = ("regex", "pattern", "token")
    elif kind == "conversion":
        rows = _as_list(data.get("rules"))
        key = "rules"
        fields = ("pattern", "regex")
    else:
        rows = _as_list(data.get("transforms"))
        key = "transforms"
        fields = ("pattern", "regex")

    for index, row in enumerate(rows):
        row_map = _as_mapping(row)
        if not row_map and not isinstance(row, dict):
            continue
        pattern: str | None = None
        for field_name in fields:
            pattern = _as_str(row_map.get(field_name))
            if pattern:
                break
        if kind == "iwxxm_validation" and pattern and pattern.startswith(("/", "iwxxm:")):
            continue
        if kind == "decoding" and pattern and not any(ch in pattern for ch in r".*+?[](){}|"):
            continue
        if pattern:
            sample_key = "sample" if "sample" in row_map else "token"
            found.append((f"{key}[{index}].pattern", pattern, _as_str(row_map.get(sample_key))))
    return found


def _rule_rows_for_checks(kind: LibraryKind, data: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    """
    Internal helper ``_rule_rows_for_checks``.

    Parameters
    ----------
    kind : object
        Argument ``kind``.
    data : object
        Argument ``data``.

    Returns
    -------
    object
        Return value.
    """
    found: list[tuple[str, dict[str, Any]]] = []
    if kind == "tac_validation":
        rows = _as_list(data.get("rules"))
        key = "rules"
    elif kind == "iwxxm_validation":
        rows = _as_list(data.get("custom_rules"))
        if not rows:
            rows = _as_list(data.get("rules"))
        key = "custom_rules" if data.get("custom_rules") is not None else "rules"
    else:
        return found
    for index, row in enumerate(rows):
        row_map = _as_mapping(row)
        if row_map:
            found.append((f"{key}[{index}]", row_map))
    return found


def _numeric_check_diagnostics(
    kind: LibraryKind,
    data: dict[str, Any],
) -> tuple[RegexDiagnostic, ...]:
    """
    Internal helper ``_numeric_check_diagnostics``.

    Parameters
    ----------
    kind : object
        Argument ``kind``.
    data : object
        Argument ``data``.

    Returns
    -------
    object
        Return value.
    """
    out: list[RegexDiagnostic] = []
    for path, row in _rule_rows_for_checks(kind, data):
        if "check" not in row:
            continue
        check = row.get("check")
        shape_error = validate_numeric_check_shape(check)
        if shape_error is not None:
            out.append(
                RegexDiagnostic(
                    path=f"{path}.check",
                    pattern="",
                    severity="fail",
                    message=shape_error,
                )
            )
            continue
        if not isinstance(check, dict):
            continue
        check_map = cast(dict[str, Any], check)
        sample = _as_str(row.get("sample"))
        if sample is None:
            continue
        field = _as_str(check_map.get("field"))
        candidate: object = sample
        pattern = _as_str(row.get("pattern")) or _as_str(row.get("regex"))
        if pattern and field:
            try:
                compiled = re.compile(pattern)
            except re.error:
                continue
            match = compiled.search(sample)
            if match is not None:
                try:
                    candidate = match.group(field)
                except IndexError:
                    candidate = sample
        result = evaluate_numeric_check(check_map, candidate)
        if result is False:
            out.append(
                RegexDiagnostic(
                    path=f"{path}.check",
                    pattern=pattern or "",
                    severity="fail",
                    message="Sample value fails numeric check",
                    sample_matched=False,
                )
            )
    return tuple(out)


def diagnose_regex(pattern: str, *, sample: str | None = None, path: str = "pattern") -> RegexDiagnostic:
    """
    Compile one pattern and classify ok / warn / fail.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (diagnose_regex)
    2

    Parameters
    ----------
    pattern : object
        Argument ``pattern``.
    sample : object
        Argument ``sample``.
    path : object
        Argument ``path``.

    Returns
    -------
    object
        Return value.
    """
    try:
        compiled = re.compile(pattern)
    except re.error as exc:
        return RegexDiagnostic(
            path=path,
            pattern=pattern,
            severity="fail",
            message=f"Does not compile: {exc}",
        )

    names = compiled.groupindex
    captures = tuple(
        CaptureSummary(index=index, name=name) for name, index in sorted(names.items(), key=lambda item: item[1])
    )
    if not captures:
        captures = tuple(CaptureSummary(index=i, name=f"group{i}") for i in range(1, compiled.groups + 1))

    sample_matched: bool | None = None
    if sample is not None:
        sample_matched = compiled.search(sample) is not None
        if not sample_matched:
            return RegexDiagnostic(
                path=path,
                pattern=pattern,
                severity="fail",
                message="Required sample has no match",
                captures=captures,
                sample_matched=False,
            )

    if _NESTED_QUANTIFIER.search(pattern) or (compiled.groups and not names):
        return RegexDiagnostic(
            path=path,
            pattern=pattern,
            severity="warn",
            message="Compiles, but may backtrack or leave unnamed groups unused",
            captures=captures,
            sample_matched=sample_matched,
        )
    return RegexDiagnostic(
        path=path,
        pattern=pattern,
        severity="ok",
        message="Compiles",
        captures=captures,
        sample_matched=sample_matched,
    )


def _secret_violation(data: dict[str, Any]) -> str | None:
    """
    Internal helper ``_secret_violation``.

    Parameters
    ----------
    data : object
        Argument ``data``.

    Returns
    -------
    object
        Return value.
    """
    blob = yaml.safe_dump(data, sort_keys=False)
    if _URI_OR_SECRET.search(blob):
        return "Dissemination YAML must not include credentials or destination URIs"
    return None


def validate_library_yaml(
    raw: str,
    *,
    expected_kind: LibraryKind | None = None,
    lifecycle: LibraryLifecycle = "draft",
) -> LibraryYamlReport:
    """
    Parse YAML, enforce kind/name, and collect regex diagnostics.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (validate_library_yaml)
    2

    Parameters
    ----------
    raw : object
        Argument ``raw``.
    expected_kind : object
        Argument ``expected_kind``.
    lifecycle : object
        Argument ``lifecycle``.

    Returns
    -------
    object
        Return value.
    """
    stripped = raw.strip()
    if not stripped:
        return LibraryYamlReport(
            valid_yaml=False,
            yaml_error="YAML is empty",
            kind=expected_kind,
            name=None,
            lifecycle=lifecycle,
            diagnostics=(),
            fail_count=1,
            warn_count=0,
            can_activate=False,
        )
    try:
        loaded_raw: object = yaml.safe_load(stripped)
    except yaml.YAMLError as exc:
        return LibraryYamlReport(
            valid_yaml=False,
            yaml_error=str(exc).split("\n", 1)[0],
            kind=expected_kind,
            name=None,
            lifecycle=lifecycle,
            diagnostics=(),
            fail_count=1,
            warn_count=0,
            can_activate=False,
        )
    if not isinstance(loaded_raw, dict):
        return LibraryYamlReport(
            valid_yaml=False,
            yaml_error="YAML root must be a mapping",
            kind=expected_kind,
            name=None,
            lifecycle=lifecycle,
            diagnostics=(),
            fail_count=1,
            warn_count=0,
            can_activate=False,
        )

    data = _as_mapping(cast(object, loaded_raw))
    kind_raw = data.get("kind")
    kind: LibraryKind | None
    if isinstance(kind_raw, str) and kind_raw in LIBRARY_KINDS:
        kind = kind_raw
    else:
        kind = expected_kind
        return LibraryYamlReport(
            valid_yaml=False,
            yaml_error="kind must be one of the five library kinds",
            kind=expected_kind,
            name=_as_str(data.get("name")),
            lifecycle=lifecycle,
            diagnostics=(),
            fail_count=1,
            warn_count=0,
            can_activate=False,
            data=data,
        )
    if expected_kind is not None and kind != expected_kind:
        return LibraryYamlReport(
            valid_yaml=False,
            yaml_error=f"kind must be {expected_kind}",
            kind=kind,
            name=_as_str(data.get("name")),
            lifecycle=lifecycle,
            diagnostics=(),
            fail_count=1,
            warn_count=0,
            can_activate=False,
            data=data,
        )

    name = _as_str(data.get("name"))
    if name is None:
        return LibraryYamlReport(
            valid_yaml=False,
            yaml_error="name is required",
            kind=kind,
            name=None,
            lifecycle=lifecycle,
            diagnostics=(),
            fail_count=1,
            warn_count=0,
            can_activate=False,
            data=data,
        )

    if kind == "dissemination":
        secret_error = _secret_violation(data)
        if secret_error is not None:
            return LibraryYamlReport(
                valid_yaml=False,
                yaml_error=secret_error,
                kind=kind,
                name=name,
                lifecycle=lifecycle,
                diagnostics=(),
                fail_count=1,
                warn_count=0,
                can_activate=False,
                data=data,
            )

    diagnostics = tuple(
        diagnose_regex(pattern, sample=sample, path=path) for path, pattern, sample in _extract_patterns(kind, data)
    ) + _numeric_check_diagnostics(kind, data)
    fail_count = sum(1 for item in diagnostics if item.severity == "fail")
    warn_count = sum(1 for item in diagnostics if item.severity == "warn")
    return LibraryYamlReport(
        valid_yaml=True,
        yaml_error=None,
        kind=kind,
        name=name,
        lifecycle=lifecycle,
        diagnostics=diagnostics,
        fail_count=fail_count,
        warn_count=warn_count,
        can_activate=fail_count == 0,
        data=data,
    )
