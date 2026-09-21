"""TC-EV-VPL-006 — iwxxm-validate CLI --policy binding (#1216 M5)."""

from __future__ import annotations

import builtins
import io
from contextlib import redirect_stderr
from pathlib import Path

import pytest
from iwxxm_validate.cli import _bind_output_policy


def test_default_profile_policy_activates() -> None:
    assert _bind_output_policy("annex3", None) is None
    assert _bind_output_policy("ICAO_2025", "annex3-iwxxm-output") is None


def test_cli_policy_error_exits_2(tmp_path: Path) -> None:
    from iwxxm_validate.cli import main

    xml = tmp_path / "x.xml"
    xml.write_text("<not-iwxxm/>", encoding="utf-8")
    err = io.StringIO()
    with redirect_stderr(err):
        code = main(["--policy", "missing-out", str(xml)])
    assert code == 2
    assert "unknown IWXXM output policy" in err.getvalue()

    assert _bind_output_policy("nope", None)
    assert "unknown IWXXM output policy" in (_bind_output_policy("annex3", "missing-out") or "")


def test_import_error_without_override(monkeypatch: pytest.MonkeyPatch) -> None:
    real_import = builtins.__import__

    def _blocked(name: str, *args: object, **kwargs: object) -> object:
        if name == "tac2iwxxm.profile_resolve":
            raise ImportError(name)
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _blocked)
    assert _bind_output_policy("annex3", None) is None
    assert "unknown IWXXM output policy" in (_bind_output_policy("annex3", "missing-out") or "")


def test_activated_policy_with_stale_id(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    overlay = tmp_path / "pol"
    overlay.mkdir()
    (overlay / "bad.yaml").write_text(
        "schema_version: 1\nid: stale-out\nlifecycle: activated\npin: '2025-2'\nselect: [NOT_A_REAL_ASSERT]\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("IWXXM_VALIDATE_POLICY_DIR", str(overlay))
    message = _bind_output_policy("annex3", "stale-out") or ""
    assert "NOT_A_REAL_ASSERT" in message
