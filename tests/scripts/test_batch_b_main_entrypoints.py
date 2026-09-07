"""In-process __main__ entrypoints for Batch B script coverage (EV-080 M4)."""

from __future__ import annotations

import importlib
import runpy
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(0, str(ROOT / "packages" / "tac2iwxxm" / "src"))
from tac2iwxxm.ca_ops_corpus import ops_fixture_root  # noqa: E402

_OPS_ROOT = ops_fixture_root(ROOT)


def _restore_iwxxm_validate() -> None:
    for key in list(sys.modules):
        if key == "iwxxm_validate" or key.startswith("iwxxm_validate."):
            del sys.modules[key]
    importlib.import_module("iwxxm_validate")


@pytest.mark.parametrize(
    ("relpath", "argv"),
    [
        (
            "scripts/ci/collect_quality_pr_stats.py",
            [
                "--repo-root",
                str(ROOT),
                "--out",
                str(ROOT / "artifacts" / "batch-b-quality-out"),
            ],
        ),
        (
            "scripts/ci/format_coverage_pr_comment.py",
            [str(ROOT / "artifacts" / "empty-cov")],
        ),
        (
            "scripts/ci/format_quality_pr_comment.py",
            [str(ROOT / "artifacts" / "empty-quality")],
        ),
        ("scripts/ci/generate_quality_metrics.py", []),
        ("scripts/codegen/iwxxm_xsd.py", ["--check"]),
        ("scripts/bench/validation_stack.py", []),
        ("scripts/iwxxm/codelist_uri_drift.py", []),
        ("scripts/iwxxm/iwxxm_us_compat_gate.py", []),
        (
            "scripts/iwxxm/harvest_ca_eccc_ops.py",
            ["--skip-network", "--fixtures-root", str(_OPS_ROOT)],
        ),
        (
            "scripts/iwxxm/harvest_ca_eccc_vaac_tac.py",
            ["--skip-network", "--fixtures-root", str(_OPS_ROOT)],
        ),
    ],
)
def test_batch_b_main_entrypoint(
    relpath: str,
    argv: list[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    if relpath.endswith("validation_stack.py"):
        _restore_iwxxm_validate()
    script = ROOT / relpath
    monkeypatch.setattr(sys, "argv", [relpath, *argv])
    with pytest.raises(SystemExit) as exc:
        runpy.run_path(str(script), run_name="__main__")
    assert exc.value.code == 0
