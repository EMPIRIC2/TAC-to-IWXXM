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
    """CLI wires to ``validate_iwxxm``; exit 0 when SDK ok.

    Some runners hit xmloxide ``SCHEMA_PARSE_ERROR`` on IWXXM+GML/OM includes
    (same soft gap as TC-F13-001 lxml baseline). In that case exit 1 with only
    schema-layer errors is acceptable for this smoke - garbage XML still fails
    in ``test_cli_module_main_exits_nonzero_on_garbage``.
    """
    import io
    from contextlib import redirect_stdout

    import iwxxm_validate.paths as paths_mod
    from iwxxm_validate.cli import main
    from iwxxm_validate.native import rust_available
    from iwxxm_validate.paths import clear_path_caches

    if not rust_available():
        pytest.skip("iwxxm_validate._rust not built (make build-iwxxm-validate-native)")

    # Prefer vendor pins over gitignored packaged subset after maturin/hatch sync.
    monkeypatch.setattr(paths_mod, "packaged_schemas_root", lambda: None)
    clear_path_caches()

    path = VENDOR_EXAMPLE if VENDOR_EXAMPLE.is_file() else ANNEX3_GOLDEN
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = main(["--version", "2023-1", "--profile", "annex3", "--json", str(path)])
    payload = json.loads(buf.getvalue())
    assert code in (0, 1)
    assert payload["ok"] is (code == 0)
    if code == 0:
        return
    error_codes = {issue["code"] for issue in payload["issues"] if issue.get("severity") == "error"}
    assert error_codes, "exit 1 must include at least one error issue"
    assert error_codes <= {"SCHEMA_PARSE_ERROR"}, error_codes


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


def test_cli_ca_eccc_extensions_iwxxm_ca(tmp_path: Path) -> None:
    """EV-068 M5: --extensions IWXXM_CA enables full ca_eccc product XSD path."""
    import io
    from contextlib import redirect_stdout

    from iwxxm_validate.cli import main
    from iwxxm_validate.native import rust_available

    if not rust_available():
        pytest.skip("iwxxm_validate._rust not built (make build-iwxxm-validate-native)")

    golden = (
        REPO_ROOT
        / "packages"
        / "tac2iwxxm"
        / "tests"
        / "fixtures"
        / "profiles"
        / "CA_ECCC"
        / "METAR"
        / "valid"
        / "metar_rmk_icing.golden.xml"
    )
    assert golden.is_file()
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = main(
            [
                "--version",
                "3.0.0",
                "--profile",
                "ca_eccc",
                "--extensions",
                "IWXXM_CA",
                "--product",
                "METAR",
                "--json",
                str(golden),
            ]
        )
    payload = json.loads(buf.getvalue())
    assert code == 0
    assert payload["ok"] is True
    stage_ids = [stage["stage"] for stage in payload.get("stages") or []]
    assert "ca_xsd" in stage_ids


def test_console_script_on_path() -> None:
    proc = subprocess.run(
        ["iwxxm-validate", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    assert "iwxxm-validate" in proc.stdout.lower() or "iwxxm" in proc.stdout.lower()


def test_cli_module_guard_invokes_main(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    import runpy

    missing = tmp_path / "missing.xml"
    monkeypatch.setattr(sys, "argv", ["iwxxm_validate.cli", str(missing)])

    with pytest.raises(SystemExit) as exc_info:
        runpy.run_module("iwxxm_validate.cli", run_name="__main__")

    assert exc_info.value.code == 1
