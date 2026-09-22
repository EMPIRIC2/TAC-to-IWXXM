"""Family-aware rule catalog aggregator (ADR-044)."""

from __future__ import annotations

from typing import Any, Literal

RuleFamily = Literal["tac", "iwxxm", "conversion", "dissemination", "decoding"]

_FAMILIES: frozenset[str] = frozenset({"tac", "iwxxm", "conversion", "dissemination", "decoding"})


def known_families() -> frozenset[str]:
    """
    Return supported ``family`` query values.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (known_families)
    2

    Returns
    -------
    object
        Return value.
    """
    return _FAMILIES


def catalog_for_family(family: str, *, product: str | None = None) -> list[dict[str, Any]]:
    """
    Aggregate package-owned catalog rows for ``family``.

    Parameters
    ----------
    family :
        One of ``tac``, ``iwxxm``, ``conversion``, ``dissemination``, ``decoding``.
    product :
        Optional product filter (TAC / IWXXM families).

    Returns
    -------
    list[dict[str, Any]]
        Normalized catalog items (``id``, ``title``, ``summary``, ``tags``).

    Raises
    ------
    ValueError
        When ``family`` is unknown.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (catalog_for_family)
    2
    """
    key = family.strip().lower()
    if key not in _FAMILIES:
        raise ValueError(f"Unknown catalog family {family!r}")

    if key == "tac":
        from tac_validate.issue_registry import catalog_entries

        return [
            {
                "id": spec.code,
                "title": spec.code,
                "summary": spec.message_template,
                "severity": spec.severity,
                "tags": [*list(spec.tags), "tac"],
            }
            for spec in catalog_entries(product=product)
        ]

    if key == "iwxxm":
        from src.services.iwxxm_validation_catalog import iwxxm_validation_catalog_rows

        return [
            {
                "id": (code := str(row.get("code") or row.get("id") or "")),
                "title": code,
                "summary": str(row.get("message_template") or row.get("summary") or ""),
                "severity": row.get("severity"),
                "tags": [*list(row.get("tags") or []), "iwxxm"],
            }
            for row in iwxxm_validation_catalog_rows()
        ]

    if key == "conversion":
        from tac2iwxxm.profile_registry import known_semantic_profile_ids

        return [
            {
                "id": pid,
                "title": pid,
                "summary": f"Semantic conversion profile {pid}",
                "tags": ["conversion", "profile"],
            }
            for pid in sorted(known_semantic_profile_ids())
        ]

    if key == "dissemination":
        from dissemination.exchange_registry import known_exchange_profile_ids

        return [
            {
                "id": pid,
                "title": pid,
                "summary": f"Exchange / dissemination profile {pid}",
                "tags": ["dissemination", "exchange"],
            }
            for pid in sorted(known_exchange_profile_ids())
        ]

    from tac_decoding import catalog_entries as decoding_catalog

    return decoding_catalog()


def selection_options(kind: str) -> list[dict[str, Any]]:
    """
    Lightweight dropdown options for deployed registries.

    Parameters
    ----------
    kind :
        ``conversion`` | ``dissemination`` | ``decoding``.

    Returns
    -------
    list[dict[str, Any]]
        ``id`` / ``label`` pairs.

    Raises
    ------
    ValueError
        When ``kind`` is unknown.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (selection_options)
    2
    """
    key = kind.strip().lower()
    if key == "conversion":
        from tac2iwxxm.profile_registry import known_semantic_profile_ids

        return [{"id": pid, "label": pid} for pid in sorted(known_semantic_profile_ids())]
    if key == "dissemination":
        from dissemination.exchange_registry import known_exchange_profile_ids

        return [{"id": pid, "label": pid} for pid in sorted(known_exchange_profile_ids())]
    if key == "decoding":
        from tac_decoding import catalog_entries

        return [{"id": row["id"], "label": row["title"]} for row in catalog_entries(limit=200)]
    raise ValueError(f"Unknown selection kind {kind!r}")
