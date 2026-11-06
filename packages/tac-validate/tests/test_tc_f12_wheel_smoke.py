"""T2.5 / UJ-DEV-005: clean-venv wheel install smoke for tac-validate (local)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PACKAGE_ROOT.parents[1]
ACCEPT_METAR = Path(__file__).resolve().parent / "fixtures" / "accept" / "metar_basic.tac"


@pytest.mark.slow
def test_clean_venv_wheel_install_and_cli_smoke(tmp_path: Path) -> None:
    """
    Build the local wheel with ``uv build``, install into a fresh venv, lint + CLI.
    """
    if not ACCEPT_METAR.is_file():
        pytest.skip("accept METAR fixture missing")

    dist = tmp_path / "dist"
    dist.mkdir()
    # metar-shared is a workspace dep (ADR-055 inherit factory); build both wheels
    # so a clean venv can resolve without PyPI (F12 smoke).
    for package in ("metar-shared", "tac-validate"):
        build = subprocess.run(
            ["uv", "build", "--package", package, "-o", str(dist)],
            check=False,
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        assert build.returncode == 0, f"uv build {package} failed:\n{build.stdout}\n{build.stderr}"

    shared_wheels = sorted(dist.glob("metar_shared-*.whl"))
    tac_wheels = sorted(dist.glob("tac_validate-*.whl"))
    assert shared_wheels, f"no metar-shared wheel in {dist}: {list(dist.iterdir())}"
    assert tac_wheels, f"no tac-validate wheel in {dist}: {list(dist.iterdir())}"
    shared_wheel = shared_wheels[0]
    wheel = tac_wheels[0]

    venv_dir = tmp_path / "venv"
    create = subprocess.run(
        ["uv", "venv", str(venv_dir)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert create.returncode == 0, create.stderr

    python = venv_dir / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    script = venv_dir / ("Scripts/tac-validate.exe" if sys.platform == "win32" else "bin/tac-validate")

    install = subprocess.run(
        ["uv", "pip", "install", "--python", str(python), str(shared_wheel), str(wheel)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert install.returncode == 0, install.stderr

    lib = subprocess.run(
        [
            str(python),
            "-c",
            "from pathlib import Path; from tac_validate import lint; "
            f"r=lint(Path({str(ACCEPT_METAR)!r}).read_text(), product='METAR'); "
            "assert r.ok; print('ok')",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert lib.returncode == 0, lib.stderr + lib.stdout
    assert "ok" in lib.stdout

    assert script.is_file(), f"console script missing: {script}"
    cli = subprocess.run(
        [str(script), "--product", "METAR", str(ACCEPT_METAR)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert cli.returncode == 0, cli.stderr + cli.stdout

    loc = subprocess.run(
        [str(python), "-c", "import tac_validate; print(tac_validate.__file__)"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    assert "site-packages" in loc
