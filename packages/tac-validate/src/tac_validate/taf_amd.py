"""Tell a real TAF amendment from the ``AMD NOT SKED`` trailer."""

from __future__ import annotations


def amd_modifier_present(tokens: list[str]) -> bool:
    """
    Return whether ``tokens`` contain an amendment marker.

    Parameters
    ----------
    tokens : list[str]
        Uppercase TAC tokens with the end-of-message mark already removed.

    Returns
    -------
    bool
        True when ``AMD`` appears and is not the ``AMD NOT SKED`` trailer.

    Examples
    --------
    >>> amd_modifier_present(["TAF", "AMD", "MKJP"])
    True
    >>> amd_modifier_present(["AMD", "NOT", "SKED"])
    False
    """
    for index, token in enumerate(tokens):
        if token != "AMD":
            continue
        trailer = index + 2 < len(tokens) and tokens[index + 1] == "NOT" and tokens[index + 2] == "SKED"
        if trailer:
            continue
        return True
    return False
