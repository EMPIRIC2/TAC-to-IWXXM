"""Plain language for a few remarks kept out of the international report."""

from __future__ import annotations

import re

_VIS_KM = re.compile(r"^VIS(?P<km>[1-9]\d?)KM$")


def explain_remark_plain(token: str) -> str | None:
    """
    Explain vicinity showers or a visibility of 1 to 99 kilometres.

    Parameters
    ----------
    token :
        One uppercased group from after ``RMK``.

    Returns
    -------
    str | None
        Plain language, or ``None`` when this helper does not know the token.

    Examples
    --------
    >>> explain_remark_plain("VCSH")
    'Showers in the vicinity'
    >>> explain_remark_plain("VIS1KM")
    'Visibility 1 kilometre'
    >>> explain_remark_plain("VIS16KM")
    'Visibility 16 kilometres'
    >>> explain_remark_plain("VIS100KM") is None
    True
    """
    if token == "VCSH":
        return "Showers in the vicinity"
    match = _VIS_KM.fullmatch(token)
    if match is None:
        return None
    kilometres = int(match["km"])
    if kilometres == 1:
        return "Visibility 1 kilometre"
    return f"Visibility {kilometres} kilometres"
