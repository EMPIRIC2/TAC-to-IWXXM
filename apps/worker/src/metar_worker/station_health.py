"""Best-effort station health observation writer for the ingest worker (F39)."""

from __future__ import annotations

import logging
import re
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)

_METAR_SPECI_ICAO_RE = re.compile(
    r"^(?:METAR|SPECI)\s+([A-Z][A-Z0-9]{3})\b",
    re.IGNORECASE | re.MULTILINE,
)
_TAF_ICAO_RE = re.compile(
    r"^TAF(?:\s+AMD|\s+COR)?\s+([A-Z][A-Z0-9]{3})\b",
    re.IGNORECASE | re.MULTILINE,
)
_MISSING_DIGIT_RE = re.compile(r"/{2,}")


def extract_icao(tac_text: str, product: str) -> str | None:
    """Return a station ICAO from METAR, SPECI, or TAF text."""
    product_u = (product or "").upper()
    text_body = tac_text or ""
    if product_u == "TAF":
        matched = _TAF_ICAO_RE.search(text_body)
    elif product_u in {"METAR", "SPECI"}:
        matched = _METAR_SPECI_ICAO_RE.search(text_body)
    else:
        return None
    if matched is None:
        return None
    return matched.group(1).upper()


def solidus_counts(tac_text: str) -> tuple[int, int]:
    """Return ``(solidus_count, missing_digit_count)`` for TAC text."""
    body = tac_text or ""
    return body.count("/"), sum(1 for _ in _MISSING_DIGIT_RE.finditer(body))


def record_station_observation(
    engine: Engine,
    *,
    tac_text: str,
    product: str,
    convert_ok: bool,
    source: str = "ingest",
) -> str | None:
    """
    Upsert station registry and append one TAC observation row.

    Returns
    -------
    str | None
        ICAO when recorded, otherwise ``None``.
    """
    icao = extract_icao(tac_text, product)
    if not icao:
        return None
    product_l = (product or "").strip().lower() or "unknown"
    solidus_count, missing_digit_count = solidus_counts(tac_text)
    now = datetime.now(UTC)
    try:
        with engine.begin() as conn:
            conn.execute(
                text(
                    """
                    INSERT INTO station_registry (
                        icao, name, country, latitude, longitude,
                        first_seen_at, last_seen_at, updated_at
                    ) VALUES (
                        :icao, NULL, NULL, NULL, NULL,
                        :now, :now, :now
                    )
                    ON CONFLICT (icao) DO UPDATE SET
                        last_seen_at = EXCLUDED.last_seen_at,
                        updated_at = EXCLUDED.updated_at
                    """
                ),
                {"icao": icao, "now": now},
            )
            conn.execute(
                text(
                    """
                    INSERT INTO station_tac_records (
                        icao, product, observed_at, ingested_at, tac_text, source,
                        solidus_count, missing_digit_count,
                        lint_error_count, lint_warning_count, convert_ok
                    ) VALUES (
                        :icao, :product, :observed_at, :ingested_at, :tac_text, :source,
                        :solidus_count, :missing_digit_count,
                        0, 0, :convert_ok
                    )
                    """
                ),
                {
                    "icao": icao,
                    "product": product_l,
                    "observed_at": now,
                    "ingested_at": now,
                    "tac_text": tac_text or "",
                    "source": source,
                    "solidus_count": solidus_count,
                    "missing_digit_count": missing_digit_count,
                    "convert_ok": convert_ok,
                },
            )
    except Exception:
        logger.exception("station health record failed for %s", icao)
        return None
    return icao


def maybe_record_from_row(
    engine: Engine | None, row: dict[str, Any], *, convert_ok: bool
) -> None:
    """Record when an engine is available; swallow failures."""
    if engine is None:
        return
    record_station_observation(
        engine,
        tac_text=str(row.get("tac_input") or ""),
        product=str(row.get("product") or ""),
        convert_ok=convert_ok,
        source="ingest",
    )


__all__ = [
    "extract_icao",
    "maybe_record_from_row",
    "record_station_observation",
    "solidus_counts",
]
