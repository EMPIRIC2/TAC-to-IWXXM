"""Optional PyO3 extension loader (ADR-017 / T4.3).

The ``tac2iwxxm._rust`` module is built by maturin. Pure-Python paths keep working when
the extension is absent (local without rustc); CI rust job requires it.
"""

from __future__ import annotations

from typing import Any


def rust_available() -> bool:
    """Return True when the compiled ``tac2iwxxm._rust`` extension imports."""
    try:
        from tac2iwxxm import _rust  # type: ignore[attr-defined]
    except ImportError:
        return False
    return _rust is not None


def rust_module() -> Any | None:
    """
    Return the loaded ``_rust`` module, or ``None`` if unavailable.

    Returns
    -------
    Any | None
        Extension module or ``None``.
    """
    try:
        from tac2iwxxm import _rust  # type: ignore[attr-defined]
    except ImportError:
        return None
    return _rust
