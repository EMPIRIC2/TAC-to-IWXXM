"""Part 1 of ``api_wire.py`` (line-cap split)."""

from __future__ import annotations

import logging
import os
import re
from collections.abc import Callable
from typing import Any, TypeGuard, cast

from fastapi import HTTPException, Request, UploadFile

try:
    from .schemas.conversion import ConversionIssue, ConversionIssueSeverity, ErrorDetail
    from .utilities.extension_wire import (
        parse_extension_tokens,
        validate_extension_tokens,
    )
except ImportError:  # pragma: no cover - Docker/local import path mirror
    from schemas.conversion import ConversionIssue, ConversionIssueSeverity, ErrorDetail
    from utilities.extension_wire import (
        parse_extension_tokens,
        validate_extension_tokens,
    )

from iwxxm_validate.models import ValidationReport

logger = logging.getLogger(__name__)


def _iwxxm_validate_fn() -> Callable[..., ValidationReport]:
    """
    Internal helper ``_iwxxm_validate_fn``.

    Returns
    -------
    object
        Return value.
    """
    try:
        from . import api as api_mod
    except ImportError:  # pragma: no cover - Docker/local import path mirror
        import api as api_mod

    return cast(Callable[..., ValidationReport], api_mod.iwxxm_validate_fn)


def is_dev_cors_relaxation_enabled() -> bool:
    """
    Enable relaxed CORS behavior for local debugging when explicitly requested.


    Returns
    -------
    object
        Return value.
    """
    return os.getenv("ENABLE_DEV_CORS_RELAXATION", "").lower() in (
        "true",
        "1",
        "yes",
        "on",
    )


def add_origin_if_missing(origins: list[str], origin: str) -> list[str]:
    """
    Append origin if not present.


    Parameters
    ----------
    origins : object
        Argument ``origins``.
    origin : object
        Argument ``origin``.

    Returns
    -------
    object
        Return value.
    """
    if origin and origin not in origins:
        origins.append(origin)
    return origins


def add_loopback_origin_variants(origins: list[Any]) -> list[Any]:
    """
    Ensure localhost and 127.0.0.1 variants are both allowed for local dev.


    Parameters
    ----------
    origins : object
        Argument ``origins``.

    Returns
    -------
    object
        Return value.
    """
    expanded_origins = list(origins)
    for origin in origins:
        if "localhost" in origin:
            loopback_variant = origin.replace("localhost", "127.0.0.1")
            add_origin_if_missing(expanded_origins, loopback_variant)
        if "127.0.0.1" in origin:
            localhost_variant = origin.replace("127.0.0.1", "localhost")
            add_origin_if_missing(expanded_origins, localhost_variant)
    return expanded_origins


def get_cors_origins() -> list[Any]:
    """
    Get allowed CORS origins from config with deprecated env fallbacks.


    Returns
    -------
    object
        Return value.
    """
    import warnings

    from metar_shared import METAR_CORS_ORIGINS_ENV, parse_comma_separated_origins
    from metar_shared.config_loader import get_cors_origins_from_config, get_frontend_url_from_config

    relaxed_cors = is_dev_cors_relaxation_enabled()
    origins = get_cors_origins_from_config()

    allowed_origins_env = os.getenv(METAR_CORS_ORIGINS_ENV, "").strip()
    if allowed_origins_env:
        env_origins = list(parse_comma_separated_origins(allowed_origins_env))
        if origins:
            warnings.warn(
                f"{METAR_CORS_ORIGINS_ENV} supplements config.*.api.corsOrigins (deprecated env)",
                DeprecationWarning,
                stacklevel=2,
            )
            for origin in env_origins:
                add_origin_if_missing(origins, origin)
        else:
            warnings.warn(
                f"{METAR_CORS_ORIGINS_ENV} is deprecated; use config.*.api.corsOrigins",
                DeprecationWarning,
                stacklevel=2,
            )
            origins = env_origins

    if not origins:
        frontend_url = os.getenv("FRONTEND_URL", "").strip() or get_frontend_url_from_config()
        if not frontend_url:
            frontend_url = "http://localhost:18000"
        origins = [frontend_url, "http://localhost:3000"]

    if relaxed_cors:
        add_origin_if_missing(origins, "http://localhost:5173")
        add_origin_if_missing(origins, "http://localhost:18000")
    return add_loopback_origin_variants(origins)


def get_cors_allowed_headers() -> list[Any]:
    """
    Get allowed CORS request headers.


    Returns
    -------
    object
        Return value.
    """
    if is_dev_cors_relaxation_enabled():
        return ["*"]
    return ["Authorization", "Content-Type"]


def _is_named_upload(value: object) -> TypeGuard[UploadFile]:
    """
    Internal helper ``_is_named_upload``.

    Parameters
    ----------
    value : object
        Argument ``value``.

    Returns
    -------
    object
        Return value.
    """
    if isinstance(value, str) or not value:
        return False
    return bool(getattr(value, "filename", None))


async def parse_files(request: Request) -> list[UploadFile]:
    """
    Parse files parameter from request, handling edge cases:
    - Swagger UI 'Send empty value' sends empty string which FastAPI can't parse
    - This manually extracts files from the form, filtering out empty strings


    Parameters
    ----------
    request : object
        Argument ``request``.

    Returns
    -------
    object
        Return value.
    """
    try:
        form = await request.form()
        files: list[UploadFile] = []
        for key, value in form.multi_items():
            if key == "files" and _is_named_upload(value):
                files.append(value)
        return files
    except Exception as e:
        logger.warning(f"Error parsing files from request: {e}")
        raise HTTPException(
            status_code=400,
            detail=ErrorDetail(
                message="Invalid file upload payload",
                errors=[str(e)],
                issues=[
                    ConversionIssue(
                        source="request",
                        message="Unable to parse multipart file upload payload.",
                        severity=ConversionIssueSeverity.ERROR,
                        hint="Ensure the request uses multipart/form-data and each file field is named 'files'.",
                        code="INVALID_MULTIPART_PAYLOAD",
                    )
                ],
                total_errors=1,
            ).model_dump(),
        ) from e


_MULTILINE_TEMPLATE_PRODUCTS = frozenset({"SIGMET", "AIRMET", "VAA", "TCA", "SWXA", "VONA", "IWXXM"})

_API_PRODUCTS = frozenset({"AIRMET", "METAR", "SIGMET", "SPECI", "TAF", "VAA", "TCA", "SWXA", "VONA", "IWXXM"})


def normalize_api_product(
    product: str | None,
    *,
    default: str | None = "METAR",
) -> str:
    """
    Normalize multipart/JSON ``product`` to uppercase enum or raise ``unknown_product`` 400.


    Parameters
    ----------
    product : object
        Argument ``product``.
    default : object
        Argument ``default``.

    Returns
    -------
    object
        Return value.
    """
    raw = (product or "").strip()
    if not raw:
        if default is None:
            raise HTTPException(
                status_code=400,
                detail={"code": "unknown_product", "message": "product is required"},
            )
        raw = default
    product_u = raw.upper()
    if product_u not in _API_PRODUCTS:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "unknown_product",
                "message": (
                    f"Unknown product {raw!r}; expected one of "
                    f"{', '.join(sorted(p.lower() for p in _API_PRODUCTS))} "
                    "(canonical SWXA wire value is swxa, not swx; "
                    "canonical VONA wire value is vona; "
                    "canonical IWXXM wire value is iwxxm)"
                ),
            },
        )
    return product_u


def _coerce_form_list(value: object) -> list[str]:
    """
    Internal helper ``_coerce_form_list``.

    Parameters
    ----------
    value : object
        Argument ``value``.

    Returns
    -------
    object
        Return value.
    """
    if isinstance(value, list):
        return [item for item in cast(list[object], value) if isinstance(item, str)]
    return []


def _coerce_form_str(value: object, default: str = "") -> str:
    """
    Internal helper ``_coerce_form_str``.

    Parameters
    ----------
    value : object
        Argument ``value``.
    default : object
        Argument ``default``.

    Returns
    -------
    object
        Return value.
    """
    return value if isinstance(value, str) else default


def _resolve_request_extensions(
    form_extensions: list[str],
    json_extensions: list[str] | None,
) -> list[str]:
    """
    Internal helper ``_resolve_request_extensions``.

    Parameters
    ----------
    form_extensions : object
        Argument ``form_extensions``.
    json_extensions : object
        Argument ``json_extensions``.

    Returns
    -------
    object
        Return value.
    """
    if json_extensions is not None:
        tokens = parse_extension_tokens(json_extensions)
    else:
        tokens = parse_extension_tokens(form_extensions)
    validate_extension_tokens(tokens)
    return tokens


def _package_issue_payload(issue: object) -> dict[str, Any]:
    """
    Internal helper ``_package_issue_payload``.

    Parameters
    ----------
    issue : object
        Argument ``issue``.

    Returns
    -------
    object
        Return value.
    """
    return {
        "layer": str(getattr(issue, "layer", "")),
        "severity": str(getattr(issue, "severity", "error")),
        "message": str(getattr(issue, "message", "")),
        "location": getattr(issue, "location", None),
        "code": getattr(issue, "code", None),
        "start": getattr(issue, "start", None),
        "end": getattr(issue, "end", None),
    }


def _package_stages_payload(report: object) -> list[dict[str, Any]] | None:
    """
    Internal helper ``_package_stages_payload``.

    Parameters
    ----------
    report : object
        Argument ``report``.

    Returns
    -------
    object
        Return value.
    """
    stages_obj = getattr(report, "stages", None)
    if not isinstance(stages_obj, list):
        return None
    stages: list[object] = cast(list[object], stages_obj)
    if not stages:
        return None
    out: list[dict[str, Any]] = []
    for stage in stages:
        issues_obj = getattr(stage, "issues", None)
        stage_issues: list[object] = cast(list[object], issues_obj) if isinstance(issues_obj, list) else []
        out.append(
            {
                "stage": str(getattr(stage, "stage", "")),
                "label": str(getattr(stage, "label", "")),
                "ok": bool(getattr(stage, "ok", False)),
                "issues": [_package_issue_payload(issue) for issue in stage_issues],
            }
        )
    return out


def _is_multiline_template_product(product: str | None) -> bool:
    """
    Internal helper ``_is_multiline_template_product``.

    Parameters
    ----------
    product : object
        Argument ``product``.

    Returns
    -------
    object
        Return value.
    """
    return (product or "").strip().upper() in _MULTILINE_TEMPLATE_PRODUCTS


MAX_BULLETIN_REPORTS = 100

_BULLETIN_ID_RE = re.compile(r"^[A-Z]{4}[0-9]{2}$")

_CCCC_RE = re.compile(r"^[A-Z]{4}$")

_AHL_HEADING_SPLIT_CODES = frozenset({"bulletin_split_failed", "invalid_bbb"})

_INVALID_AHL_MESSAGE = (
    "The abbreviated heading is not valid. Use TTAAii CCCC YYGGgg (optional BBB), then one or more TAC reports."
)

_EMPTY_BULLETIN_MESSAGE = "No TAC reports found after the abbreviated heading."
