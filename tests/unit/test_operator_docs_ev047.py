"""TC-EV047-009 / TC-EV047-010 — operator one-pager + handbook content gates."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
ONE_PAGER = ROOT / "docs" / "guides" / "operator-one-pager.md"
HANDBOOK = ROOT / "docs" / "guides" / "operator-handbook.md"
README = ROOT / "README.md"


@pytest.mark.unit
def test_operator_one_pager_exists_and_covers_flow() -> None:
    text = ONE_PAGER.read_text(encoding="utf-8")
    assert "Convert" in text or "convert" in text
    assert "Validate" in text or "validate" in text
    assert "Download" in text or "download" in text
    assert "IWXXM version" in text or "version" in text.lower()
    assert "soft preview" in text.lower()
    assert "[Corpus:" not in text
    assert "ADR-" not in text
    assert "EV-0" not in text
    assert "operator-handbook.md" in text


@pytest.mark.unit
def test_operator_handbook_required_sections() -> None:
    text = HANDBOOK.read_text(encoding="utf-8")
    lower = text.lower()
    assert "login" in lower
    assert "convert" in lower and "validate" in lower
    assert "work history" in lower or "history" in lower
    assert "dissemination" in lower
    assert "troubleshooting" in lower
    assert "do not rely on manual" in lower or "manual updates alone" in lower
    assert "ingest" in lower
    assert "[Corpus:" not in text
    assert "operator-one-pager.md" in text


@pytest.mark.unit
def test_readme_quick_start_links_operator_docs() -> None:
    text = README.read_text(encoding="utf-8")
    assert "docs/guides/operator-one-pager.md" in text
    assert "docs/guides/operator-handbook.md" in text
