"""TC-EV047-009 / TC-EV047-010 - operator docs gates after EV-repo-docs-cleanup.

Operator guides under ``docs/guides/`` are local opt-in (#1597). Tracked corpus
still documents the public Convert path. [Corpus: tests] — no skip wrappers.
"""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
ONE_PAGER = ROOT / "docs" / "guides" / "operator-one-pager.md"
HANDBOOK = ROOT / "docs" / "guides" / "operator-handbook.md"
README = ROOT / "README.md"
AGENTS = ROOT / "AGENTS.md"
PRODUCT = ROOT / "docs" / "product-requirements.md"


@pytest.mark.unit
def test_operator_one_pager_local_opt_in_or_covers_flow() -> None:
    """Success: local one-pager covers Convert flow; else AGENTS lists local opt-in."""
    if ONE_PAGER.is_file():
        text = ONE_PAGER.read_text(encoding="utf-8")
        assert "Convert" in text or "convert" in text
        assert "Validate" in text or "validate" in text
        assert "Download" in text or "download" in text
        assert "[Corpus:" not in text
        return
    agents = AGENTS.read_text(encoding="utf-8")
    assert "docs/guides/" in agents
    assert "Local opt-in" in agents or "local opt-in" in agents.lower()


@pytest.mark.unit
def test_operator_handbook_local_opt_in_or_required_sections() -> None:
    """Failure path covered when handbook absent: product requirements still list F7."""
    if HANDBOOK.is_file():
        text = HANDBOOK.read_text(encoding="utf-8")
        lower = text.lower()
        assert "convert" in lower
        assert "validate" in lower
        assert "dissemination" in lower
        return
    product = PRODUCT.read_text(encoding="utf-8")
    assert "F7" in product or "Convert" in product


@pytest.mark.unit
def test_readme_mentions_docs_or_operator_surface() -> None:
    """Validation: README points operators at docs without requiring local guides."""
    text = README.read_text(encoding="utf-8")
    assert "docs/" in text
    if ONE_PAGER.is_file() and HANDBOOK.is_file():
        assert "docs/guides/operator-one-pager.md" in text
        assert "docs/guides/operator-handbook.md" in text
