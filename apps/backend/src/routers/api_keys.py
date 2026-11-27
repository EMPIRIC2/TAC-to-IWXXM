"""Public API key issue / revoke routes (NFR-007)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, cast
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, Request, status
from pydantic import BaseModel, Field
from slowapi import Limiter

try:
    from ..services.api_key_store import (
        issue_api_key,
        issued_to_dict,
        revoke_api_key,
    )
    from ..utilities.abuse_controls import (
        get_limiter,
        get_rate_limit_api_key_issue_per_min,
    )
except ImportError:  # pragma: no cover - script load
    from services.api_key_store import (  # type: ignore[no-redef]
        issue_api_key,
        issued_to_dict,
        revoke_api_key,
    )
    from utilities.abuse_controls import (  # type: ignore[no-redef]
        get_limiter,
        get_rate_limit_api_key_issue_per_min,
    )

router = APIRouter(prefix="/api/v1", tags=["API Keys"])
_limiter = get_limiter()


class IssueApiKeyRequest(BaseModel):
    """Optional label for a newly issued key."""

    label: str = Field(default="", max_length=128)


def _issue_limit_string() -> str:
    """Slowapi limit string for public key issue."""
    return f"{get_rate_limit_api_key_issue_per_min()}/minute"


def _typed_limit(limiter: Limiter, limit_value: str | Callable[[], str]) -> Callable[..., Any]:
    """Wrap slowapi ``limit`` with a typed decorator (basedpyright)."""
    limiter_any = cast(Any, limiter)
    return cast(Callable[..., Any], limiter_any.limit(limit_value))


@router.post("/api-keys", status_code=status.HTTP_201_CREATED)
@_typed_limit(_limiter, _issue_limit_string)
async def create_api_key(
    request: Request,
    body: IssueApiKeyRequest | None = None,
) -> dict[str, Any]:
    """
    Issue an API key to anyone (hash stored; plaintext returned once).

    Parameters
    ----------
    request : Request
        Incoming request (slowapi).
    body : IssueApiKeyRequest or None, optional
        Optional label.

    Returns
    -------
    dict
        Issue payload.
    """
    label = (body.label if body is not None else "") or ""
    try:
        issued = issue_api_key(label=label)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    return issued_to_dict(issued)


@router.delete("/api-keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
@_typed_limit(_limiter, "30/minute")
async def delete_api_key(
    request: Request,
    key_id: UUID,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> None:
    """
    Soft-revoke a key when the caller presents that key.

    Parameters
    ----------
    request : Request
        Incoming request (slowapi).
    key_id : UUID
        Key id.
    x_api_key : str or None
        Caller key.
    """
    if not x_api_key or not x_api_key.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
        )
    ok = revoke_api_key(key_id=key_id, plaintext=x_api_key)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )


# Tests may rebind the process limiter.
limiter = _limiter
