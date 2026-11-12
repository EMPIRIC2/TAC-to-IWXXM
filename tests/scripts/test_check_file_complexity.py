"""Unit tests for scripts/ci/check_file_complexity.py."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from tests.scripts.conftest import load_script


@pytest.fixture
def complexity() -> Any:
    """Load the complexity checker module under test."""
    return load_script(
        "ci/check_file_complexity.py", "check_file_complexity_under_test"
    )


@pytest.mark.unit
def test_main_missing_config(
    complexity: Any,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Missing ruff-complexity.toml exits 2 with a clear error."""
    monkeypatch.setattr(complexity, "ROOT", tmp_path)
    monkeypatch.setattr(complexity, "CONFIG", tmp_path / "missing.toml")
    assert complexity.main() == 2
    assert "missing" in capsys.readouterr().err


@pytest.mark.unit
def test_main_invokes_ruff(
    complexity: Any,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """When config exists, main shells out to ``uv run ruff check``."""
    cfg = tmp_path / "ruff-complexity.toml"
    cfg.write_text('[lint]\nselect = ["C901"]\n', encoding="utf-8")
    monkeypatch.setattr(complexity, "ROOT", tmp_path)
    monkeypatch.setattr(complexity, "CONFIG", cfg)

    calls: list[tuple[list[str], Path]] = []

    def _call(cmd: list[str], cwd: Path | None = None) -> int:
        calls.append((list(cmd), cwd or Path(".")))
        return 0

    monkeypatch.setattr(complexity.subprocess, "call", _call)
    assert complexity.main() == 0
    assert len(calls) == 1
    cmd, cwd = calls[0]
    assert cmd[:4] == ["uv", "run", "ruff", "check"]
    assert str(cfg) in cmd
    assert cwd == tmp_path
    assert "uv run ruff check" in capsys.readouterr().out


@pytest.mark.unit
def test_main_propagates_ruff_exit(
    complexity: Any,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Non-zero ruff exit codes are returned unchanged."""
    cfg = tmp_path / "ruff-complexity.toml"
    cfg.write_text("[lint]\n", encoding="utf-8")
    monkeypatch.setattr(complexity, "ROOT", tmp_path)
    monkeypatch.setattr(complexity, "CONFIG", cfg)
    monkeypatch.setattr(complexity.subprocess, "call", lambda *_a, **_k: 7)
    assert complexity.main() == 7
