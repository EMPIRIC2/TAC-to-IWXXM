"""Plain language for a few remarks kept out of the international report."""

from __future__ import annotations

import re

_VIS_KM = re.compile(r"^VIS(?P<km>[1-9]\d?)KM$")
_VCSH_DIR = re.compile(r"^VCSH(?:-(?P<dir>N|NE|E|SE|S|SW|W|NW))?$")
_DIR_NAME = {
    "N": "North",
    "NE": "Northeast",
    "E": "East",
    "SE": "Southeast",
    "S": "South",
    "SW": "Southwest",
    "W": "West",
    "NW": "Northwest",
}


def explain_remark_plain(token: str) -> str | None:
    """
    Explain vicinity showers or a visibility of 1 to 99 kilometres.

    Parameters
    ----------
    token : str
        One uppercased group from after ``RMK``.

    Returns
    -------
    str | None
        Plain language, or ``None`` when this helper does not know the token.

    Examples
    --------
    >>> explain_remark_plain("VCSH")
    'Showers in the vicinity'
    >>> explain_remark_plain("VCSH-N")
    'Showers in the vicinity, North'
    >>> explain_remark_plain("VIS1KM")
    'Visibility 1 kilometre'
    >>> explain_remark_plain("VIS16KM")
    'Visibility 16 kilometres'
    >>> explain_remark_plain("VIS100KM") is None
    True
    """
    vcsh = _VCSH_DIR.fullmatch(token)
    if vcsh is not None:
        direction = vcsh.group("dir")
        if direction:
            return f"Showers in the vicinity, {_DIR_NAME[direction]}"
        return "Showers in the vicinity"
    match = _VIS_KM.fullmatch(token)
    if match is None:
        return None
    kilometres = int(match["km"])
    if kilometres == 1:
        return "Visibility 1 kilometre"
    return f"Visibility {kilometres} kilometres"
