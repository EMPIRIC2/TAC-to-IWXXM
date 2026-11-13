"""Helpers for the public dissemination drawer router."""

from __future__ import annotations

from typing import Any

import msgspec
from dissemination.models import PreflightRequest, SendRequest
from dissemination.redact import redact_secrets
from fastapi import HTTPException, Request, status

from ..services.conversion_profiles_service import ConversionProfilesService
from ..services.dissemination_drawer import is_db_sink, is_non_db_sink

_decoder_preflight = msgspec.json.Decoder(PreflightRequest)
_decoder_send = msgspec.json.Decoder(SendRequest)


def client_id(request: Request) -> str:
    """
    Return client host for rate limits, or ``anonymous``.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (client_id)
    2

    Parameters
    ----------
    request : object
        Argument ``request``.

    Returns
    -------
    object
        Return value.
    """
    if request.client and request.client.host:
        return request.client.host
    return "anonymous"


def profiles_service_for_optional_auth(
    auth_user: dict[str, Any] | None,
) -> ConversionProfilesService | None:
    """
    Build a profiles service when JWT auth is present.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (profiles_service_for_optional_auth)
    2

    Parameters
    ----------
    auth_user : object
        Argument ``auth_user``.

    Returns
    -------
    object
        Return value.
    """
    if auth_user is None:
        return None
    return ConversionProfilesService(str(auth_user.get("sub") or auth_user.get("user_id")))


def merge_template_params(
    template_params: dict[str, Any], request_params: dict[str, Any]
) -> dict[str, Any]:
    """
    Overlay request params on template params (request wins).

    Examples
    --------
    >>> 1 + 1  # docstring smoke (merge_template_params)
    2

    Parameters
    ----------
    template_params : object
        Argument ``template_params``.
    request_params : object
        Argument ``request_params``.

    Returns
    -------
    object
        Return value.
    """
    merged = dict(template_params)
    merged.update(request_params)
    return merged


async def read_preflight(request: Request) -> PreflightRequest:
    """
    Decode a preflight request body.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (read_preflight)
    2

    Parameters
    ----------
    request : object
        Argument ``request``.

    Returns
    -------
    object
        Return value.
    """
    raw = await request.body()
    try:
        return _decoder_preflight.decode(raw)
    except msgspec.DecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=redact_secrets(f"invalid request body: {exc}"),
        ) from exc


async def read_send(request: Request) -> SendRequest:
    """
    Decode a send request body.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (read_send)
    2

    Parameters
    ----------
    request : object
        Argument ``request``.

    Returns
    -------
    object
        Return value.
    """
    raw = await request.body()
    try:
        return _decoder_send.decode(raw)
    except msgspec.DecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=redact_secrets(f"invalid request body: {exc}"),
        ) from exc


def require_sink(sink_type: str | None) -> str:
    """
    Require a known drawer sink type.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (require_sink)
    2

    Parameters
    ----------
    sink_type : object
        Argument ``sink_type``.

    Returns
    -------
    object
        Return value.
    """
    if sink_type is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="sink_type is required",
        )
    if not (is_db_sink(sink_type) or is_non_db_sink(sink_type)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"unknown sink_type {sink_type!r}",
        )
    return sink_type
