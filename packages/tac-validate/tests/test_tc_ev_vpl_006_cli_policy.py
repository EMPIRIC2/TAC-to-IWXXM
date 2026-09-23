"""TC-EV-VPL-006 — tac-validate CLI --profile / --policy (#1216 M5)."""

from __future__ import annotations

import builtins
import io
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import pytest
from tac_validate.cli import _bound_policy, main
from tac_validate.models import Issue, LintReport
from tac_validate.policy import PolicyError, apply_policy_to_report

FIXTURES = Path(__file__).resolve().parent / "fixtures"
NEG_METAR = FIXTURES / "negative" / "metar" / "missing_cccc.tac"


def test_profile_alias_still_lints(monkeypatch: pytest.MonkeyPatch) -> None:
    err = io.StringIO()
    with redirect_stderr(err):
        code = main(["--product", "METAR", "--profile", "ICAO_2025", str(NEG_METAR)])
    assert code == 1
    assert err.getvalue() == ""


def test_unknown_profile_exits_2() -> None:
    err = io.StringIO()
    with redirect_stderr(err):
        code = main(["--product", "METAR", "--profile", "nope", str(NEG_METAR)])
    assert code == 2
    assert "unknown conversion profile" in err.getvalue()


def test_unknown_policy_exits_2() -> None:
    err = io.StringIO()
    with redirect_stderr(err):
        code = main(["--product", "METAR", "--policy", "missing-policy", str(NEG_METAR)])
    assert code == 2
    assert "unknown TAC quality policy" in err.getvalue()


def test_policy_severity_override_and_filter(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    overlay = tmp_path / "policies"
    overlay.mkdir()
    (overlay / "sev.yaml").write_text(
        "\n".join(
            [
                "schema_version: 1",
                "id: sev-only",
                "lifecycle: draft",
                "product: metar",
                "select: [MISSING_CCCC]",
                "severity:",
                "  MISSING_CCCC: warning",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("TAC_VALIDATE_POLICY_DIR", str(overlay))
    out = io.StringIO()
    with redirect_stdout(out):
        code = main(["--product", "METAR", "--policy", "sev-only", "--json", str(NEG_METAR)])
    assert code == 0
    assert "warning" in out.getvalue()


def test_apply_policy_unknown_id(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    report = LintReport(
        ok=False,
        product="METAR",
        issues=[
            Issue(severity="error", code="MISSING_CCCC", message="m"),
            Issue(severity="error", code="MISSING_WIND", message="w"),
        ],
    )
    with pytest.raises(PolicyError, match="unknown TAC quality policy"):
        apply_policy_to_report(report, "no-such")
    overlay = tmp_path / "policies"
    overlay.mkdir()
    (overlay / "only.yaml").write_text(
        "schema_version: 1\nid: only-cccc\nlifecycle: draft\nproduct: metar\nselect: [MISSING_CCCC]\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("TAC_VALIDATE_POLICY_DIR", str(overlay))
    filtered = apply_policy_to_report(report, "only-cccc")
    assert [issue.code for issue in filtered.issues] == ["MISSING_CCCC"]


def test_resolver_import_error_falls_back(monkeypatch: pytest.MonkeyPatch) -> None:
    real_import = builtins.__import__

    def _blocked(name: str, *args: object, **kwargs: object) -> object:
        if name == "tac2iwxxm.profile_resolve":
            raise ImportError(name)
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _blocked)
    emit, policy_id = _bound_policy("hk_hko", None)
    assert emit == "hk_hko"
    assert policy_id == ""
    fallback, fallback_policy = _bound_policy("not_a_profile", None)
    assert fallback == "annex3"
    assert fallback_policy == ""
    emit2, policy_id2 = _bound_policy("iwxxm_us", "annex3-metar-quality")
    assert emit2 == "iwxxm_us"
    assert policy_id2 == "annex3-metar-quality"

    out = io.StringIO()
    with redirect_stdout(out):
        code = main(["--product", "METAR", str(NEG_METAR)])
    assert code == 1
