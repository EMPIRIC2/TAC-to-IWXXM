"""Accept a recent-weather code, including bare showers."""

from __future__ import annotations

from re import Pattern


def accept_recent_code(code: str, *, weather_token: Pattern[str]) -> str | None:
    """
    Return ``code`` when it is recent weather, including bare ``SH``.

    Parameters
    ----------
    code : str
        The token after the ``RE`` prefix.

    weather_token : Pattern[str]
        Present-weather pattern. A match means the code is a complete weather group.

    Returns
    -------
    str | None
        The same code, or ``None`` when it is not recent weather. ``SH`` stays ``SH``.

    Examples
    --------
    >>> import re
    >>> accept_recent_code("SH", weather_token=re.compile("SHRA"))
    'SH'
    >>> accept_recent_code("FOO", weather_token=re.compile("SHRA")) is None
    True
    """
    if code == "SH" or weather_token.fullmatch(code):
        return code
    return None
