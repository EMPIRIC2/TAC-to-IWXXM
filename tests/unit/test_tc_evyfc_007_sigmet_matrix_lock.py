"""TC-EVYFC-007 — M4 SIGMET matrix row lock (#1230)."""

from __future__ import annotations

import re
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_MATRIX = _REPO / "docs" / "domain" / "overlays" / "product-engine-matrix.md"

_SIGMET_EXPECTED = ("full", "full", "full", "full", "full", "full")


def _parse_row(product: str, text: str) -> tuple[str, ...]:
    pattern = rf"^\|\s*{re.escape(product)}\s\|(.+)\|\s*$"
    for line in text.splitlines():
        match = re.match(pattern, line.strip())
        if match is None:
            continue
        cells = [c.strip() for c in match.group(1).split("|")]
        normalized: list[str] = []
        for cell in cells:
            token = cell.split()[0].lower() if cell.strip() else ""
            if token.startswith("partial"):
                normalized.append("partial")
            elif token.startswith("full"):
                normalized.append("full")
            elif token.startswith("stub"):
                normalized.append("stub")
            else:
                normalized.append(token)
        return tuple(normalized)
    msg = f"missing matrix row for {product}"
    raise AssertionError(msg)


def test_tc_evyfc_007_sigmet_row_lock() -> None:
    text = _MATRIX.read_text(encoding="utf-8")
    assert "TC-EVYFC-007" in text
    assert "hatch_sigmet" in text
    assert "sigmet-core" in text
    got = _parse_row("SIGMET", text)
    assert got == _SIGMET_EXPECTED, f"SIGMET: got {got!r} expected {_SIGMET_EXPECTED!r}"


def test_tc_evyfc_007_sigmet_sots_exist() -> None:
    roots = (
        _REPO
        / "packages"
        / "tac-decoding"
        / "src"
        / "tac_decoding"
        / "data"
        / "packs"
        / "sigmet.yaml",
        _REPO
        / "packages"
        / "tac-decoding"
        / "src"
        / "tac_decoding"
        / "data"
        / "packs"
        / "va_sigmet.yaml",
        _REPO
        / "packages"
        / "tac-decoding"
        / "src"
        / "tac_decoding"
        / "data"
        / "packs"
        / "tc_sigmet.yaml",
        _REPO
        / "packages"
        / "tac-validate"
        / "src"
        / "tac_validate"
        / "data"
        / "policies"
        / "annex3-sigmet-quality.yaml",
        _REPO
        / "packages"
        / "tac-validate"
        / "src"
        / "tac_validate"
        / "data"
        / "detectors"
        / "sigmet-core.yaml",
        _REPO
        / "packages"
        / "tac2iwxxm"
        / "src"
        / "tac2iwxxm"
        / "data"
        / "emit_maps"
        / "annex3-sigmet.yaml",
        _REPO
        / "packages"
        / "tac2iwxxm"
        / "src"
        / "tac2iwxxm"
        / "data"
        / "emit_maps"
        / "iwxxm-us-sigmet.yaml",
    )
    for path in roots:
        assert path.is_file(), path
    policy = (
        _REPO
        / "packages"
        / "tac-validate"
        / "src"
        / "tac_validate"
        / "data"
        / "policies"
        / "annex3-sigmet-quality.yaml"
    ).read_text(encoding="utf-8")
    assert "sigmet-core" in policy
    assert "product: sigmet" in policy
