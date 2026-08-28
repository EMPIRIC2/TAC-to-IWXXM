"""EV-080 M4 — 100% coverage for scripts/codegen/iwxxm_xsd.py."""

from __future__ import annotations

import json
import subprocess
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from scripts.codegen import iwxxm_xsd as mod

ROOT = Path(__file__).resolve().parents[2]


def test_fix_duplicate_field_defaults(tmp_path: Path) -> None:
    src = tmp_path / "m.py"
    src.write_text(
        "x = field(default=1,\n    default=1)\nField(default=2, default=2)\n",
        encoding="utf-8",
    )
    assert mod.fix_duplicate_field_defaults(tmp_path) == 1
    fixed = src.read_text(encoding="utf-8")
    assert fixed.count("default=") == 2


def test_version_package() -> None:
    assert mod._version_package("2025-2") == "v2025_2"
    assert mod._version_package("2023.1") == "v2023_1"


def test_load_and_resolve_versions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    vendor_iwxxm = tmp_path / "vendor" / "schemas" / "iwxxm"
    version_dir = vendor_iwxxm / "2099-9" / "IWXXM"
    version_dir.mkdir(parents=True)
    (version_dir / "iwxxm.xsd").write_text("<xsd/>", encoding="utf-8")
    monkeypatch.setattr(mod, "VENDOR_IWXXM", vendor_iwxxm)

    versions = mod.load_manifest_versions()
    assert versions == ["2099-9"]
    assert mod.resolve_versions(None) == ["2099-9"]
    assert mod.resolve_versions(["2099-9"]) == ["2099-9"]
    with pytest.raises(FileNotFoundError, match="not in vendor pin"):
        mod.resolve_versions(["missing"])

    empty_vendor = tmp_path / "empty"
    empty_vendor.mkdir()
    monkeypatch.setattr(mod, "VENDOR_IWXXM", empty_vendor)
    with pytest.raises(FileNotFoundError, match="no IWXXM version trees"):
        mod.load_manifest_versions()

    monkeypatch.setattr(mod, "VENDOR_IWXXM", tmp_path / "nope")
    with pytest.raises(FileNotFoundError, match="vendor iwxxm missing"):
        mod.load_manifest_versions()


def test_write_package_init_creates_and_updates(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    out = tmp_path / "packages" / "shared" / "src" / "metar_shared" / "iwxxm_xsd"
    monkeypatch.setattr(mod, "OUT_ROOT", out)
    monkeypatch.setattr(mod, "MANIFEST", tmp_path / "vendor" / "manifest.json")
    mod.write_package_init(["2025-2"])
    assert (out / "__init__.py").is_file()
    assert (out / "README.md").is_file()
    status = json.loads((out / "STATUS.json").read_text(encoding="utf-8"))
    assert status["versions"] == ["2025-2"]
    assert status["manifest_pin"] is None

    manifest = tmp_path / "vendor" / "manifest.json"
    manifest.parent.mkdir(parents=True)
    manifest.write_text(
        json.dumps({"bundles": {"iwxxm": {"tag": "2025-2"}}}), encoding="utf-8"
    )
    mod.write_package_init(["2025-2"])
    status2 = json.loads((out / "STATUS.json").read_text(encoding="utf-8"))
    assert status2["manifest_pin"]["tag"] == "2025-2"


def test_check_only(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    vendor_iwxxm = tmp_path / "vendor" / "schemas" / "iwxxm"
    version_dir = vendor_iwxxm / "2025-2" / "IWXXM"
    version_dir.mkdir(parents=True)
    (version_dir / "iwxxm.xsd").write_text("<xsd/>", encoding="utf-8")
    monkeypatch.setattr(mod, "VENDOR_IWXXM", vendor_iwxxm)
    monkeypatch.setattr(mod, "OUT_ROOT", tmp_path / "out")
    monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(mod, "MANIFEST", tmp_path / "missing-manifest.json")
    assert mod.check_only() == 1

    manifest = tmp_path / "vendor" / "manifest.json"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(mod, "MANIFEST", manifest)
    assert mod.check_only() == 0


def test_generate_version_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    vendor_iwxxm = tmp_path / "vendor" / "schemas" / "iwxxm"
    version_dir = vendor_iwxxm / "2025-2" / "IWXXM"
    version_dir.mkdir(parents=True)
    monkeypatch.setattr(mod, "VENDOR_IWXXM", vendor_iwxxm)
    monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)

    with pytest.raises(FileNotFoundError, match="entry XSD missing"):
        mod.generate_version("2025-2")

    (version_dir / "iwxxm.xsd").write_text("<xsd/>", encoding="utf-8")
    bad_out = tmp_path / "bad"
    bad_out.mkdir()
    with pytest.raises(ValueError, match="out_root must end with"):
        mod.generate_version("2025-2", out_root=bad_out)


@pytest.mark.slow
def test_generate_version_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    vendor_iwxxm = ROOT / "vendor" / "schemas" / "iwxxm"
    monkeypatch.setattr(mod, "VENDOR_IWXXM", vendor_iwxxm)
    monkeypatch.setattr(mod, "REPO_ROOT", ROOT)

    out_root = tmp_path / "src" / "metar_shared" / "iwxxm_xsd"
    out_root.mkdir(parents=True)
    (tmp_path / "src" / "metar_shared" / "__init__.py").write_text("", encoding="utf-8")
    (out_root / "__init__.py").write_text("", encoding="utf-8")

    summary = mod.generate_version("2025-2", entry="metarSpeci.xsd", out_root=out_root)
    assert summary["py_files"] > 0
    assert summary["output"] is not None


def test_patch_xsdata_generators_soft_fail(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pytest.importorskip("xsdata")
    from xsdata.formats.dataclass.generator import DataclassGenerator

    def _boom_ruff(self: object, file_paths: list[str]) -> None:
        raise RuntimeError("ruff broke")

    def _boom_validate(self: object) -> None:
        raise RuntimeError("imports broke")

    monkeypatch.setattr(DataclassGenerator, "ruff_code", _boom_ruff)
    monkeypatch.setattr(DataclassGenerator, "validate_imports", _boom_validate)
    mod._patch_xsdata_generators()

    err = StringIO()
    old = sys.stderr
    sys.stderr = err
    try:
        DataclassGenerator.ruff_code(MagicMock(), [str(tmp_path)])
    finally:
        sys.stderr = old
    assert "ruff soft-fail" in err.getvalue()

    err2 = StringIO()
    sys.stderr = err2
    try:
        DataclassGenerator.validate_imports(MagicMock())
    finally:
        sys.stderr = err2
    assert "import-validation soft-fail" in err2.getvalue()


def test_main_branches(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(mod, "check_only", lambda: 0)
    assert mod.main(["--check"]) == 0

    monkeypatch.setattr(
        mod,
        "resolve_versions",
        lambda _v: (_ for _ in ()).throw(FileNotFoundError("bad pin")),
    )
    err = StringIO()
    old = sys.stderr
    sys.stderr = err
    try:
        assert mod.main([]) == 1
    finally:
        sys.stderr = old
    assert "error:" in err.getvalue()

    monkeypatch.setattr(mod, "resolve_versions", lambda _v: ["2025-2"])
    monkeypatch.setattr(mod, "write_package_init", lambda _v: None)
    monkeypatch.setattr(
        mod,
        "generate_version",
        lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    err2 = StringIO()
    sys.stderr = err2
    try:
        assert mod.main(["--version", "2025-2"]) == 1
    finally:
        sys.stderr = err2
    assert "codegen failed" in err2.getvalue()

    monkeypatch.setattr(
        mod,
        "generate_version",
        lambda *_a, **_k: {
            "version": "2025-2",
            "py_files": 1,
            "bytes": 100,
            "package": "pkg",
        },
    )
    monkeypatch.setattr(mod, "OUT_ROOT", tmp_path / "out")
    (tmp_path / "out").mkdir()
    assert mod.main(["--version", "2025-2"]) == 0
    assert (tmp_path / "out" / "LAST_RUN.json").is_file()


def test_generate_version_rmtree_and_fixup_message(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    pytest.importorskip("xsdata")

    vendor_iwxxm = tmp_path / "vendor" / "schemas" / "iwxxm"
    version_dir = vendor_iwxxm / "2025-2" / "IWXXM"
    version_dir.mkdir(parents=True)
    (version_dir / "iwxxm.xsd").write_text("<xsd/>", encoding="utf-8")
    monkeypatch.setattr(mod, "VENDOR_IWXXM", vendor_iwxxm)
    monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)

    out_root = tmp_path / "src" / "metar_shared" / "iwxxm_xsd"
    out_root.mkdir(parents=True)
    out_dir = out_root / "v2025_2"
    out_dir.mkdir()
    (out_dir / "stale.py").write_text("stale\n", encoding="utf-8")

    class FakeTransformer:
        def __init__(self, config: object | None = None) -> None:
            pass

        def process(self, uris: list[str]) -> None:
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / "broken.py").write_text(
                "x = field(default=1,\n    default=1)\n",
                encoding="utf-8",
            )

    fake_cfg = MagicMock()
    monkeypatch.setattr(
        "xsdata.models.config.GeneratorConfig.create",
        lambda: fake_cfg,
    )
    monkeypatch.setattr(
        "xsdata.codegen.transformer.ResourceTransformer",
        FakeTransformer,
    )

    summary = mod.generate_version("2025-2", out_root=out_root)
    assert not (out_dir / "stale.py").exists()
    assert summary["py_files"] >= 1
    assert "fixed duplicate default=" in capsys.readouterr().err


def test_generate_version_no_fixup_message(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    pytest.importorskip("xsdata")

    vendor_iwxxm = tmp_path / "vendor" / "schemas" / "iwxxm"
    version_dir = vendor_iwxxm / "2025-2" / "IWXXM"
    version_dir.mkdir(parents=True)
    (version_dir / "iwxxm.xsd").write_text("<xsd/>", encoding="utf-8")
    monkeypatch.setattr(mod, "VENDOR_IWXXM", vendor_iwxxm)
    monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)

    out_root = tmp_path / "src" / "metar_shared" / "iwxxm_xsd"
    out_root.mkdir(parents=True)

    class FakeTransformer:
        def __init__(self, config: object | None = None) -> None:
            pass

        def process(self, uris: list[str]) -> None:
            out_dir = out_root / "v2025_2"
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / "clean.py").write_text("x = 1\n", encoding="utf-8")

    fake_cfg = MagicMock()
    monkeypatch.setattr(
        "xsdata.models.config.GeneratorConfig.create",
        lambda: fake_cfg,
    )
    monkeypatch.setattr(
        "xsdata.codegen.transformer.ResourceTransformer",
        FakeTransformer,
    )

    summary = mod.generate_version("2025-2", out_root=out_root)
    assert summary["py_files"] == 1
    assert capsys.readouterr().err == ""


def test_generate_version_skips_fixup_when_out_dir_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pytest.importorskip("xsdata")

    vendor_iwxxm = tmp_path / "vendor" / "schemas" / "iwxxm"
    version_dir = vendor_iwxxm / "2025-2" / "IWXXM"
    version_dir.mkdir(parents=True)
    (version_dir / "iwxxm.xsd").write_text("<xsd/>", encoding="utf-8")
    monkeypatch.setattr(mod, "VENDOR_IWXXM", vendor_iwxxm)
    monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)

    out_root = tmp_path / "src" / "metar_shared" / "iwxxm_xsd"
    out_root.mkdir(parents=True)

    class FakeTransformer:
        def __init__(self, config: object | None = None) -> None:
            pass

        def process(self, uris: list[str]) -> None:
            return

    fake_cfg = MagicMock()
    monkeypatch.setattr(
        "xsdata.models.config.GeneratorConfig.create",
        lambda: fake_cfg,
    )
    monkeypatch.setattr(
        "xsdata.codegen.transformer.ResourceTransformer",
        FakeTransformer,
    )

    summary = mod.generate_version("2025-2", out_root=out_root)
    assert summary["py_files"] == 0
    assert summary["output"] is None


def test_main_entrypoint_runpy(monkeypatch: pytest.MonkeyPatch) -> None:
    import runpy

    monkeypatch.setattr(sys, "argv", ["iwxxm_xsd.py", "--check"])
    with pytest.raises(SystemExit) as exc:
        runpy.run_path(str(ROOT / "scripts/codegen/iwxxm_xsd.py"), run_name="__main__")
    assert exc.value.code == 0


def test_main_entrypoint_subprocess() -> None:

    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/codegen/iwxxm_xsd.py"), "--check"],
        check=False,
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert proc.returncode == 0
