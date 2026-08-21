"""Load precomputed quality-metrics corpus artifact (F7.q / EV-054)."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, cast

_DEFAULT_ARTIFACT = Path(__file__).resolve().parent.parent / "data" / "quality_metrics" / "corpus_metrics.json"


class QualityMetricsArtifactMissing(FileNotFoundError):
    """Raised when the committed corpus metrics JSON is absent."""


@lru_cache(maxsize=1)
def load_corpus_metrics(path: str | None = None) -> dict[str, Any]:
    """
    Load and cache ``corpus_metrics.json``.

    Parameters
    ----------
    path :
        Optional override path (tests). ``None`` uses the packaged default.

    Returns
    -------
    dict[str, Any]
        Parsed artifact with ``summaries``, ``files``, and ``details``.

    Raises
    ------
    QualityMetricsArtifactMissing
        When the artifact file is not present.
    """
    artifact = Path(path) if path else _DEFAULT_ARTIFACT
    if not artifact.is_file():
        raise QualityMetricsArtifactMissing(str(artifact))
    return json.loads(artifact.read_text(encoding="utf-8"))


def clear_corpus_metrics_cache() -> None:
    """Clear the cached artifact (tests / regenerate)."""
    load_corpus_metrics.cache_clear()


def list_file_rows(
    doc: dict[str, Any],
    *,
    product: str | None = None,
) -> list[dict[str, Any]]:
    """
    Return slim file inventory rows, optionally filtered by product.

    Parameters
    ----------
    doc :
        Loaded corpus metrics document.
    product :
        Optional product key (case-insensitive), e.g. ``metar``.

    Returns
    -------
    list[dict[str, Any]]
        File rows from ``doc["files"]``.
    """
    rows = list(doc.get("files") or [])
    if product is None:
        return rows
    key = product.strip().lower()
    return [r for r in rows if str(r.get("product", "")).lower() == key]


def get_detail(doc: dict[str, Any], stem: str) -> dict[str, Any] | None:
    """
    Return per-stem detail or ``None`` when unknown.

    Parameters
    ----------
    doc :
        Loaded corpus metrics document.
    stem :
        Catalog / fixture stem (e.g. ``metar-A3-1``).

    Returns
    -------
    dict[str, Any] | None
        Detail blob, or ``None``.
    """
    raw_details = doc.get("details")
    if not isinstance(raw_details, dict):
        return None
    found = cast(dict[str, Any], raw_details).get(stem)
    return cast(dict[str, Any], found) if isinstance(found, dict) else None
