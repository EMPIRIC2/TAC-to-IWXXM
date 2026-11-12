"""100% coverage for scripts/ci/format_contracts_pr_comment.py. [Corpus: api] [Corpus: tests]"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
from scripts.ci import format_contracts_pr_comment as mod

ROOT = Path(__file__).resolve().parents[2]
MARKER = "<!-- tooling-contracts-pr-comment -->"


def _oasdiff(
    status: str = "pass", findings: list[dict[str, str]] | None = None
) -> dict[str, object]:
    findings = findings or []
    return {
        "base": "origin/stage:docs/api/openapi.json",
        "revision": "docs/api/openapi.json",
        "frontend_copy": "apps/frontend/openapi/openapi.json",
        "fail_on": "ERR",
        "status": status,
        "breaking": {
            "status": status,
            "error": len(findings),
            "warning": 0,
            "info": 0,
            "findings": findings,
        },
        "parity": {"status": "pass"},
    }


def _schemathesis(status: str = "pass", failed: int = 0) -> dict[str, object]:
    results = [
        {"operation": f"POST /bad/{i}", "outcome": "failed", "detail": "500 | boom"}
        for i in range(failed)
    ]
    return {
        "status": status,
        "max_examples": 25,
        "schemathesis_version": "4.24.3",
        "counts": {"total": 2 + failed, "passed": 2, "failed": failed, "skipped": 0},
        "results": [
            {"operation": "GET /ok", "outcome": "passed", "detail": ""},
            *results,
        ],
    }


def test_load_report_missing_invalid_and_non_object(tmp_path: Path) -> None:
    assert mod.load_report(tmp_path / "nope.json") is None
    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    assert mod.load_report(bad) is None
    arr = tmp_path / "arr.json"
    arr.write_text("[]", encoding="utf-8")
    assert mod.load_report(arr) is None
    ok = tmp_path / "ok.json"
    ok.write_text('{"a": 1}', encoding="utf-8")
    assert mod.load_report(ok) == {"a": 1}


def test_badge_known_and_unknown() -> None:
    assert mod._badge("pass") == "PASS"
    assert mod._badge("weird") == "WEIRD"


def test_overall_status_precedence() -> None:
    assert mod.overall_status(None, None) == "skipped"
    assert mod.overall_status({"status": "pass"}, None) == "pass"
    assert mod.overall_status({"status": "pass"}, {"status": "fail"}) == "fail"


def test_render_not_run_blocks() -> None:
    assert "Not run" in "\n".join(mod.render_oasdiff(None))
    assert "Not run" in "\n".join(mod.render_schemathesis(None))


def test_render_oasdiff_defaults_when_sparse() -> None:
    text = "\n".join(mod.render_oasdiff({}))
    assert "no base spec" in text
    assert "0 error" in text


def test_render_oasdiff_findings_truncated() -> None:
    findings = [
        {
            "level": "error",
            "operation": "GET",
            "path": f"/p/{i}",
            "text": "removed | gone",
        }
        for i in range(mod.MAX_ROWS + 3)
    ]
    text = "\n".join(mod.render_oasdiff(_oasdiff("fail", findings)))
    assert "`GET /p/0`" in text
    assert "removed \\| gone" in text
    assert "3 more" in text


def test_render_oasdiff_findings_not_truncated_when_few() -> None:
    findings = [{"level": "error", "operation": "GET", "path": "/p", "text": "removed"}]
    text = "\n".join(mod.render_oasdiff(_oasdiff("fail", findings)))
    assert "more in" not in text


def test_render_schemathesis_defaults_and_failures() -> None:
    assert "0 operations" in "\n".join(mod.render_schemathesis({}))
    text = "\n".join(
        mod.render_schemathesis(_schemathesis("fail", failed=mod.MAX_ROWS + 2))
    )
    assert "FAIL" in text
    assert "500 \\| boom" in text
    assert "2 more" in text
    no_detail = {"results": [{"operation": "GET /x", "outcome": "failed"}]}
    assert "see CI log" in "\n".join(mod.render_schemathesis(no_detail))


def test_build_comment_combines_both_reports(tmp_path: Path) -> None:
    (tmp_path / "oasdiff.json").write_text(json.dumps(_oasdiff()), encoding="utf-8")
    (tmp_path / "schemathesis.json").write_text(
        json.dumps(_schemathesis()), encoding="utf-8"
    )
    body = mod.build_comment(tmp_path)
    assert body.startswith(MARKER)
    assert "Overall: **PASS**" in body
    assert "### oasdiff" in body
    assert "### Schemathesis" in body


def test_build_comment_empty_dir_is_skipped(tmp_path: Path) -> None:
    body = mod.build_comment(tmp_path)
    assert "Overall: **SKIPPED**" in body


def test_main_default_dir_and_explicit(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "oasdiff.json").write_text(
        json.dumps(_oasdiff("fail")), encoding="utf-8"
    )
    assert mod.main(["prog", str(tmp_path)]) == 0
    assert "Overall: **FAIL**" in capsys.readouterr().out
    assert mod.main(["prog"]) == 0
    assert MARKER in capsys.readouterr().out


def test_cli_entrypoint(tmp_path: Path) -> None:
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/ci/format_contracts_pr_comment.py"),
            str(tmp_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert proc.stdout.startswith(MARKER)
