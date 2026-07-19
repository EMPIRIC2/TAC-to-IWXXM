"""T2.3 / F12: CLI smoke tests for ``tac-validate`` entry point."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

FIXTURES = Path(__file__).resolve().parent / "fixtures"
ACCEPT_METAR = FIXTURES / "accept" / "metar_basic.tac"
NEG_METAR = FIXTURES / "negative" / "metar" / "missing_cccc.tac"


def test_cli_module_main_exits_zero_on_accept() -> None:
    from tac_validate.cli import main

    assert main(["--product", "METAR", str(ACCEPT_METAR)]) == 0


def test_cli_module_main_exits_nonzero_on_negative() -> None:
    from tac_validate.cli import main

    assert main(["--product", "METAR", str(NEG_METAR)]) == 1


def test_cli_json_stdout_roundtrip() -> None:
    import io
    from contextlib import redirect_stdout

    from tac_validate.cli import main

    buf = io.StringIO()
    with redirect_stdout(buf):
        code = main(["--product", "METAR", "--json", str(NEG_METAR)])
    assert code == 1
    payload = json.loads(buf.getvalue())
    assert payload["ok"] is False
    assert payload["product"] == "METAR"
    assert any(i["code"] == "MISSING_CCCC" for i in payload["issues"])


def test_console_script_on_path() -> None:
    proc = subprocess.run(
        ["tac-validate", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    assert "tac-validate" in proc.stdout.lower() or "product" in proc.stdout.lower()


def test_cli_fixture_paths_exist() -> None:
    assert ACCEPT_METAR.is_file()
    assert NEG_METAR.is_file()
    assert sys.version_info >= (3, 12)
