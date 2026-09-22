"""TC-EVYFC-003 — starter templates, --check-overlay, README install smoke (#1227)."""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_COOKBOOK = _REPO / "docs" / "domain" / "overlays" / "overlay-cookbook.md"
_MATRIX = _REPO / "docs" / "domain" / "overlays" / "product-engine-matrix.md"
_PREFLIGHT = _REPO / "scripts" / "overlays" / "preflight.py"

_STARTER_ROOTS: tuple[tuple[str, Path], ...] = (
    ("pack", _REPO / "packages" / "tac-decoding" / "examples" / "starters"),
    ("tac-policy", _REPO / "packages" / "tac-validate" / "examples" / "starters"),
    ("iwxxm-policy", _REPO / "packages" / "iwxxm-validate" / "examples" / "starters"),
    ("profile-binding", _REPO / "packages" / "tac2iwxxm" / "examples" / "starters"),
)

_CHECK_OVERLAY_CLIS: tuple[tuple[str, str, Path], ...] = (
    (
        "tac-decoding",
        "tac_decoding.cli",
        _REPO / "packages" / "tac-decoding" / "examples" / "overlays" / "valid",
    ),
    (
        "tac-validate",
        "tac_validate.cli",
        _REPO / "packages" / "tac-validate" / "examples" / "overlays" / "valid",
    ),
    (
        "iwxxm-validate",
        "iwxxm_validate.cli",
        _REPO / "packages" / "iwxxm-validate" / "examples" / "overlays" / "valid",
    ),
    (
        "tac2iwxxm",
        "tac2iwxxm.cli",
        _REPO / "packages" / "tac2iwxxm" / "examples" / "overlays" / "valid",
    ),
)

_README_SMOKE: tuple[tuple[Path, str], ...] = (
    (_REPO / "packages" / "tac-decoding" / "README.md", "tac-decoding --check-overlay"),
    (_REPO / "packages" / "tac-validate" / "README.md", "tac-validate --check-overlay"),
    (
        _REPO / "packages" / "iwxxm-validate" / "README.md",
        "iwxxm-validate --check-overlay",
    ),
    (_REPO / "packages" / "tac2iwxxm" / "README.md", "tac2iwxxm --check-overlay"),
)


def test_tc_evyfc_003_starter_templates_present_and_load() -> None:
    """VA-YAML-02: each package ships starters/ that preflight accepts."""
    for _kind, root in _STARTER_ROOTS:
        assert root.is_dir(), f"missing starter tree {root.relative_to(_REPO)}"
        yaml_files = list(root.glob("*.yaml")) + list(root.glob("*.yml"))
        assert yaml_files, f"no starter YAML under {root.relative_to(_REPO)}"
        readme = root / "README.md"
        assert readme.is_file(), f"missing {readme.relative_to(_REPO)}"

    proc = subprocess.run(
        [sys.executable, str(_PREFLIGHT), "--all-examples"],
        cwd=_REPO,
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
    assert "starters" in proc.stdout.lower() or "starter" in proc.stdout.lower()


def test_tc_evyfc_003_check_overlay_cli_hooks() -> None:
    """Optional --check-overlay on each package CLI accepts valid overlay dirs."""
    env = os.environ.copy()
    env["PYTHONPATH"] = ":".join(
        str(_REPO / "packages" / name / "src")
        for name in ("tac-decoding", "tac-validate", "iwxxm-validate", "tac2iwxxm")
    )
    for prog, module, overlay_dir in _CHECK_OVERLAY_CLIS:
        assert overlay_dir.is_dir(), overlay_dir
        proc = subprocess.run(
            [sys.executable, "-m", module, "--check-overlay", str(overlay_dir)],
            cwd=_REPO,
            check=False,
            capture_output=True,
            text=True,
            env=env,
        )
        assert proc.returncode == 0, f"{prog}: {proc.stderr or proc.stdout}"


def test_tc_evyfc_003_readme_install_smoke_documented() -> None:
    """VA-YAML-03: package READMEs document --check-overlay install smoke."""
    for readme, needle in _README_SMOKE:
        body = readme.read_text(encoding="utf-8")
        assert needle in body, f"{readme.name} missing smoke command {needle!r}"
        assert "examples/starters" in body or "examples/overlays" in body

    cookbook = _COOKBOOK.read_text(encoding="utf-8")
    assert "--check-overlay" in cookbook
    assert "starters" in cookbook.lower()
    assert not re.search(r"\(draft\)", cookbook.splitlines()[0], re.I)


def test_tc_evyfc_003_matrix_evidence_section() -> None:
    """Evidence citations exist; M2 may mark some METAR/SPECI cells full."""
    text = _MATRIX.read_text(encoding="utf-8")
    assert re.search(r"## Evidence", text, re.I)
    assert (
        "partial" in text
    )  # honesty: not all-full yet (detectors/emit/other products)
    assert "data/packs" in text or "policies" in text
    assert "| METAR |" in text
    assert "| SPECI |" in text
