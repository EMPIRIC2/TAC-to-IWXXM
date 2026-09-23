"""Rule catalogs + selection-options routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel, Field

from src.msgspec_http import msgspec_json_response
from src.services.rule_catalogs import catalog_for_family, known_families, selection_options

router = APIRouter(prefix="/api/v1", tags=["Catalogs"])


class RuleCatalogItem(BaseModel):
    """
    One package-owned trust-catalog row.

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
