"""Unit tests for weekly staging validation catalog probe helpers.

Offline only — no live network. [Corpus: tests]
"""

from __future__ import annotations

import io
import json
from pathlib import Path
from typing import Any

from scripts.ci.weekly_validation_catalog import (
    count_codes,
    count_raised_issue_line_items,
    count_severities,
    encode_multipart,
    extract_issues,
    load_manifest,
    render_markdown,
    run_probe,
)

MANIFEST = (
    Path(__file__).resolve().parents[2]
    / "scripts"
    / "ci"
    / "weekly_validation_catalog_manifest.json"
)
REPO_ROOT = Path(__file__).resolve().parents[2]


def test_count_severities_buckets() -> None:
    issues = [
        {"severity": "error", "code": "A"},
        {"severity": "WARNING", "code": "B"},
        {"severity": "info", "code": "C"},
        {"severity": "critical", "code": "D"},
        {"severity": None, "code": "E"},
    ]
    counts = count_severities(issues)
    assert counts["error"] == 1
    assert counts["warning"] == 1
    assert counts["info"] == 1
    assert counts["critical"] == 1
    assert counts["unknown"] == 1
    assert counts["total"] == 5


def test_count_severities_honors_validate_level() -> None:
    """ValidateIssueModel uses ``level``; weekly rollup must not under-count (G5)."""
    counts = count_severities(
        [
            {"level": "error", "message": "xsd fail"},
            {"level": "warning", "message": "schematron soft"},
            {"severity": "info", "message": "note"},
            {"severity": "warning", "level": "error", "message": "severity wins"},
        ]
    )
    assert counts["error"] == 1
    assert counts["warning"] == 2
    assert counts["info"] == 1
    assert counts["total"] == 4


def test_count_codes_top() -> None:
    issues = [{"code": "X"}, {"code": "Y"}, {"code": "X"}, {"id": "Z"}]
    top = count_codes(issues, limit=10)
    assert top[0] == {"code": "X", "count": 2}
    assert {row["code"] for row in top} == {"X", "Y", "Z"}


def test_count_raised_issue_line_items_by_code_and_severity() -> None:
    """One report row per distinct (code, severity) from sample-probe issues."""
    issues = [
        {"code": "MISSING_TERMINATOR", "severity": "info"},
        {"code": "MISSING_TERMINATOR", "severity": "info"},
        {"code": "INVALID_RVR", "level": "error"},
        {"code": "INVALID_RVR", "severity": "warning"},
        {"id": "ORPHAN_ID", "severity": "warning"},
        {"severity": "error"},  # no code → skipped from line items
    ]
    rows = count_raised_issue_line_items(issues)
    assert rows == [
        {"code": "MISSING_TERMINATOR", "severity": "info", "count": 2},
        {"code": "INVALID_RVR", "severity": "error", "count": 1},
        {"code": "INVALID_RVR", "severity": "warning", "count": 1},
        {"code": "ORPHAN_ID", "severity": "warning", "count": 1},
    ]
    assert sum(row["count"] for row in rows) == 5


def test_extract_issues_from_catalog_shapes() -> None:
    assert extract_issues({"issues": [{"code": "A"}]}) == [{"code": "A"}]
    assert extract_issues({"items": [{"id": "B"}]}) == [{"id": "B"}]
    assert extract_issues({"package_issues": [{"code": "C"}]}) == [{"code": "C"}]
    assert extract_issues("nope") == []


def test_encode_multipart_roundtrip_fields() -> None:
    body, ctype = encode_multipart({"manual_text": "METAR KJFK=", "product": "METAR"})
    assert "multipart/form-data; boundary=" in ctype
    assert b"METAR KJFK=" in body
    assert b'name="product"' in body


def test_manifest_samples_exist() -> None:
    manifest = load_manifest(MANIFEST)
    assert manifest["samples"]
    for sample in manifest["samples"]:
        path = REPO_ROOT / sample["path"]
        assert path.is_file(), f"missing fixture {sample['path']}"


def test_render_markdown_includes_tables() -> None:
    report = {
        "generated_at": "2026-10-30T00:00:00Z",
        "api_url": "https://api.staging.tac-to-iwxxm.com",
        "health": {"status": 200},
        "catalogs": [
            {
                "label": "lint-issue-catalog-all",
                "status": 200,
                "severity_counts": {
                    "critical": 0,
                    "error": 2,
                    "warning": 3,
                    "info": 1,
                    "unknown": 0,
                    "total": 6,
                },
            }
        ],
        "samples": [
            {
                "id": "metar_basic",
                "product": "METAR",
                "probes": [
                    {
                        "name": "lint-tac",
                        "status": 200,
                        "severity_counts": {
                            "critical": 0,
                            "error": 0,
                            "warning": 0,
                            "info": 1,
                            "unknown": 0,
                            "total": 1,
                        },
                    }
                ],
            }
        ],
        "aggregate": {
            "top_codes": [{"code": "MISSING_TERMINATOR", "count": 1}],
            "raised_issue_line_items": [
                {
                    "code": "MISSING_TERMINATOR",
                    "severity": "info",
                    "count": 1,
                },
                {
                    "code": "INVALID_RVR",
                    "severity": "error",
                    "count": 2,
                },
            ],
            "raised_issue_total": 3,
            "severity_counts": {
                "critical": 0,
                "error": 2,
                "warning": 0,
                "info": 1,
                "unknown": 0,
                "total": 3,
            },
        },
    }
    md = render_markdown(report)
    assert "Weekly validation catalog report" in md
    assert "lint-issue-catalog-all" in md
    assert "## Raised validation issues" in md
    assert "| Code | Severity | Count |" in md
    assert "| `MISSING_TERMINATOR` | info | 1 |" in md
    assert "| `INVALID_RVR` | error | 2 |" in md
    assert "**Total raised:** 3" in md
    # Catalog registry rollups must not be the only place codes appear;
    # the raised section is sample-probe driven.
    raised_section = md.split("## Raised validation issues", 1)[1]
    assert "MISSING_TERMINATOR" in raised_section
    assert "INVALID_RVR" in raised_section


class _FakeClient:
    def __init__(self) -> None:
        self.api_url = "https://api.staging.tac-to-iwxxm.com"
        self.bearer_token = None
        self.calls: list[tuple[str, str]] = []

    def request(
        self,
        method: str,
        path: str,
        *,
        data: bytes | None = None,
        content_type: str | None = None,
    ) -> tuple[int, Any, str]:
        del data, content_type
        self.calls.append((method, path))
        if path == "/health":
            return 200, {"status": "ok"}, '{"status":"ok"}'
        if path.startswith("/api/v1/lint-issue-catalog") or path.startswith(
            "/api/v1/rule-catalogs"
        ):
            return 200, {"issues": [{"code": "DEMO", "severity": "info"}]}, "{}"
        if path == "/api/v1/lint-tac":
            return (
                200,
                {"ok": True, "issues": [{"code": "LINT_A", "severity": "warning"}]},
                "{}",
            )
        if path == "/api/v1/validate":
            return 200, {"issues": [{"code": "VAL_B", "severity": "error"}]}, "{}"
        return 404, None, "missing"


def test_run_probe_aggregates_with_fake_client() -> None:
    manifest = {
        "default_semantic_profile": "ICAO_2025",
        "default_iwxxm_version": "2025-2",
        "catalog_queries": [{"path": "/api/v1/lint-issue-catalog", "label": "all"}],
        "samples": [
            {
                "id": "metar_basic",
                "product": "METAR",
                "path": "packages/tac-validate/tests/fixtures/accept/metar_basic.tac",
                "probes": ["lint-tac", "validate"],
            }
        ],
    }
    client = _FakeClient()
    report = run_probe(
        client=client,  # type: ignore[arg-type]
        manifest=manifest,
        repo_root=REPO_ROOT,
        fail_on_sample_error=True,
    )
    assert report["ok"] is True
    assert report["health"]["status"] == 200
    assert report["catalogs"][0]["severity_counts"]["info"] == 1
    assert report["aggregate"]["severity_counts"]["warning"] == 1
    assert report["aggregate"]["severity_counts"]["error"] == 1
    assert report["aggregate"]["raised_issue_total"] == 2
    line_items = report["aggregate"]["raised_issue_line_items"]
    assert line_items == [
        {"code": "LINT_A", "severity": "warning", "count": 1},
        {"code": "VAL_B", "severity": "error", "count": 1},
    ]
    # Catalog DEMO must not leak into sample-probe raised line items.
    assert all(row["code"] != "DEMO" for row in line_items)
    md = render_markdown(report)
    assert "## Raised validation issues" in md
    assert "| `LINT_A` | warning | 1 |" in md
    assert "| `VAL_B` | error | 1 |" in md
    assert "**Total raised:** 2" in md
    assert ("GET", "/health") in client.calls
    assert any(c[1] == "/api/v1/lint-tac" for c in client.calls)


def test_run_probe_fails_closed_on_health() -> None:
    class DownClient(_FakeClient):
        def request(
            self, method: str, path: str, **kwargs: Any
        ) -> tuple[int, Any, str]:
            del method, kwargs
            if path == "/health":
                return 503, None, "down"
            return 200, {}, "{}"

    report = run_probe(
        client=DownClient(),  # type: ignore[arg-type]
        manifest={"catalog_queries": [], "samples": []},
        repo_root=REPO_ROOT,
        fail_on_sample_error=False,
    )
    assert report["ok"] is False
    assert report["health"]["status"] == 503


def test_manifest_json_is_valid() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert "samples" in data
    assert "catalog_queries" in data


def test_severity_bucket_aliases_and_non_dict_skips() -> None:
    counts = count_severities(
        [
            {"severity": "err"},
            {"severity": "warn"},
            {"severity": "i"},
            {"severity": "  "},
            "not-a-dict",
            {"code": "ONLY"},
        ]
    )
    assert counts["error"] == 1
    assert counts["warning"] == 1
    assert counts["info"] == 1
    assert counts["unknown"] >= 1
    assert count_codes(["x", {"code": ""}, {"rule_id": "R1"}], limit=5) == [
        {"code": "R1", "count": 1}
    ]
    assert count_raised_issue_line_items(["x", {"severity": "error"}]) == []
    assert extract_issues({"issues": [{"code": "A"}, "skip"]}) == [{"code": "A"}]
    assert extract_issues({"nope": []}) == []


def test_render_markdown_empty_raised_section() -> None:
    md = render_markdown(
        {
            "generated_at": "t",
            "api_url": "https://example",
            "health": {"status": 200},
            "catalogs": [],
            "samples": [],
            "aggregate": {"raised_issue_line_items": [], "severity_counts": {}},
        }
    )
    assert "_No raised validation issues recorded._" in md


def test_render_markdown_raised_total_fallback() -> None:
    md = render_markdown(
        {
            "generated_at": "t",
            "api_url": "https://example",
            "health": {"status": 200},
            "catalogs": [],
            "samples": [],
            "aggregate": {
                "raised_issue_line_items": [
                    {"code": "A", "severity": "error", "count": 2},
                    {"code": "B", "severity": "warning", "count": None},
                ],
                "severity_counts": {},
            },
        }
    )
    assert "**Total raised:** 2" in md


def test_staging_client_request_paths(monkeypatch: Any, tmp_path: Path) -> None:
    from scripts.ci import weekly_validation_catalog as mod

    class _Resp:
        def __init__(self, status: int, body: bytes) -> None:
            self.status = status
            self._body = body

        def read(self) -> bytes:
            return self._body

        def __enter__(self) -> _Resp:
            return self

        def __exit__(self, *args: object) -> None:
            return None

    calls: list[Any] = []

    def lb_fallback(req: Any, timeout: float = 0) -> _Resp:
        del timeout
        calls.append((req.full_url, dict(req.headers)))
        if req.full_url.startswith("https://"):
            raise OSError("tls-down")
        assert req.headers.get("Host") == "api.example.com"
        assert "Authorization" in req.headers
        assert (
            req.headers.get("Content-type") == "application/json"
            or req.headers.get("Content-Type") == "application/json"
        )
        return _Resp(200, b'{"ok":true}')

    monkeypatch.setattr(mod.urllib.request, "urlopen", lb_fallback)
    client = mod.StagingClient(
        "https://api.example.com", lb_ip="1.2.3.4", bearer_token=" tok "
    )
    status, body, _raw = client.request(
        "POST", "health", data=b"{}", content_type="application/json"
    )
    assert status == 200
    assert body == {"ok": True}
    assert any("1.2.3.4" in u for u, _h in calls)

    def bad_json_ok(req: Any, timeout: float = 0) -> _Resp:
        del timeout
        return _Resp(200, b"{")

    monkeypatch.setattr(mod.urllib.request, "urlopen", bad_json_ok)
    status_j, body_j, raw_j = client.request("GET", "/health")
    assert status_j == 200
    assert body_j is None
    assert raw_j == "{"

    def http_error(req: Any, timeout: float = 0) -> _Resp:
        del timeout
        raise mod.urllib.error.HTTPError(
            req.full_url, 503, "nope", hdrs=None, fp=io.BytesIO(b"{")
        )

    monkeypatch.setattr(mod.urllib.request, "urlopen", http_error)
    status2, body2, raw2 = client.request("GET", "/health")
    assert status2 == 503
    assert body2 is None
    assert raw2 == "{"

    def http_error_json(req: Any, timeout: float = 0) -> _Resp:
        del timeout
        raise mod.urllib.error.HTTPError(
            req.full_url, 502, "bad", hdrs=None, fp=io.BytesIO(b'{"err":1}')
        )

    monkeypatch.setattr(mod.urllib.request, "urlopen", http_error_json)
    status3, body3, raw3 = client.request("GET", "/health")
    assert status3 == 502
    assert body3 == {"err": 1}
    assert "err" in raw3

    def always_fail(req: Any, timeout: float = 0) -> _Resp:
        del timeout
        raise OSError(f"down:{req.full_url}")

    monkeypatch.setattr(mod.urllib.request, "urlopen", always_fail)
    status4, body4, raw4 = client.request("GET", "/health")
    assert status4 == 0
    assert body4 is None
    assert "down:" in raw4

    # No bearer / no content-type headers branch
    bare = mod.StagingClient("https://api.example.com", lb_ip="9.9.9.9")
    hdr = bare._headers()
    assert "Authorization" not in hdr
    assert "Content-Type" not in hdr
    assert bare._headers(host_override=True)["Host"] == "api.example.com"


def test_run_probe_sample_error_paths() -> None:
    class Client(_FakeClient):
        def request(
            self, method: str, path: str, **kwargs: Any
        ) -> tuple[int, Any, str]:
            if path == "/health":
                return 200, {"status": "ok"}, "{}"
            if path.startswith("/api/v1/lint-issue-catalog"):
                return 500, None, "catalog-down"
            if path == "/api/v1/lint-tac":
                return 500, None, "lint-down"
            return 200, {"issues": []}, "{}"

    report = run_probe(
        client=Client(),  # type: ignore[arg-type]
        manifest={
            "catalog_queries": [{"path": "/api/v1/lint-issue-catalog", "label": "all"}],
            "samples": [
                {
                    "id": "missing",
                    "product": "METAR",
                    "path": "does-not-exist.tac",
                    "probes": ["lint-tac"],
                },
                {
                    "id": "metar_basic",
                    "product": "METAR",
                    "path": "packages/tac-validate/tests/fixtures/accept/metar_basic.tac",
                    "probes": ["lint-tac", "unknown-probe"],
                },
            ],
        },
        repo_root=REPO_ROOT,
        fail_on_sample_error=True,
    )
    assert report["ok"] is False
    assert report["catalogs"][0]["ok"] is False
    probe_names = [p["name"] for s in report["samples"] for p in s["probes"]]
    assert "load-fixture" in probe_names
    assert "unknown-probe" in probe_names


def test_main_writes_artifacts(monkeypatch: Any, tmp_path: Path) -> None:
    from scripts.ci.weekly_validation_catalog import main

    class Client(_FakeClient):
        pass

    monkeypatch.setattr(
        "scripts.ci.weekly_validation_catalog.StagingClient",
        lambda *a, **k: Client(),
    )
    out = tmp_path / "out"
    rc = main(
        [
            "--manifest",
            str(MANIFEST),
            "--out-dir",
            str(out),
            "--api-url",
            "https://api.staging.tac-to-iwxxm.com",
            "--lb-ip",
            "127.0.0.1",
        ]
    )
    assert rc == 0
    assert (out / "weekly-validation-catalog.json").is_file()
    assert (out / "weekly-validation-catalog.md").is_file()

    class Down(_FakeClient):
        def request(
            self, method: str, path: str, **kwargs: Any
        ) -> tuple[int, Any, str]:
            del method, kwargs
            if path == "/health":
                return 503, None, "down"
            return 200, {}, "{}"

    monkeypatch.setattr(
        "scripts.ci.weekly_validation_catalog.StagingClient",
        lambda *a, **k: Down(),
    )
    rc2 = main(["--manifest", str(MANIFEST), "--out-dir", str(tmp_path / "out2")])
    assert rc2 == 1
