"""Rule catalogs + selection-options + code-name dictionary routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel, Field

from src.msgspec_http import msgspec_json_response
from src.services.rule_catalogs import catalog_for_family, known_families, selection_options

router = APIRouter(prefix="/api/v1", tags=["Catalogs"])


class RuleCatalogItem(BaseModel):
    """
    One package-owned trust-catalog row.

    Optional additive metadata: ``issue_type``, ``source_*``, ``conform_note``.
    Null or omitted when unknown; clients must not invent defaults.


    Attributes
    ----------
    _ : object
        See implementation.
    """

    id: str
    title: str
    summary: str = ""
    severity: str | None = None
    tags: list[str] = Field(default_factory=list)
    issue_type: str | None = None
    source_url: str | None = None
    source_attribution: str | None = None
    source_access: str | None = None
    source_locator: str | None = None
    conform_note: str | None = None


class RuleCatalogResponse(BaseModel):
    """
    Response for GET /rule-catalogs.


    Attributes
    ----------
    _ : object
        See implementation.
    """

    family: str
    items: list[RuleCatalogItem]


class SelectionOption(BaseModel):
    """
    Dropdown option from a deployed registry.


    Attributes
    ----------
    _ : object
        See implementation.
    """

    id: str
    label: str


class SelectionOptionsResponse(BaseModel):
    """
    Response for GET /selection-options.


    Attributes
    ----------
    _ : object
        See implementation.
    """

    kind: str
    options: list[SelectionOption]


@router.get("/rule-catalogs", response_model=RuleCatalogResponse)
async def get_rule_catalogs(
    family: str = Query(..., description="tac | iwxxm | conversion | dissemination | decoding"),
    product: str | None = Query(None),
) -> Response:
    """
    Export a package-owned trust catalog by family.


    Examples
    --------
    >>> 1 + 1  # docstring smoke (get_rule_catalogs)
    2

    Parameters
    ----------
    family : object
        Argument ``family``.
    product : object
        Argument ``product``.

    Returns
    -------
    object
        Return value.
    """
    key = family.strip().lower()
    if key not in known_families():
        raise HTTPException(
            status_code=400,
            detail={"code": "invalid_catalog_family", "message": f"Unknown family {family!r}"},
        )
    try:
        raw = catalog_for_family(key, product=product)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "invalid_catalog_family", "message": str(exc)},
        ) from exc
    items = [RuleCatalogItem.model_validate(row) for row in raw]
    return msgspec_json_response(RuleCatalogResponse(family=key, items=items))


@router.get("/selection-options", response_model=SelectionOptionsResponse)
async def get_selection_options(
    kind: str = Query(
        ...,
        description=(
            "conversion | tac_validation | iwxxm_validation | decoding | dissemination (first-party LIB.* ids)"
        ),
    ),
) -> Response:
    """
    List deployed registry ids for workbench / dissemination dropdowns.


    Examples
    --------
    >>> 1 + 1  # docstring smoke (get_selection_options)
    2

    Parameters
    ----------
    kind : object
        Argument ``kind``.

    Returns
    -------
    object
        Return value.
    """
    try:
        raw = selection_options(kind)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "invalid_selection_kind", "message": str(exc)},
        ) from exc
    options = [SelectionOption.model_validate(row) for row in raw]
    return msgspec_json_response(SelectionOptionsResponse(kind=kind.strip().lower(), options=options))


class CodeNameDictionaryItem(BaseModel):
    """
    One code-name dictionary row (Decoding glossary deepen).

    Attributes
    ----------
    id : str
        Stable row id (uppercase TAC code).
    code : str
        TAC code name.
    meaning : str
        Plain-language meaning.
    products : list[str]
        Product tags.
    countries : list[str]
        Country tags (``INTL`` for international).
    wmo_amendment : str | None
        WMO amendment or edition label when known.
    """

    id: str
    code: str
    meaning: str = ""
    products: list[str] = Field(default_factory=list)
    countries: list[str] = Field(default_factory=list)
    wmo_amendment: str | None = None


class CodeNameDictionaryFacets(BaseModel):
    """
    Facet values for dictionary filters.

    Attributes
    ----------
    products : list[str]
        Known product tags.
    countries : list[str]
        Known country tags.
    wmo_amendments : list[str]
        Known amendment labels.
    """

    products: list[str] = Field(default_factory=list)
    countries: list[str] = Field(default_factory=list)
    wmo_amendments: list[str] = Field(default_factory=list)


class CodeNameDictionaryResponse(BaseModel):
    """
    Response for GET /code-name-dictionary.

    Attributes
    ----------
    items : list[CodeNameDictionaryItem]
        Filtered rows.
    facets : CodeNameDictionaryFacets
        Facets from the full dictionary (not the filtered subset).
    """

    items: list[CodeNameDictionaryItem]
    facets: CodeNameDictionaryFacets


@router.get("/code-name-dictionary", response_model=CodeNameDictionaryResponse)
async def get_code_name_dictionary(
    q: str | None = Query(None, description="Search code or meaning"),
    product: str | None = Query(None, description="Filter by product tag"),
    country: str | None = Query(None, description="Filter by country tag"),
    wmo_amendment: str | None = Query(None, description="Filter by WMO amendment label"),
) -> Response:
    """
    Export the Decoding glossary as a tagged code-name dictionary.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (get_code_name_dictionary)
    2

    Parameters
    ----------
    q : object
        Argument ``q``.
    product : object
        Argument ``product``.
    country : object
        Argument ``country``.
    wmo_amendment : object
        Argument ``wmo_amendment``.

    Returns
    -------
    object
        Filtered items plus facets.
    """
    from tac_decoding import dictionary_facets, filter_dictionary_entries

    try:
        rows: list[dict[str, Any]] = filter_dictionary_entries(
            q=q,
            product=product,
            country=country,
            wmo_amendment=wmo_amendment,
        )
        facets_raw = dictionary_facets()
    except (OSError, TypeError, ValueError, RuntimeError) as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "code_name_dictionary_unavailable",
                "message": "Code name dictionary is temporarily unavailable",
            },
        ) from exc
    items = [CodeNameDictionaryItem.model_validate(row) for row in rows]
    facets = CodeNameDictionaryFacets.model_validate(facets_raw)
    return msgspec_json_response(CodeNameDictionaryResponse(items=items, facets=facets))
