"""Execute Batch A script __main__ blocks for coverage."""
# ruff: noqa: SIM117

from __future__ import annotations

import runpy
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from tests.scripts.conftest import REPO_ROOT

_BATCH_A = REPO_ROOT / "scripts"


@pytest.mark.unit
def test_check_per_file_coverage_main(tmp_path: Path) -> None:
    cov_json = tmp_path / "coverage.json"
    cov_json.write_text(
        '{"files": {"a.py": {"summary": {"num_statements": 1, "percent_covered": 100.0}}}}',
        encoding="utf-8",
    )
    path = _BATCH_A / "ci/check_per_file_coverage.py"
    with patch.object(sys, "argv", [str(path), str(cov_json)]):
        with pytest.raises(SystemExit) as exc:
            runpy.run_path(str(path), run_name="__main__")
    assert exc.value.code == 0


@pytest.mark.unit
def test_check_issue_registry_literals_main(tmp_path: Path) -> None:
    rule = tmp_path / "packages/tac-validate/src/tac_validate/rules/clean.py"
    rule.parent.mkdir(parents=True)
    rule.write_text("ok = True\n", encoding="utf-8")
    path = _BATCH_A / "ci/check_issue_registry_literals.py"
    with patch.object(sys, "argv", [str(path), str(rule)]):
        with pytest.raises(SystemExit) as exc:
            runpy.run_path(str(path), run_name="__main__")
    assert exc.value.code == 0


@pytest.mark.unit
def test_validate_ingest_poller_url_main() -> None:
    path = _BATCH_A / "deploy/validate_ingest_poller_url.py"
    url = "https://example.com/feed.json"
    with patch.object(sys, "argv", [str(path), url]):
        with pytest.raises(SystemExit) as exc:
            runpy.run_path(str(path), run_name="__main__")
    assert exc.value.code == 0


@pytest.mark.unit
def test_harvest_wmo_membership_main() -> None:
    path = _BATCH_A / "iwxxm/harvest_wmo_membership.py"
    out = REPO_ROOT / "packages/tac-validate/src/tac_validate/data/wmo_membership.json"
    with (
        patch.object(sys, "argv", [str(path)]),
        patch("tac_validate.membership.write_membership_artifact", return_value=out),
    ):
        with pytest.raises(SystemExit) as exc:
            runpy.run_path(str(path), run_name="__main__")
    assert exc.value.code == 0


@pytest.mark.unit
def test_record_converter_pr_baselines_main(tmp_path: Path) -> None:
    out = tmp_path / "converter_pr.yaml"
    path = _BATCH_A / "bench/record_converter_pr_baselines.py"
    payload = {"version": 1, "status": "laptop_seed", "products": {}}
    with (
        patch.object(
            sys,
            "argv",
            [str(path), "--out", str(out), "--host", "test", "--status", "laptop_seed"],
        ),
        patch(
            "scripts.bench.record_converter_pr_baselines.load_converter_pr_baselines"
        ),
        patch(
            "scripts.bench.record_converter_pr_baselines.record_baselines_dict",
            return_value=payload,
        ),
        pytest.raises(SystemExit) as exc,
    ):
        runpy.run_path(str(path), run_name="__main__")
    assert exc.value.code == 0


@pytest.mark.unit
def test_syntax_check_main(tmp_path: Path) -> None:
    good = tmp_path / "ok.py"
    good.write_text("x = 1\n", encoding="utf-8")
    path = _BATCH_A / "utilities/syntax_check.py"
    with patch.object(sys, "argv", [str(path), str(good)]):
        with pytest.raises(SystemExit) as exc:
            runpy.run_path(str(path), run_name="__main__")
    assert exc.value.code == 0


@pytest.mark.unit
def test_parse_airports_csv_main(tmp_path: Path) -> None:
    scripts_data = REPO_ROOT / "scripts" / "data"
    scripts_data.mkdir(parents=True, exist_ok=True)
    csv_path = scripts_data / "af-airports.csv"
    csv_path.write_text(
        "icao_code,name,municipality,country_name,type,iata_code,latitude_deg,longitude_deg,elevation_ft\n"
        "KJFK,JFK,New York,USA,large_airport,JFK,40.6,-73.7,13\n",
        encoding="utf-8",
    )
    frontend_out = tmp_path / "frontend.json"
    backend_out = tmp_path / "backend.json"
    path = _BATCH_A / "utilities/parse_airports_csv.py"
    source = (
        path.read_text(encoding="utf-8")
        .replace(
            "frontend_output = project_root / 'frontend' / 'src' / 'data' / 'airports.json'",
            f"frontend_output = Path('{frontend_out}')",
        )
        .replace(
            "backend_output = project_root / 'backend' / 'src' / 'data' / 'airports.json'",
            f"backend_output = Path('{backend_out}')",
        )
    )
    try:
        with patch.object(sys, "argv", [str(path)]):
            exec(
                compile(source, str(path), "exec"),
                {"__name__": "__main__", "__file__": str(path), "Path": Path},
            )
    finally:
        csv_path.unlink(missing_ok=True)
        if scripts_data.exists() and not any(scripts_data.iterdir()):
            scripts_data.rmdir()
    assert frontend_out.is_file()
    assert backend_out.is_file()


@pytest.mark.unit
def test_extract_email_templates_main(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    templates = tmp_path / "frontend/templates/authentication"
    templates.mkdir(parents=True)
    (templates / "01-confirmation.md").write_text(
        "## Subject\n```\nHi\n```\n## HTML\n```html\n<p>x</p>\n```",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    path = _BATCH_A / "utilities/extract_email_templates.py"
    runpy.run_path(str(path), run_name="__main__")


@pytest.mark.unit
def test_create_admin_user_main(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_SECRET_KEY", "service-key")
    monkeypatch.setenv("ADMIN_EMAIL", "admin@example.com")
    monkeypatch.setenv("ADMIN_PASSWORD", "secret-pass")
    path = _BATCH_A / "utilities/create_admin_user.py"
    user_resp = MagicMock(status_code=201, text="ok")
    user_resp.json.return_value = {"id": "u1"}
    profile_resp = MagicMock(status_code=201, text="ok")
    with (
        patch(
            "metar_shared.supabase_env.get_supabase_url",
            return_value="https://example.supabase.co",
        ),
        patch(
            "metar_shared.supabase_env.get_supabase_secret_key",
            return_value="service-key",
        ),
        patch("dotenv.load_dotenv"),
        patch("requests.post", side_effect=[user_resp, profile_resp]),
    ):
        with pytest.raises(SystemExit) as exc:
            runpy.run_path(str(path), run_name="__main__")
    assert exc.value.code == 0


@pytest.mark.unit
def test_upload_email_templates_main_verify_only(tmp_path: Path) -> None:
    template_dir = tmp_path / "frontend/templates/authentication"
    template_dir.mkdir(parents=True)
    md = "## HTML\n```html\n<p>Body</p>\n```"
    for name in (
        "01-confirmation.md",
        "02-magic-link.md",
        "03-password-reset.md",
        "05-email-changed.md",
    ):
        (template_dir / name).write_text(md, encoding="utf-8")

    path = _BATCH_A / "utilities/upload_email_templates.py"
    source = path.read_text(encoding="utf-8")
    for name in (
        "01-confirmation.md",
        "02-magic-link.md",
        "03-password-reset.md",
        "05-email-changed.md",
    ):
        source = source.replace(
            f"frontend/templates/authentication/{name}",
            str(template_dir / name),
        )
    namespace: dict = {"__name__": "__main__", "__file__": str(path)}

    def noop_exit(code: int = 0) -> None:
        raise SystemExit(code)

    with (
        patch.object(
            sys,
            "argv",
            [
                str(path),
                "--access-token",
                "tok",
                "--project-id",
                "proj",
                "--verify-only",
            ],
        ),
        patch("sys.exit", noop_exit),
        pytest.raises(SystemExit) as exc,
    ):
        exec(compile(source, str(path), "exec"), namespace)
    assert exc.value.code == 0


@pytest.mark.unit
def test_upload_email_templates_duplicate_main_tail(tmp_path: Path) -> None:
    """Cover duplicate __main__ tail after a no-op sys.exit."""
    template_dir = tmp_path / "frontend/templates/authentication"
    template_dir.mkdir(parents=True)
    md = "## HTML\n```html\n<p>Body</p>\n```"
    for name in (
        "01-confirmation.md",
        "02-magic-link.md",
        "03-password-reset.md",
        "05-email-changed.md",
    ):
        (template_dir / name).write_text(md, encoding="utf-8")

    path = _BATCH_A / "utilities/upload_email_templates.py"
    source = path.read_text(encoding="utf-8")
    for name in (
        "01-confirmation.md",
        "02-magic-link.md",
        "03-password-reset.md",
        "05-email-changed.md",
    ):
        source = source.replace(
            f"frontend/templates/authentication/{name}",
            str(template_dir / name),
        )

    def noop_exit(code: int = 0) -> None:
        return None

    namespace: dict = {"__name__": "__main__", "__file__": str(path)}
    with (
        patch.object(
            sys,
            "argv",
            [
                str(path),
                "--access-token",
                "tok",
                "--project-id",
                "proj",
                "--verify-only",
            ],
        ),
        patch("requests.patch", return_value=MagicMock(status_code=200, text="ok")),
        patch("sys.exit", noop_exit),
    ):
        exec(compile(source, str(path), "exec"), namespace)
