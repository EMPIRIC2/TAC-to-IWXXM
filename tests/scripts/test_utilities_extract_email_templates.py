"""Coverage for scripts/utilities/extract_email_templates.py."""

from __future__ import annotations

from pathlib import Path

import pytest
import scripts.utilities.extract_email_templates as extract


@pytest.mark.unit
def test_extract_sections_parses_markdown() -> None:
    content = "## Subject\n```\nHello\n```\n## HTML\n```html\n<p>Hi</p>\n```"
    subject, html = extract.extract_sections(content)
    assert subject == "Hello"
    assert html == "<p>Hi</p>"


@pytest.mark.unit
def test_extract_sections_missing_blocks() -> None:
    subject, html = extract.extract_sections("no sections")
    assert subject == "No subject found"
    assert html == "No HTML found"


@pytest.mark.unit
def test_print_template(capsys: pytest.CaptureFixture[str]) -> None:
    extract.print_template("Name", "file.md", "Confirmation", "Subj", "<p>x</p>")
    out = capsys.readouterr().out
    assert "Name" in out
    assert "Subj" in out
    assert "<p>x</p>" in out


@pytest.mark.unit
def test_main_skips_missing_and_extracts_existing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    templates_dir = tmp_path / "frontend" / "templates" / "authentication"
    templates_dir.mkdir(parents=True)
    md = templates_dir / "01-confirmation.md"
    md.write_text(
        "## Subject\n```\nConfirm\n```\n## HTML\n```html\n<p>Go</p>\n```",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    extract.main()
    out = capsys.readouterr().out
    assert "SUPABASE EMAIL TEMPLATES" in out
    assert "Warning: 02-magic-link.md not found" in out
    assert "Confirm" in out
