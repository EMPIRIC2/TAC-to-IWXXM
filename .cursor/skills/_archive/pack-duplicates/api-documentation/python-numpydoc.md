# Python — NumPy Docstring Reference

Follow [numpydoc](https://numpydoc.readthedocs.io/en/latest/format.html) conventions. Compatible with Sphinx + numpydoc if API docs are generated later.

## Module

```python
"""
Short module title or purpose sentence.

Longer description when the module coordinates multiple concerns. Mention
primary entry points and how this module fits in the stack (e.g. backend
config, GIFTs conversion pipeline).

Notes
-----
Optional cross-references to ``docs/spec.md`` sections or related modules.
"""
```

## Class

```python
class VersionDeprecatedError(ValueError):
    """Raised when attempting to use a deprecated IWXXM version."""

class MetarConverter:
    """
    Convert METAR TAC input to IWXXM XML for a selected schema version.

    Parameters
    ----------
    default_version : str, optional
        IWXXM release line when the caller omits a version, by default ``"2025-2"``.

    Attributes
    ----------
    default_version : str
        Active default IWXXM version string.

    Raises
    ------
    VersionDeprecatedError
        If ``default_version`` is deprecated at construction time.
    """
```

## Function

```python
def get_version_config(version: str) -> dict[str, Any]:
    """
    Return configuration for a specific IWXXM version.

    Parameters
    ----------
    version : str
        IWXXM version string (e.g. ``"2025-2"``, ``"2023-1"``).

    Returns
    -------
    dict[str, Any]
        Version metadata including namespace URIs and schema paths.

    Raises
    ------
    VersionDeprecatedError
        If ``version`` is deprecated.
    ValueError
        If ``version`` is not supported.

    Examples
    --------
    >>> cfg = get_version_config("2025-2")
    >>> "namespace" in cfg
    True
    """
```

## Optional sections

| Section | Use when |
|---------|----------|
| `Notes` | Non-obvious behavior, performance, threading |
| `See Also` | Related functions/modules |
| `References` | External specs (WMO, ICAO) |
| `Examples` | Non-trivial usage or doctest-worthy behavior |

## Formatting rules

1. Summary line is **imperative mood** ("Return …", "Convert …", "Raise …").
2. Blank line after summary before sections.
3. Section title on its own line; underline of `-` characters **same length** as title.
4. Parameter format: `name : type` then indented description on the next line.
5. Optional parameters: `name : type, optional` and mention default in description.
6. Multiple types: `name : type1 or type2`.
7. No redundant type info in summary when the signature is typed.

## One-line docstrings

Acceptable for obvious helpers:

```python
def _detect_project_root() -> Path:
    """Detect project root across local, devcontainer, and deployment layouts."""
```

## Migrating existing Google-style docs

Replace:

```python
    Args:
        version: IWXXM version string

    Returns:
        Configuration dictionary
```

With NumPy:

```python
    Parameters
    ----------
    version : str
        IWXXM version string.

    Returns
    -------
    dict
        Configuration dictionary for the version.
```

## Private symbols

- `_leading_underscore`: one-line docstring or omit if trivial.
- `__dunder__`: document only when behavior is non-standard.
