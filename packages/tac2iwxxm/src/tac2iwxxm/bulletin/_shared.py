"""WMO AHL bulletin helpers and splitter (F6.bulletin / TC-EV029-003).

Shared parse / format / ``T1T2`` map / BBB→``reportStatus`` / IWXXM filename
helpers live here so ``packages/dissemination`` can import them without
duplicating AHL rules (EV-029 / E29-T2).
"""

from __future__ import annotations

# Imports/constants consumed by exec'd part bodies.
import re
from datetime import UTC, datetime
from typing import Literal

from tac2iwxxm.models import AhlParts, BulletinMeta, BulletinSplit

ReportStatus = Literal["NORMAL", "AMENDMENT", "CORRECTION"]


class BulletinSplitError(ValueError):
    """
    Bulletin or AHL could not be parsed.

    Parameters
    ----------
    code : str
        Machine-readable error (``bulletin_split_failed``, ``empty_bulletin``,
        or ``invalid_bbb``).

    message : str
        Human-readable description.
    """

    def __init__(self, code: str, message: str) -> None:
        """
        Store ``code`` and ``message``.

        Parameters
        ----------
        code : str
            Machine-readable error code.

        message : str
            Human-readable message.
        """
        self.code = code
        self.message = message
        super().__init__(message)


_TAC_TO_IWXXM: dict[str, str] = {
    "SA": "LA",
    "SP": "LP",
    "FC": "LC",
    "FT": "LT",
    "FK": "LK",
    "FN": "LN",
    "FV": "LU",
    "WA": "LW",
    "WS": "LS",
    "WC": "LY",
    "WV": "LV",
    "WM": "LM",  # VONA (F32 / G-VONA-4)
}

_AHL_LINE = re.compile(
    r"^(?P<tt>[A-Z]{2})(?P<aa>[A-Z]{2})(?P<ii>\d{2})\s+"
    r"(?P<cccc>[A-Z]{4})\s+(?P<yygggg>\d{6})"
    r"(?:\s+(?P<bbb>[A-Z]{1,3}))?\s*$"
)

_BBB_VALID = re.compile(r"^(?:AA|CC|RR)[A-X]$")

_TAC_METAR_SPECI = re.compile(
    r"^(?:METAR|SPECI)\s+(?:COR\s+)?[A-Z][A-Z0-9]{3}\s.+?=",
    re.MULTILINE | re.DOTALL | re.IGNORECASE,
)

_TAC_TAF = re.compile(
    r"^TAF\s+(?:(?:AMD|COR)\s+)?[A-Z][A-Z0-9]{3}\s.+?=",
    re.MULTILINE | re.DOTALL,
)

_TAC_SEQUENCE = r"(?:[A-Z]+\s+\d+|[A-Z]?\d+)"

_SIGMET_BODY_STOP = (
    r"(?="
    r"=\s*$"
    r"|(?:^|\n)(?:WS|WV|WC)[A-Z]{2}\d{2}\s+[A-Z]{4}\s+\d{6}\b"
    r"|(?:^|\n)(?:[A-Z]{4}\s+)+SIGMET\s+"
    r"|(?:^|\n)CONVECTIVE\s+SIGMET\s+"
    r"|\Z"
    r")"
)

_GLUED_SIGMET_AHL = re.compile(
    r"(?<=\S)(?=(?:WS|WV|WC)[A-Z]{2}\d{2}\s+[A-Z]{4}\s+\d{6}\b)",
)

_TAC_SIGMET = re.compile(
    r"^(?:[A-Z]{4}\s+)+SIGMET\s+" + _TAC_SEQUENCE + r"\s+VALID\s+\d{6}/\d{6}\s+[A-Z]{4}\s*-?\s*.+?" + _SIGMET_BODY_STOP,
    re.MULTILINE | re.DOTALL | re.IGNORECASE,
)

_TAC_CONVECTIVE_SIGMET = re.compile(
    r"^(?:(?:[A-Z]{4}\s+WST\s+\d{6}|SIG(?!MET)[A-Z0-9]*)\s*\n+)*"
    r"CONVECTIVE\s+SIGMET\s+\S+\s+"
    r"VALID\s+UNTIL\s+\d{4,6}Z\b"
    r".+?" + _SIGMET_BODY_STOP,
    re.MULTILINE | re.DOTALL | re.IGNORECASE,
)

_TAC_AIRMET = re.compile(
    r"^[A-Z]{4}\s+AIRMET\s+" + _TAC_SEQUENCE + r"\s+VALID\s+\d{6}/\d{6}\s+[A-Z]{4}-\s*.+?(?:=\s*$|\Z)",
    re.MULTILINE | re.DOTALL | re.IGNORECASE,
)

_TAC_VAA = re.compile(
    r"^VA\s+ADVISORY\b.+?(?:=\s*$|\Z)",
    re.MULTILINE | re.DOTALL | re.IGNORECASE,
)

_TAC_TCA = re.compile(
    r"^TC\s+ADVISORY\b.+?(?:=\s*$|\Z)",
    re.MULTILINE | re.DOTALL | re.IGNORECASE,
)

_TAC_SWXA = re.compile(
    r"^SWX\s+ADVISORY\b.+?(?:=\s*$|\Z)",
    re.MULTILINE | re.DOTALL | re.IGNORECASE,
)

_TAC_VONA = re.compile(
    r"^VONA\b.+?(?:=\s*$|\Z)",
    re.MULTILINE | re.DOTALL | re.IGNORECASE,
)

_PRODUCT_TT: dict[str, frozenset[str]] = {
    "METAR": frozenset({"SA"}),
    "SPECI": frozenset({"SP"}),
    "TAF": frozenset({"FC", "FT"}),
    # WS general + WV volcanic ash + WC tropical cyclone (content-selected root;
    # E19-13 / EV-029 M5-M7).
    "SIGMET": frozenset({"WS", "WV", "WC"}),
    "AIRMET": frozenset({"WA"}),
    "VAA": frozenset({"FV"}),
    "TCA": frozenset({"FK"}),
    "SWXA": frozenset({"FN"}),
    "VONA": frozenset({"WM"}),
}

_PRODUCT_BODY_RE: dict[str, re.Pattern[str]] = {
    "METAR": _TAC_METAR_SPECI,
    "SPECI": _TAC_METAR_SPECI,
    "TAF": _TAC_TAF,
    "SIGMET": _TAC_SIGMET,
    "AIRMET": _TAC_AIRMET,
    "VAA": _TAC_VAA,
    "TCA": _TAC_TCA,
    "SWXA": _TAC_SWXA,
    "VONA": _TAC_VONA,
}
