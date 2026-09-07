"""EV-080 coverage fills for scripts/test-data/export_tc_m003_golden.py."""

from __future__ import annotations

import json
import sys
import types
from pathlib import Path
from unittest.mock import patch

import pytest
from tests.scripts.conftest import REPO_ROOT, load_script


@pytest.fixture(scope="module")
def export_mod():
    baseline = types.ModuleType("tests.migration.gifts_baseline")
    baseline.convert_tac_bulletin_to_observation_xml = lambda tac: "<xml/>"
    migration = types.ModuleType("tests.migration")
    migration.gifts_baseline = baseline
    tests_pkg = types.ModuleType("tests")
    tests_pkg.migration = migration
    sys.modules.setdefault("tests", tests_pkg)
    sys.modules["tests.migration"] = migration
    sys.modules["tests.migration.gifts_baseline"] = baseline
    return load_script("test-data/export_tc_m003_golden.py")


def test_module_inserts_repo_root_on_import() -> None:
    baseline = types.ModuleType("tests.migration.gifts_baseline")
    baseline.convert_tac_bulletin_to_observation_xml = lambda tac: "<xml/>"
    migration = types.ModuleType("tests.migration")
    migration.gifts_baseline = baseline
    tests_pkg = types.ModuleType("tests")
    tests_pkg.migration = migration
    sys.modules.setdefault("tests", tests_pkg)
    sys.modules["tests.migration"] = migration
    sys.modules["tests.migration.gifts_baseline"] = baseline

    root = str(REPO_ROOT)
    saved = sys.path.copy()
    try:
        while root in sys.path:
            sys.path.remove(root)
        mod = load_script(
            "test-data/export_tc_m003_golden.py",
            module_name="ev080_export_tc_path_insert",
        )
        assert root in sys.path
        assert mod.ROOT == REPO_ROOT
    finally:
        sys.path[:] = saved
        sys.modules.pop("ev080_export_tc_path_insert", None)


def test_export_golden_baselines(
    export_mod: types.ModuleType, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    golden = tmp_path / "golden"
    cases = golden / "cases"
    monkeypatch.setattr(export_mod, "GOLDEN_DIR", golden)
    monkeypatch.setattr(export_mod, "CASES_DIR", cases)

    with patch.object(export_mod, "canonicalize_xml", return_value="<canonical/>"):
        export_mod.export_golden_baselines()

    manifest = json.loads((golden / "manifest.json").read_text(encoding="utf-8"))
    assert len(manifest["cases"]) == len(export_mod.FIXTURE_CASES)
    assert (cases / "kjfk_basic.tac").is_file()
    assert (cases / "kjfk_basic.golden.xml").read_text(
        encoding="utf-8"
    ) == "<canonical/>\n"
