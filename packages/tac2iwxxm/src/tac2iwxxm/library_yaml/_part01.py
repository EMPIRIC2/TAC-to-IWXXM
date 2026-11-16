"""Split part body (exec'd into package namespace)."""

from __future__ import annotations


def _as_str(value: object) -> str | None:
    """
    Internal helper ``_as_str``.

    Parameters
    ----------
    value : object
        Argument ``value``.

    Returns
    -------
    str | None
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
    dict[str, Any]
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
    list[object]
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
    kind : LibraryKind
        Argument ``kind``.

    data : dict[str, Any]
        Argument ``data``.

    Returns
    -------
    list[tuple[str, str, str | None]]
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
    kind : LibraryKind
        Argument ``kind``.

    data : dict[str, Any]
        Argument ``data``.

    Returns
    -------
    list[tuple[str, dict[str, Any]]]
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
    kind : LibraryKind
        Argument ``kind``.

    data : dict[str, Any]
        Argument ``data``.

    Returns
    -------
    tuple[RegexDiagnostic, ...]
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

    Parameters
    ----------
    pattern : str
        Regular expression to compile.

    sample : str | None, optional
        Sample TAC or text to try.

    path : str, optional
        Path recorded on the diagnostic.

    Returns
    -------
    RegexDiagnostic
        One pattern and classify ok / warn / fail.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (diagnose_regex)
    2
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
    data : dict[str, Any]
        Argument ``data``.

    Returns
    -------
    str | None
        Return value.
    """
    blob = yaml.safe_dump(data, sort_keys=False)
    if _URI_OR_SECRET.search(blob):
        return "Dissemination YAML must not include credentials or destination URIs"
    return None
