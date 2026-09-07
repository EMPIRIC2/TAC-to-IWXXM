"""Coverage for scripts/ci/check_cursor_no_home_paths.py (EV-095 / #1095)."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
import scripts.ci.check_cursor_no_home_paths as guard


def _git_init_with_cursor(fake: Path, rel: str, content: bytes | str) -> Path:
    cursor = fake / ".cursor"
    cursor.mkdir(parents=True, exist_ok=True)
    path = fake / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content, encoding="utf-8")
    subprocess.run(["git", "init"], cwd=fake, check=True, capture_output=True)
    subprocess.run(["git", "add", "-f", rel], cwd=fake, check=True, capture_output=True)
    return path


@pytest.mark.unit
def test_main_ok_on_portable_forms(tmp_path: Path) -> None:
    fake = tmp_path / "repo"
    _git_init_with_cursor(
        fake,
        ".cursor/ok.md",
        "EM_ROOT=${EM_ENGINEERING_MEMORY_ROOT:-$HOME/Documents/x}\n"
        'command": "${userHome}/Documents/GitHub/spec-dev-knowledge-graph/cursor-plugin/scripts/mcp-server.sh"\n',
    )
    assert guard.main(["prog", str(fake)]) == 0


@pytest.mark.unit
def test_main_fails_on_users_path(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    fake = tmp_path / "repo"
    _git_init_with_cursor(
        fake,
        ".cursor/bad.sh",
        'pluginPaths=["/Users/someone/Documents/GitHub/spec-dev-knowledge-graph/cursor-plugin"]\n',
    )
    assert guard.main(["prog", str(fake)]) == 1
    err = capsys.readouterr().err
    assert "FAIL:" in err
    assert "/Users/" in err
    assert "EM_ENGINEERING_MEMORY_ROOT" in err


@pytest.mark.unit
def test_main_fails_on_home_user_path(tmp_path: Path) -> None:
    fake = tmp_path / "repo"
    _git_init_with_cursor(
        fake,
        ".cursor/bad.md",
        "root=/home/alice/src/spec-dev-knowledge-graph/cursor-plugin\n",
    )
    assert guard.main(["prog", str(fake)]) == 1


@pytest.mark.unit
def test_tracked_skips_binary_suffix(tmp_path: Path) -> None:
    fake = tmp_path / "repo"
    _git_init_with_cursor(fake, ".cursor/icon.png", b"\x89PNG\r\n")
    files = guard._tracked_cursor_files(fake)
    assert files == []


@pytest.mark.unit
def test_tracked_skips_missing_file(tmp_path: Path) -> None:
    fake = tmp_path / "repo"
    cursor = fake / ".cursor"
    cursor.mkdir(parents=True)
    ghost = cursor / "gone.md"
    ghost.write_text("ok\n", encoding="utf-8")
    subprocess.run(["git", "init"], cwd=fake, check=True, capture_output=True)
    subprocess.run(
        ["git", "add", ".cursor/gone.md"], cwd=fake, check=True, capture_output=True
    )
    ghost.unlink()
    files = guard._tracked_cursor_files(fake)
    assert files == []


@pytest.mark.unit
def test_findings_skips_undecodeable_utf8(tmp_path: Path) -> None:
    fake = tmp_path / "repo"
    _git_init_with_cursor(fake, ".cursor/bin.dat", b"\xff\xfe/Users/evil/\n")
    # .dat not in skip suffixes — read_text raises UnicodeDecodeError → skip
    assert guard._findings(fake) == []


@pytest.mark.unit
def test_main_defaults_to_cwd(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    fake = tmp_path / "repo"
    _git_init_with_cursor(fake, ".cursor/ok.md", "portable only\n")
    monkeypatch.chdir(fake)
    assert guard.main(["prog"]) == 0


@pytest.mark.unit
def test_main_ok_on_real_repo() -> None:
    """Smoke: current checkout must stay portable after EV-095."""
    assert guard.main(["prog"]) == 0
