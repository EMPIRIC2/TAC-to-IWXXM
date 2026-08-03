"""JWKS-only Supabase Auth JWT verification (ADR-033 / D-S038-04-b1)."""

from __future__ import annotations

import os
import time
from typing import Any

import httpx
import jwt
from jwt import PyJWKSet
from jwt.exceptions import InvalidTokenError


class JwtVerificationError(Exception):
    """Raised when a bearer token fails JWKS verification."""


_JWKS_CACHE: dict[str, tuple[float, dict[str, Any]]] = {}
_JWKS_TTL_SEC = 600.0


def jwks_url_from_supabase_url(supabase_url: str) -> str:
    """
    Build the default Supabase Auth JWKS URL.

    Parameters
    ----------
    supabase_url : str
        Project Auth URL (``SUPABASE_URL``), with or without trailing slash.

    Returns
    -------
    str
        ``{url}/auth/v1/.well-known/jwks.json``
    """
    base = supabase_url.rstrip("/")
    return f"{base}/auth/v1/.well-known/jwks.json"


def resolve_jwks_url(
    *,
    jwks_url: str | None = None,
    supabase_url: str | None = None,
) -> str:
    """
    Resolve JWKS URL from explicit arg, ``SUPABASE_JWKS_URL``, or ``SUPABASE_URL``.

    Parameters
    ----------
    jwks_url : str or None
        Explicit JWKS endpoint.
    supabase_url : str or None
        Auth project URL used to derive the default JWKS path.

    Returns
    -------
    str
        Absolute JWKS URL.

    Raises
    ------
    JwtVerificationError
        If no URL can be resolved.
    """
    explicit = (jwks_url or os.getenv("SUPABASE_JWKS_URL") or "").strip()
    if explicit:
        return explicit
    project = (supabase_url or os.getenv("SUPABASE_URL") or "").strip()
    if project:
        return jwks_url_from_supabase_url(project)
    raise JwtVerificationError(
        "JWKS URL not configured (set SUPABASE_JWKS_URL or SUPABASE_URL)"
    )


def clear_jwks_client_cache() -> None:
    """Clear cached JWKS documents (tests / key rotation)."""
    _JWKS_CACHE.clear()


def _fetch_jwks_document(jwks_url: str) -> dict[str, Any]:
    now = time.monotonic()
    cached = _JWKS_CACHE.get(jwks_url)
    if cached is not None and (now - cached[0]) < _JWKS_TTL_SEC:
        return cached[1]
    try:
        response = httpx.get(jwks_url, timeout=10.0)
        response.raise_for_status()
        document = response.json()
    except Exception as exc:
        raise JwtVerificationError(f"JWKS fetch failed: {exc}") from exc
    if not isinstance(document, dict) or "keys" not in document:
        raise JwtVerificationError("JWKS document missing keys")
    _JWKS_CACHE[jwks_url] = (now, document)
    return document


def verify_access_token(
    token: str,
    *,
    jwks_url: str | None = None,
    supabase_url: str | None = None,
    audience: str | None = None,
    issuer: str | None = None,
) -> dict[str, Any]:
    """
    Verify a Supabase Auth access token using JWKS only (no HS256 secret).

    Parameters
    ----------
    token : str
        Bearer JWT.
    jwks_url : str or None
        JWKS endpoint override.
    supabase_url : str or None
        Used to derive JWKS URL when ``jwks_url`` unset.
    audience : str or None
        Optional ``aud`` claim to enforce.
    issuer : str or None
        Optional ``iss`` claim to enforce.

    Returns
    -------
    dict[str, Any]
        Decoded JWT claims.

    Raises
    ------
    JwtVerificationError
        If the token is missing, expired, malformed, or signature-invalid.
    """
    if not token or not token.strip():
        raise JwtVerificationError("Missing access token")

    url = resolve_jwks_url(jwks_url=jwks_url, supabase_url=supabase_url)
    try:
        document = _fetch_jwks_document(url)
        jwk_set = PyJWKSet.from_dict(document)
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        if not kid:
            raise JwtVerificationError("JWT missing kid header")
        signing_key = jwk_set[kid]
        decode_kwargs: dict[str, Any] = {
            "algorithms": ["RS256", "ES256"],
            "options": {"require": ["exp", "sub"]},
        }
        if audience is not None:
            decode_kwargs["audience"] = audience
        else:
            decode_kwargs["options"]["verify_aud"] = False
        if issuer is not None:
            decode_kwargs["issuer"] = issuer
        payload = jwt.decode(token, signing_key.key, **decode_kwargs)
    except JwtVerificationError:
        raise
    except InvalidTokenError as exc:
        raise JwtVerificationError(str(exc)) from exc
    except Exception as exc:
        raise JwtVerificationError(str(exc)) from exc

    return dict(payload)
