"""TC-EVPYL-MINE — Dissemination + Decoding catalogs (T-B3)."""

from __future__ import annotations

from pathlib import Path

import pytest
from tac2iwxxm.dissemination_decoding_catalogs import (
    load_decoding_library_entries,
    load_dissemination_transforms,
)
from tac2iwxxm.library_assets import get_first_party_library_asset

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_tc_evpyl_mine_020_dissemination_transforms() -> None:
    catalog = load_dissemination_transforms()
    ids = {t["id"] for t in catalog["transforms"]}
    assert ids == {"envelope", "topic_filename", "bulletin_rewrap", "checksum"}


def test_tc_evpyl_mine_021_decoding_entries_from_glossary() -> None:
    catalog = load_decoding_library_entries()
    assert len(catalog["entries"]) >= 10
    assert all("token" in e and "explanation" in e for e in catalog["entries"])


def test_tc_evpyl_mine_022_library_seeds() -> None:
    dissem = get_first_party_library_asset("LIB.DISSEMINATION.ICAO_2025")
    decode = get_first_party_library_asset("LIB.DECODING.ICAO_2025")
    assert dissem is not None
    assert decode is not None
    assert len(dissem.body["transforms"]) == 4
    assert len(decode.body["entries"]) >= 10


def test_tc_evpyl_mine_023_dissem_decode_check_clean() -> None:
    import subprocess
    import sys

    script = REPO_ROOT / "scripts" / "iwxxm" / "mine_dissemination_decoding_catalogs.py"
    result = subprocess.run(
        [sys.executable, str(script), "--check"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_dissem_decode_loaders_reject_bad(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from tac2iwxxm import dissemination_decoding_catalogs as mod

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
    mod.load_dissemination_transforms.cache_clear()
    with pytest.raises(ValueError, match="not a mapping"):
        mod.load_dissemination_transforms()
    mod.load_dissemination_transforms.cache_clear()

    monkeypatch.setattr(mod.resources, "files", lambda _pkg: _FakeFiles("schema_version: 1\n"))
    mod.load_dissemination_transforms.cache_clear()
    mod.load_decoding_library_entries.cache_clear()
    with pytest.raises(ValueError, match="missing transforms"):
        mod.load_dissemination_transforms()
    mod.load_dissemination_transforms.cache_clear()
    with pytest.raises(ValueError, match="missing entries"):
        mod.load_decoding_library_entries()
    mod.load_decoding_library_entries.cache_clear()
