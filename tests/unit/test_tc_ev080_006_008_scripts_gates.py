"""TC-EV080-006..008 — scripts Python cov + bats mapping guards (EV-080 M4)."""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def test_tc_ev080_006_makefile_scripts_coverage_fail_under_100() -> None:
    """make test-coverage-scripts must enforce fail_under 100 + per-file check."""
    mk = (REPO / "Makefile").read_text(encoding="utf-8")
    assert "test-coverage-scripts:" in mk
    assert "--cov-fail-under=100" in mk
    assert "check_per_file_coverage.py" in mk
    assert "--min-pct 100" in mk


def test_tc_ev080_007_ci_installs_bats_and_runs_scripts_coverage_job() -> None:
    """ci-cd.yml scripts-coverage job installs bats and is enabled."""
    yml = (REPO / ".github/workflows/ci-cd.yml").read_text(encoding="utf-8")
    assert "scripts-coverage:" in yml
    assert "Install bats-core" in yml or "bats" in yml
    assert "make test-coverage-scripts" in yml
    assert "make test-bats" in yml
    # Job must not stay disabled after M4
    block_start = yml.index("scripts-coverage:")
    block = yml[block_start : block_start + 800]
    assert "if: false" not in block, "scripts-coverage still disabled (if: false)"


def test_tc_ev080_008_every_shell_script_has_bats_file() -> None:
    """Each scripts/**/*.sh maps to tests/bats/<rel>.bats."""
    sh_files = sorted(REPO.glob("scripts/**/*.sh"))
    assert sh_files, "expected scripts/**/*.sh"
    missing: list[str] = []
    for sh in sh_files:
        rel = sh.relative_to(REPO / "scripts").with_suffix(".bats")
        bats = REPO / "tests" / "bats" / rel
        if not bats.is_file():
            missing.append(f"{sh.relative_to(REPO)} → missing {bats.relative_to(REPO)}")
    assert not missing, "bats mapping gaps:\n" + "\n".join(missing)
