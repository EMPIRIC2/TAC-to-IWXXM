"""Server HMAC-SHA256 for ConversionProfile overlays (EV-933 / F7.w)."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status


def overlay_hmac_secret() -> str:
    """
    Resolve the server overlay signing secret.

    Returns
    -------
    str
        Non-empty secret from ``PROFILE_OVERLAY_HMAC_SECRET``.

    Raises
    ------
    HTTPException
        503 when the secret is unset (overlays unavailable).
    """
    secret = (os.environ.get("PROFILE_OVERLAY_HMAC_SECRET") or "").strip()
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Profile overlays unavailable - missing signing secret",
        )
    return secret


def canonical_overlay_body(body: dict[str, Any]) -> str:
    """Return stable JSON for HMAC input (sorted keys, compact separators)."""
    return json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sign_overlay(*, user_id: UUID, base_profile_id: str, body: dict[str, Any]) -> str:
    """
    Compute HMAC-SHA256 hex digest for an overlay payload.

    Parameters
    ----------
    user_id :
        Owner JWT ``sub``.
    base_profile_id :
        Catalog profile id the overlay amends.
    body :
        Operator overlay JSON (no secrets).
    """
    message = f"{user_id}:{base_profile_id}:{canonical_overlay_body(body)}"
    digest = hmac.new(
        overlay_hmac_secret().encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return digest


def verify_overlay_signature(
    *,
    user_id: UUID,
    base_profile_id: str,
    body: dict[str, Any],
    signature: str,
) -> None:
    """
    Fail-closed verify of a stored overlay signature.

    Raises
    ------
    HTTPException
        400 when the signature is missing or does not match.
    """
    if not (signature or "").strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Overlay signature required",
        )
    expected = sign_overlay(user_id=user_id, base_profile_id=base_profile_id, body=body)
    if not hmac.compare_digest(expected, signature.strip()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Overlay signature invalid",
        )
