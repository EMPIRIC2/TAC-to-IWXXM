"""#1438 — the validate-IWXXM fixture must produce decode rows.

[Corpus: tests] [Corpus: product]

The backend unit job runs this on every pull request. The UJ-064 browser
spec is also on the E2E smoke list. E2E Full stays limited to promote.
"""

from __future__ import annotations

import re
from pathlib import Path

from src.utilities.iwxxm_readable_decode import readable_decode_from_iwxxm

REPO = Path(__file__).resolve().parents[4]
SPEC = REPO / "apps" / "e2e" / "tc-ev061-uj064-068.e2e.spec.ts"
_FIXTURE = re.compile(r"const DECODE_ROWS_IWXXM = `([^`]*)`", re.S)
_EMPTY_SHELL = """<?xml version="1.0" encoding="UTF-8"?>
<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2"></iwxxm:METAR>
"""


def _uj064_block(text: str) -> str:
    marker = "EV-061 T2 — UJ-064"
    return text.split(marker, 1)[1].split("test.describe(", 1)[0]


def test_validate_fixture_without_fields_has_no_decode_rows() -> None:
    decoded = readable_decode_from_iwxxm(_EMPTY_SHELL)
    assert decoded.segments == []


def test_committed_validate_fixture_has_decode_rows() -> None:
    text = SPEC.read_text(encoding="utf-8")
    match = _FIXTURE.search(text)
    assert match is not None
    decoded = readable_decode_from_iwxxm(match.group(1))
    explanations = {segment.explanation for segment in decoded.segments}
    assert {"Aerodrome", "Mean wind direction", "Air temperature"} <= explanations
    assert all("<?xml" not in segment.code for segment in decoded.segments)
    block = _uj064_block(text)
    assert "if (await segments.count())" not in block
    assert "getByTestId('decode-segments')" in block
    assert ".toBeVisible()" in block
    smoke = (REPO / "Makefile").read_text(encoding="utf-8")
    recipe = smoke.split("test-e2e-playwright-smoke:", 1)[1].split("\ntest-e2e-t2-product:", 1)[0]
    assert "tc-ev061-uj064-068.e2e.spec.ts" in recipe
    assert "required decode rows" in recipe
