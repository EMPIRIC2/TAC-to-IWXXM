"""
Helper utility for extracting ICAO airport codes from TAC messages.
"""

import re

ICAO_PATTERN = re.compile(
    r"(?:METAR|SPECI|TAF)(?:\s+(?:COR|AMD))?\s+([A-Z0-9]{4})(?=\s|$)",
    re.IGNORECASE,
)


def extract_airport_code(tac_message: str) -> str | None:
    """
    Extract ICAO aerodrome designator from METAR, SPECI, or TAF TAC.

    Parameters
    ----------
    tac_message : str
        TAC format METAR, SPECI, or TAF message.

    Returns
    -------
    str | None
        4-character ICAO designator, or None when not found.

    Examples
    --------
    >>> extract_airport_code("METAR KJFK 131051Z 18012KT 10SM FEW250")
    'KJFK'
    >>> extract_airport_code("SPECI EGLL 111520Z 27015KT 9999 BKN025")
    'EGLL'
    >>> extract_airport_code("TAF ABCD 010000Z 0100/0206 00000KT CAVOK")
    'ABCD'
    """
    if not tac_message or not tac_message.strip():
        return None

    match = ICAO_PATTERN.search(tac_message)
    if match:
        return match.group(1).upper()

    return None
