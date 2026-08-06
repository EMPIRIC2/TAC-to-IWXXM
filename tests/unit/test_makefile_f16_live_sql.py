"""EV-039 / AC7 — Makefile F16 live SQL harness targets (T1.3).

[Corpus: product §F16] [Corpus: tests] [Corpus: tech-spec]
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAKEFILE = ROOT / "Makefile"


def _makefile_recipe(makefile: str, target: str) -> str:
    pattern = re.compile(rf"^{re.escape(target)}:(.*)$", re.M)
    match = pattern.search(makefile)
    assert match is not None, f"missing Makefile target {target}"
    start = match.end()
    lines = [match.group(1)]
    for line in makefile[start:].splitlines()[1:]:
        if (
            not line.startswith("\t")
            and line.strip()
            and not line.startswith("#")
            and re.match(r"^[A-Za-z0-9_.-]+:", line)
        ):
            break
        if (
            line.startswith("\t")
            or line.endswith("\\")
            or (lines and lines[-1].endswith("\\"))
        ):
            lines.append(line)
        elif not line.strip():
            continue
        else:
            break
    return "\n".join(lines)


def test_makefile_declares_f16_live_sql_target() -> None:
    content = MAKEFILE.read_text(encoding="utf-8")
    assert "test-e2e-f16-live-sql:" in content
    assert "F16_LIVE_SQL" in content


def test_f16_live_sql_defaults_off_in_ci() -> None:
    """S05.M2 — CI must not force LIVE SQL; local default is on."""
    content = MAKEFILE.read_text(encoding="utf-8")
    # F16_LIVE_SQL ?= $(if $(CI),0,1)
    assert re.search(
        r"F16_LIVE_SQL\s*\?=\s*\$\(if\s+\$\(CI\),0,1\)",
        content,
    ), "F16_LIVE_SQL must default to 0 when CI is set, else 1"


def test_test_live_e2e_honors_f16_live_sql_flag() -> None:
    recipe = _makefile_recipe(MAKEFILE.read_text(encoding="utf-8"), "test-live-e2e")
    assert "F16_LIVE_SQL" in recipe
    assert "test-e2e-f16-live-sql" in recipe


def test_test_e2e_f16_live_sql_uses_compose_and_teardown() -> None:
    recipe = _makefile_recipe(
        MAKEFILE.read_text(encoding="utf-8"), "test-e2e-f16-live-sql"
    )
    assert "compose-mock-byoc-up" in recipe
    assert "compose-mock-byoc-down" in recipe
    assert "playwright" in recipe.lower() or "uj027-f16-live-sql" in recipe


def test_compose_mock_byoc_up_can_skip_sqlserver() -> None:
    """S05.L1 / T2.4 — omit byoc-sqlserver from --wait when F16_SKIP_SQLSERVER=1."""
    recipe = _makefile_recipe(
        MAKEFILE.read_text(encoding="utf-8"), "compose-mock-byoc-up"
    )
    assert "F16_SKIP_SQLSERVER" in recipe
    assert "byoc-postgres" in recipe
    assert "byoc-mysql" in recipe
