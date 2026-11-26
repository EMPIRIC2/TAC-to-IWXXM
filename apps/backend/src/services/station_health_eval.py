"""Join FR-045 live-map eval snapshots into Station health (FR-047 / FR-072)."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any, cast

from src.services.live_map_eval_store import empty_snapshot, get_live_map_eval_store

_ICAO_LEN = 4


def _as_str(value: object, default: str = "") -> str:
    """Coerce ``value`` to ``str``.

    Parameters
    ----------
    value :
        Raw value.
    default :
        Fallback when value is None.

    Returns
    -------
    str
        String form.
    """
    if value is None:
        return default
    return str(value)


def _as_int(value: object, default: int = 0) -> int:
    """Coerce ``value`` to ``int``.

    Parameters
    ----------
    value :
        Raw value.
    default :
        Fallback on error.

    Returns
    -------
    int
        Integer form.
    """
    try:
        return int(cast(Any, value))
    except (TypeError, ValueError):
        return default


def normalize_icao_filter(icao: str | None) -> str | None:
    """Validate an optional ICAO filter for eval-failure joins.

    Parameters
    ----------
    icao :
        Raw query value.

    Returns
    -------
    str | None
        Uppercase ICAO, or None when absent.

    Raises
    ------
    ValueError
        When the value is present but not a four-letter ICAO.
    """
    if icao is None:
        return None
    key = icao.strip().upper()
    if not key:
        return None
    if len(key) != _ICAO_LEN or not key.isalpha():
        raise ValueError("icao must be a four-letter station identifier")
    return key


def filter_failure_locations(
    rows: Sequence[Mapping[str, object]] | Sequence[object],
    *,
    icao: str | None,
) -> list[dict[str, str]]:
    """Keep failure rows whose ``place_key`` matches ``icao`` (case-insensitive).

    Parameters
    ----------
    rows :
        Snapshot ``failure_locations``.
    icao :
        Uppercase ICAO, or None to keep all rows.

    Returns
    -------
    list[dict[str, str]]
        Normalized failure rows.
    """
    out: list[dict[str, str]] = []
    needle = icao.upper() if icao else None
    for raw in rows:
        if not isinstance(raw, Mapping):
            continue
        item = cast(Mapping[str, object], raw)
        place_key = _as_str(item.get("place_key"))
        if needle is not None and place_key.upper() != needle:
            continue
        out.append(
            {
                "place_key": place_key,
                "product": _as_str(item.get("product")).lower(),
                "stage": _as_str(item.get("stage")).lower(),
                "code": _as_str(item.get("code")),
            }
        )
    return out


def product_failure_breakdown(
    failures: Sequence[Mapping[str, str]],
) -> list[dict[str, object]]:
    """Count failure rows per product for the eval-benchmark panel.

    Parameters
    ----------
    failures :
        Normalized failure locations.

    Returns
    -------
    list[dict[str, object]]
        Sorted ``{product, failure_count}`` rows.
    """
    counts: Counter[str] = Counter()
    for row in failures:
        product = _as_str(row.get("product")).lower() or "unknown"
        counts[product] += 1
    return [
        {"product": product, "failure_count": count}
        for product, count in sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))
    ]


def build_eval_benchmark(*, icao: str | None = None) -> dict[str, Any]:
    """Build the Station health eval-benchmark payload from the latest FR-045 snapshot.

    Parameters
    ----------
    icao :
        Optional ICAO filter for ``failure_locations``.

    Returns
    -------
    dict[str, Any]
        Contract-shaped body including product failure breakdown.
    """
    snapshot = get_live_map_eval_store().read_latest()
    if not snapshot:
        snapshot = empty_snapshot()
    failures_raw = snapshot.get("failure_locations")
    if not isinstance(failures_raw, list):
        failures_raw = []
    failures = filter_failure_locations(
        cast(list[object], failures_raw),
        icao=icao,
    )
    iwxxm_raw = snapshot.get("iwxxm_validation")
    iwxxm: dict[str, int]
    if isinstance(iwxxm_raw, Mapping):
        typed = cast(Mapping[str, object], iwxxm_raw)
        iwxxm = {
            "pass": _as_int(typed.get("pass")),
            "fail": _as_int(typed.get("fail")),
            "skip": _as_int(typed.get("skip")),
        }
    else:
        iwxxm = {"pass": 0, "fail": 0, "skip": 0}
    products_raw = snapshot.get("products")
    products = (
        [str(item).lower() for item in cast(list[object], products_raw)] if isinstance(products_raw, list) else []
    )
    top_raw = snapshot.get("top_lint_codes")
    top_codes: list[dict[str, object]] = []
    if isinstance(top_raw, list):
        for entry in cast(list[object], top_raw):
            if not isinstance(entry, Mapping):
                continue
            row = cast(Mapping[str, object], entry)
            top_codes.append(
                {
                    "code": _as_str(row.get("code")),
                    "count": _as_int(row.get("count")),
                }
            )
    return {
        "computed_at": _as_str(snapshot.get("computed_at")),
        "window_hours": _as_int(snapshot.get("window_hours"), 24),
        "products": products,
        "partial_decode_count": _as_int(snapshot.get("partial_decode_count")),
        "lint_count": _as_int(snapshot.get("lint_count")),
        "top_lint_codes": top_codes,
        "convert_failure_count": _as_int(snapshot.get("convert_failure_count")),
        "iwxxm_validation": iwxxm,
        "failure_locations": failures,
        "product_breakdown": product_failure_breakdown(failures),
        "icao_filter": icao,
    }
