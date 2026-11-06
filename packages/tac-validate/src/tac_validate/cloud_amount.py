"""Decide when a cloud group has a known base and a convective type."""

from __future__ import annotations

_CLOUD_AMOUNTS = frozenset({"FEW", "SCT", "BKN", "OVC"})


def known_base_convective_cloud(token: str) -> bool:
    """
    Return whether ``token`` has a three-digit base and CB or TCU.

    An unknown base (``///``) with CB or TCU is a valid cloud group and
    returns ``False``.

    Parameters
    ----------
    token : str
        One uppercased cloud group, such as ``FEW020CB`` or ``FEW///CB``.

    Returns
    -------
    bool
        ``True`` only when the amount, a three-digit base, and ``CB`` or
        ``TCU`` are all present.

    Examples
    --------
    >>> known_base_convective_cloud("FEW020CB")
    True
    >>> known_base_convective_cloud("FEW///CB")
    False
    >>> known_base_convective_cloud("BKN///TCU")
    False
    """
    if token[:3] not in _CLOUD_AMOUNTS:
        return False
    if token.endswith("TCU"):
        base = token[3 : len(token) - 3]
    elif token.endswith("CB"):
        base = token[3 : len(token) - 2]
    else:
        return False
    return len(base) == 3 and base.isdigit()
