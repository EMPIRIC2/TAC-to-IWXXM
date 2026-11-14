"""Split part body (exec'd into package namespace)."""

from __future__ import annotations


def _sm_float_to_ft(sm: float) -> int:
    """
    Internal helper ``_sm_float_to_ft``.

    Parameters
    ----------
    sm : float
        Argument ``sm``.

    Returns
    -------
    int
        Return value.
    """
    return round(sm * 5280.0)
