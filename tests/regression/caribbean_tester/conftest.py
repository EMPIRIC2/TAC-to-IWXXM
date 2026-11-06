"""Helpers for Caribbean tester regression. [Corpus: tests]"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIX = ROOT / "fixtures"
RAW = ROOT / "raw"

_PRODUCT = re.compile(r"\b(METAR|SPECI|TAF|SIGMET|AIRMET)\b", re.I)
_GTS = re.compile(r"^(SA|SP|FC|FT|WS|WA|WV)[A-Z0-9]{2}", re.I)


def load_jsonl(name: str) -> list[dict[str, object]]:
    path = FIX / name
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def strip_gts(tac: str) -> str:
    lines = tac.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    if len(lines) >= 2 and _GTS.match(lines[0].strip()):
        rest = "\n".join(lines[1:]).strip()
        if rest:
            return rest
    return tac.strip()


def guess_product(tac: str) -> str:
    match = _PRODUCT.search(tac)
    return match.group(1).upper() if match else "METAR"


def is_xml_payload(text: str) -> bool:
    stripped = text.lstrip()
    return stripped.startswith("<?xml") or stripped.startswith("<")
