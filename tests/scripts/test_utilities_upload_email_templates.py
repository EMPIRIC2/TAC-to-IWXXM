"""Coverage for scripts/utilities/upload_email_templates.py."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests
import scripts.utilities.upload_email_templates as upload


def _template_md() -> str:
    return "## HTML\n```html\n<p>Body</p>\n```"


@pytest.mark.unit
def test_extract_html_primary_pattern(tmp_path: Path) -> None:
    path = tmp_path / "t.md"
    path.write_text(_template_md(), encoding="utf-8")
    assert upload.extract_html_from_template(str(path)) == "<p>Body</p>"


@pytest.mark.unit
def test_extract_html_fallback_pattern(tmp_path: Path) -> None:
    path = tmp_path / "t.md"
    path.write_text("```html\n<p>Fallback</p>\n```", encoding="utf-8")
    assert upload.extract_html_from_template(str(path)) == "<p>Fallback</p>"


@pytest.mark.unit
def test_extract_html_missing_file(capsys: pytest.CaptureFixture[str]) -> None:
    assert upload.extract_html_from_template("/no/such/file.md") is None
    assert "File not found" in capsys.readouterr().out


@pytest.mark.unit
def test_extract_html_read_error(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "t.md"
    path.write_text("x", encoding="utf-8")
    with patch("builtins.open", side_effect=OSError("denied")):
        assert upload.extract_html_from_template(str(path)) is None
    assert "Error reading" in capsys.readouterr().out


@pytest.mark.unit
def test_extract_html_no_block(tmp_path: Path) -> None:
    path = tmp_path / "t.md"
    path.write_text("no html here", encoding="utf-8")
    assert upload.extract_html_from_template(str(path)) is None


@pytest.mark.unit
def test_upload_template_success() -> None:
    resp = MagicMock(status_code=200)
    with patch(
        "scripts.utilities.upload_email_templates.requests.patch", return_value=resp
    ):
        assert (
            upload.upload_template("tok", "proj", "confirmation", "Subj", "<p>x</p>")
            is True
        )


@pytest.mark.unit
def test_upload_template_401(capsys: pytest.CaptureFixture[str]) -> None:
    resp = MagicMock(status_code=401, text="nope")
    with patch(
        "scripts.utilities.upload_email_templates.requests.patch", return_value=resp
    ):
        assert (
            upload.upload_template("tok", "proj", "confirmation", "Subj", "<p>x</p>")
            is False
        )
    assert "Invalid access token" in capsys.readouterr().out


@pytest.mark.unit
def test_upload_template_404(capsys: pytest.CaptureFixture[str]) -> None:
    resp = MagicMock(status_code=404, text="nope")
    with patch(
        "scripts.utilities.upload_email_templates.requests.patch", return_value=resp
    ):
        assert (
            upload.upload_template("tok", "proj", "confirmation", "Subj", "<p>x</p>")
            is False
        )
    assert "Project not found" in capsys.readouterr().out


@pytest.mark.unit
def test_upload_template_other_status(capsys: pytest.CaptureFixture[str]) -> None:
    resp = MagicMock(status_code=500, text="server error")
    with patch(
        "scripts.utilities.upload_email_templates.requests.patch", return_value=resp
    ):
        assert (
            upload.upload_template("tok", "proj", "confirmation", "Subj", "<p>x</p>")
            is False
        )
    assert "server error" in capsys.readouterr().out


@pytest.mark.unit
def test_upload_template_request_exception(capsys: pytest.CaptureFixture[str]) -> None:
    with patch(
        "scripts.utilities.upload_email_templates.requests.patch",
        side_effect=requests.exceptions.RequestException("down"),
    ):
        assert (
            upload.upload_template("tok", "proj", "confirmation", "Subj", "<p>x</p>")
            is False
        )
    assert "Error: down" in capsys.readouterr().out


@pytest.mark.unit
def test_main_verify_only(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    template = tmp_path / "01-confirmation.md"
    template.write_text(_template_md(), encoding="utf-8")
    monkeypatch.setattr(
        upload,
        "TEMPLATES",
        [("confirmation", str(template), "Confirm your email address")],
    )
    with patch(
        "sys.argv",
        ["prog", "--access-token", "tok", "--project-id", "proj", "--verify-only"],
    ):
        assert upload.main() == 0


@pytest.mark.unit
def test_main_upload_partial_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    template = tmp_path / "01-confirmation.md"
    template.write_text(_template_md(), encoding="utf-8")
    monkeypatch.setattr(
        upload,
        "TEMPLATES",
        [("confirmation", str(template), "Confirm your email address")],
    )
    with (
        patch(
            "sys.argv",
            ["prog", "--access-token", "tok", "--project-id", "proj"],
        ),
        patch(
            "scripts.utilities.upload_email_templates.upload_template",
            return_value=False,
        ),
    ):
        assert upload.main() == 1


@pytest.mark.unit
def test_main_read_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        upload,
        "TEMPLATES",
        [("confirmation", str(tmp_path / "missing.md"), "Subject")],
    )
    with patch(
        "sys.argv",
        ["prog", "--access-token", "tok", "--project-id", "proj"],
    ):
        assert upload.main() == 1


@pytest.mark.unit
def test_upload_template_201_status() -> None:
    resp = MagicMock(status_code=201)
    with patch(
        "scripts.utilities.upload_email_templates.requests.patch", return_value=resp
    ):
        assert (
            upload.upload_template("tok", "proj", "confirmation", "Subj", "<p>x</p>")
            is True
        )


@pytest.mark.unit
def test_main_upload_all_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    template = tmp_path / "01-confirmation.md"
    template.write_text(_template_md(), encoding="utf-8")
    monkeypatch.setattr(
        upload,
        "TEMPLATES",
        [("confirmation", str(template), "Confirm your email address")],
    )
    with (
        patch(
            "sys.argv",
            ["prog", "--access-token", "tok", "--project-id", "proj"],
        ),
        patch(
            "scripts.utilities.upload_email_templates.upload_template",
            return_value=True,
        ),
    ):
        assert upload.main() == 0
