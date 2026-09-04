"""TC-EV080-002 / TC-EV080-003 — Python coverage gates at 100% (EV-080 / ADR-007).

[Corpus: adr/ADR-007] [Corpus: tests]
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

PYPROJECTS = [
    ROOT / "pyproject.toml",
    ROOT / "apps/backend/pyproject.toml",
    ROOT / "apps/worker/pyproject.toml",
    ROOT / "packages/shared/pyproject.toml",
    ROOT / "packages/auth/pyproject.toml",
    ROOT / "packages/tac2iwxxm/pyproject.toml",
    ROOT / "packages/tac-validate/pyproject.toml",
    ROOT / "packages/iwxxm-validate/pyproject.toml",
    ROOT / "packages/dissemination/pyproject.toml",
]


@pytest.mark.unit
class TestTcEv080002PythonFailUnder:
    """Every gated Python surface fail_under / CI fail-under is 100."""

    def test_pyproject_fail_under_100(self) -> None:
        for path in PYPROJECTS:
            text = path.read_text(encoding="utf-8")
            assert "fail_under = 100" in text, f"{path} missing fail_under = 100"
            assert "fail_under = 95" not in text, f"{path} still has fail_under = 95"
            assert "fail_under = 98" not in text, f"{path} still has fail_under = 98"

    def test_ci_and_makefile_cov_fail_under_100(self) -> None:
        ci = (ROOT / ".github/workflows/ci-cd.yml").read_text(encoding="utf-8")
        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
        diss = (ROOT / "scripts/ci/run_dissemination_coverage.sh").read_text(
            encoding="utf-8"
        )
        for label, text in (
            ("ci-cd.yml", ci),
            ("Makefile", makefile),
            ("dissemination", diss),
        ):
            values = [int(m) for m in re.findall(r"--cov-fail-under=(\d+)", text)]
            assert values, f"expected --cov-fail-under in {label}"
            below = [v for v in values if v < 100]
            assert not below, f"{label} --cov-fail-under below 100: {below}"

    def test_root_does_not_omit_init(self) -> None:
        root = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        backend = (ROOT / "apps/backend/pyproject.toml").read_text(encoding="utf-8")
        assert '"**/__init__.py"' not in root
        assert '"*/__init__.py"' not in backend
        assert '"src/**/__init__.py"' not in backend
        assert '"src/__init__.py"' not in backend


@pytest.mark.unit
class TestTcEv080003PerFileCheckerDefault:
    """check_per_file_coverage.py defaults to --min-pct 100."""

    def test_checker_default_min_pct_100(self) -> None:
        script = (ROOT / "scripts/ci/check_per_file_coverage.py").read_text(
            encoding="utf-8"
        )
        assert "default=100.0" in script or "default=100" in script
        assert "min_pct: float = 100.0" in script
        assert "default 95.0" not in script
