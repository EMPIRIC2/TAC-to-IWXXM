"""Split part body (exec'd into package namespace)."""

from __future__ import annotations


def validate_library_yaml(
    raw: str,
    *,
    expected_kind: LibraryKind | None = None,
    lifecycle: LibraryLifecycle = "draft",
) -> LibraryYamlReport:
    """
    Parse YAML, enforce kind/name, and collect regex diagnostics.

    Parameters
    ----------
    raw : str
        Library YAML mapping.

    expected_kind : LibraryKind | None, optional
        Expected library kind.

    lifecycle : LibraryLifecycle, optional
        Library lifecycle value.

    Returns
    -------
    LibraryYamlReport
        YAML, enforce kind/name, and collect regex diagnostics.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (validate_library_yaml)
    2
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
