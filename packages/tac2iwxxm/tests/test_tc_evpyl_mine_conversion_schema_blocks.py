"""TC-EVPYL-MINE — Conversion IWXXM schema blocks catalog (T-B1)."""

from __future__ import annotations

from pathlib import Path

import pytest
from tac2iwxxm.conversion_schema_blocks import (
    load_conversion_schema_blocks,
    schema_blocks_for_national_line,
)
from tac2iwxxm.library_assets import get_first_party_library_asset

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_tc_evpyl_mine_001_catalog_has_wmo_and_nationals() -> None:
    """Catalog includes WMO + US + CA authorities with non-empty cards."""
    catalog = load_conversion_schema_blocks()
    authorities = {b["authority"] for b in catalog["blocks"]}
    assert {"wmo", "us", "ca"} <= authorities
    assert catalog["iwxxm_version"] == "2025-2"
    assert all(len(b["cards"]) > 0 for b in catalog["blocks"])


def test_tc_evpyl_mine_002_known_observation_cards() -> None:
    """METAR observation cards include surface wind / visibility / RVR / cloud."""
    blocks = schema_blocks_for_national_line("ICAO_2025")
    card_ids = {c["id"] for b in blocks for c in b["cards"]}
    assert "iwxxm:AerodromeSurfaceWind" in card_ids
    assert "iwxxm:AerodromeHorizontalVisibility" in card_ids
    assert "iwxxm:AerodromeRunwayVisualRange" in card_ids
    assert "iwxxm:AerodromeCloud" in card_ids


def test_tc_evpyl_mine_003_national_filter() -> None:
    """US/CA blocks attach only to matching national lines; WMO uses *."""
    icao = schema_blocks_for_national_line("ICAO_2025")
    us = schema_blocks_for_national_line("US_FAA_NWS")
    assert all(b["authority"] == "wmo" for b in icao)
    assert any(b["authority"] == "us" for b in us)
    assert any(b["authority"] == "wmo" for b in us)
    ca = schema_blocks_for_national_line("CA_ECCC")
    assert any(b["authority"] == "ca" for b in ca)


def test_tc_evpyl_mine_004_conversion_library_seed_includes_blocks() -> None:
    """First-party conversion library body embeds mined schema_blocks."""
    asset = get_first_party_library_asset("LIB.CONVERSION.ICAO_2025")
    assert asset is not None
    blocks = asset.body.get("schema_blocks")
    assert isinstance(blocks, list)
    assert len(blocks) >= 1


def test_tc_evpyl_mine_005_mine_script_check_clean() -> None:
    """Committed YAML matches a fresh mine (--check)."""
    import subprocess
    import sys

    script = REPO_ROOT / "scripts" / "iwxxm" / "mine_conversion_schema_blocks.py"
    result = subprocess.run(
        [sys.executable, str(script), "--check"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_load_rejects_invalid_catalog(monkeypatch: pytest.MonkeyPatch) -> None:
    """Corrupt package data raises ValueError."""
    from tac2iwxxm import conversion_schema_blocks as mod

    class _FakePath:
        def read_text(self, encoding: str = "utf-8") -> str:
            return "schema_version: 1\n"

    class _FakeFiles:
        def joinpath(self, _name: str) -> _FakePath:
            return _FakePath()

    monkeypatch.setattr(mod.resources, "files", lambda _pkg: _FakeFiles())
    mod.load_conversion_schema_blocks.cache_clear()
    with pytest.raises(ValueError, match="missing blocks"):
        mod.load_conversion_schema_blocks()
    mod.load_conversion_schema_blocks.cache_clear()


def test_schema_blocks_skips_malformed_entries(monkeypatch: pytest.MonkeyPatch) -> None:
    """Non-list blocks and bad entries are ignored."""
    from tac2iwxxm import conversion_schema_blocks as mod

    monkeypatch.setattr(
        mod,
        "load_conversion_schema_blocks",
        lambda: {"blocks": "nope"},
    )
    assert mod.schema_blocks_for_national_line("ICAO_2025") == []

    monkeypatch.setattr(
        mod,
        "load_conversion_schema_blocks",
        lambda: {
            "blocks": [
                "skip-me",
                {"id": "bad-lines", "national_lines": "x"},
                {"id": "ok", "national_lines": ["*"], "cards": []},
            ]
        },
    )
    blocks = mod.schema_blocks_for_national_line("ICAO_2025")
    assert len(blocks) == 1
    assert blocks[0]["id"] == "ok"
