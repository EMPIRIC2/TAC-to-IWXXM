"""Cover scripts/cmo_week1_matrix.py CLI wrapper (EV-080 scripts gate)."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from tests.scripts.conftest import REPO_ROOT


@pytest.mark.unit
def test_cmo_week1_matrix_cli_main(tmp_path: Path) -> None:
    path = REPO_ROOT / "scripts" / "cmo_week1_matrix.py"
    with (
        patch.object(
            sys,
            "argv",
            [str(path), "--limit", "1", "--evidence", str(tmp_path)],
        ),
        pytest.raises(SystemExit) as exc,
    ):
        runpy.run_path(str(path), run_name="__main__")
    assert exc.value.code == 0
    assert (tmp_path / "matrix-report.json").is_file()
