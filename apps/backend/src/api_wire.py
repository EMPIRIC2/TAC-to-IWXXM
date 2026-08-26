"""Shared wire helpers for conversion routes (EV-037 TD-2).

Extracted from ``api.py`` for modularity. Route handlers remain in ``api.py``;
names are re-exported there for ``src.api.*`` monkeypatch compatibility.
"""

from __future__ import annotations

import logging
import os
import re
from typing import Any, Dict, List, Optional, Tuple, TypeGuard

from fastapi import HTTPException, Request, UploadFile

try:
    from .schemas.conversion import ConversionIssue, ConversionIssueSeverity, ErrorDetail
    from .utilities.extension_wire import (
        ca_eccc_validate_product,
        parse_extension_tokens,
        validate_extension_tokens,
    )
    from .utilities.observability import record_profile_wire_metrics
    from .utilities.profile_wire import WireProfileSelection, resolve_route_profiles
except ImportError:
    from schemas.conversion import ConversionIssue, ConversionIssueSeverity, ErrorDetail
    from utilities.extension_wire import (
        ca_eccc_validate_product,
        parse_extension_tokens,
        validate_extension_tokens,
    )
    from utilities.observability import record_profile_wire_metrics
    from utilities.profile_wire import WireProfileSelection, resolve_route_profiles

from iwxxm_validate.models import ValidationReport
from tac2iwxxm import BulletinSplitError

logger = logging.getLogger(__name__)


def _iwxxm_validate_fn():
    """Resolve the patchable SDK alias from ``api`` (TC-F6-033 / F11)."""
    try:
        from . import api as api_mod
    except ImportError:
        import api as api_mod

    return api_mod.iwxxm_validate_fn


def is_dev_cors_relaxation_enabled() -> bool:
    """Enable relaxed CORS behavior for local debugging when explicitly requested."""
    return os.getenv("ENABLE_DEV_CORS_RELAXATION", "").lower() in (
        "true",
        "1",
        "yes",
        "on",
    )


def add_origin_if_missing(origins: list, origin: str) -> list:
    """Append origin if not present."""
    if origin and origin not in origins:
        origins.append(origin)
    return origins


def add_loopback_origin_variants(origins: list) -> list:
    """Ensure localhost and 127.0.0.1 variants are both allowed for local dev."""
    expanded_origins = list(origins)
    for origin in origins:
        if "localhost" in origin:
            loopback_variant = origin.replace("localhost", "127.0.0.1")
            add_origin_if_missing(expanded_origins, loopback_variant)
        if "127.0.0.1" in origin:
            localhost_variant = origin.replace("127.0.0.1", "localhost")
            add_origin_if_missing(expanded_origins, localhost_variant)
    return expanded_origins


def get_cors_origins() -> list:
    """Get allowed CORS origins from config with deprecated env fallbacks."""
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


def get_cors_allowed_headers() -> list:
    """Get allowed CORS request headers."""
    if is_dev_cors_relaxation_enabled():
        return ["*"]
    return ["Authorization", "Content-Type"]


def _is_named_upload(value: object) -> TypeGuard[UploadFile]:
    """Return True for Starlette/FastAPI uploads and duck-typed upload objects."""
    if isinstance(value, str) or not value:
        return False
    return bool(getattr(value, "filename", None))


async def parse_files(request: Request) -> List[UploadFile]:
    """
    Parse files parameter from request, handling edge cases:
    - Swagger UI 'Send empty value' sends empty string which FastAPI can't parse
    - This manually extracts files from the form, filtering out empty strings
    """
    try:
        form = await request.form()
        files = []
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
        )


# Multi-line TAC products — keep the whole buffer as one entry (do not line-split).
# SIGMET/AIRMET: WMO examples are header- + body= across lines (BUG-2026-07-30 / F23 UI).
# VAA/TCA/SWXA/VONA: advisory / notice templates with labeled fields (F26/F27/F28/F32).
# IWXXM: pass-through XML document (F7.t / EV-060 / #1003) — never line-split.
_MULTILINE_TEMPLATE_PRODUCTS = frozenset({"SIGMET", "AIRMET", "VAA", "TCA", "SWXA", "VONA", "IWXXM"})

# Wire product enum (api-contract EV-029 / F28 / EV-032 F32 / EV-060 F7.t).
# Canonical ``swxa`` / ``vona`` / ``iwxxm``.
_API_PRODUCTS = frozenset({"AIRMET", "METAR", "SIGMET", "SPECI", "TAF", "VAA", "TCA", "SWXA", "VONA", "IWXXM"})


def normalize_api_product(
    product: Optional[str],
    *,
    default: Optional[str] = "METAR",
) -> str:
    """Normalize multipart/JSON ``product`` to uppercase enum or raise ``unknown_product`` 400."""
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
    """Return list form field values; direct endpoint calls leave ``Form()`` defaults."""
    return value if isinstance(value, list) else []


def _coerce_form_str(value: object, default: str = "") -> str:
    """Return string form field values; direct endpoint calls leave ``Form()`` defaults."""
    return value if isinstance(value, str) else default


def _resolve_request_extensions(
    form_extensions: List[str],
    json_extensions: list[str] | None,
) -> list[str]:
    """Merge multipart and JSON extension tokens; reject unknown ids."""
    if json_extensions is not None:
        tokens = parse_extension_tokens(json_extensions)
    else:
        tokens = parse_extension_tokens(form_extensions)
    validate_extension_tokens(tokens)
    return tokens


def _package_issue_payload(issue: object) -> dict[str, Any]:
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
    stages = getattr(report, "stages", None) or []
    if not stages:
        return None
    out: list[dict[str, Any]] = []
    for stage in stages:
        stage_issues = getattr(stage, "issues", None) or []
        out.append(
            {
                "stage": str(getattr(stage, "stage", "")),
                "label": str(getattr(stage, "label", "")),
                "ok": bool(getattr(stage, "ok", False)),
                "issues": [_package_issue_payload(issue) for issue in stage_issues],
            }
        )
    return out


def _call_iwxxm_validate(
    xml_content: str,
    *,
    iwxxm_version: str,
    profile: str,
    levels: tuple[str, ...],
    emit_key: str,
    extensions: list[str],
    product: str,
) -> ValidationReport:
    validate_product = ca_eccc_validate_product(emit_key, extensions, product)
    return _iwxxm_validate_fn()(
        xml_content,
        iwxxm_version=iwxxm_version,
        profile=profile or "annex3",
        levels=levels,
        product=validate_product,
    )


def _resolve_request_profiles(
    *,
    route: str = "",
    profile: str = "",
    semantic_profile: str = "",
    exchange_profile: str = "",
    json_profile: str | None = None,
    json_semantic_profile: str | None = None,
    json_exchange_profile: str | None = None,
    for_packaging: bool = False,
) -> WireProfileSelection:
    """Merge multipart and JSON profile fields, then resolve to emit keys."""
    wire = resolve_route_profiles(
        profile=json_profile if json_profile is not None else profile,
        semantic_profile=json_semantic_profile if json_semantic_profile is not None else semantic_profile,
        exchange_profile=json_exchange_profile if json_exchange_profile is not None else exchange_profile,
        for_packaging=for_packaging,
    )
    if route:
        record_profile_wire_metrics(route, wire)
    return wire


def _is_multiline_template_product(product: Optional[str]) -> bool:
    """Return True for products whose TAC must not be split one-entry-per-line."""
    return (product or "").strip().upper() in _MULTILINE_TEMPLATE_PRODUCTS


def split_manual_entries(manual_text: str, product: Optional[str] = None) -> List[str]:
    """Split manual text into TAC entries.

    Default (METAR/SPECI/TAF): one entry per non-empty line.
    SIGMET/AIRMET/VAA/TCA/SWXA/VONA: entire buffer is one multi-line document —
    line-splitting would shred the header/body (SIGMET/AIRMET) or template
    fields (``VA ADVISORY`` / ``SWX ADVISORY`` / ``VONA`` / ``DTG:`` / …).
    """
    if not manual_text:
        return []
    if _is_multiline_template_product(product):
        text = manual_text.strip()
        return [text] if text else []
    return [line.strip() for line in manual_text.splitlines() if line.strip()]


def manual_entries_with_offsets(manual_text: str, product: Optional[str] = None) -> List[Tuple[str, int]]:
    """Split like ``split_manual_entries`` with start offsets into the original buffer.

    Offsets point at the first non-whitespace character of each kept entry so
    soft-preview ``failed_spans`` can be remapped onto the full editor document.
    For SIGMET/AIRMET/VAA/TCA/SWXA/VONA the single entry offset is the first
    non-whitespace character of the buffer (document preserved with internal newlines).
    """
    if not manual_text:
        return []
    if _is_multiline_template_product(product):
        stripped = manual_text.strip()
        if not stripped:
            return []
        lead = len(manual_text) - len(manual_text.lstrip())
        # Preserve internal newlines; only trim outer whitespace for the entry text.
        return [(stripped, lead)]
    out: List[Tuple[str, int]] = []
    offset = 0
    for line in manual_text.splitlines(keepends=True):
        raw = line[:-1] if line.endswith("\n") else line
        if raw.endswith("\r"):
            raw = raw[:-1]
        stripped = raw.strip()
        if stripped:
            lead = len(raw) - len(raw.lstrip())
            out.append((stripped, offset + lead))
        offset += len(line)
    return out


async def read_uploaded_text(upload_file: UploadFile) -> Tuple[Optional[str], Optional[str]]:
    """Read uploaded text file using strict UTF-8 decoding with a size limit.

    Gzip payloads (``.gz`` / magic ``1f 8b``) are inflated before decode.
    """
    import gzip

    max_upload_bytes = 10 * 1024 * 1024  # 10 MiB
    raw_bytes = await upload_file.read(max_upload_bytes + 1)
    if not raw_bytes or not raw_bytes.strip():
        return None, "empty file"

    if len(raw_bytes) > max_upload_bytes:
        return None, f"file too large (limit {max_upload_bytes} bytes)"

    name = (upload_file.filename or "").lower()
    if name.endswith(".gz") or name.endswith(".gzip") or raw_bytes[:2] == b"\x1f\x8b":
        try:
            import io

            # Cap inflate size during decompression (avoid gzip bombs).
            inflated = bytearray()
            with gzip.GzipFile(fileobj=io.BytesIO(raw_bytes), mode="rb") as gz:
                while True:
                    chunk = gz.read(64 * 1024)
                    if not chunk:
                        break
                    inflated.extend(chunk)
                    if len(inflated) > max_upload_bytes:
                        return None, f"decompressed file too large (limit {max_upload_bytes} bytes)"
            raw_bytes = bytes(inflated)
        except OSError as exc:
            return None, f"gzip decompress failed ({exc})"

    try:
        decoded = raw_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        return None, f"file must be UTF-8 encoded ({exc})"

    content = decoded.strip()
    if not content:
        return None, "empty file"

    return content, None


# Cap per-request bulletin fan-out (lint + convert per report).
MAX_BULLETIN_REPORTS = 100


async def read_upload_files_text(files: Optional[List[UploadFile]]) -> Tuple[str, Optional[str]]:
    """Join multipart uploads via ``read_uploaded_text`` (10 MiB each).

    Returns
    -------
    tuple[str, str | None]
        Joined text and an error message when a non-empty upload fails limits/encoding.
    """
    if not files:
        return "", None
    chunks: list[str] = []
    for upload in files:
        content, err = await read_uploaded_text(upload)
        if err == "empty file":
            continue
        if err:
            return "", err
        if content:
            chunks.append(content)
    return "\n".join(chunks), None


def is_xml_input(filename: Optional[str], content: str) -> bool:
    """Determine if uploaded content looks like XML input."""
    lowered_name = (filename or "").lower()
    if lowered_name.endswith(".xml"):
        return True
    return content.lstrip().startswith("<")


def classify_and_validate_upload_content(
    *,
    filename: Optional[str],
    content: str | None,
    iwxxm_version: str,
    endpoint_path: str,
    validation_orchestrator: Optional[Any],
) -> Optional[Dict[str, str]]:
    """Return a standardized XML rejection payload for TAC-only conversion endpoints."""
    if not content or not is_xml_input(filename, content):
        return None

    if not validation_orchestrator:
        return {
            "message": "XML validation is unavailable in this environment.",
            "hint": "Retry later or use TAC input for conversion.",
            "code": "XML_VALIDATION_UNAVAILABLE",
            "layer": "xml_input",
        }

    xml_wellformed_result = validation_orchestrator.validate_wellformed(content)
    if not xml_wellformed_result.passed:
        issue_message = (
            xml_wellformed_result.issues[0].message if xml_wellformed_result.issues else "XML is not well-formed"
        )
        return {
            "message": issue_message,
            "hint": "Fix XML syntax before upload.",
            "code": "XML_NOT_WELLFORMED",
            "layer": "xml_input",
        }

    xml_schema_result = validation_orchestrator.validate_xml_schema(content, iwxxm_version)
    blocking_schema_issues = [
        issue
        for issue in xml_schema_result.issues
        if getattr(issue, "level", None) and str(issue.level).lower().endswith("error")
    ]
    if not xml_schema_result.is_valid or blocking_schema_issues:
        schema_message = blocking_schema_issues[0].message if blocking_schema_issues else "XML schema validation failed"
        return {
            "message": schema_message,
            "hint": "Use an IWXXM XML file matching the selected IWXXM schema version.",
            "code": "XML_SCHEMA_VALIDATION_FAILED",
            "layer": "xml_input",
        }

    return {
        "message": f"XML input is valid, but {endpoint_path} is TAC only.",
        "hint": "Use TAC files for conversion. Use XML validation endpoints for XML-only checks.",
        "code": "XML_INPUT_NOT_CONVERTIBLE",
        "layer": "xml_input",
    }


def normalize_code(value: Optional[str], max_length: int) -> Optional[str]:
    """Normalize optional alphanumeric code-like fields."""
    if not value:
        return None
    normalized = value.strip().upper()
    if not normalized:
        return None
    return normalized[:max_length]


_BULLETIN_ID_RE = re.compile(r"^[A-Z]{4}[0-9]{2}$")
_CCCC_RE = re.compile(r"^[A-Z]{4}$")


def parse_optional_bulletin_id(value: Optional[str]) -> str:
    """Return uppercase bulletin id, or empty when omitted.

    Raises
    ------
    HTTPException
        400 when a non-empty value is not 4 letters + 2 digits.
    """
    raw = (value or "").strip().upper()
    if not raw:
        return ""
    if _BULLETIN_ID_RE.fullmatch(raw) is None:
        raise HTTPException(
            status_code=400,
            detail=ErrorDetail(
                message="Bulletin ID must be 4 letters followed by 2 digits.",
                errors=["bulletin_id"],
                issues=[
                    ConversionIssue(
                        source="request",
                        message="Bulletin ID must be 4 letters followed by 2 digits.",
                        severity=ConversionIssueSeverity.ERROR,
                        hint="Example: SAAA00. Leave blank to discover from the AHL or use defaults.",
                        code="INVALID_BULLETIN_ID",
                    )
                ],
                total_errors=1,
            ).model_dump(),
        )
    return raw


def parse_optional_issuing_center(value: Optional[str]) -> str:
    """Return uppercase ICAO CCCC, or empty when omitted.

    Raises
    ------
    HTTPException
        400 when a non-empty value is not exactly 4 letters.
    """
    raw = (value or "").strip().upper()
    if not raw:
        return ""
    if _CCCC_RE.fullmatch(raw) is None:
        raise HTTPException(
            status_code=400,
            detail=ErrorDetail(
                message="Issuing center must be a 4-letter ICAO code.",
                errors=["issuing_center"],
                issues=[
                    ConversionIssue(
                        source="request",
                        message="Issuing center must be a 4-letter ICAO code.",
                        severity=ConversionIssueSeverity.ERROR,
                        hint="Example: KWBC. Leave blank to discover from the AHL or use defaults.",
                        code="INVALID_ISSUING_CENTER",
                    )
                ],
                total_errors=1,
            ).model_dump(),
        )
    return raw


def normalize_validation_level(value: Optional[str]) -> str:
    """Normalize validation level to one of the supported API values."""
    allowed_levels = {"basic", "schema", "schematron", "icao_opmet", "comprehensive"}
    level = (value or "basic").strip().lower().replace("-", "_")
    return level if level in allowed_levels else "basic"


def _product_uses_metar_tac_layers(product: Optional[str]) -> bool:
    """Return True when legacy METAR/SPECI TAC keyword layers apply.

    F6.e non-METAR products (TAF, SIGMET, ...) must not be rejected by
    ``ValidationService.validate_all_layers`` which requires METAR/SPECI keywords.
    """
    product_u = (product or "METAR").strip().upper()
    return product_u in {"METAR", "SPECI"}


async def parse_optional_files(request: Request) -> List[UploadFile]:
    """Parse optional file uploads, filtering out empty strings from form data."""
    form = await request.form()
    files_data = form.getlist("files")
    return [f for f in files_data if _is_named_upload(f)]


_AHL_HEADING_SPLIT_CODES = frozenset({"bulletin_split_failed", "invalid_bbb"})
_INVALID_AHL_MESSAGE = (
    "The abbreviated heading is not valid. Use TTAAii CCCC YYGGgg (optional BBB), then one or more TAC reports."
)
_EMPTY_BULLETIN_MESSAGE = "No TAC reports found after the abbreviated heading."


def bulletin_split_http_error(exc: BulletinSplitError) -> HTTPException:
    """
    Map a bulletin split failure to an operator-facing HTTP error.

    Malformed heading codes become ``INVALID_AHL`` with ``alias`` preserving the
    engine code. Empty body after a valid heading stays ``empty_bulletin``.

    Parameters
    ----------
    exc :
        Split failure from ``tac2iwxxm.split_bulletin``.

    Returns
    -------
    HTTPException
        400 for empty bulletins; 422 for malformed headings.
    """
    if exc.code == "empty_bulletin":
        return HTTPException(
            status_code=400,
            detail={"code": "empty_bulletin", "message": _EMPTY_BULLETIN_MESSAGE},
        )
    if exc.code in _AHL_HEADING_SPLIT_CODES:
        return HTTPException(
            status_code=422,
            detail={
                "code": "INVALID_AHL",
                "alias": exc.code,
                "message": _INVALID_AHL_MESSAGE,
            },
        )
    return HTTPException(
        status_code=422,
        detail={"code": exc.code, "message": exc.message},
    )
