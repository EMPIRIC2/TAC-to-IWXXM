"""T3.6 / ADR-027: xsdata codegen pipeline config + CI hook wiring."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "codegen" / "iwxxm_xsd.py"
VENDOR_SYNC = REPO_ROOT / ".github" / "workflows" / "vendor-sync.yml"
MAKEFILE = REPO_ROOT / "Makefile"
OUT_ROOT = REPO_ROOT / "packages" / "shared" / "src" / "metar_shared" / "iwxxm_xsd"


def _load_script():
    spec = importlib.util.spec_from_file_location("iwxxm_xsd_codegen", SCRIPT)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_codegen_script_exists() -> None:
    assert SCRIPT.is_file()


def test_makefile_codegen_target_invokes_script() -> None:
    text = MAKEFILE.read_text(encoding="utf-8")
    assert "codegen-iwxxm-xsd:" in text
    assert "scripts/codegen/iwxxm_xsd.py" in text


def test_codegen_check_passes() -> None:
    mod = _load_script()
    assert mod.check_only() == 0
    versions = mod.load_manifest_versions()
    assert "2023-1" in versions
    assert "2025-2" in versions


def test_vendor_sync_workflow_runs_codegen_on_pin_bumps() -> None:
    """CI hook: vendor-sync PR regenerates xsdata models (E10-23 / E10-40)."""
    text = VENDOR_SYNC.read_text(encoding="utf-8")
    assert "codegen-iwxxm-xsd" in text or "scripts/codegen/iwxxm_xsd.py" in text
    data = yaml.safe_load(text)
    steps = data["jobs"]["vendor-sync"]["steps"]
    joined = " ".join(str(s.get("run", s.get("name", ""))) for s in steps)
    assert "codegen" in joined.lower()


def test_output_package_skeleton_after_check() -> None:
    """``--check`` does not require models; init helpers create markers when generating."""
    mod = _load_script()
    mod.write_package_init(mod.load_manifest_versions())
    assert (OUT_ROOT / "__init__.py").is_file()
    assert (OUT_ROOT / "README.md").is_file()
    assert (OUT_ROOT / "STATUS.json").is_file()


@pytest.mark.slow
def test_codegen_smoke_one_version_metar_entry() -> None:
    """Optional slow smoke: generate 2025-2 from metarSpeci.xsd (non-empty tree)."""
    mod = _load_script()
    summary = mod.generate_version("2025-2", entry="metarSpeci.xsd")
    assert summary["py_files"] > 0
    assert summary["bytes"] > 1000
    out = REPO_ROOT / summary["output"]
    assert out.is_dir()
    assert any(out.rglob("*.py"))
