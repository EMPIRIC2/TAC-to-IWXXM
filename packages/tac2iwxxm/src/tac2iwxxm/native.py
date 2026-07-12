"""Optional PyO3 extension loader (ADR-017 / T4.3–T4.5).

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
        from tac2iwxxm import _rust  # type: ignore[attr-defined]
    except ImportError:
        return None
    return _rust  # type: ignore[no-any-return]  # pragma: no cover


def scan_metar_tokens(tac: str) -> list[str]:
    """
    Tokenize METAR/SPECI TAC via the PyO3 hotspot (T4.5).

    Parameters
    ----------
    tac :
        METAR or SPECI TAC text.

    Returns
    -------
    list[str]
        Ordered TAC tokens.

    Raises
    ------
    NotImplementedError
        When the native extension is missing or hotspot is not yet linked.
    """
    mod = rust_module()
    if mod is None or not hasattr(mod, "scan_metar_tokens"):
        raise NotImplementedError(
            "PyO3 scan_metar_tokens hotspot not available (build with maturin; implement in T4.5)"
        )
    result = mod.scan_metar_tokens(tac)
    return list(result)
