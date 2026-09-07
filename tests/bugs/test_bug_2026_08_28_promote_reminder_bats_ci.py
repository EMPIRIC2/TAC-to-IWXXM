"""BUG-2026-08-28 — promote_release_reminder bats must tolerate stage→main CI env.

On promote PRs Actions sets GITHUB_EVENT_NAME/BASE_REF/HEAD_REF to stage→main.
The skip-path bats case must clear those vars (or it hits the stub git and fails).
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
BATS_FILE = ROOT / "tests" / "bats" / "ci" / "promote_release_reminder.bats"


def test_bug_2026_08_28_bats_file_clears_stage_main_github_env() -> None:
    src = BATS_FILE.read_text(encoding="utf-8")
    for var in ("GITHUB_EVENT_NAME", "GITHUB_BASE_REF", "GITHUB_HEAD_REF"):
        assert f"-u {var}" in src, f"expected env -u {var} in {BATS_FILE.name}"


@pytest.mark.skipif(shutil.which("bats") is None, reason="bats not installed")
def test_bug_2026_08_28_promote_reminder_bats_ok_under_stage_main_ci_env() -> None:
    env = os.environ.copy()
    env.update(
        {
            "GITHUB_EVENT_NAME": "pull_request",
            "GITHUB_BASE_REF": "main",
            "GITHUB_HEAD_REF": "stage",
        }
    )
    proc = subprocess.run(
        ["bats", str(BATS_FILE)],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
