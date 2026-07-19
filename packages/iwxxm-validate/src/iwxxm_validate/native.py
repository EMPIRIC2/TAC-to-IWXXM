"""Optional PyO3 extension loader (F13 / E10-36; mirrors tac2iwxxm ADR-017).

The ``iwxxm_validate._rust`` module is built by maturin. Pure-Python lxml paths keep
working when the extension is absent (local without rustc); CI rust job requires it.
"""

from __future__ import annotations

from typing import Any


def rust_available() -> bool:
    """Return True when the compiled ``iwxxm_validate._rust`` extension imports."""
    try:
        from iwxxm_validate import _rust  # type: ignore[attr-defined]
    except ImportError:
        return False
    return _rust is not None  # pragma: no cover


def rust_module() -> Any | None:
    """
    Return the loaded ``_rust`` module, or ``None`` if unavailable.

    Returns
    -------
    Any | None
        Extension module or ``None``.
    """
    try:
        from iwxxm_validate import _rust  # type: ignore[attr-defined]
    except ImportError:
        return None
    return _rust  # type: ignore[no-any-return]  # pragma: no cover
