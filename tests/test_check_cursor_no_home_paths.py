"""Regression: tracked .cursor must not embed /Users/ or /home/<user>/ (EV-095 / #1095)."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "ci" / "check_cursor_no_home_paths.py"


def test_check_cursor_no_home_paths_passes_on_repo() -> None:
    proc = subprocess.run(
        ["python3", str(SCRIPT), str(REPO)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout


def test_check_cursor_no_home_paths_fails_on_synthetic_users_path(
    tmp_path: Path,
) -> None:
    """Guard detects /Users/... when present in a fake git tree under .cursor."""
    fake = tmp_path / "repo"
    cursor = fake / ".cursor"
    cursor.mkdir(parents=True)
    bad = cursor / "bad.sh"
    bad.write_text(
        'pluginPaths=["/Users/someone/Documents/GitHub/spec-dev-knowledge-graph/cursor-plugin"]\n',
        encoding="utf-8",
    )
    subprocess.run(["git", "init"], cwd=fake, check=True, capture_output=True)
    subprocess.run(
        ["git", "add", ".cursor/bad.sh"], cwd=fake, check=True, capture_output=True
    )
    proc = subprocess.run(
        ["python3", str(SCRIPT), str(fake)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 1
    assert "/Users/" in (proc.stderr or "")


@pytest.mark.parametrize(
    "line",
    [
        'command": "${userHome}/Documents/GitHub/spec-dev-knowledge-graph/cursor-plugin/scripts/mcp-server.sh"',
        "EM_ROOT=${EM_ENGINEERING_MEMORY_ROOT:-$HOME/Documents/GitHub/spec-dev-knowledge-graph}",
    ],
)
def test_portable_forms_not_flagged(tmp_path: Path, line: str) -> None:
    fake = tmp_path / "repo"
    cursor = fake / ".cursor"
    cursor.mkdir(parents=True)
    (cursor / "ok.md").write_text(line + "\n", encoding="utf-8")
    subprocess.run(["git", "init"], cwd=fake, check=True, capture_output=True)
    subprocess.run(
        ["git", "add", ".cursor/ok.md"], cwd=fake, check=True, capture_output=True
    )
    proc = subprocess.run(
        ["python3", str(SCRIPT), str(fake)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
