"""National IWXXM extension token wire (EV-068 / ADR-036).

Parses optional ``extensions`` on convert/validate routes and maps tokens to
validation behaviour (e.g. ``IWXXM_CA`` enables the full Canadian XSD stack).
"""

from __future__ import annotations

import json
from collections.abc import Sequence

from fastapi import HTTPException

IWXXM_CA_TOKEN = "IWXXM_CA"

_KNOWN_EXTENSION_TOKENS = frozenset({IWXXM_CA_TOKEN})


def _normalize_token(raw: str) -> str:
    return raw.strip().upper().replace("-", "_")


def parse_extension_tokens(values: Sequence[str] | None) -> list[str]:
    """
    Parse multipart ``extensions`` values into normalized canonical tokens.

    Accepts repeated form fields and/or a single JSON array string.
    """
    if not values:
        return []

    tokens: list[str] = []
    for value in values:
        cleaned = (value or "").strip()
        if not cleaned:
            continue
        if cleaned.startswith("[") and cleaned.endswith("]"):
            try:
                parsed = json.loads(cleaned)
            except json.JSONDecodeError as exc:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "code": "invalid_extensions",
                        "message": f"extensions JSON array is invalid: {exc}",
                    },
                ) from exc
            if not isinstance(parsed, list):
                raise HTTPException(
                    status_code=400,
                    detail={
                        "code": "invalid_extensions",
                        "message": "extensions JSON must be an array of strings",
                    },
                )
            for item in parsed:
                if not isinstance(item, str) or not item.strip():
                    raise HTTPException(
                        status_code=400,
                        detail={
                            "code": "invalid_extensions",
                            "message": "extensions JSON array entries must be non-empty strings",
                        },
                    )
                tokens.append(_normalize_token(item))
            continue
        tokens.append(_normalize_token(cleaned))

    # Preserve order while deduplicating.
    seen: set[str] = set()
    ordered: list[str] = []
    for token in tokens:
        if token not in seen:
            seen.add(token)
            ordered.append(token)
    return ordered


def validate_extension_tokens(tokens: Sequence[str]) -> None:
    """Reject unknown extension tokens (fail closed)."""
    unknown = [token for token in tokens if token not in _KNOWN_EXTENSION_TOKENS]
    if unknown:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "invalid_extensions",
                "message": (f"Unknown extension token(s): {unknown}; known tokens: {sorted(_KNOWN_EXTENSION_TOKENS)}"),
            },
        )


def ca_eccc_validate_product(
    emit_key: str,
    extensions: Sequence[str],
    product: str,
) -> str | None:
    """
    Return API product for ``ca_xsd`` when the full Canadian stack is requested.

    ``CA_ECCC`` without ``IWXXM_CA`` keeps the backward-compatible WMO scaffold only.
    """
    if emit_key != "ca_eccc":
        return None
    if IWXXM_CA_TOKEN in extensions:
        return product
    return None


__all__ = [
    "IWXXM_CA_TOKEN",
    "ca_eccc_validate_product",
    "parse_extension_tokens",
    "validate_extension_tokens",
]
