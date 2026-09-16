"""TC-EVPYL-MINE — TAC + IWXXM validation catalogs (T-B2)."""

from __future__ import annotations

from pathlib import Path

import pytest
from tac2iwxxm.library_assets import get_first_party_library_asset
from tac2iwxxm.validation_library_catalogs import (
    load_iwxxm_validation_asserts,
    load_tac_validation_rules,
)

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_tc_evpyl_mine_010_tac_rules_nonempty() -> None:
    catalog = load_tac_validation_rules()
    assert len(catalog["rules"]) >= 50
    codes = {r["code"] for r in catalog["rules"]}
    assert "UNKNOWN_PRODUCT" in codes


def test_tc_evpyl_mine_011_iwxxm_asserts_nonempty() -> None:
    catalog = load_iwxxm_validation_asserts()
    assert catalog["iwxxm_version"] == "2025-2"
    assert len(catalog["asserts"]) >= 50
    assert all(a.get("enabled_default") is True for a in catalog["asserts"])


def test_tc_evpyl_mine_012_library_seeds_include_rules() -> None:
    tac = get_first_party_library_asset("LIB.TAC_VALIDATION.ICAO_2025")
    iwx = get_first_party_library_asset("LIB.IWXXM_VALIDATION.ICAO_2025")
    assert tac is not None
    assert iwx is not None
    assert len(tac.body["rules"]) >= 50
    assert len(iwx.body["rules"]) >= 50


def test_tc_evpyl_mine_013_validation_mine_check_clean() -> None:
    import subprocess
    import sys

    script = REPO_ROOT / "scripts" / "iwxxm" / "mine_validation_library_catalogs.py"
    result = subprocess.run(
        [sys.executable, str(script), "--check"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_validation_loaders_reject_bad_yaml(monkeypatch: pytest.MonkeyPatch) -> None:
    from tac2iwxxm import validation_library_catalogs as mod

    class _FakePath:
        def __init__(self, text: str) -> None:
            self._text = text

        def read_text(self, encoding: str = "utf-8") -> str:
            return self._text

    class _FakeFiles:
        def __init__(self, text: str) -> None:
            self._text = text

        def joinpath(self, _name: str) -> _FakePath:
            return _FakePath(self._text)

    monkeypatch.setattr(mod.resources, "files", lambda _pkg: _FakeFiles("[]\n"))
    mod.load_tac_validation_rules.cache_clear()
    mod.load_iwxxm_validation_asserts.cache_clear()
    with pytest.raises(ValueError, match="not a mapping"):
        mod.load_tac_validation_rules()
    mod.load_tac_validation_rules.cache_clear()
    mod.load_iwxxm_validation_asserts.cache_clear()

    monkeypatch.setattr(mod.resources, "files", lambda _pkg: _FakeFiles("schema_version: 1\n"))
    with pytest.raises(ValueError, match="missing rules"):
        mod.load_tac_validation_rules()
    mod.load_tac_validation_rules.cache_clear()
    with pytest.raises(ValueError, match="missing asserts"):
        mod.load_iwxxm_validation_asserts()
    mod.load_iwxxm_validation_asserts.cache_clear()
