"""TC-EV047-001..004 - slim husky shape A (lint commit + fast-unit push)."""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def test_tc_ev047_001_pre_commit_lint_only() -> None:
    """Husky pre-commit runs lint/format only - not full pre-commit / medium validate."""
    text = (REPO / ".husky" / "pre-commit").read_text(encoding="utf-8")
    assert "validate-ci-medium" not in text
    assert "uv run pre-commit run\n" not in text
    assert "pre-commit run --all-files" not in text
    assert "make lint-fast" in text
    assert "EV-047" in text or "#833" in text


def test_tc_ev047_002_pre_push_fast_units_only() -> None:
    """Husky pre-push runs fast unit subset - not make ci / Compose integration."""
    text = (REPO / ".husky" / "pre-push").read_text(encoding="utf-8")
    commands = [
        ln.strip() for ln in text.splitlines() if ln.strip().startswith("make ")
    ]
    assert commands == ["make test-unit-fast"]
    assert "test-integration" not in text


def test_tc_ev047_003_makefile_test_unit_fast() -> None:
    makefile = (REPO / "Makefile").read_text(encoding="utf-8")
    assert "test-unit-fast:" in makefile
    assert "test-unit-workspace" in makefile
    assert "test-unit-tac2iwxxm" in makefile


def test_tc_ev047_004_development_docs_shape_a() -> None:
    """DEVELOPMENT.md documents slim husky + opt-in heavy make targets."""
    text = (REPO / "docs" / "ops" / "DEVELOPMENT.md").read_text(encoding="utf-8")
    assert "EV-047" in text or "lint" in text.lower()
    assert "test-unit-fast" in text or "fast unit" in text.lower()
