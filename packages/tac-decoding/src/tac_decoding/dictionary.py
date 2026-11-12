"""Code-name dictionary rows tagged by product, country, and WMO amendment.

Extends the Decoding glossary for the operator Code names tab (F9 deepen / F7).
Rows are read-only. Do not put planning ids in operator-facing strings.
"""

from __future__ import annotations

from collections.abc import Mapping
from functools import lru_cache
from importlib import resources
from pathlib import Path
from typing import Any, cast

import yaml

from tac_decoding.glossary import load_glossary

_CORE_OBS = ("METAR", "SPECI")
_CORE_FCST = ("TAF",)
_SIGMET_FAMILY = ("SIGMET", "AIRMET")
_ADVISORY_VA = ("VAA", "SIGMET")
_ADVISORY_TC = ("TCA", "SIGMET")
_ADVISORY_SW = ("SWXA",)
_ADVISORY_VONA = ("VONA",)
_ALL_COMMON = ("METAR", "SPECI", "TAF", "SIGMET", "AIRMET")

# Token → (products, countries, wmo_amendment) when YAML omits dictionary tags.
_DEFAULT_TAGS: dict[str, tuple[tuple[str, ...], tuple[str, ...], str | None]] = {
    "OBSC": (_SIGMET_FAMILY, ("INTL",), "WMO No. 306"),
    "EMBD": (_SIGMET_FAMILY + _CORE_OBS, ("INTL",), "WMO No. 306"),
    "FRQ": (_SIGMET_FAMILY, ("INTL",), "WMO No. 306"),
    "SQL": (_SIGMET_FAMILY, ("INTL",), "WMO No. 306"),
    "ISOL": (_SIGMET_FAMILY + _CORE_OBS, ("INTL",), "WMO No. 306"),
    "OCNL": (_SIGMET_FAMILY + _CORE_OBS, ("INTL",), "WMO No. 306"),
    "SEV": (_SIGMET_FAMILY, ("INTL",), "WMO No. 306"),
    "MOD": (_SIGMET_FAMILY + _CORE_OBS, ("INTL",), "WMO No. 306"),
    "HVY": (_CORE_OBS + _SIGMET_FAMILY, ("INTL",), "WMO No. 306"),
    "VALID": (_SIGMET_FAMILY + _ADVISORY_VA[:1] + _ADVISORY_TC[:1], ("INTL",), "WMO No. 306"),
    "OF": (_ALL_COMMON, ("INTL",), "WMO No. 306"),
    "AND": (_ALL_COMMON, ("INTL",), "WMO No. 306"),
    "FIR/UIR": (_SIGMET_FAMILY, ("INTL",), "WMO No. 306"),
    "TS": (_CORE_OBS + _SIGMET_FAMILY, ("INTL",), "WMO No. 306"),
    "TSGR": (_CORE_OBS + _SIGMET_FAMILY, ("INTL",), "WMO No. 306"),
    "ICE": (_SIGMET_FAMILY, ("INTL",), "WMO No. 306"),
    "TURB": (_SIGMET_FAMILY, ("INTL",), "WMO No. 306"),
    "MTW": (_SIGMET_FAMILY, ("INTL",), "WMO No. 306"),
    "DS": (_CORE_OBS + _SIGMET_FAMILY, ("INTL",), "WMO No. 306"),
    "SS": (_CORE_OBS + _SIGMET_FAMILY, ("INTL",), "WMO No. 306"),
    "VA": (_ADVISORY_VA + _CORE_OBS, ("INTL",), "WMO No. 306"),
    "TC": (_ADVISORY_TC, ("INTL",), "WMO No. 306"),
    "GR": (_CORE_OBS + _SIGMET_FAMILY, ("INTL",), "WMO No. 306"),
    "FZRA": (_CORE_OBS + _CORE_FCST + _SIGMET_FAMILY, ("INTL",), "WMO No. 306"),
    "LINE": (_SIGMET_FAMILY, ("INTL",), "WMO No. 306"),
    "RDOACT": (_SIGMET_FAMILY, ("INTL",), "WMO No. 306"),
    "CLD": (_SIGMET_FAMILY + _ADVISORY_VA[:1], ("INTL",), "WMO No. 306"),
    "CB": (_CORE_OBS + _SIGMET_FAMILY, ("INTL",), "WMO No. 306"),
    "TCU": (_CORE_OBS, ("INTL",), "WMO No. 306"),
    "STNR": (_SIGMET_FAMILY, ("INTL",), "WMO No. 306"),
    "WKN": (_SIGMET_FAMILY, ("INTL",), "WMO No. 306"),
    "INTSF": (_SIGMET_FAMILY, ("INTL",), "WMO No. 306"),
    "NC": (_SIGMET_FAMILY, ("INTL",), "WMO No. 306"),
    "MOV": (_SIGMET_FAMILY + _ADVISORY_VA[:1] + _ADVISORY_TC[:1], ("INTL",), "WMO No. 306"),
    "OBS": (_SIGMET_FAMILY + _ADVISORY_VA[:1], ("INTL",), "WMO No. 306"),
    "FCST": (_SIGMET_FAMILY + _CORE_FCST, ("INTL",), "WMO No. 306"),
    "TOP": (_SIGMET_FAMILY + _ADVISORY_VA[:1], ("INTL",), "WMO No. 306"),
    "ABV": (_SIGMET_FAMILY, ("INTL",), "WMO No. 306"),
    "BLW": (_SIGMET_FAMILY, ("INTL",), "WMO No. 306"),
    "FL": (_SIGMET_FAMILY + _ADVISORY_VA[:1] + _ADVISORY_TC[:1], ("INTL",), "WMO No. 306"),
    "FIR": (_SIGMET_FAMILY + _ADVISORY_VA[:1] + _ADVISORY_TC[:1], ("INTL",), "WMO No. 306"),
    "UIR": (_SIGMET_FAMILY, ("INTL",), "WMO No. 306"),
    "CNL": (_SIGMET_FAMILY + _ADVISORY_VA[:1] + _ADVISORY_TC[:1], ("INTL",), "WMO No. 306"),
    "ADVISORY": (_ADVISORY_VA[:1] + _ADVISORY_TC[:1] + _ADVISORY_SW, ("INTL",), "WMO No. 306"),
    "VAA": (_ADVISORY_VA[:1], ("INTL",), "Amd 77"),
    "TCA": (_ADVISORY_TC[:1], ("INTL",), "Amd 77"),
    "DTG": (_ADVISORY_VA[:1] + _ADVISORY_TC[:1] + _ADVISORY_SW, ("INTL",), "WMO No. 306"),
    "VOLCANO": (_ADVISORY_VA[:1] + _ADVISORY_VONA, ("INTL",), "Amd 77"),
    "PSN": (_ADVISORY_VA[:1] + _ADVISORY_TC[:1] + _ADVISORY_VONA, ("INTL",), "WMO No. 306"),
    "AREA": (_ADVISORY_VA[:1] + _ADVISORY_TC[:1] + _SIGMET_FAMILY, ("INTL",), "WMO No. 306"),
    "SUMMIT": (_ADVISORY_VA[:1] + _ADVISORY_VONA, ("INTL",), "Amd 77"),
    "VAAC": (_ADVISORY_VA[:1], ("INTL",), "Amd 77"),
    "TCAC": (_ADVISORY_TC[:1], ("INTL",), "Amd 77"),
}


def _string_list(raw: object) -> list[str]:
    """
    Normalize a YAML list or comma-separated string into unique uppercase labels.

    Parameters
    ----------
    raw : object
        YAML value.

    Returns
    -------
    list[str]
        Stable unique non-empty strings.
    """
    values: list[str] = []
    if isinstance(raw, str):
        parts = [part.strip() for part in raw.split(",")]
        values.extend(part for part in parts if part)
    elif isinstance(raw, list):
        values.extend(item.strip() for item in raw if isinstance(item, str) and item.strip())
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            out.append(value)
    return out


def _tokens_dictionary_from_mapping(raw: object) -> dict[str, dict[str, Any]]:
    """
    Parse dictionary tag fields from ``catalog_meta.yaml``.

    Parameters
    ----------
    raw : object
        Loaded YAML document.

    Returns
    -------
    dict[str, dict[str, Any]]
        Uppercase token → products / countries / wmo_amendment overrides.
    """
    if not isinstance(raw, dict):
        return {}
    mapping = cast(Mapping[Any, Any], raw)
    tokens_raw = mapping.get("tokens", {})
    if not isinstance(tokens_raw, dict):
        return {}
    token_map = cast(Mapping[Any, Any], tokens_raw)
    out: dict[str, dict[str, Any]] = {}
    for key, value in token_map.items():
        if not isinstance(key, str) or not key.strip():
            continue
        if not isinstance(value, dict):
            continue
        value_map = cast(Mapping[Any, Any], value)
        fields: dict[str, Any] = {}
        if "products" in value_map:
            fields["products"] = [p.upper() for p in _string_list(value_map.get("products"))]
        if "countries" in value_map:
            fields["countries"] = [c.upper() for c in _string_list(value_map.get("countries"))]
        amendment = value_map.get("wmo_amendment")
        if isinstance(amendment, str) and amendment.strip():
            fields["wmo_amendment"] = amendment.strip()
        elif amendment is None and "wmo_amendment" in value_map:
            fields["wmo_amendment"] = None
        if fields:
            out[key.strip().upper()] = fields
    return out


def _load_raw_catalog_meta_doc() -> object:
    """
    Load the packaged catalog meta YAML document.

    Returns
    -------
    object
        Parsed YAML or empty mapping.
    """
    try:
        root = resources.files("tac_decoding")
        data = root.joinpath("data", "catalog_meta.yaml")
        if not data.is_file():
            fallback = Path(__file__).resolve().parent / "data" / "catalog_meta.yaml"
            text = fallback.read_text(encoding="utf-8")
        else:
            text = data.read_text(encoding="utf-8")
    except (OSError, TypeError, ValueError):
        fallback = Path(__file__).resolve().parent / "data" / "catalog_meta.yaml"
        if not fallback.is_file():
            return {}
        text = fallback.read_text(encoding="utf-8")
    try:
        loaded = yaml.safe_load(text)
    except yaml.YAMLError:
        return {}
    return loaded if loaded is not None else {}


@lru_cache(maxsize=1)
def load_dictionary_meta() -> dict[str, dict[str, Any]]:
    """
    Load dictionary tag overrides from ``catalog_meta.yaml``.

    Returns
    -------
    dict[str, dict[str, Any]]
        Token → override fields.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (load_dictionary_meta)
    2
    """
    return _tokens_dictionary_from_mapping(_load_raw_catalog_meta_doc())


def reload_dictionary_meta() -> dict[str, dict[str, Any]]:
    """
    Clear dictionary meta cache and reload (tests).

    Returns
    -------
    dict[str, dict[str, Any]]
        Fresh overrides.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (reload_dictionary_meta)
    2
    """
    load_dictionary_meta.cache_clear()
    dictionary_entries.cache_clear()
    return load_dictionary_meta()


def _resolved_tags(token: str, override: Mapping[str, Any] | None) -> tuple[list[str], list[str], str | None]:
    """
    Resolve products, countries, and amendment for one token.

    Parameters
    ----------
    token : str
        Uppercase TAC token.
    override : Mapping[str, Any] | None
        YAML overrides.

    Returns
    -------
    tuple[list[str], list[str], str | None]
        products, countries, wmo_amendment.
    """
    products: list[str] = []
    countries: list[str] = []
    amendment: str | None = None
    defaults = _DEFAULT_TAGS.get(token)
    if defaults is not None:
        products = list(defaults[0])
        countries = list(defaults[1])
        amendment = defaults[2]
    if override:
        if "products" in override:
            products = list(cast(list[str], override["products"]))
        if "countries" in override:
            countries = list(cast(list[str], override["countries"]))
        if "wmo_amendment" in override:
            raw_amd = override["wmo_amendment"]
            amendment = str(raw_amd) if isinstance(raw_amd, str) else None
    return products, countries, amendment


@lru_cache(maxsize=1)
def dictionary_entries() -> tuple[dict[str, Any], ...]:
    """
    Export glossary tokens as code-name dictionary rows.

    Returns
    -------
    tuple[dict[str, Any], ...]
        Immutable sequence of rows with ``id``, ``code``, ``meaning``,
        ``products``, ``countries``, ``wmo_amendment``.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (dictionary_entries)
    2
    """
    glossary = load_glossary()
    meta = load_dictionary_meta()
    items: list[dict[str, Any]] = []
    for token in sorted(glossary):
        products, countries, amendment = _resolved_tags(token, meta.get(token))
        items.append(
            {
                "id": token,
                "code": token,
                "meaning": glossary[token],
                "products": products,
                "countries": countries,
                "wmo_amendment": amendment,
            }
        )
    return tuple(items)


def dictionary_facets(rows: list[dict[str, Any]] | None = None) -> dict[str, list[str]]:
    """
    Collect sorted facet values for dictionary filters.

    Parameters
    ----------
    rows : list[dict[str, Any]] | None, optional
        Rows to scan; defaults to full dictionary.

    Returns
    -------
    dict[str, list[str]]
        ``products``, ``countries``, ``wmo_amendments`` sorted lists.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (dictionary_facets)
    2
    """
    source = rows if rows is not None else list(dictionary_entries())
    products: set[str] = set()
    countries: set[str] = set()
    amendments: set[str] = set()
    for row in source:
        products.update(str(p) for p in cast(list[Any], row.get("products") or []))
        countries.update(str(c) for c in cast(list[Any], row.get("countries") or []))
        amd = row.get("wmo_amendment")
        if isinstance(amd, str) and amd.strip():
            amendments.add(amd.strip())
    return {
        "products": sorted(products),
        "countries": sorted(countries),
        "wmo_amendments": sorted(amendments),
    }


def filter_dictionary_entries(
    *,
    q: str | None = None,
    product: str | None = None,
    country: str | None = None,
    wmo_amendment: str | None = None,
) -> list[dict[str, Any]]:
    """
    Filter dictionary rows by search text and tag selectors.

    Parameters
    ----------
    q : str | None, optional
        Case-insensitive substring match on code or meaning.
    product : str | None, optional
        Product tag (case-insensitive).
    country : str | None, optional
        Country tag (case-insensitive).
    wmo_amendment : str | None, optional
        Exact amendment label match (case-insensitive).

    Returns
    -------
    list[dict[str, Any]]
        Matching rows (copies).

    Examples
    --------
    >>> 1 + 1  # docstring smoke (filter_dictionary_entries)
    2
    """
    query = (q or "").strip().lower()
    product_key = (product or "").strip().upper()
    country_key = (country or "").strip().upper()
    amendment_key = (wmo_amendment or "").strip().lower()
    out: list[dict[str, Any]] = []
    for row in dictionary_entries():
        products = [str(p).upper() for p in cast(list[Any], row.get("products") or [])]
        countries = [str(c).upper() for c in cast(list[Any], row.get("countries") or [])]
        amd = row.get("wmo_amendment")
        amd_text = amd.strip().lower() if isinstance(amd, str) else ""
        if product_key and product_key not in products:
            continue
        if country_key and country_key not in countries:
            continue
        if amendment_key and amd_text != amendment_key:
            continue
        if query:
            code = str(row.get("code") or "").lower()
            meaning = str(row.get("meaning") or "").lower()
            if query not in code and query not in meaning:
                continue
        out.append(dict(row))
    return out
