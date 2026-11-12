"""TC-EV047-009 / TC-EV047-010 - operator one-pager + handbook content gates.

Operator guides under ``docs/guides/`` are local opt-in after EV-repo-docs-cleanup
(#1597). Skip content gates when those files are not checked out.
"""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
ONE_PAGER = ROOT / "docs" / "guides" / "operator-one-pager.md"
HANDBOOK = ROOT / "docs" / "guides" / "operator-handbook.md"
README = ROOT / "README.md"


@pytest.mark.unit
def test_operator_one_pager_exists_and_covers_flow() -> None:
    if not ONE_PAGER.is_file():
        pytest.skip("operator-one-pager.md is local opt-in (not in git after #1597)")
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
    if not HANDBOOK.is_file():
        pytest.skip("operator-handbook.md is local opt-in (not in git after #1597)")
    text = HANDBOOK.read_text(encoding="utf-8")
    lower = text.lower()
    assert "login" in lower
    assert "convert" in lower
    assert "validate" in lower
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
    # README may still point at local-opt-in paths; require links only when guides exist.
    if not ONE_PAGER.is_file() or not HANDBOOK.is_file():
        pytest.skip(
            "operator guides local opt-in — README links deferred until docs restore"
        )
    assert "docs/guides/operator-one-pager.md" in text
    assert "docs/guides/operator-handbook.md" in text
