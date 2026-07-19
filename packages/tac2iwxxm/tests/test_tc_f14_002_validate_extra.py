"""T4.1 / TC-F14-002: clean-venv convert + ``tac2iwxxm[validate]`` extras (UJ-DEV-005)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PACKAGE_ROOT.parents[1]
SAMPLE_METAR = PACKAGE_ROOT / "tests" / "fixtures" / "annex3_golden" / "metar_basic.tac"

_PACKAGES = ("tac2iwxxm", "tac-validate", "iwxxm-validate")


def _uv_build(dist: Path, package: str) -> None:
    # --wheel: build from the checkout so iwxxm-validate's hatch hook can
    # reach monorepo vendor/schemas (sdist rebuild in the uv cache cannot).
    build = subprocess.run(
        ["uv", "build", "--wheel", "--package", package, "-o", str(dist)],
        check=False,
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    assert build.returncode == 0, f"uv build {package} failed:\n{build.stdout}\n{build.stderr}"


def _wheel_for(dist: Path, name: str) -> Path:
    # Normalized dist name uses underscores (PEP 427).
    needle = name.replace("-", "_")
    wheels = sorted(dist.glob(f"{needle}-*.whl"))
    assert wheels, f"no wheel for {name} in {dist}: {list(dist.iterdir())}"
    return wheels[0]


@pytest.mark.slow
def test_clean_venv_convert_and_validate_extra(tmp_path: Path) -> None:
    """
    Convert-only wheel works; ``[validate]`` pulls ``tac-validate`` + ``iwxxm-validate``.

    Builds all three local wheels, installs convert-only into a fresh venv, then
    reinstalls with the ``[validate]`` extra resolved via ``--find-links``.
    """
    if not SAMPLE_METAR.is_file():
        pytest.skip("sample METAR fixture missing")

    dist = tmp_path / "dist"
    dist.mkdir()
    for package in _PACKAGES:
        _uv_build(dist, package)

    tac2_wheel = _wheel_for(dist, "tac2iwxxm")
    _wheel_for(dist, "tac-validate")
    _wheel_for(dist, "iwxxm-validate")

    venv_dir = tmp_path / "venv"
    create = subprocess.run(
        ["uv", "venv", str(venv_dir)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert create.returncode == 0, create.stderr

    python = venv_dir / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")

    # --- Convert-only install ---
    install_core = subprocess.run(
        ["uv", "pip", "install", "--python", str(python), str(tac2_wheel)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert install_core.returncode == 0, install_core.stderr

    convert_smoke = subprocess.run(
        [
            str(python),
            "-c",
            "from pathlib import Path; from tac2iwxxm import convert; "
            f"r=convert(Path({str(SAMPLE_METAR)!r}).read_text(), product='METAR'); "
            "assert r.ok and r.xml and 'METAR' in r.xml; print(r.xml[:80])",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert convert_smoke.returncode == 0, convert_smoke.stderr + convert_smoke.stdout

    missing = subprocess.run(
        [
            str(python),
            "-c",
            "import importlib.util as u; "
            "assert u.find_spec('tac_validate') is None; "
            "assert u.find_spec('iwxxm_validate') is None; "
            "print('validators-absent')",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert missing.returncode == 0, missing.stderr + missing.stdout
    assert "validators-absent" in missing.stdout

    # --- [validate] extra resolves both validators from local find-links ---
    install_extra = subprocess.run(
        [
            "uv",
            "pip",
            "install",
            "--python",
            str(python),
            "--find-links",
            str(dist),
            f"{tac2_wheel}[validate]",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert install_extra.returncode == 0, install_extra.stderr

    validators = subprocess.run(
        [
            str(python),
            "-c",
            "import tac_validate; import iwxxm_validate; "
            "from tac_validate import lint; from iwxxm_validate import validate_iwxxm; "
            "from pathlib import Path; from tac2iwxxm import convert; "
            f"tac=Path({str(SAMPLE_METAR)!r}).read_text(); "
            "assert lint(tac, product='METAR').ok; "
            "xml=convert(tac, product='METAR').xml; "
            "assert xml and validate_iwxxm(xml, iwxxm_version='2025-2').ok; "
            "print('validate-extra-ok')",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert validators.returncode == 0, validators.stderr + validators.stdout
    assert "validate-extra-ok" in validators.stdout
