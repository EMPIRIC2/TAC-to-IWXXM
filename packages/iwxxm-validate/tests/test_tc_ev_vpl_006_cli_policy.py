"""TC-EV-VPL-006 — iwxxm-validate CLI --policy binding (#1216 M5)."""

from __future__ import annotations

import builtins
import io
from contextlib import redirect_stderr
from pathlib import Path

import pytest
from iwxxm_validate.cli import _bind_output_policy
from iwxxm_validate.models import ValidationReport


def test_default_profile_policy_activates() -> None:
    policy_id, error = _bind_output_policy("annex3", None)
    assert error is None
    assert policy_id == "annex3-iwxxm-output"
    policy_id, error = _bind_output_policy("ICAO_2025", "annex3-iwxxm-output")
    assert error is None
    assert policy_id == "annex3-iwxxm-output"


def test_cli_policy_error_exits_2(tmp_path: Path) -> None:
    from iwxxm_validate.cli import main

    xml = tmp_path / "x.xml"
    xml.write_text("<not-iwxxm/>", encoding="utf-8")
    err = io.StringIO()
    with redirect_stderr(err):
        code = main(["--policy", "missing-out", str(xml)])
    assert code == 2
    assert "unknown IWXXM output policy" in err.getvalue()

    _id, error = _bind_output_policy("nope", None)
    assert error
    _id, error = _bind_output_policy("annex3", "missing-out")
    assert error is not None
    assert "unknown IWXXM output policy" in error


def test_import_error_without_override(monkeypatch: pytest.MonkeyPatch) -> None:
    real_import = builtins.__import__

    def _blocked(name: str, *args: object, **kwargs: object) -> object:
        if name == "tac2iwxxm.profile_resolve":
            raise ImportError(name)
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _blocked)
    policy_id, error = _bind_output_policy("annex3", None)
    assert policy_id is None
    assert error is None
    _id, error = _bind_output_policy("annex3", "missing-out")
    assert error is not None
    assert "unknown IWXXM output policy" in error


def test_activated_policy_with_stale_id(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    overlay = tmp_path / "pol"
    overlay.mkdir()
    (overlay / "bad.yaml").write_text(
        "schema_version: 1\nid: stale-out\nlifecycle: activated\npin: '2025-2'\nselect: [NOT_A_REAL_ASSERT]\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("IWXXM_VALIDATE_POLICY_DIR", str(overlay))
    _id, message = _bind_output_policy("annex3", "stale-out")
    assert message is not None
    assert "NOT_A_REAL_ASSERT" in message


def test_cli_passes_policy_into_validate(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from iwxxm_validate import cli

    seen: dict[str, object] = {}

    def _fake(text: str, **kwargs: object) -> ValidationReport:
        seen["text"] = text
        seen.update(kwargs)
        return ValidationReport(ok=True, iwxxm_version="2025-2", profile="annex3", issues=[])

    monkeypatch.setattr(cli, "validate_iwxxm", _fake)
    xml = tmp_path / "x.xml"
    xml.write_text("<Metar/>", encoding="utf-8")
    assert cli.main(["--policy", "annex3-iwxxm-output", str(xml)]) == 0
    assert seen["output_policy_id"] == "annex3-iwxxm-output"
