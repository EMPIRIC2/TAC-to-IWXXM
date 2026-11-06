#!/usr/bin/env python3
"""Weekly staging validation catalog probe (GHA → DOKS staging HTTPS).

Calls public catalog + lint/validate endpoints on the staging API, aggregates
severity/code counts, and writes JSON + Markdown report artifacts.

Credentials: optional ``STAGING_API_BEARER_TOKEN`` (Authorization Bearer). Public
F21 convert/lint/validate/catalog routes do not require a token; the secret is
for optional authenticated probes or future rate-limit bypass without hardcoding.

Environment
-----------
LIVE_API_URL / STAGING_API_URL
    Staging API origin (default ``https://api.staging.tac-to-iwxxm.com``).
STAGING_LB_IP / DOKS_LB_IP
    Host-header fallback LB IP (default ``143.244.202.13``).
STAGING_API_BEARER_TOKEN
    Optional Bearer token; never logged.
WEEKLY_VALIDATION_OUT_DIR
    Output directory (default ``artifacts/weekly-validation-catalog``).
WEEKLY_VALIDATION_MANIFEST
    Manifest JSON path (default next to this script).
WEEKLY_VALIDATION_FAIL_ON_SAMPLE_ERROR
    When ``1``, non-2xx sample probes fail the process (default ``0`` — soft).

[Corpus: api] [Corpus: deploy] [Corpus: tests]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

DEFAULT_API = "https://api.staging.tac-to-iwxxm.com"
DEFAULT_LB = "143.244.202.13"
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = Path(__file__).with_name("weekly_validation_catalog_manifest.json")


def _severity_bucket(raw: object) -> str:
    """Normalize issue severity / validate ``level`` to a lowercase bucket name."""
    if raw is None:
        return "unknown"
    text = str(raw).strip().lower()
    if text in {"critical", "error", "warning", "info", "unknown"}:
        return text
    if text in {"err", "e", "fail", "failed"}:
        return "error"
    if text in {"warn", "w"}:
        return "warning"
    if text in {"i"}:
        return "info"
    return text or "unknown"


def _issue_severity_raw(issue: dict[str, Any]) -> object:
    """Prefer convert/lint ``severity``; fall back to validate ``level`` (G5)."""
    if "severity" in issue and issue.get("severity") is not None:
        return issue.get("severity")
    if "level" in issue and issue.get("level") is not None:
        return issue.get("level")
    return issue.get("severity", issue.get("level"))


def count_severities(issues: list[dict[str, Any]]) -> dict[str, int]:
    """Count issues by normalized severity.

    Convert / lint-tac rows use ``severity``; ``POST /api/v1/validate`` uses
    ``level`` on ``ValidateIssueModel``. Honor both so weekly validate probes
    do not under-count. [Corpus: api]
    """
    counter: Counter[str] = Counter()
    for issue in issues:
        if not isinstance(issue, dict):
            continue
        counter[_severity_bucket(_issue_severity_raw(issue))] += 1
    return {
        "critical": int(counter.get("critical", 0)),
        "error": int(counter.get("error", 0)),
        "warning": int(counter.get("warning", 0)),
        "info": int(counter.get("info", 0)),
        "unknown": int(counter.get("unknown", 0)),
        "total": sum(counter.values()),
    }


def count_codes(
    issues: list[dict[str, Any]], *, limit: int = 50
) -> list[dict[str, Any]]:
    """Top issue codes by frequency."""
    counter: Counter[str] = Counter()
    for issue in issues:
        if not isinstance(issue, dict):
            continue
        code = issue.get("code") or issue.get("id") or issue.get("rule_id")
        if code:
            counter[str(code)] += 1
    return [
        {"code": code, "count": count} for code, count in counter.most_common(limit)
    ]


def _issue_code(issue: dict[str, Any]) -> str | None:
    """Stable issue identity for report line items (code / id / rule_id)."""
    raw = issue.get("code") or issue.get("id") or issue.get("rule_id")
    if raw is None:
        return None
    text = str(raw).strip()
    return text or None


def count_raised_issue_line_items(
    issues: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """One row per distinct (code, severity) from sample-probe raised issues.

    Catalog registry GETs are not included — only issues actually raised by
    lint/validate sample probes. Sorted by count desc, then code, severity.
    """
    counter: Counter[tuple[str, str]] = Counter()
    for issue in issues:
        if not isinstance(issue, dict):
            continue
        code = _issue_code(issue)
        if not code:
            continue
        severity = _severity_bucket(_issue_severity_raw(issue))
        counter[(code, severity)] += 1
    rows = [
        {"code": code, "severity": severity, "count": count}
        for (code, severity), count in counter.items()
    ]
    rows.sort(
        key=lambda row: (-int(row["count"]), str(row["code"]), str(row["severity"]))
    )
    return rows


def extract_issues(payload: object) -> list[dict[str, Any]]:
    """Pull issue-like rows from catalog or probe JSON bodies."""
    if not isinstance(payload, dict):
        return []
    for key in ("issues", "items", "package_issues"):
        value = payload.get(key)
        if isinstance(value, list):
            return [row for row in value if isinstance(row, dict)]
    return []


class StagingClient:
    """Minimal HTTPS client with Host-header LB fallback (staging_smoke pattern)."""

    def __init__(
        self,
        api_url: str,
        *,
        lb_ip: str,
        bearer_token: str | None = None,
        timeout: float = 60.0,
    ) -> None:
        self.api_url = api_url.rstrip("/")
        self.lb_ip = lb_ip
        self.bearer_token = (bearer_token or "").strip() or None
        self.timeout = timeout
        host = (
            urllib.parse.urlparse(self.api_url).hostname
            or "api.staging.tac-to-iwxxm.com"
        )
        self.api_host = host

    def _headers(
        self, *, content_type: str | None = None, host_override: bool = False
    ) -> dict[str, str]:
        headers: dict[str, str] = {
            "Accept": "application/json",
            "User-Agent": "weekly-validation-catalog/1.0",
        }
        if content_type:
            headers["Content-Type"] = content_type
        if self.bearer_token:
            headers["Authorization"] = f"Bearer {self.bearer_token}"
        if host_override:
            headers["Host"] = self.api_host
        return headers

    def request(
        self,
        method: str,
        path: str,
        *,
        data: bytes | None = None,
        content_type: str | None = None,
    ) -> tuple[int, Any, str]:
        """Return ``(status, json_or_none, raw_text)`` trying HTTPS then LB Host-header."""
        path = path if path.startswith("/") else f"/{path}"
        attempts: list[tuple[str, bool]] = [
            (f"{self.api_url}{path}", False),
            (f"http://{self.lb_ip}{path}", True),
        ]
        last_error = ""
        for url, host_override in attempts:
            req = urllib.request.Request(
                url,
                data=data,
                method=method,
                headers=self._headers(
                    content_type=content_type, host_override=host_override
                ),
            )
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    raw = resp.read().decode("utf-8", errors="replace")
                    status = int(resp.status)
                    try:
                        body: Any = json.loads(raw) if raw else None
                    except json.JSONDecodeError:
                        body = None
                    return status, body, raw
            except urllib.error.HTTPError as exc:
                raw = exc.read().decode("utf-8", errors="replace")
                try:
                    body = json.loads(raw) if raw else None
                except json.JSONDecodeError:
                    body = None
                return int(exc.code), body, raw
            except Exception as exc:
                last_error = str(exc)
                continue
        return 0, None, last_error


def encode_multipart(fields: dict[str, str]) -> tuple[bytes, str]:
    """Encode simple multipart/form-data without file parts."""
    boundary = "----WeeklyValidationCatalogBoundary7MA4YWxk"
    lines: list[bytes] = []
    for name, value in fields.items():
        lines.append(f"--{boundary}".encode())
        lines.append(f'Content-Disposition: form-data; name="{name}"'.encode())
        lines.append(b"")
        lines.append(value.encode("utf-8"))
    lines.append(f"--{boundary}--".encode())
    lines.append(b"")
    body = b"\r\n".join(lines)
    return body, f"multipart/form-data; boundary={boundary}"


def load_manifest(path: Path) -> dict[str, Any]:
    """Load fixture/catalog manifest JSON."""
    return json.loads(path.read_text(encoding="utf-8"))


def render_markdown(report: dict[str, Any]) -> str:
    """Render a human-readable weekly report."""
    lines = [
        "# Weekly validation catalog report",
        "",
        f"- Generated (UTC): `{report.get('generated_at')}`",
        f"- API: `{report.get('api_url')}`",
        f"- Health status: `{report.get('health', {}).get('status')}`",
        "",
        "## Catalog totals",
        "",
        "| Catalog | HTTP | Issues/items | critical | error | warning | info | unknown |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report.get("catalogs", []):
        sev = row.get("severity_counts") or {}
        lines.append(
            "| {label} | {status} | {total} | {critical} | {error} | {warning} | {info} | {unknown} |".format(
                label=row.get("label"),
                status=row.get("status"),
                total=sev.get("total", 0),
                critical=sev.get("critical", 0),
                error=sev.get("error", 0),
                warning=sev.get("warning", 0),
                info=sev.get("info", 0),
                unknown=sev.get("unknown", 0),
            )
        )
    lines.extend(["", "## Sample probes", ""])
    lines.append(
        "| Sample | Product | Probe | HTTP | critical | error | warning | info | total |"
    )
    lines.append("|---|---|---|---:|---:|---:|---:|---:|---:|")
    for sample in report.get("samples", []):
        for probe in sample.get("probes", []):
            sev = probe.get("severity_counts") or {}
            lines.append(
                "| {sid} | {product} | {probe} | {status} | {critical} | {error} | {warning} | {info} | {total} |".format(
                    sid=sample.get("id"),
                    product=sample.get("product"),
                    probe=probe.get("name"),
                    status=probe.get("status"),
                    critical=sev.get("critical", 0),
                    error=sev.get("error", 0),
                    warning=sev.get("warning", 0),
                    info=sev.get("info", 0),
                    total=sev.get("total", 0),
                )
            )
    lines.extend(["", "## Raised validation issues", ""])
    lines.append(
        "Distinct codes raised by sample lint/validate probes "
        "(not catalog registry rollups)."
    )
    lines.append("")
    aggregate = report.get("aggregate") or {}
    line_items = aggregate.get("raised_issue_line_items") or []
    if not line_items:
        lines.append("_No raised validation issues recorded._")
    else:
        lines.append("| Code | Severity | Count |")
        lines.append("|---|---|---:|")
        lines.extend(
            f"| `{row['code']}` | {row['severity']} | {row['count']} |"
            for row in line_items
        )
        total = aggregate.get("raised_issue_total")
        if total is None:
            total = sum(int(row.get("count") or 0) for row in line_items)
        lines.append("")
        lines.append(f"**Total raised:** {total}")
    lines.append("")
    return "\n".join(lines)


def run_probe(
    *,
    client: StagingClient,
    manifest: dict[str, Any],
    repo_root: Path,
    fail_on_sample_error: bool,
) -> dict[str, Any]:
    """Execute health + catalog + sample probes and return the report dict."""
    generated_at = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    health_status, health_body, health_raw = client.request("GET", "/health")
    report: dict[str, Any] = {
        "generated_at": generated_at,
        "api_url": client.api_url,
        "bearer_configured": bool(client.bearer_token),
        "health": {
            "status": health_status,
            "ok": health_status == 200,
            "body": health_body if isinstance(health_body, dict) else None,
            "error": None if health_status == 200 else health_raw[:500],
        },
        "catalogs": [],
        "samples": [],
        "aggregate": {
            "severity_counts": count_severities([]),
            "top_codes": [],
            "raised_issue_line_items": [],
            "raised_issue_total": 0,
        },
        "ok": health_status == 200,
    }
    if health_status != 200:
        return report

    all_raised: list[dict[str, Any]] = []

    for query in manifest.get("catalog_queries") or []:
        path = str(query.get("path") or "")
        label = str(query.get("label") or path)
        status, body, raw = client.request("GET", path)
        issues = extract_issues(body)
        sev = count_severities(issues)
        entry = {
            "label": label,
            "path": path,
            "status": status,
            "ok": 200 <= status < 300,
            "severity_counts": sev,
            "top_codes": count_codes(issues, limit=20),
            "item_count": len(issues),
            "error": None if 200 <= status < 300 else raw[:500],
        }
        report["catalogs"].append(entry)
        if not entry["ok"]:
            report["ok"] = False

    semantic = str(manifest.get("default_semantic_profile") or "ICAO_2025")
    version = str(manifest.get("default_iwxxm_version") or "2025-2")

    for sample in manifest.get("samples") or []:
        sample_id = str(sample.get("id") or "sample")
        product = str(sample.get("product") or "METAR")
        rel = str(sample.get("path") or "")
        tac_path = repo_root / rel
        sample_row: dict[str, Any] = {
            "id": sample_id,
            "product": product,
            "path": rel,
            "probes": [],
        }
        if not tac_path.is_file():
            sample_row["probes"].append(
                {
                    "name": "load-fixture",
                    "status": 0,
                    "ok": False,
                    "severity_counts": count_severities([]),
                    "error": f"missing fixture: {rel}",
                }
            )
            report["samples"].append(sample_row)
            report["ok"] = False if fail_on_sample_error else report["ok"]
            continue

        tac = tac_path.read_text(encoding="utf-8").strip()
        for probe_name in sample.get("probes") or []:
            name = str(probe_name)
            if name == "lint-tac":
                body_bytes, ctype = encode_multipart(
                    {
                        "manual_text": tac,
                        "product": product,
                        "semantic_profile": semantic,
                    }
                )
                status, body, raw = client.request(
                    "POST", "/api/v1/lint-tac", data=body_bytes, content_type=ctype
                )
            elif name == "validate":
                body_bytes, ctype = encode_multipart(
                    {
                        "manual_text": tac,
                        "product": product,
                        "semantic_profile": semantic,
                        "iwxxm_version": version,
                        "layers": "ALL",
                        "stop_on_error": "false",
                    }
                )
                status, body, raw = client.request(
                    "POST", "/api/v1/validate", data=body_bytes, content_type=ctype
                )
            else:
                sample_row["probes"].append(
                    {
                        "name": name,
                        "status": 0,
                        "ok": False,
                        "severity_counts": count_severities([]),
                        "error": f"unknown probe: {name}",
                    }
                )
                continue

            issues = extract_issues(body)
            all_raised.extend(issues)
            ok = 200 <= status < 300
            sample_row["probes"].append(
                {
                    "name": name,
                    "status": status,
                    "ok": ok,
                    "severity_counts": count_severities(issues),
                    "top_codes": count_codes(issues, limit=20),
                    "issue_count": len(issues),
                    "error": None if ok else raw[:500],
                }
            )
            if not ok and fail_on_sample_error:
                report["ok"] = False

        report["samples"].append(sample_row)

    line_items = count_raised_issue_line_items(all_raised)
    report["aggregate"] = {
        "severity_counts": count_severities(all_raised),
        "top_codes": count_codes(all_raised, limit=50),
        "raised_issue_line_items": line_items,
        "raised_issue_total": len(all_raised),
    }
    return report


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path(
            os.environ.get("WEEKLY_VALIDATION_MANIFEST", str(DEFAULT_MANIFEST))
        ),
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path(
            os.environ.get(
                "WEEKLY_VALIDATION_OUT_DIR", "artifacts/weekly-validation-catalog"
            )
        ),
    )
    parser.add_argument(
        "--api-url",
        default=os.environ.get("STAGING_API_URL")
        or os.environ.get("LIVE_API_URL")
        or DEFAULT_API,
    )
    parser.add_argument(
        "--lb-ip",
        default=os.environ.get("STAGING_LB_IP")
        or os.environ.get("DOKS_LB_IP")
        or DEFAULT_LB,
    )
    parser.add_argument(
        "--fail-on-sample-error",
        action="store_true",
        default=os.environ.get("WEEKLY_VALIDATION_FAIL_ON_SAMPLE_ERROR", "0") == "1",
    )
    args = parser.parse_args(argv)

    manifest = load_manifest(args.manifest)
    token = os.environ.get("STAGING_API_BEARER_TOKEN") or os.environ.get(
        "STAGING_API_TOKEN"
    )
    client = StagingClient(args.api_url, lb_ip=args.lb_ip, bearer_token=token)
    report = run_probe(
        client=client,
        manifest=manifest,
        repo_root=REPO_ROOT,
        fail_on_sample_error=bool(args.fail_on_sample_error),
    )

    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "weekly-validation-catalog.json"
    md_path = out_dir / "weekly-validation-catalog.md"
    json_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    md_path.write_text(render_markdown(report), encoding="utf-8")

    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    print(
        "aggregate raised={total} error={error} warning={warning} info={info}".format(
            total=report["aggregate"]["severity_counts"]["total"],
            error=report["aggregate"]["severity_counts"]["error"],
            warning=report["aggregate"]["severity_counts"]["warning"],
            info=report["aggregate"]["severity_counts"]["info"],
        )
    )

    if not report.get("ok"):
        print(
            "::error::Weekly validation catalog probe failed (health or catalog)",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
