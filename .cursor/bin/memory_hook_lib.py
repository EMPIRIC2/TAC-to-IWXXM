#!/usr/bin/env python3
"""Engineering memory hook library. [Corpus: skill-integration] [Corpus: hook-contract]"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_BIN = Path(__file__).resolve().parent
if str(_BIN) not in sys.path:
    sys.path.insert(0, str(_BIN))

from hook_telemetry import (
    default_telemetry_path,
    emit_hook_event,
    export_events_csv,
    format_report,
    read_events,
    summarize_events,
)

SESSION_SEGMENTS = ("workflow", "sessions")
DEFAULT_LIMIT_RETRIEVE = 10
DEFAULT_LIMIT_RECOMMEND = 10
_pending_telemetry_result: dict[str, Any] | None = None


def _set_telemetry_result(result: dict[str, Any] | None) -> None:
    global _pending_telemetry_result
    _pending_telemetry_result = result


def _take_telemetry_result() -> dict[str, Any] | None:
    global _pending_telemetry_result
    result, _pending_telemetry_result = _pending_telemetry_result, None
    return result


def _engineering_memory_root() -> Path:
    override = os.environ.get("EM_ENGINEERING_MEMORY_ROOT", "").strip()
    if override:
        return Path(override).resolve()
    here = Path(__file__).resolve()
    candidate = here.parents[3]
    if (candidate / "packages" / "engineering-memory" / "pyproject.toml").is_file():
        return candidate
    return Path.home() / "Documents" / "GitHub" / "spec-dev-knowledge-graph"


def _repo_root() -> Path:
    return _engineering_memory_root()


def _ensure_engineering_memory_importable() -> None:
    src = _repo_root() / "packages" / "engineering-memory" / "src"
    if src.is_dir():
        path = str(src)
        if path not in sys.path:
            sys.path.insert(0, path)


def hooks_enabled() -> bool:
    """Return whether memory hook CLI commands should call engineering-memory."""
    return os.environ.get("EM_MEMORY_HOOKS_ENABLED", "1").strip() not in ("0", "false", "False")


def graphiti_episodic_enabled() -> bool:
    """Return whether Graphiti episodic memory hooks are enabled."""
    return os.environ.get("EM_GRAPHITI_EPISODIC_ENABLED", "0").strip() == "1"


def _graphiti_core_available() -> bool:
    try:
        _ensure_engineering_memory_importable()
        from engineering_memory.graphiti.runner import graphiti_core_available

        return graphiti_core_available()
    except ImportError:
        return False


def _graphiti_group_prefix() -> str:
    return os.environ.get("GRAPHITI_GROUP_PREFIX", "em").strip() or "em"


def _worker_env() -> dict[str, str]:
    env = os.environ.copy()
    src = _repo_root() / "packages" / "engineering-memory" / "src"
    if src.is_dir():
        path = str(src)
        existing = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = f"{path}{os.pathsep}{existing}" if existing else path
    return env


def _queue_graphiti_worker(session_path: Path) -> dict[str, Any]:
    if not graphiti_episodic_enabled():
        return {"status": "disabled"}
    if not _graphiti_core_available():
        return {"status": "skipped", "reason": "graphiti-core not installed"}
    try:
        _ensure_engineering_memory_importable()
        from engineering_memory.graphiti.episodes import build_episodes

        episodes = build_episodes(session_path, group_prefix=_graphiti_group_prefix())
        if not episodes:
            return {"status": "skipped", "reason": "no episode sources in session directory"}

        proc = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "engineering_memory.graphiti.worker",
                "--session-path",
                str(session_path.resolve()),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
            cwd=str(_repo_root()),
            env=_worker_env(),
        )
        return {"status": "queued", "worker_pid": proc.pid}
    except ValueError as exc:
        return {"status": "skipped", "reason": str(exc)}
    except Exception as exc:  # noqa: BLE001
        return {"status": "skipped", "reason": str(exc)}


def _resolve_session_group_id(session_path: Path) -> str | None:
    try:
        _ensure_engineering_memory_importable()
        from engineering_memory.graphiti.episodes import build_episodes

        episodes = build_episodes(session_path, group_prefix=_graphiti_group_prefix())
        return episodes[0].group_id if episodes else None
    except ValueError:
        return None
    except Exception:
        return None


def _derive_owner_repo_from_session_path(session_path: Path) -> str | None:
    candidate = session_path.resolve()
    parts = candidate.parts
    for idx, part in enumerate(parts):
        if part == "workflow" and idx + 2 < len(parts):
            owner = parts[idx + 1]
            repo = parts[idx + 2]
            if owner and repo and repo != "sessions":
                return f"{owner}/{repo}"
    return None


def _git_root_from_path(start: Path) -> Path | None:
    """Walk parents from start until a .git directory is found."""
    current = start.resolve()
    if current.is_file():
        current = current.parent
    for parent in [current, *current.parents]:
        if (parent / ".git").exists():
            return parent
    return None


def _register_session_path_alias(session_path: Path, canonical_project_id: str) -> None:
    override = os.environ.get("EM_CONTEXT_PROJECT_ID", "").strip()
    if not override or not hooks_enabled():
        return
    alias = _derive_owner_repo_from_session_path(session_path)
    if not alias or alias == canonical_project_id:
        return
    try:
        _with_service(
            lambda svc: svc.append_project_alias(canonical_project_id, alias),
        )
    except Exception:
        pass


def resolve_project_id(session_path: Path | None = None) -> str | None:
    """Resolve canonical engineering-memory project id from env, session, or git remote."""
    override = os.environ.get("EM_CONTEXT_PROJECT_ID", "").strip()
    if override:
        return override

    candidate = session_path or Path.cwd()
    candidate = candidate.resolve()
    raw = _derive_owner_repo_from_session_path(candidate)
    if raw:
        return _canonicalize_project_id(raw)

    git_root = _git_root_from_path(candidate)
    try:
        url = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=True,
            cwd=git_root or candidate,
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

    match = re.search(r"[:/](?P<owner>[^/]+)/(?P<repo>[^/.]+?)(?:\.git)?$", url)
    if match:
        return _canonicalize_project_id(f"{match.group('owner')}/{match.group('repo')}")
    return None


def _canonicalize_project_id(raw_id: str) -> str:
    if not hooks_enabled():
        return raw_id
    candidates = [raw_id]
    if "/" in raw_id:
        repo_slug = raw_id.rsplit("/", 1)[-1]
        if repo_slug and repo_slug != raw_id:
            candidates.append(repo_slug)
    for candidate in candidates:
        try:
            result = _with_service(
                lambda svc, pid=candidate: svc.resolve_canonical_project_id(pid)
            )
            if result.get("status") == "ok":
                data = result.get("data") or {}
                canonical = data.get("canonical_project_id")
                if isinstance(canonical, str) and canonical:
                    return canonical
        except Exception:
            pass
    return raw_id


def _skip_payload(reason: str) -> dict[str, Any]:
    return {"status": "skipped", "reason": reason}


def _print_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def _service_result_to_exit(result: dict[str, Any]) -> int:
    if result.get("status") == "skipped":
        return 0
    if result.get("status") != "ok":
        return 1
    return 0


def cmd_check() -> int:
    """Run Neo4j health check and print JSON result."""
    if not hooks_enabled():
        payload = _skip_payload("EM_MEMORY_HOOKS_ENABLED=0")
        _set_telemetry_result(payload)
        _print_json(payload)
        return 0
    try:
        _ensure_engineering_memory_importable()
        from engineering_memory.config import load_settings
        from engineering_memory.db import check_neo4j_health

        settings = load_settings()
        health = check_neo4j_health(settings)
        payload = health.to_dict()
        _set_telemetry_result(payload)
        _print_json(payload)
        return 0 if health.status == "ok" else 1
    except ImportError as exc:
        payload = _skip_payload(f"engineering-memory not importable: {exc}")
        _set_telemetry_result(payload)
        _print_json(payload)
        return 1
    except Exception as exc:  # noqa: BLE001 — CLI boundary
        payload = {"status": "error", "message": str(exc)}
        _set_telemetry_result(payload)
        _print_json(payload)
        return 1


def _with_service(fn):  # type: ignore[no-untyped-def]
    _ensure_engineering_memory_importable()
    from engineering_memory.config import load_settings
    from engineering_memory.mcp.service import McpService

    settings = load_settings()
    with McpService(settings) as service:
        return fn(service)


def cmd_retrieve(project_id: str, query: str, limit: int) -> int:
    """Retrieve ranked knowledge for a project and query."""
    if not hooks_enabled():
        result = _skip_payload("EM_MEMORY_HOOKS_ENABLED=0")
        _set_telemetry_result(result)
        _print_json(result)
        return 0
    try:
        result = _with_service(
            lambda svc: svc.retrieve_relevant_knowledge(project_id, query, limit=limit)
        )
        _set_telemetry_result(result)
        _print_json(result)
        return _service_result_to_exit(result)
    except Exception as exc:  # noqa: BLE001
        result = {"status": "error", "message": str(exc)}
        _set_telemetry_result(result)
        _print_json(result)
        return 1


def cmd_recommend(project_id: str, query: str, limit: int) -> int:
    """Fetch advisory recommendations for a project and query."""
    if not hooks_enabled():
        result = _skip_payload("EM_MEMORY_HOOKS_ENABLED=0")
        _set_telemetry_result(result)
        _print_json(result)
        return 0
    try:
        result = _with_service(
            lambda svc: svc.get_recommendations(project_id, query, limit=limit)
        )
        _set_telemetry_result(result)
        _print_json(result)
        return _service_result_to_exit(result)
    except Exception as exc:  # noqa: BLE001
        result = {"status": "error", "message": str(exc)}
        _set_telemetry_result(result)
        _print_json(result)
        return 1


def cmd_record(project_id: str, session_path: Path, include_verification: bool) -> int:
    """Ingest a workflow session into engineering-memory."""
    if not hooks_enabled():
        result = _skip_payload("EM_MEMORY_HOOKS_ENABLED=0")
        _set_telemetry_result(result)
        _print_json(result)
        return 0
    try:
        result = _with_service(
            lambda svc: svc.ingest_session(
                project_id,
                str(session_path),
                include_verification=include_verification,
            )
        )
        _set_telemetry_result(result)
        _print_json(result)
        return _service_result_to_exit(result)
    except Exception as exc:  # noqa: BLE001
        result = {"status": "error", "message": str(exc)}
        _set_telemetry_result(result)
        _print_json(result)
        return 1


def _summarize_items(items: list[dict[str, Any]], max_items: int = 5) -> list[str]:
    lines: list[str] = []
    for item in items[:max_items]:
        label = item.get("label", "?")
        entity_id = item.get("entity_id", "?")
        score = item.get("score", "")
        props = item.get("properties") or {}
        title = props.get("title") or props.get("question") or props.get("name") or entity_id
        lines.append(f"- **{label}** `{entity_id}` (score={score}): {title}")
    return lines


def write_memory_context_report(
    report_path: Path,
    *,
    project_id: str | None,
    query: str,
    retrieve_result: dict[str, Any],
    recommend_result: dict[str, Any],
    skip_reason: str | None = None,
) -> None:
    """Write memory-context.md from retrieve and recommend hook results."""
    report_path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Memory context",
        "",
        f"Generated: {now}",
        "",
        f"**Project ID:** {project_id or '(unresolved)'}",
        f"**Query:** {query}",
        "",
    ]
    if skip_reason:
        lines.extend(["## Status", "", f"Skipped: {skip_reason}", ""])
    elif retrieve_result.get("status") == "skipped" or recommend_result.get("status") == "skipped":
        reason = retrieve_result.get("reason") or recommend_result.get("reason") or "hooks disabled"
        lines.extend(["## Status", "", f"Skipped: {reason}", ""])
    else:
        if retrieve_result.get("status") != "ok":
            lines.extend(
                [
                    "## Retrieve",
                    "",
                    f"Error: {retrieve_result.get('message', retrieve_result)}",
                    "",
                ]
            )
        else:
            items = (retrieve_result.get("data") or {}).get("items") or []
            lines.append("## Top retrieved knowledge")
            lines.append("")
            if items:
                lines.extend(_summarize_items(items))
            else:
                lines.append("(no items)")
            lines.append("")

        if recommend_result.get("status") != "ok":
            lines.extend(
                [
                    "## Recommendations",
                    "",
                    f"Error: {recommend_result.get('message', recommend_result)}",
                    "",
                ]
            )
        else:
            data = recommend_result.get("data") or {}
            recs = data.get("recommendations") or []
            amb = data.get("ambiguities") or []
            lines.append("## Advisory recommendations")
            lines.append("")
            if recs:
                for rec in recs[:3]:
                    summary = rec.get("summary", "")
                    conf = rec.get("confidence", "")
                    lines.append(f"- {summary} (confidence={conf})")
            else:
                lines.append("(none)")
            lines.append("")
            if amb:
                lines.append("## Ambiguities")
                lines.append("")
                for item in amb[:3]:
                    lines.append(f"- {item.get('kind', 'conflict')}: {item.get('description', '')}")
                lines.append("")

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def cmd_session_open(session_path: Path, query: str, report_path: Path | None) -> int:
    """Open a session: retrieve knowledge, recommend, and write memory-context.md."""
    report = report_path or (session_path / "reports" / "memory-context.md")
    if not hooks_enabled():
        write_memory_context_report(
            report,
            project_id=resolve_project_id(session_path),
            query=query,
            retrieve_result=_skip_payload("EM_MEMORY_HOOKS_ENABLED=0"),
            recommend_result=_skip_payload("EM_MEMORY_HOOKS_ENABLED=0"),
            skip_reason="EM_MEMORY_HOOKS_ENABLED=0",
        )
        _set_telemetry_result(_skip_payload("EM_MEMORY_HOOKS_ENABLED=0"))
        return 0

    project_id = resolve_project_id(session_path)
    if not project_id:
        result = {"status": "skipped", "reason": "project_id unresolved"}
        write_memory_context_report(
            report,
            project_id=None,
            query=query,
            retrieve_result={"status": "error", "message": "project_id unresolved"},
            recommend_result={"status": "error", "message": "project_id unresolved"},
            skip_reason="could not resolve project_id",
        )
        _set_telemetry_result(result)
        return 0

    check_code = cmd_check()
    if check_code != 0:
        result = {"status": "skipped", "reason": "engineering-memory unavailable (check failed)"}
        write_memory_context_report(
            report,
            project_id=project_id,
            query=query,
            retrieve_result={"status": "error", "message": "health check failed"},
            recommend_result={"status": "error", "message": "health check failed"},
            skip_reason="engineering-memory unavailable (check failed)",
        )
        _set_telemetry_result(result)
        return 0

    try:
        retrieve_result = _with_service(
            lambda svc: svc.retrieve_relevant_knowledge(
                project_id, query, limit=DEFAULT_LIMIT_RETRIEVE
            )
        )
        recommend_result = _with_service(
            lambda svc: svc.get_recommendations(project_id, query, limit=DEFAULT_LIMIT_RECOMMEND)
        )
    except Exception as exc:  # noqa: BLE001
        result = {"status": "error", "message": str(exc)}
        write_memory_context_report(
            report,
            project_id=project_id,
            query=query,
            retrieve_result={"status": "error", "message": str(exc)},
            recommend_result={"status": "error", "message": str(exc)},
            skip_reason=str(exc),
        )
        _set_telemetry_result(result)
        return 0

    write_memory_context_report(
        report,
        project_id=project_id,
        query=query,
        retrieve_result=retrieve_result,
        recommend_result=recommend_result,
    )
    retrieve_items = ((retrieve_result.get("data") or {}).get("items") or [])
    recommend_items = ((recommend_result.get("data") or {}).get("recommendations") or [])
    ok_payload = {
        "status": "ok",
        "data": {
            "items": retrieve_items,
            "recommendations": recommend_items,
        },
    }
    _set_telemetry_result(ok_payload)
    _print_json(
        {
            "status": "ok",
            "report": str(report),
            "project_id": project_id,
            "retrieve_status": retrieve_result.get("status"),
            "recommend_status": recommend_result.get("status"),
        }
    )
    return 0


def cmd_search_episodic(query: str, session_path: Path, limit: int) -> int:
    """Search Graphiti episodic memory for the session group."""
    if not hooks_enabled():
        result = _skip_payload("EM_MEMORY_HOOKS_ENABLED=0")
        _set_telemetry_result(result)
        _print_json(result)
        return 0

    if not graphiti_episodic_enabled():
        result = {"status": "skipped", "reason": "EM_GRAPHITI_EPISODIC_ENABLED=0"}
        _set_telemetry_result(result)
        _print_json(result)
        return 0

    gid = _resolve_session_group_id(session_path)
    if not gid:
        result = {
            "status": "error",
            "message": "could not derive group_id from session-path (missing or disallowed path)",
        }
        _set_telemetry_result(result)
        _print_json(result)
        return 1

    try:
        result = _with_service(
            lambda svc: svc.search_episodic_memory(query, group_ids=[gid], limit=limit)
        )
        _set_telemetry_result(result)
        _print_json(result)
        if result.get("status") == "skipped":
            return 0
        return _service_result_to_exit(result)
    except Exception as exc:  # noqa: BLE001
        result = {"status": "error", "message": str(exc)}
        _set_telemetry_result(result)
        _print_json(result)
        return 1


def cmd_session_close(session_path: Path, include_verification: bool) -> int:
    """Close a session: ingest session and optionally queue Graphiti worker."""
    project_id = resolve_project_id(session_path)
    if not project_id:
        result = _skip_payload("project_id unresolved")
        _set_telemetry_result(result)
        _print_json(result)
        return 0

    _register_session_path_alias(session_path, project_id)

    pending: dict[str, Any] | None = None
    if hooks_enabled():
        try:
            count_result = _with_service(lambda svc: svc.count_proposed_knowledge(project_id))
            if count_result.get("status") == "ok":
                count = int((count_result.get("data") or {}).get("count", 0))
                if count > 0:
                    pending = {
                        "count": count,
                        "review_command": (
                            f"engineering-memory review --project-id {project_id}"
                        ),
                    }
        except Exception:  # noqa: BLE001
            pending = None

    if not hooks_enabled():
        result = _skip_payload("EM_MEMORY_HOOKS_ENABLED=0")
        _set_telemetry_result(result)
        _print_json(result)
        return 0

    try:
        result = _with_service(
            lambda svc: svc.ingest_session(
                project_id,
                str(session_path),
                include_verification=include_verification,
            )
        )
        if pending and result.get("status") == "ok":
            data = dict(result.get("data") or {})
            data["pending_proposals"] = pending
            result = {**result, "data": data}
            print(
                f"Note: {pending['count']} proposed knowledge item(s) pending review — "
                f"run: {pending['review_command']}",
                file=sys.stderr,
            )
        graphiti_episodic: dict[str, Any]
        if result.get("status") == "ok":
            graphiti_episodic = _queue_graphiti_worker(session_path)
        else:
            graphiti_episodic = {
                "status": "skipped",
                "reason": "canonical ingest did not succeed",
            }
        data = dict(result.get("data") or {}) if isinstance(result.get("data"), dict) else {}
        data["graphiti_episodic"] = graphiti_episodic
        result = {**result, "data": data}
        _set_telemetry_result(result)
        _print_json(result)
        return _service_result_to_exit(result)
    except Exception as exc:  # noqa: BLE001
        result = {"status": "error", "message": str(exc)}
        _set_telemetry_result(result)
        _print_json(result)
        return 1


def cmd_telemetry_summary(days: int, project_id: str | None) -> int:
    """Print aggregated hook telemetry summary as JSON."""
    events = read_events(days=days, project_id=project_id)
    summary = summarize_events(events)
    payload = {"status": "ok", "data": summary}
    _set_telemetry_result(payload)
    _print_json(payload)
    return 0


def cmd_telemetry_export(days: int, fmt: str, output: Path | None) -> int:
    """Export hook telemetry events as JSON or CSV."""
    events = read_events(days=days)
    if fmt == "csv":
        content = export_events_csv(events)
    else:
        content = json.dumps(events, indent=2, sort_keys=True)
    payload = {"status": "ok", "data": {"count": len(events), "format": fmt}}
    _set_telemetry_result(payload)
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(content, encoding="utf-8")
        _print_json({**payload, "output": str(output)})
    else:
        print(content, end="\n" if fmt == "json" else "")
    return 0


def cmd_telemetry_report(days: int, project_id: str | None) -> int:
    """Print a markdown hook telemetry report."""
    events = read_events(days=days, project_id=project_id)
    summary = summarize_events(events)
    report = format_report(summary, days=days, project_id=project_id)
    payload = {"status": "ok", "data": summary}
    _set_telemetry_result(payload)
    print(report)
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build the memory-hook CLI argument parser."""
    parser = argparse.ArgumentParser(prog="memory-hook")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("check", help="Neo4j health check")

    p_ret = sub.add_parser("retrieve", help="Ranked knowledge retrieval")
    p_ret.add_argument("--project-id", required=True)
    p_ret.add_argument("--query", required=True)
    p_ret.add_argument("--limit", type=int, default=DEFAULT_LIMIT_RETRIEVE)

    p_rec = sub.add_parser("recommend", help="Advisory recommendations")
    p_rec.add_argument("--project-id", required=True)
    p_rec.add_argument("--query", required=True)
    p_rec.add_argument("--limit", type=int, default=DEFAULT_LIMIT_RECOMMEND)

    p_record = sub.add_parser("record", help="Ingest workflow session")
    p_record.add_argument("--project-id", required=True)
    p_record.add_argument("--session-path", type=Path, required=True)
    p_record.add_argument("--include-verification", action="store_true")

    p_open = sub.add_parser("session-open", help="Retrieve + recommend; write memory-context.md")
    p_open.add_argument("--session-path", type=Path, required=True)
    p_open.add_argument("--query", required=True)
    p_open.add_argument("--report", type=Path, default=None)

    p_close = sub.add_parser("session-close", help="Record session on orchestrator close")
    p_close.add_argument("--session-path", type=Path, required=True)
    p_close.add_argument("--include-verification", action="store_true")

    p_epi = sub.add_parser("search-episodic", help="Search Graphiti episodic memory")
    p_epi.add_argument("--query", required=True)
    p_epi.add_argument("--session-path", type=Path, required=True)
    p_epi.add_argument("--limit", type=int, default=5)

    p_resolve = sub.add_parser("resolve-project-id", help="Print resolved project id")
    p_resolve.add_argument("--session-path", type=Path, default=None)

    p_telemetry = sub.add_parser("telemetry", help="Hook telemetry summary and export")
    tel_sub = p_telemetry.add_subparsers(dest="telemetry_cmd", required=True)

    p_sum = tel_sub.add_parser("summary", help="Aggregate skip/latency/error rates")
    p_sum.add_argument("--days", type=int, default=7)
    p_sum.add_argument("--project-id", default=None)

    p_exp = tel_sub.add_parser("export", help="Export JSONL events")
    p_exp.add_argument("--days", type=int, default=7)
    p_exp.add_argument("--format", choices=("json", "csv"), default="json")
    p_exp.add_argument("--output", type=Path, default=None)

    p_rep = tel_sub.add_parser("report", help="Markdown telemetry report")
    p_rep.add_argument("--days", type=int, default=7)
    p_rep.add_argument("--project-id", default=None)

    return parser


def _resolve_telemetry_context(args: argparse.Namespace) -> tuple[str | None, str | None]:
    project_id: str | None = getattr(args, "project_id", None)
    query: str | None = getattr(args, "query", None)
    session_path = getattr(args, "session_path", None)
    if project_id:
        return project_id, query
    if session_path is not None:
        return resolve_project_id(session_path), query
    return None, query


def _run_with_telemetry(args: argparse.Namespace, command: str, runner) -> int:  # type: ignore[no-untyped-def]
    project_id, query = _resolve_telemetry_context(args)
    start = time.perf_counter()
    exit_code = runner()
    duration_ms = int((time.perf_counter() - start) * 1000)
    emit_hook_event(
        command=command,
        duration_ms=duration_ms,
        exit_code=exit_code,
        project_id=project_id,
        result=_take_telemetry_result(),
        query=query,
        path=default_telemetry_path(),
    )
    return exit_code


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for memory-hook commands."""
    args = build_parser().parse_args(argv)
    if args.cmd == "telemetry":
        if args.telemetry_cmd == "summary":
            return _run_with_telemetry(
                args, f"telemetry-{args.telemetry_cmd}", lambda: cmd_telemetry_summary(args.days, args.project_id)
            )
        if args.telemetry_cmd == "export":
            return _run_with_telemetry(
                args,
                f"telemetry-{args.telemetry_cmd}",
                lambda: cmd_telemetry_export(args.days, args.format, args.output),
            )
        if args.telemetry_cmd == "report":
            return _run_with_telemetry(
                args, f"telemetry-{args.telemetry_cmd}", lambda: cmd_telemetry_report(args.days, args.project_id)
            )
        return 1
    if args.cmd == "check":
        return _run_with_telemetry(args, args.cmd, cmd_check)
    if args.cmd == "retrieve":
        return _run_with_telemetry(
            args, args.cmd, lambda: cmd_retrieve(args.project_id, args.query, args.limit)
        )
    if args.cmd == "recommend":
        return _run_with_telemetry(
            args, args.cmd, lambda: cmd_recommend(args.project_id, args.query, args.limit)
        )
    if args.cmd == "record":
        return _run_with_telemetry(
            args,
            args.cmd,
            lambda: cmd_record(args.project_id, args.session_path, args.include_verification),
        )
    if args.cmd == "session-open":
        return _run_with_telemetry(
            args, args.cmd, lambda: cmd_session_open(args.session_path, args.query, args.report)
        )
    if args.cmd == "session-close":
        return _run_with_telemetry(
            args,
            args.cmd,
            lambda: cmd_session_close(args.session_path, args.include_verification),
        )
    if args.cmd == "search-episodic":
        return _run_with_telemetry(
            args,
            args.cmd,
            lambda: cmd_search_episodic(args.query, args.session_path, args.limit),
        )
    if args.cmd == "resolve-project-id":
        def _resolve() -> int:
            pid = resolve_project_id(args.session_path)
            _set_telemetry_result({"status": "ok" if pid else "error", "project_id": pid})
            _print_json({"project_id": pid})
            return 0 if pid else 1

        return _run_with_telemetry(args, args.cmd, _resolve)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
