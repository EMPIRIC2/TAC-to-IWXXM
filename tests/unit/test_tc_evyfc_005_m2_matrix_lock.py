"""TC-EVYFC-005 — M2 METAR/SPECI matrix row lock (#1228)."""

from __future__ import annotations

import re
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_MATRIX = _REPO / "docs" / "domain" / "overlays" / "product-engine-matrix.md"

# product -> engine cells (decode, quality, detectors, iwxxm, pack-IR, emit)
_M2_ROWS: dict[str, tuple[str, str, str, str, str, str]] = {
    "METAR": ("full", "full", "full", "full", "full", "full"),
    "SPECI": ("full", "full", "full", "full", "full", "full"),
}


def _parse_row(product: str, text: str) -> tuple[str, ...]:
    # Match markdown table row: | METAR | a | b | c | d | e | f |
    pattern = rf"^\|\s*{re.escape(product)}\s*\|(.+)\|\s*$"
    for line in text.splitlines():
        match = re.match(pattern, line.strip())
        if match is None:
            continue
        cells = [c.strip() for c in match.group(1).split("|")]
        # last cell may include trailing notes in paren — normalize to first word
        normalized: list[str] = []
        for cell in cells:
            token = cell.split()[0].lower() if cell.strip() else ""
            # "partial (Python plugins)" -> partial
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


def test_tc_evyfc_005_metar_speci_m2_row_lock() -> None:
    text = _MATRIX.read_text(encoding="utf-8")
    assert "TC-EVYFC-005" in text
    assert (
        "enrichment does **not** block decode" in text
        or "enrichment does not block decode" in text.lower()
    )
    assert (
        "do **not** block detectors" in text or "do not block detectors" in text.lower()
    )
    assert "hatch_r3" in text
    assert "emit_maps" in text or "emit map" in text.lower()
    for product, expected in _M2_ROWS.items():
        got = _parse_row(product, text)
        assert got == expected, f"{product}: got {got!r} expected {expected!r}"


def test_tc_evyfc_005_builtin_sots_exist() -> None:
    """Cheap SoT path presence for upgraded METAR/SPECI engines."""
    roots = (
        _REPO
        / "packages"
        / "tac-decoding"
        / "src"
        / "tac_decoding"
        / "data"
        / "packs"
        / "metar.yaml",
        _REPO
        / "packages"
        / "tac-decoding"
        / "src"
        / "tac_decoding"
        / "data"
        / "packs"
        / "speci.yaml",
        _REPO
        / "packages"
        / "tac-validate"
        / "src"
        / "tac_validate"
        / "data"
        / "policies"
        / "annex3-metar-quality.yaml",
        _REPO
        / "packages"
        / "iwxxm-validate"
        / "src"
        / "iwxxm_validate"
        / "data"
        / "policies"
        / "annex3-iwxxm-output.yaml",
        _REPO
        / "packages"
        / "tac2iwxxm"
        / "src"
        / "tac2iwxxm"
        / "data"
        / "emit_maps"
        / "annex3-metar-speci.yaml",
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
        / "annex3-metar-quality.yaml"
    ).read_text(encoding="utf-8")
    assert "metar-speci-r8-modifiers" in policy
    assert "detectors:" in policy
