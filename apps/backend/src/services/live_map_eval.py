"""Build and schedule live-map evaluation snapshots (FR-045 / D-027)."""

from __future__ import annotations

import asyncio
import contextlib
import logging
import os
from collections import Counter
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from typing import Any, cast

from src.services.live_map_cache import LiveMapCache
from src.services.live_map_eval_store import (
    LiveMapEvalStore,
    empty_snapshot,
    get_live_map_eval_store,
)

logger = logging.getLogger(__name__)

# Keep in sync with ``routers.live_map.MAP_PRODUCTS`` (avoid importing the router
# here — that creates a circular import with ``live_map`` → ``live_map_eval``).
_MAP_PRODUCTS = frozenset({"metar", "speci", "taf", "airmet", "sigmet", "vaa", "tca", "vona"})
_WORLD = {"west": -180.0, "south": -90.0, "east": 180.0, "north": 90.0}
_eval_stop: asyncio.Event | None = None
_eval_task: asyncio.Task[None] | None = None


def _live_map_cache() -> LiveMapCache:
    """Lazy import so the router can depend on this module at load time.

    Returns
    -------
    LiveMapCache
        Process cache from the live-map router singleton.
    """
    from src.routers.live_map import get_live_map_cache

    return get_live_map_cache()


def eval_interval_seconds() -> int:
    """Return cron interval from ``LIVE_MAP_EVAL_INTERVAL_SEC`` (default 900).

    Returns
    -------
    int
        Seconds between computes; at least 60.
    """
    raw = (os.getenv("LIVE_MAP_EVAL_INTERVAL_SEC") or "900").strip()
    try:
        value = int(raw)
    except ValueError:
        return 900
    return max(60, value)


def refresh_enabled() -> bool:
    """Whether ``POST /eval/refresh`` is allowed.

    Returns
    -------
    bool
        True when the refresh env flag is on.
    """
    return (os.getenv("LIVE_MAP_EVAL_REFRESH_ENABLED") or "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def _report_issues(report: Mapping[str, object]) -> list[str]:
    """Return string issue codes from one cache report.

    Parameters
    ----------
    report :
        One report mapping from a live-map place payload.

    Returns
    -------
    list[str]
        Issue strings (empty when absent or not a list).
    """
    issues_value = report.get("issues")
    if not isinstance(issues_value, list):
        return []
    return [str(item) for item in cast(list[object], issues_value)]


def _accumulate_report(
    report: Mapping[str, object],
    *,
    place_key: str,
    product: str,
    code_counts: Counter[str],
    failures: list[dict[str, str]],
) -> tuple[int, int, int, int, int]:
    """Fold one report into lint/IWXXM counters.

    Parameters
    ----------
    report :
        One report mapping.
    place_key :
        Station or place id.
    product :
        Map product id.
    code_counts :
        Running lint-code histogram (mutated).
    failures :
        Running failure rows (mutated).

    Returns
    -------
    tuple[int, int, int, int, int]
        ``(lint_delta, convert_fail, iwxxm_pass, iwxxm_fail, partial)``.
    """
    issues = _report_issues(report)
    lint_delta = 0
    if issues:
        lint_delta = len(issues)
        for issue in issues:
            code = issue.split(":", 1)[0].strip() or issue.strip()
            if code:
                code_counts[code] += 1
            failures.append(
                {
                    "place_key": place_key,
                    "product": product,
                    "stage": "lint",
                    "code": code or "ISSUE",
                }
            )
    iwxxm = report.get("iwxxm")
    iwxxm_text = str(iwxxm) if iwxxm else ""
    # Quarantine shells carry original TAC (#1563). Label as translation-failed
    # XML / blocked-with-TAC — not operational IWXXM pass and not iwxxm_skip.
    if iwxxm_text and "translationFailedTAC" in iwxxm_text:
        failures.append(
            {
                "place_key": place_key,
                "product": product,
                "stage": "convert",
                "code": "TRANSLATION_FAILED",
            }
        )
        return lint_delta, 1, 0, 0, 0
    if iwxxm_text:
        return lint_delta, 0, 1, 0, 0
    if issues:
        failures.append(
            {
                "place_key": place_key,
                "product": product,
                "stage": "convert",
                "code": "TRANSLATION_FAILED",
            }
        )
        return lint_delta, 1, 0, 1, 0
    return lint_delta, 0, 0, 0, 1


def build_snapshot_from_places(
    places: Sequence[Mapping[str, Any]],
    *,
    computed_at: datetime | None = None,
) -> dict[str, Any]:
    """Aggregate live-map place payloads into an FR-045 snapshot.

    Parameters
    ----------
    places :
        ``LiveMapCache.query`` place dicts.
    computed_at :
        Snapshot timestamp.

    Returns
    -------
    dict[str, Any]
        Contract-shaped payload.
    """
    stamp = computed_at or datetime.now(tz=UTC)
    body = empty_snapshot(computed_at=stamp)
    products = sorted({str(p.get("product", "")).lower() for p in places} & set(_MAP_PRODUCTS))
    if products:
        body["products"] = products

    code_counts: Counter[str] = Counter()
    failures: list[dict[str, str]] = []
    lint_total = 0
    convert_fail = 0
    iwxxm_pass = 0
    iwxxm_fail = 0
    partial = 0

    for place in places:
        place_key = str(place.get("place_key") or "")
        product = str(place.get("product") or "")
        reports_raw = place.get("reports")
        if not isinstance(reports_raw, list):
            continue
        for report_raw in cast(list[object], reports_raw):
            if not isinstance(report_raw, Mapping):
                continue
            lint_d, conv_d, pass_d, fail_d, part_d = _accumulate_report(
                cast(Mapping[str, object], report_raw),
                place_key=place_key,
                product=product,
                code_counts=code_counts,
                failures=failures,
            )
            lint_total += lint_d
            convert_fail += conv_d
            iwxxm_pass += pass_d
            iwxxm_fail += fail_d
            partial += part_d

    body["partial_decode_count"] = partial
    body["lint_count"] = lint_total
    body["top_lint_codes"] = [{"code": code, "count": count} for code, count in code_counts.most_common(10)]
    body["convert_failure_count"] = convert_fail
    body["iwxxm_validation"] = {
        "pass": iwxxm_pass,
        "fail": iwxxm_fail,
        "skip": partial,
    }
    body["failure_locations"] = failures[:100]
    return body


def compute_and_store(
    cache: LiveMapCache | None = None,
    store: LiveMapEvalStore | None = None,
) -> dict[str, Any]:
    """Scan world bbox cache and write a snapshot.

    Parameters
    ----------
    cache :
        Live-map cache; defaults to the process singleton.
    store :
        Snapshot store; defaults to the process singleton.

    Returns
    -------
    dict[str, Any]
        Stored snapshot.
    """
    cache = cache or _live_map_cache()
    store = store or get_live_map_eval_store()
    places = cache.query(**_WORLD, products=set(_MAP_PRODUCTS))
    payload = build_snapshot_from_places(places)
    return store.write_snapshot(payload)


async def _eval_loop(stop: asyncio.Event) -> None:
    """Sleep ``LIVE_MAP_EVAL_INTERVAL_SEC`` between computes.

    Parameters
    ----------
    stop :
        Event set by ``stop_live_map_eval`` to end the loop.
    """
    while not stop.is_set():
        try:
            await asyncio.to_thread(compute_and_store)
        except Exception:  # pragma: no cover - keep loop alive
            logger.exception("live_map_eval: compute failed")
        try:
            await asyncio.wait_for(stop.wait(), timeout=float(eval_interval_seconds()))
        except TimeoutError:
            continue


def start_live_map_eval() -> asyncio.Event | None:
    """Start the eval cron loop when not disabled.

    Returns
    -------
    asyncio.Event | None
        Stop event, or None when not started.
    """
    global _eval_stop, _eval_task
    if _eval_task is not None and not _eval_task.done():
        return _eval_stop
    raw = (os.getenv("LIVE_MAP_EVAL_INTERVAL_SEC") or "900").strip()
    if raw in {"0", "false", "off"}:
        return None
    stop = asyncio.Event()
    _eval_stop = stop
    _eval_task = asyncio.create_task(_eval_loop(stop), name="live-map-eval")
    logger.info("live_map_eval: loop started interval=%ss", eval_interval_seconds())
    return stop


async def stop_live_map_eval(stop: asyncio.Event | None) -> None:
    """Stop the eval loop.

    Parameters
    ----------
    stop :
        Stop event from ``start_live_map_eval``, or None when never started.
    """
    global _eval_task, _eval_stop
    if stop is not None:
        stop.set()
    task = _eval_task
    _eval_task = None
    _eval_stop = None
    if task is not None:
        try:
            await asyncio.wait_for(task, timeout=5.0)
        except (TimeoutError, asyncio.CancelledError):
            task.cancel()
            with contextlib.suppress(TimeoutError, asyncio.CancelledError):
                await task
