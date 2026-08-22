"""T3.4 / E10-34: runtime schema subset sync + packaged path resolution."""

from __future__ import annotations

import importlib
import importlib.util
import json
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

from iwxxm_validate.paths import (
    clear_path_caches,
    packaged_schemas_root,
    schematron_path,
    us_catalog_path,
    vendor_iwxxm_root,
    xsd_path,
)

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PACKAGE_ROOT.parents[1]
SYNC_SCRIPT = PACKAGE_ROOT / "scripts" / "sync_runtime_schemas.py"
MANIFEST = PACKAGE_ROOT / "src" / "iwxxm_validate" / "schemas" / "MANIFEST.json"
SCHEMAS_ROOT = PACKAGE_ROOT / "src" / "iwxxm_validate" / "schemas"


def _load_sync():
    spec = importlib.util.spec_from_file_location("sync_runtime_schemas", SYNC_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_manifest_policy_excludes_modelling_and_translation() -> None:
    """Committed MANIFEST documents E10-34 exclusions."""
    policy = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert policy["decision"] == "E10-34"
    assert "2023-1" in policy["iwxxm_versions"]
    assert "2025-2" in policy["iwxxm_versions"]
    excluded = " ".join(policy["exclude"])
    assert "iwxxm-modelling" in excluded
    assert "iwxxm-translation" in excluded
    assert "html" in excluded
    assert "examples" in excluded


def test_sync_runtime_schemas_subset_layout() -> None:
    """Sync copies XSD+rule+externalSchema+iwxxm-us; omits html/examples/modelling."""
    sync = _load_sync()
    summary = sync.sync(clean=True)
    assert summary["total_files"] > 50
    assert (SCHEMAS_ROOT / "iwxxm" / "2023-1" / "IWXXM" / "iwxxm.xsd").is_file()
    assert (SCHEMAS_ROOT / "iwxxm" / "2025-2" / "IWXXM" / "rule" / "iwxxm.sch").is_file()
    assert (SCHEMAS_ROOT / "iwxxm" / "externalSchema").is_dir()
    assert (SCHEMAS_ROOT / "iwxxm-us" / "3.0" / "united-states-catalog.xml").is_file()

    # Exclusions
    assert not (SCHEMAS_ROOT / "iwxxm" / "2023-1" / "IWXXM" / "html").exists()
    assert not (SCHEMAS_ROOT / "iwxxm" / "2023-1" / "IWXXM" / "examples").exists()
    assert not (SCHEMAS_ROOT / "iwxxm-modelling").exists()
    assert not (SCHEMAS_ROOT / "iwxxm-translation").exists()
    assert not (SCHEMAS_ROOT / "iwxxm-codelists").exists()


def test_packaged_paths_preferred_after_sync(monkeypatch: pytest.MonkeyPatch) -> None:
    """After sync, path helpers resolve under the package schemas tree."""
    sync = _load_sync()
    sync.sync(clean=True)
    clear_path_caches()
    monkeypatch.delenv("IWXXM_VALIDATE_REPO_ROOT", raising=False)
    monkeypatch.delenv("IWXXM_SCHEMAS_ROOT", raising=False)

    root = packaged_schemas_root()
    assert root is not None
    assert root == SCHEMAS_ROOT.resolve() or root == SCHEMAS_ROOT

    xsd = xsd_path("2023-1")
    assert "iwxxm_validate" in str(xsd).replace("\\", "/")
    assert "schemas/iwxxm/2023-1" in str(xsd).replace("\\", "/")
    assert schematron_path("2025-2").is_file()
    assert us_catalog_path() is not None
    assert vendor_iwxxm_root().is_relative_to(SCHEMAS_ROOT) or str(SCHEMAS_ROOT) in str(vendor_iwxxm_root())


def test_vendor_fallback_when_packaged_absent(monkeypatch: pytest.MonkeyPatch) -> None:
    """Without a materialised subset, paths resolve to monorepo vendor/."""
    import iwxxm_validate.paths as paths_mod

    monkeypatch.setattr(paths_mod, "packaged_schemas_root", lambda: None)
    clear_path_caches()
    monkeypatch.delenv("IWXXM_VALIDATE_REPO_ROOT", raising=False)
    monkeypatch.delenv("IWXXM_SCHEMAS_ROOT", raising=False)

    assert "vendor/schemas/iwxxm" in str(paths_mod.vendor_iwxxm_root()).replace("\\", "/")
    assert "vendor/schemas/iwxxm-us" in str(paths_mod.vendor_iwxxm_us_root()).replace("\\", "/")
    assert paths_mod.xsd_path("2023-1").is_file()


def test_packaged_schemas_root_none_without_version_trees(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """MANIFEST-only or empty iwxxm/ does not count as a packaged subset."""
    import iwxxm_validate.paths as paths_mod

    empty = tmp_path / "schemas"
    (empty / "iwxxm").mkdir(parents=True)
    (empty / "MANIFEST.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(paths_mod, "_PACKAGE_SCHEMAS", empty)
    assert paths_mod.packaged_schemas_root() is None


def test_validate_iwxxm_guard_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    """SDK rejects bad profile/levels and missing US catalog / schema files."""
    # Package ``__init__`` re-exports ``validate_iwxxm``, shadowing the submodule name.
    vi = importlib.import_module("iwxxm_validate.validate_iwxxm")
    validate_iwxxm = vi.validate_iwxxm

    bad_profile = validate_iwxxm("<r/>", iwxxm_version="2023-1", profile="nope")
    assert bad_profile.issues[0].code == "INVALID_PROFILE"

    bad_levels = validate_iwxxm("<r/>", iwxxm_version="2023-1", levels=("nope",))
    assert bad_levels.issues[0].code == "INVALID_LEVELS"

    monkeypatch.setattr(vi, "us_catalog_path", lambda: None)
    missing_us = validate_iwxxm("<r/>", iwxxm_version="2023-1", profile="iwxxm_us")
    assert missing_us.issues[0].code == "US_CATALOG_NOT_FOUND"

    wrong_ver = validate_iwxxm("<r/>", iwxxm_version="2025-2", profile="ca_eccc")
    assert wrong_ver.issues[0].code == "INVALID_IWXXM_VERSION"

    monkeypatch.setattr(vi, "ca_xsd_path", lambda **_: None)
    missing_ca = validate_iwxxm("<r/>", iwxxm_version="3.0.0", profile="ca_eccc")
    assert missing_ca.issues[0].code == "CA_SCHEMA_NOT_FOUND"

    monkeypatch.setattr(vi, "rust_available", lambda: False)
    monkeypatch.setattr(
        vi,
        "validate",
        lambda *a, **k: __import__("iwxxm_validate").ValidationReport(
            ok=True, iwxxm_version="2023-1", profile="annex3", issues=[]
        ),
    )
    fallback = validate_iwxxm("<r/>", iwxxm_version="2023-1")
    assert fallback.ok is True

    monkeypatch.setattr(vi, "rust_available", lambda: True)
    monkeypatch.setattr(
        vi,
        "rust_module",
        lambda: type("R", (), {"validate_document": staticmethod(lambda *a, **k: [])})(),
    )
    monkeypatch.setattr(
        vi,
        "xsd_path",
        lambda _v: (_ for _ in ()).throw(FileNotFoundError("missing xsd")),
    )
    missing = validate_iwxxm("<r/>", iwxxm_version="2023-1")
    assert missing.issues[0].code == "SCHEMA_NOT_AVAILABLE"


@pytest.mark.slow
def test_wheel_contains_runtime_schema_subset(tmp_path: Path) -> None:
    """``uv build`` runs the hatch hook and ships the subset inside the wheel."""
    dist = tmp_path / "dist"
    dist.mkdir()
    build = subprocess.run(
        [
            "uv",
            "build",
            "--wheel",
            "--package",
            "iwxxm-validate",
            "-o",
            str(dist),
        ],
        check=False,
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    assert build.returncode == 0, f"uv build failed:\n{build.stdout}\n{build.stderr}"

    wheels = sorted(dist.glob("*.whl"))
    assert wheels, f"no wheel in {dist}: {list(dist.iterdir())}"
    wheel = wheels[0]

    with zipfile.ZipFile(wheel) as zf:
        names = zf.namelist()
    joined = "\n".join(names)
    assert "iwxxm_validate/schemas/MANIFEST.json" in joined
    assert any("iwxxm_validate/schemas/iwxxm/2023-1/IWXXM/iwxxm.xsd" in n for n in names)
    assert any("iwxxm_validate/schemas/iwxxm/2025-2/IWXXM/rule/iwxxm.sch" in n for n in names)
    assert any("iwxxm_validate/schemas/iwxxm/externalSchema/" in n for n in names)
    assert any("united-states-catalog.xml" in n for n in names)
    assert "iwxxm-modelling" not in joined
    assert "/html/" not in joined
    assert "/examples/" not in joined

    # Install into a clean venv and resolve schemas without monorepo vendor.
    venv_dir = tmp_path / "venv"
    create = subprocess.run(
        ["uv", "venv", str(venv_dir)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert create.returncode == 0, create.stderr
    python = venv_dir / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    install = subprocess.run(
        ["uv", "pip", "install", "--python", str(python), str(wheel)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert install.returncode == 0, install.stderr

    probe = subprocess.run(
        [
            str(python),
            "-c",
            "from pathlib import Path; "
            "from iwxxm_validate.paths import packaged_schemas_root, xsd_path, schematron_path; "
            "root = packaged_schemas_root(); "
            "assert root is not None, 'packaged schemas missing'; "
            "assert xsd_path('2023-1').is_file(); "
            "assert schematron_path('2023-1').is_file(); "
            "assert 'site-packages' in str(xsd_path('2023-1')); "
            "print('ok')",
        ],
        check=False,
        capture_output=True,
        text=True,
        env={
            **dict(__import__("os").environ),
            "IWXXM_VALIDATE_REPO_ROOT": str(tmp_path / "no-vendor"),
        },
    )
    assert probe.returncode == 0, probe.stderr + probe.stdout
    assert "ok" in probe.stdout
