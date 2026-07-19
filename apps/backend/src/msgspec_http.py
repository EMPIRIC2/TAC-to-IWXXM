"""msgspec JSON response helper for high-churn HTTP routes (ADR-026 / E10-38).

Prefer encoding ``msgspec.Struct`` values. ``pydantic.BaseModel`` OpenAPI alias
instances are accepted via ``model_dump(mode="json")`` then a single msgspec
encode — **no** dual runtime validation.
"""

from __future__ import annotations

from typing import Any

import msgspec
from fastapi.responses import Response
from pydantic import BaseModel

json_encoder = msgspec.json.Encoder()

__all__ = ["json_encoder", "msgspec_json_response"]


def msgspec_json_response(
    obj: Any,
    *,
    status_code: int = 200,
    media_type: str = "application/json",
) -> Response:
    """
    Encode ``obj`` with the module-level msgspec Encoder into a JSON Response.

    Parameters
    ----------
    obj : Any
        Prefer a ``msgspec.Struct``. ``BaseModel`` instances are dumped to a
        JSON-friendly mapping before encode. Plain mappings/lists are encoded
        directly.
    status_code : int, optional
        HTTP status code (default ``200``).
    media_type : str, optional
        Response media type (default ``application/json``).

    Returns
    -------
    Response
        Starlette/FastAPI response whose body is msgspec-encoded JSON bytes.
    """
    if isinstance(obj, BaseModel):
        payload: Any = obj.model_dump(mode="json")
    else:
        payload = obj
    body = json_encoder.encode(payload)
    return Response(content=body, status_code=status_code, media_type=media_type)
