#!/usr/bin/env python3
"""Fetch and gate Supabase project advisors (Management API).

[Corpus: tech-spec] / [Corpus: deploy] — CI uses this from
``.github/workflows/supabase-sync.yml`` and ``scripts/security/run-supabase-advisors.sh``.

Available Management API advisor types (OpenAPI + probed): ``security``, ``performance``,
and ``health`` when the endpoint exists. MCP ``get_advisors`` exposes security + performance;
CLI ``supabase db advisors --type all`` covers the same two. Health is included when the
API returns 200.

Fail policy matches ``docs/policies/CONSUMER-GATES.md`` (ERROR) unless overridden with
``SEC_SUPABASE_ADVISORS_FAIL_ON`` / ``--fail-on`` (``none`` | ``info`` | ``warn`` | ``error``).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable, Iterable, Mapping, Sequence
from contextlib import AbstractContextManager
from dataclasses import dataclass
from typing import Any

# urllib.request.urlopen-compatible opener used for tests.
UrlOpener = Callable[..., AbstractContextManager[object]]

DEFAULT_API_BASE = "https://api.supabase.com/v1"
# All known advisor type paths. OpenAPI documents security + performance; health is
# probed (Studio Health Advisor). Unknown/404 types are skipped, not failures.
DEFAULT_ADVISOR_TYPES: tuple[str, ...] = ("security", "performance", "health")
LEVEL_RANK: dict[str, int] = {"INFO": 0, "WARN": 1, "ERROR": 2}
FAIL_ON_CHOICES: tuple[str, ...] = ("none", "info", "warn", "error")


@dataclass(frozen=True)
class AdvisorFetchResult:
    """One advisor-type fetch outcome."""

    advisor_type: str
    status: int | None
    lints: list[dict[str, Any]]
    skipped: bool
    skip_reason: str | None = None
    error: str | None = None


def normalize_level(raw: object) -> str:
    """Return uppercase INFO|WARN|ERROR; unknown values map to INFO (non-failing)."""
    if not isinstance(raw, str):
        return "INFO"
    key = raw.strip().upper()
    if key in LEVEL_RANK:
        return key
    # Tolerate CLI-ish aliases
    aliases = {"WARNING": "WARN", "ERR": "ERROR", "CRITICAL": "ERROR", "HIGH": "ERROR"}
    return aliases.get(key, "INFO")


def fail_threshold(fail_on: str) -> int | None:
    """Minimum LEVEL_RANK that fails; ``None`` means never fail on lint level."""
    key = fail_on.strip().lower()
    if key == "none":
        return None
    if key == "info":
        return LEVEL_RANK["INFO"]
    if key == "warn":
        return LEVEL_RANK["WARN"]
    if key == "error":
        return LEVEL_RANK["ERROR"]
    raise ValueError(f"invalid fail_on={fail_on!r}; choose from {FAIL_ON_CHOICES}")


def advisor_url(api_base: str, project_ref: str, advisor_type: str) -> str:
    """Build Management API advisors URL for one type (adds lint_type=sql for security)."""
    base = api_base.rstrip("/")
    path = f"{base}/projects/{urllib.parse.quote(project_ref)}/advisors/{urllib.parse.quote(advisor_type)}"
    if advisor_type == "security":
        # Documented optional query; SQL lint pack for security advisors.
        return f"{path}?{urllib.parse.urlencode({'lint_type': 'sql'})}"
    return path


def parse_lints_payload(payload: object) -> list[dict[str, Any]]:
    """Extract lint objects from a Management API advisors response body."""
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    if isinstance(payload, Mapping):
        lints = payload.get("lints")
        if isinstance(lints, list):
            return [x for x in lints if isinstance(x, dict)]
    return []


def fetch_advisor_type(
    *,
    api_base: str,
    project_ref: str,
    token: str,
    advisor_type: str,
    timeout: float = 60.0,
    opener: UrlOpener | None = None,
) -> AdvisorFetchResult:
    """GET one advisor type. 404 → skipped; other HTTP/network errors → error result."""
    url = advisor_url(api_base, project_ref, advisor_type)
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "User-Agent": "tac-to-iwxxm-supabase-advisors/1.0",
        },
        method="GET",
    )
    open_fn: UrlOpener = opener or urllib.request.urlopen
    try:
        with open_fn(req, timeout=timeout) as resp:
            status = getattr(resp, "status", 200)
            raw = resp.read()
    except urllib.error.HTTPError as exc:
        body = exc.read() if hasattr(exc, "read") else b""
        if exc.code == 404:
            return AdvisorFetchResult(
                advisor_type=advisor_type,
                status=404,
                lints=[],
                skipped=True,
                skip_reason="endpoint not available (404)",
            )
        detail = body.decode("utf-8", errors="replace")[:500]
        return AdvisorFetchResult(
            advisor_type=advisor_type,
            status=exc.code,
            lints=[],
            skipped=False,
            error=f"HTTP {exc.code}: {detail or exc.reason}",
        )
    except OSError as exc:
        return AdvisorFetchResult(
            advisor_type=advisor_type,
            status=None,
            lints=[],
            skipped=False,
            error=f"{type(exc).__name__}: {exc}",
        )

    try:
        payload: object = json.loads(
            raw.decode("utf-8") if isinstance(raw, bytes) else raw
        )
    except json.JSONDecodeError as exc:
        return AdvisorFetchResult(
            advisor_type=advisor_type,
            status=int(status),
            lints=[],
            skipped=False,
            error=f"invalid JSON: {exc}",
        )
    return AdvisorFetchResult(
        advisor_type=advisor_type,
        status=int(status),
        lints=parse_lints_payload(payload),
        skipped=False,
    )


def summarize_lints(lints: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    """Count lint findings by normalized severity level."""
    counts = {"ERROR": 0, "WARN": 0, "INFO": 0, "OTHER": 0}
    for lint in lints:
        level = normalize_level(lint.get("level"))
        if level in counts:
            counts[level] += 1
        else:
            counts["OTHER"] += 1
    return counts


def failing_lints(
    lints: Iterable[Mapping[str, Any]], fail_on: str
) -> list[dict[str, Any]]:
    """Return lints at or above the configured fail-on threshold."""
    threshold = fail_threshold(fail_on)
    if threshold is None:
        return []
    out: list[dict[str, Any]] = []
    for lint in lints:
        level = normalize_level(lint.get("level"))
        if LEVEL_RANK.get(level, 0) >= threshold:
            out.append(dict(lint))
    return out


def format_lint_line(lint: Mapping[str, Any], advisor_type: str) -> str:
    """One-line CI log summary for a single advisor finding."""
    level = normalize_level(lint.get("level"))
    name = lint.get("name") or lint.get("title") or "(unnamed)"
    title = lint.get("title") or ""
    cats = lint.get("categories") or []
    cat_s = ",".join(str(c) for c in cats) if isinstance(cats, list) else str(cats)
    detail = lint.get("detail") or lint.get("description") or ""
    remediation = lint.get("remediation") or ""
    parts = [
        f"[{advisor_type}] {level} {name}",
        f"title={title}" if title else "",
        f"categories={cat_s}" if cat_s else "",
        f"detail={detail}" if detail else "",
        f"remediation={remediation}" if remediation else "",
    ]
    return " | ".join(p for p in parts if p)


def run_advisors(
    *,
    project_ref: str,
    token: str,
    advisor_types: Sequence[str] = DEFAULT_ADVISOR_TYPES,
    fail_on: str = "error",
    api_base: str = DEFAULT_API_BASE,
    timeout: float = 60.0,
    opener: UrlOpener | None = None,
) -> tuple[int, list[str]]:
    """Fetch all advisor types; return (exit_code, log_lines)."""
    lines: list[str] = []
    all_lints: list[tuple[str, dict[str, Any]]] = []
    fetch_errors = 0
    fetched_any = False

    lines.append(
        f"Supabase advisors: project={project_ref} types={','.join(advisor_types)} "
        f"fail_on={fail_on}"
    )

    for advisor_type in advisor_types:
        result = fetch_advisor_type(
            api_base=api_base,
            project_ref=project_ref,
            token=token,
            advisor_type=advisor_type,
            timeout=timeout,
            opener=opener,
        )
        if result.skipped:
            lines.append(f"  skip {advisor_type}: {result.skip_reason or 'skipped'}")
            continue
        if result.error:
            fetch_errors += 1
            lines.append(f"  ERROR fetching {advisor_type}: {result.error}")
            continue
        fetched_any = True
        counts = summarize_lints(result.lints)
        lines.append(
            f"  {advisor_type}: {len(result.lints)} finding(s) "
            f"(ERROR={counts['ERROR']} WARN={counts['WARN']} INFO={counts['INFO']})"
        )
        for lint in result.lints:
            lines.append("    " + format_lint_line(lint, advisor_type))
            all_lints.append((advisor_type, lint))

    if fetch_errors:
        lines.append(
            f"Advisor fetch failed for {fetch_errors} type(s) "
            "(check SUPABASE_ACCESS_TOKEN: Dashboard → Account → Access Tokens)."
        )
        return 1, lines

    if not fetched_any:
        lines.append("No advisor endpoints returned data — treating as failure.")
        return 1, lines

    bad = failing_lints((lint for _, lint in all_lints), fail_on)
    total = summarize_lints([lint for _, lint in all_lints])
    lines.append(
        f"Summary: ERROR={total['ERROR']} WARN={total['WARN']} INFO={total['INFO']} "
        f"failing_under_{fail_on}={len(bad)}"
    )
    if bad:
        lines.append(
            f"FAIL: {len(bad)} advisor finding(s) at or above fail_on={fail_on}"
        )
        return 1, lines
    lines.append(f"PASS: no advisor findings at or above fail_on={fail_on}")
    return 0, lines


def _env_token() -> str:
    return (
        os.environ.get("SUPABASE_ACCESS_TOKEN", "").strip()
        or os.environ.get("SUPABASE_TOKEN", "").strip()
    )


def _env_ref() -> str:
    return (
        os.environ.get("SUPABASE_PROJECT_REF", "").strip()
        or os.environ.get("SUPABASE_PROJECT_ID", "").strip()
        or "ktvxijislbtgqapllmuk"
    )


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry: fetch advisors and exit non-zero on threshold / auth failures."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-ref",
        default=_env_ref(),
        help="Supabase project ref (default: SUPABASE_PROJECT_REF or ktvxijislbtgqapllmuk)",
    )
    parser.add_argument(
        "--token",
        default="",
        help="Access token (default: SUPABASE_ACCESS_TOKEN)",
    )
    parser.add_argument(
        "--type",
        dest="advisor_types",
        action="append",
        choices=[*DEFAULT_ADVISOR_TYPES, "all"],
        help="Advisor type to fetch (repeatable; default: all known types)",
    )
    parser.add_argument(
        "--fail-on",
        default=os.environ.get("SEC_SUPABASE_ADVISORS_FAIL_ON", "error"),
        choices=FAIL_ON_CHOICES,
        help="Minimum severity that fails the run (default: error / CONSUMER-GATES)",
    )
    parser.add_argument(
        "--api-base",
        default=os.environ.get("SUPABASE_MANAGEMENT_API_BASE", DEFAULT_API_BASE),
        help="Management API base URL",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    token = (args.token or _env_token()).strip()
    if not token:
        print(
            "ERROR: SUPABASE_ACCESS_TOKEN is required "
            "(Supabase Dashboard → Account → Access Tokens).",
            file=sys.stderr,
        )
        return 1

    types = args.advisor_types
    if not types or "all" in types:
        advisor_types: Sequence[str] = DEFAULT_ADVISOR_TYPES
    else:
        advisor_types = tuple(dict.fromkeys(types))

    code, lines = run_advisors(
        project_ref=args.project_ref.strip(),
        token=token,
        advisor_types=advisor_types,
        fail_on=args.fail_on,
        api_base=args.api_base,
    )
    for line in lines:
        print(line)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
