"""T3.9 / E10-39: optional ``iwxxm-validate`` CLI smoke."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
VENDOR_EXAMPLE = REPO_ROOT / "vendor" / "schemas" / "iwxxm" / "2023-1" / "IWXXM" / "examples" / "metar-A3-1.xml"
ANNEX3_GOLDEN = REPO_ROOT / "packages" / "tac2iwxxm" / "tests" / "fixtures" / "annex3_golden" / "metar_basic.golden.xml"


def test_cli_fixture_paths_exist() -> None:
    assert VENDOR_EXAMPLE.is_file() or ANNEX3_GOLDEN.is_file()
    assert sys.version_info >= (3, 12)


def test_cli_module_main_exits_zero_on_example(monkeypatch: pytest.MonkeyPatch) -> None:
    import iwxxm_validate.paths as paths_mod
    from iwxxm_validate.cli import main
    from iwxxm_validate.native import rust_available
    from iwxxm_validate.paths import clear_path_caches

    # WMO vendor examples need the Rust/xmloxide path for full XSD resolution;
    # pure-lxml often returns SCHEMA_PARSE_ERROR on GML AngleType imports.
    if not rust_available():
        pytest.skip("iwxxm_validate._rust not built (make build-iwxxm-validate-native)")

    # Packaged subset is gitignored; maturin/hatch may materialise an incomplete tree
    # that xmloxide rejects (observation.xsd NS). Monorepo CI uses vendor pins.
    monkeypatch.setattr(paths_mod, "packaged_schemas_root", lambda: None)
    clear_path_caches()

    path = VENDOR_EXAMPLE if VENDOR_EXAMPLE.is_file() else ANNEX3_GOLDEN
    assert main(["--version", "2023-1", "--profile", "annex3", str(path)]) == 0


def test_cli_module_main_exits_nonzero_on_garbage(tmp_path: Path) -> None:
    from iwxxm_validate.cli import main

    bad = tmp_path / "bad.xml"
    bad.write_text("<not-iwxxm/>", encoding="utf-8")
    assert main(["--version", "2023-1", str(bad)]) == 1


def test_cli_json_stdout_roundtrip(tmp_path: Path) -> None:
    import io
    from contextlib import redirect_stdout

    from iwxxm_validate.cli import main

    bad = tmp_path / "bad.xml"
    bad.write_text("<not-iwxxm/>", encoding="utf-8")
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = main(["--version", "2023-1", "--json", str(bad)])
    assert code == 1
    payload = json.loads(buf.getvalue())
    assert payload["ok"] is False
    assert payload["iwxxm_version"] == "2023-1"
    assert isinstance(payload["issues"], list)


def test_cli_missing_file_exits_nonzero(tmp_path: Path) -> None:
    from iwxxm_validate.cli import main

    missing = tmp_path / "nope.xml"
    assert main([str(missing)]) == 1


def test_console_script_on_path() -> None:
    proc = subprocess.run(
        ["iwxxm-validate", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    assert "iwxxm-validate" in proc.stdout.lower() or "iwxxm" in proc.stdout.lower()
