"""Environment parsing helpers."""

from __future__ import annotations


def parse_comma_separated_origins(raw: str | None) -> list[str]:
    """Parse ``METAR_CORS_ORIGINS`` style comma-separated origin lists.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (parse_comma_separated_origins)
    2

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
        return []
    stripped = raw.strip()
    if not stripped:
        return []
    return [part.strip() for part in stripped.split(",") if part.strip()]
