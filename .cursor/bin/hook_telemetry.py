#!/usr/bin/env python3
"""Hook telemetry — JSONL events and aggregation. [Corpus: skill-integration]"""

from __future__ import annotations

import csv
import io
import json
import os
import re
import statistics
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1


def telemetry_enabled() -> bool:
    """Return whether hook telemetry JSONL logging is enabled."""
    if os.environ.get("EM_HOOK_TELEMETRY_ENABLED", "1").strip() in ("0", "false", "False"):
        return False
    return True


def _repo_root() -> Path:
    override = os.environ.get("EM_ENGINEERING_MEMORY_ROOT", "").strip()
    if override:
        return Path(override).resolve()
    here = Path(__file__).resolve()
    candidate = here.parents[3]
    if (candidate / "packages" / "engineering-memory" / "pyproject.toml").is_file():
        return candidate
    return Path.home() / "Documents" / "GitHub" / "spec-dev-knowledge-graph"


def _workflow_owner_repo() -> tuple[str, str]:
    try:
        url = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=True,
            cwd=_repo_root(),
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "_local", _repo_root().name

    match = re.search(r"[:/](?P<owner>[^/]+)/(?P<repo>[^/.]+?)(?:\.git)?$", url)
    if match:
        return match.group("owner"), match.group("repo")
    return "_local", _repo_root().name


def default_telemetry_path() -> Path:
    """Return the JSONL path for hook telemetry events."""
    override = os.environ.get("EM_HOOK_TELEMETRY_PATH", "").strip()
    if override:
        return Path(override).expanduser()
    owner, repo = _workflow_owner_repo()
    return Path.home() / ".cursor" / "workflow" / owner / repo / "telemetry" / "hook-events.jsonl"


def build_event(
    *,
    command: str,
    duration_ms: int,
    exit_code: int,
    project_id: str | None = None,
    result: dict[str, Any] | None = None,
    query: str | None = None,
) -> dict[str, Any]:
    """Build a normalized telemetry event dict for a hook invocation."""
    status, reason, retrieve_count, recommend_count = _derive_metrics(result, exit_code)
    return {
        "schema_version": SCHEMA_VERSION,
        "timestamp_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "command": command,
        "project_id": project_id,
        "duration_ms": duration_ms,
        "status": status,
        "reason": reason,
        "retrieve_count": retrieve_count,
        "recommend_count": recommend_count,
        "query_length": len(query) if query else None,
    }


def _derive_metrics(
    result: dict[str, Any] | None, exit_code: int
) -> tuple[str, str | None, int | None, int | None]:
    retrieve_count: int | None = None
    recommend_count: int | None = None

    if result is None:
        if exit_code == 0:
            return "ok", None, None, None
        return "error", "non-zero exit", None, None

    status = result.get("status")
    if status == "skipped":
        reason_val = result.get("reason")
        return "skipped", str(reason_val) if reason_val else "skipped", None, None

    data = result.get("data") if isinstance(result.get("data"), dict) else {}
    if status == "ok" and data:
        items = data.get("items")
        if isinstance(items, list):
            retrieve_count = len(items)
        recs = data.get("recommendations")
        if isinstance(recs, list):
            recommend_count = len(recs)

    if status == "error" or exit_code != 0:
        message = result.get("message") or result.get("reason") or "error"
        return "error", str(message), retrieve_count, recommend_count

    return "ok", None, retrieve_count, recommend_count


def append_event(event: dict[str, Any], path: Path | None = None) -> None:
    """Append one telemetry event to the JSONL log (no-op when disabled)."""
    if not telemetry_enabled():
        return
    log_path = path or default_telemetry_path()
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, sort_keys=True) + "\n")
    except OSError:
        pass


def emit_hook_event(
    *,
    command: str,
    duration_ms: int,
    exit_code: int,
    project_id: str | None = None,
    result: dict[str, Any] | None = None,
    query: str | None = None,
    path: Path | None = None,
) -> None:
    """Build and append a hook telemetry event."""
    append_event(
        build_event(
            command=command,
            duration_ms=duration_ms,
            exit_code=exit_code,
            project_id=project_id,
            result=result,
            query=query,
        ),
        path,
    )


def read_events(
    *,
    days: int | None = None,
    project_id: str | None = None,
    path: Path | None = None,
) -> list[dict[str, Any]]:
    """Read telemetry events from JSONL with optional day and project filters."""
    log_path = path or default_telemetry_path()
    if not log_path.is_file():
        return []

    cutoff: datetime | None = None
    if days is not None and days > 0:
        cutoff = datetime.now(UTC) - timedelta(days=days)

    events: list[dict[str, Any]] = []
    for line in log_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue
        if project_id and event.get("project_id") != project_id:
            continue
        if cutoff is not None:
            ts_raw = event.get("timestamp_utc")
            if isinstance(ts_raw, str):
                try:
                    ts = datetime.strptime(ts_raw, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
                    if ts < cutoff:
                        continue
                except ValueError:
                    continue
        events.append(event)
    return events


def summarize_events(events: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate rates, latency, and retrieval counts from hook events."""
    total = len(events)
    if total == 0:
        return {
            "total": 0,
            "skip_rate": 0.0,
            "error_rate": 0.0,
            "ok_rate": 0.0,
            "latency_ms": {"p50": 0, "p95": 0, "avg": 0},
            "avg_retrieve_count": 0.0,
            "avg_recommend_count": 0.0,
            "by_command": {},
        }

    skipped = sum(1 for e in events if e.get("status") == "skipped")
    errors = sum(1 for e in events if e.get("status") == "error")
    ok = total - skipped - errors
    durations = [int(e["duration_ms"]) for e in events if isinstance(e.get("duration_ms"), int)]
    retrieve_counts = [
        int(e["retrieve_count"]) for e in events if isinstance(e.get("retrieve_count"), int)
    ]
    recommend_counts = [
        int(e["recommend_count"]) for e in events if isinstance(e.get("recommend_count"), int)
    ]

    by_command: dict[str, int] = {}
    for event in events:
        cmd = str(event.get("command", "unknown"))
        by_command[cmd] = by_command.get(cmd, 0) + 1

    latency: dict[str, float | int] = {"p50": 0, "p95": 0, "avg": 0}
    if durations:
        sorted_d = sorted(durations)
        latency["avg"] = round(statistics.mean(sorted_d), 1)
        latency["p50"] = sorted_d[len(sorted_d) // 2]
        p95_idx = min(len(sorted_d) - 1, int(len(sorted_d) * 0.95))
        latency["p95"] = sorted_d[p95_idx]

    return {
        "total": total,
        "skip_rate": round(skipped / total, 4),
        "error_rate": round(errors / total, 4),
        "ok_rate": round(ok / total, 4),
        "latency_ms": latency,
        "avg_retrieve_count": round(statistics.mean(retrieve_counts), 2) if retrieve_counts else 0.0,
        "avg_recommend_count": round(statistics.mean(recommend_counts), 2)
        if recommend_counts
        else 0.0,
        "by_command": by_command,
    }


def export_events_csv(events: list[dict[str, Any]]) -> str:
    """Serialize telemetry events to CSV text."""
    fields = [
        "timestamp_utc",
        "command",
        "project_id",
        "duration_ms",
        "status",
        "reason",
        "retrieve_count",
        "recommend_count",
        "query_length",
    ]
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    for event in events:
        writer.writerow({key: event.get(key) for key in fields})
    return buffer.getvalue()


def format_report(summary: dict[str, Any], *, days: int, project_id: str | None) -> str:
    """Format a markdown telemetry summary report."""
    lines = [
        "# Hook telemetry report",
        "",
        f"**Window:** last {days} day(s)",
        f"**Project filter:** {project_id or '(all)'}",
        "",
        "## Summary",
        "",
        f"- Total invocations: {summary['total']}",
        f"- OK rate: {summary['ok_rate']:.1%}",
        f"- Skip rate: {summary['skip_rate']:.1%}",
        f"- Error rate: {summary['error_rate']:.1%}",
        "",
        "## Latency (ms)",
        "",
        f"- p50: {summary['latency_ms']['p50']}",
        f"- p95: {summary['latency_ms']['p95']}",
        f"- avg: {summary['latency_ms']['avg']}",
        "",
        "## Retrieval quality",
        "",
        f"- Avg retrieve count: {summary['avg_retrieve_count']}",
        f"- Avg recommend count: {summary['avg_recommend_count']}",
        "",
    ]
    if summary.get("by_command"):
        lines.extend(["## By command", ""])
        for cmd, count in sorted(summary["by_command"].items()):
            lines.append(f"- `{cmd}`: {count}")
        lines.append("")
    return "\n".join(lines)
