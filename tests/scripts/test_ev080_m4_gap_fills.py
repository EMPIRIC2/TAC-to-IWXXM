"""EV-080 M4 — final gap fills for 100% scripts coverage."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest
from scripts.bench import validation_stack as validation_stack_mod
from scripts.ci import format_coverage_pr_comment as coverage_comment_mod
from scripts.codegen import iwxxm_xsd as iwxxm_mod
from scripts.deploy import trigger_render_image_deploy as deploy_mod
from scripts.ops import verify_supabase_to_do_migrate as verify_mod
from scripts.ops.run_supabase_to_do_migrate import copy_table_rows
from tests.scripts.conftest import REPO_ROOT, load_script
from tests.scripts.test_run_supabase_to_do_migrate import _FakeConn

regen = load_script("tac-validate/regen_issue_catalog.py")


def test_matrix_as_dict_serializes_layer_cost_matrix() -> None:
    cell = validation_stack_mod.LayerTiming(
        "xsd",
        "single_metar",
        0.01,
        0.02,
        "ok",
    )
    matrix = validation_stack_mod.LayerCostMatrix(
        cells=(cell,),
        implemented=True,
        iwxxm_version="2025-2",
        profile="annex3",
    )
    payload = validation_stack_mod.matrix_as_dict(matrix)
    assert payload["implemented"] is True
    assert payload["iwxxm_version"] == "2025-2"
    assert payload["cells"][0]["layer"] == "xsd"


def test_package_label_packages_value_error_fallback(tmp_path: Path) -> None:
    root = tmp_path / "root"
    tricky = root / "mypackages" / "foo" / "coverage.xml"
    tricky.parent.mkdir(parents=True)
    tricky.touch()
    assert coverage_comment_mod.package_label(tricky, root) == "foo"


def _fake_xsdata_transformer(
    monkeypatch: pytest.MonkeyPatch,
    pkg_dir: Path,
    *,
    py_body: str = "field(default=1, default=1)\n",
) -> None:
    class _FakeTransformer:
        def __init__(self, config: object | None = None) -> None:
            self.config = config

        def process(self, urls: list[str]) -> None:
            pkg_dir.mkdir(parents=True, exist_ok=True)
            (pkg_dir / "generated.py").write_text(py_body, encoding="utf-8")

    fake_cfg = SimpleNamespace(
        output=SimpleNamespace(
            package="",
            format="pydantic",
            structure_style="filenames",
            docstring_style="numpy",
            max_line_length=120,
            relative_imports=True,
            include_header=True,
        )
    )

    monkeypatch.setattr(
        "xsdata.codegen.transformer.ResourceTransformer",
        _FakeTransformer,
    )
    monkeypatch.setattr(
        "xsdata.models.config.GeneratorConfig",
        SimpleNamespace(create=lambda: fake_cfg),
    )
    monkeypatch.setattr("xsdata.models.config.OutputFormat", lambda value: value)
    monkeypatch.setattr(
        "xsdata.models.config.StructureStyle",
        SimpleNamespace(FILENAMES="filenames"),
    )
    monkeypatch.setattr(
        "xsdata.models.config.DocstringStyle",
        SimpleNamespace(NUMPY="numpy"),
    )


def _iwxxm_vendor(tmp_path: Path) -> Path:
    vendor_iwxxm = tmp_path / "vendor" / "schemas" / "iwxxm"
    version_dir = vendor_iwxxm / "2025-2" / "IWXXM"
    version_dir.mkdir(parents=True)
    (version_dir / "metarSpeci.xsd").write_text("<xsd/>", encoding="utf-8")
    return vendor_iwxxm


def test_fix_duplicate_field_defaults_noop_branch(tmp_path: Path) -> None:
    src = tmp_path / "clean.py"
    src.write_text("x = 1\n", encoding="utf-8")
    assert iwxxm_mod.fix_duplicate_field_defaults(tmp_path) == 0


def test_generate_version_rmtree_existing_out_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    vendor_iwxxm = _iwxxm_vendor(tmp_path)
    monkeypatch.setattr(iwxxm_mod, "VENDOR_IWXXM", vendor_iwxxm)
    monkeypatch.setattr(iwxxm_mod, "REPO_ROOT", tmp_path)

    out_root = tmp_path / "src" / "metar_shared" / "iwxxm_xsd"
    pkg_dir = out_root / "v2025_2"
    pkg_dir.mkdir(parents=True)
    (pkg_dir / "stale.py").write_text("stale\n", encoding="utf-8")

    removed: list[Path] = []
    real_rmtree = iwxxm_mod.shutil.rmtree

    def _rmtree(path: Path) -> None:
        removed.append(path)
        real_rmtree(path)

    monkeypatch.setattr(iwxxm_mod.shutil, "rmtree", _rmtree)
    _fake_xsdata_transformer(monkeypatch, pkg_dir, py_body="x = 1\n")

    summary = iwxxm_mod.generate_version(
        "2025-2", entry="metarSpeci.xsd", out_root=out_root
    )
    assert removed == [pkg_dir]
    assert summary["py_files"] >= 1


def test_generate_version_output_rel_value_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    vendor_iwxxm = _iwxxm_vendor(tmp_path)
    monkeypatch.setattr(iwxxm_mod, "VENDOR_IWXXM", vendor_iwxxm)
    monkeypatch.setattr(iwxxm_mod, "REPO_ROOT", tmp_path / "other-root")

    out_root = tmp_path / "src" / "metar_shared" / "iwxxm_xsd"
    pkg_dir = out_root / "v2025_2"
    _fake_xsdata_transformer(monkeypatch, pkg_dir, py_body="x = 1\n")

    summary = iwxxm_mod.generate_version(
        "2025-2", entry="metarSpeci.xsd", out_root=out_root
    )
    assert summary["output"] == str(pkg_dir)


def test_generate_version_fixup_prints_stderr(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    vendor_iwxxm = _iwxxm_vendor(tmp_path)
    monkeypatch.setattr(iwxxm_mod, "VENDOR_IWXXM", vendor_iwxxm)
    monkeypatch.setattr(iwxxm_mod, "REPO_ROOT", tmp_path)

    out_root = tmp_path / "src" / "metar_shared" / "iwxxm_xsd"
    pkg_dir = out_root / "v2025_2"
    _fake_xsdata_transformer(monkeypatch, pkg_dir)

    summary = iwxxm_mod.generate_version(
        "2025-2", entry="metarSpeci.xsd", out_root=out_root
    )
    err = capsys.readouterr().err
    assert summary["py_files"] >= 1
    assert "fixed duplicate default=" in err


def test_trigger_image_deploy_rest_not_suspended_continues() -> None:
    def http(url: str, method: str, headers: object, body: object) -> tuple[int, str]:
        if "imgURL=" in url:
            return 500, "hook fail"
        if method == "POST":
            return 500, "internal error"
        return 404, ""

    result = deploy_mod.trigger_image_deploy(
        deploy_hook="https://api.render.com/deploy/srv-abc?k=1",
        image_url="img:1",
        api_key="key",
        http=http,
        hook_retries=1,
        allow_hook_without_imgurl=False,
        skip_if_suspended=True,
    )
    assert result.ok is False


def test_trigger_image_deploy_fallback_not_suspended_continues() -> None:
    def http(url: str, method: str, headers: object, body: object) -> tuple[int, str]:
        if "imgURL=" in url:
            return 500, "hook img fail"
        return 500, "internal error"

    result = deploy_mod.trigger_image_deploy(
        deploy_hook="https://api.render.com/deploy/srv-abc?k=1",
        image_url="img:1",
        api_key=None,
        http=http,
        hook_retries=1,
        allow_hook_without_imgurl=True,
        skip_if_suspended=True,
    )
    assert result.ok is False


def test_trigger_image_deploy_rest_suspended_skip() -> None:
    def http(url: str, method: str, headers: object, body: object) -> tuple[int, str]:
        if "imgURL=" in url:
            return 500, "hook fail"
        if method == "POST":
            return 400, "service is suspended"
        return 404, ""

    result = deploy_mod.trigger_image_deploy(
        deploy_hook="https://api.render.com/deploy/srv-abc?k=1",
        image_url="img:1",
        api_key="key",
        http=http,
        hook_retries=1,
        allow_hook_without_imgurl=False,
        skip_if_suspended=True,
    )
    assert result.method == "skipped_suspended"


def test_trigger_image_deploy_final_hook_suspended_skip() -> None:
    result = deploy_mod.trigger_image_deploy(
        deploy_hook="https://api.render.com/deploy/srv-abc?k=1",
        image_url="img:1",
        api_key=None,
        http=lambda url, *_a: (
            (500, "service is suspended") if "imgURL=" in url else (500, "x")
        ),
        hook_retries=1,
        allow_hook_without_imgurl=False,
        skip_if_suspended=True,
    )
    assert result.method == "skipped_suspended"


def test_trigger_image_deploy_fallback_suspended_skip() -> None:
    def http(url: str, method: str, headers: object, body: object) -> tuple[int, str]:
        if "imgURL=" in url:
            return 500, "hook img fail"
        return 409, "cannot deploy suspended service"

    result = deploy_mod.trigger_image_deploy(
        deploy_hook="https://api.render.com/deploy/srv-abc?k=1",
        image_url="img:1",
        api_key=None,
        http=http,
        hook_retries=1,
        allow_hook_without_imgurl=True,
        skip_if_suspended=True,
    )
    assert result.method == "skipped_suspended"


def test_normalize_database_url_rewrites_asyncpg() -> None:
    assert (
        verify_mod.normalize_database_url("postgresql+asyncpg://u:p@h/db")
        == "postgresql+psycopg://u:p@h/db"
    )


def test_copy_table_rows_exact_batch_multiple_skips_tail() -> None:
    columns = __import__(
        "scripts.ops.run_supabase_to_do_migrate", fromlist=["COPY_COLUMNS"]
    ).COPY_COLUMNS["tac_work_sessions"]
    row = tuple(f"v{i}" for i in range(len(columns)))
    source = _FakeConn(
        counts={"tac_work_sessions": 2},
        ids={"tac_work_sessions": ["1", "2"]},
        full_rows={"tac_work_sessions": [row, row]},
    )
    target = _FakeConn(
        counts={"tac_work_sessions": 0},
        ids={"tac_work_sessions": []},
        full_rows={},
    )
    _, _, missing, inserted = copy_table_rows(
        source,
        target,
        "tac_work_sessions",
        batch_size=2,
        apply=True,  # type: ignore[arg-type]
    )
    assert missing == 2
    assert inserted == 2
    assert len(target.insert_batches) == 1


def test_export_tc_m003_golden_inserts_repo_root_on_import() -> None:
    repo = str(REPO_ROOT)
    saved_path = sys.path.copy()
    for name in list(sys.modules):
        if name.endswith("export_tc_m003_golden") or name == "ev080_export_tc_m003":
            del sys.modules[name]
    try:
        sys.path[:] = [p for p in sys.path if p != repo]
        baseline = ModuleType("tests.migration.gifts_baseline")
        baseline.convert_tac_bulletin_to_observation_xml = lambda tac: "<xml/>"
        migration = ModuleType("tests.migration")
        migration.gifts_baseline = baseline
        tests_pkg = ModuleType("tests")
        tests_pkg.migration = migration
        sys.modules["tests"] = tests_pkg
        sys.modules["tests.migration"] = migration
        sys.modules["tests.migration.gifts_baseline"] = baseline
        canonical = ModuleType("metar_shared.xml_canonical")
        canonical.canonicalize_xml = lambda xml: xml
        sys.modules["metar_shared.xml_canonical"] = canonical

        spec = importlib.util.spec_from_file_location(
            "ev080_export_tc_m003",
            REPO_ROOT / "scripts/test-data/export_tc_m003_golden.py",
        )
        assert spec is not None
        assert spec.loader is not None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        assert repo in sys.path
    finally:
        sys.path[:] = saved_path


def test_regen_stable_generated_preserves_nonempty_prev(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    js = tmp_path / "catalog.json"
    rows = [{"code": "A"}]
    js.write_text(
        json.dumps({"source": "src", "issues": rows, "generated": "2019-06-15"}),
        encoding="utf-8",
    )
    monkeypatch.setattr(regen, "CATALOG_JSON", js)
    assert regen._stable_generated(rows, "src") == "2019-06-15"


def test_regen_stable_generated_empty_prev_string_falls_back_to_today(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    js = tmp_path / "catalog.json"
    rows = [{"code": "A"}]
    js.write_text(
        json.dumps({"source": "src", "issues": rows, "generated": ""}),
        encoding="utf-8",
    )
    monkeypatch.setattr(regen, "CATALOG_JSON", js)
    assert regen._stable_generated(rows, "src") != ""
