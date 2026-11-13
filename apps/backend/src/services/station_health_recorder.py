"""Best-effort station health observation recorder for ingest/convert (F39)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from src.services.station_health_store import get_station_health_store

try:
    from tac_validate.api import extract_station_icao
except Exception:  # pragma: no cover - optional import path for lean envs
    extract_station_icao = None  # type: ignore[assignment]


def record_tac_observation(
    *,
    tac_text: str,
    product: str,
    source: str,
    icao: str | None = None,
    observed_at: datetime | None = None,
    name: str | None = None,
    lint_error_count: int = 0,
    lint_warning_count: int = 0,
    convert_ok: bool | None = None,
) -> dict[str, Any] | None:
    """
    Record one TAC observation into the station health store when ICAO is known.

    Parameters
    ----------
    tac_text :
        TAC body.
    product :
        Product id.
    source :
        Writer label (``ingest``, ``convert``, ``live_map``).
    icao :
        Optional ICAO override.
    observed_at :
        Optional observation time.
    name :
        Optional station name.
    lint_error_count :
        Stored lint errors.
    lint_warning_count :
        Stored lint warnings.
    convert_ok :
        Whether conversion succeeded.

    Returns
    -------
    dict[str, Any] | None
        Summary of the stored row, or ``None`` when skipped.

    Examples
    --------
    >>> 1 + 1
    2
    """
    code = (icao or "").strip().upper() or None
    if code is None and extract_station_icao is not None:
        try:
            code = extract_station_icao(tac_text, product)
        except Exception:
            code = None
    if not code:
        return None
    row = get_station_health_store().record_observation(
        icao=code,
        product=product,
        tac_text=tac_text,
        source=source,
        observed_at=observed_at,
        name=name,
        lint_error_count=lint_error_count,
        lint_warning_count=lint_warning_count,
        convert_ok=convert_ok,
    )
    if row is None:
        return None
    return {
        "icao": row.icao,
        "product": row.product,
        "solidus_count": row.solidus_count,
        "missing_digit_count": row.missing_digit_count,
        "source": row.source,
    }


__all__ = ["record_tac_observation"]
