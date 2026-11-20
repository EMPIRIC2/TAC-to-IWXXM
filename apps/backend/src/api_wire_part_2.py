"""Part 2 of ``api_wire.py`` (line-cap split)."""

from __future__ import annotations

from fastapi import UploadFile
from iwxxm_validate.models import ValidationReport
from tac2iwxxm.taf_lines import join_taf_entries, join_taf_lines

from src.services.validation_orchestrator import ValidationOrchestrator
from src.utilities.extension_wire import ca_eccc_validate_product
from src.utilities.observability import record_profile_wire_metrics
from src.utilities.profile_wire import WireProfileSelection, resolve_route_profiles

from .api_wire_part_1 import (
    _is_multiline_template_product,
    _iwxxm_validate_fn,
    logger,
)


def _call_iwxxm_validate(
    xml_content: str,
    *,
    iwxxm_version: str,
    profile: str,
    levels: tuple[str, ...],
    emit_key: str,
    extensions: list[str],
    product: str,
    output_policy_id: str | None = None,
) -> ValidationReport:
    """
    Internal helper ``_call_iwxxm_validate``.

    Parameters
    ----------
    xml_content : object
        Argument ``xml_content``.
    iwxxm_version : object
        Argument ``iwxxm_version``.
    profile : object
        Argument ``profile``.
    levels : object
        Argument ``levels``.
    emit_key : object
        Argument ``emit_key``.
    extensions : object
        Argument ``extensions``.
    product : object
        Argument ``product``.
    output_policy_id : object
        Argument ``output_policy_id``.

    Returns
    -------
    object
        Return value.
    """
    validate_product = ca_eccc_validate_product(emit_key, extensions, product)
    logger.debug("iwxxm output policy %s", output_policy_id)
    return _iwxxm_validate_fn()(
        xml_content,
        iwxxm_version=iwxxm_version,
        profile=profile or "annex3",
        levels=levels,
        product=validate_product,
        output_policy_id=output_policy_id,
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
    """
    Internal helper ``_resolve_request_profiles``.

    Parameters
    ----------
    route : object
        Argument ``route``.
    profile : object
        Argument ``profile``.
    semantic_profile : object
        Argument ``semantic_profile``.
    exchange_profile : object
        Argument ``exchange_profile``.
    json_profile : object
        Argument ``json_profile``.
    json_semantic_profile : object
        Argument ``json_semantic_profile``.
    json_exchange_profile : object
        Argument ``json_exchange_profile``.
    for_packaging : object
        Argument ``for_packaging``.

    Returns
    -------
    object
        Return value.
    """
    wire = resolve_route_profiles(
        profile=json_profile if json_profile is not None else profile,
        semantic_profile=json_semantic_profile if json_semantic_profile is not None else semantic_profile,
        exchange_profile=json_exchange_profile if json_exchange_profile is not None else exchange_profile,
        for_packaging=for_packaging,
    )
    if route:
        record_profile_wire_metrics(route, wire)
    return wire


def split_manual_entries(manual_text: str, product: str | None = None) -> list[str]:
    """
    Split manual text into TAC entries.

    Default (METAR/SPECI/TAF): one entry per non-empty line.
    SIGMET/AIRMET/VAA/TCA/SWXA/VONA: entire buffer is one multi-line document -
    line-splitting would shred the header/body (SIGMET/AIRMET) or template
    fields (``VA ADVISORY`` / ``SWX ADVISORY`` / ``VONA`` / ``DTG:`` / …).


    Parameters
    ----------
    manual_text : object
        Argument ``manual_text``.
    product : object
        Argument ``product``.

    Returns
    -------
    object
        Return value.
    """
    if not manual_text:
        return []
    if _is_multiline_template_product(product):
        text = manual_text.strip()
        return [text] if text else []
    lines = [line.strip() for line in manual_text.splitlines() if line.strip()]
    if (product or "").strip().upper() == "TAF":
        return join_taf_lines(lines)
    return lines


def manual_entries_with_offsets(manual_text: str, product: str | None = None) -> list[tuple[str, int]]:
    """
    Split like ``split_manual_entries`` with start offsets into the original buffer.

    Offsets point at the first non-whitespace character of each kept entry so
    soft-preview ``failed_spans`` can be remapped onto the full editor document.
    For SIGMET/AIRMET/VAA/TCA/SWXA/VONA the single entry offset is the first
    non-whitespace character of the buffer (document preserved with internal newlines).


    Parameters
    ----------
    manual_text : object
        Argument ``manual_text``.
    product : object
        Argument ``product``.

    Returns
    -------
    object
        Return value.
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
    out: list[tuple[str, int]] = []
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
    if (product or "").strip().upper() == "TAF":
        return join_taf_entries(out)
    return out


async def read_uploaded_text(upload_file: UploadFile) -> tuple[str | None, str | None]:
    """
    Read uploaded text file using strict UTF-8 decoding with a size limit.

    Gzip payloads (``.gz`` / magic ``1f 8b``) are inflated before decode.


    Parameters
    ----------
    upload_file : object
        Argument ``upload_file``.

    Returns
    -------
    object
        Return value.
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


async def read_upload_files_text(files: list[UploadFile] | None) -> tuple[str, str | None]:
    """
    Join multipart uploads via ``read_uploaded_text`` (10 MiB each).

    Returns
    -------
    tuple[str, str | None]
        Joined text and an error message when a non-empty upload fails limits/encoding.


    Parameters
    ----------
    files : object
        Argument ``files``.
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


def is_xml_input(filename: str | None, content: str) -> bool:
    """
    Determine if uploaded content looks like XML input.


    Parameters
    ----------
    filename : object
        Argument ``filename``.
    content : object
        Argument ``content``.

    Returns
    -------
    object
        Return value.
    """
    lowered_name = (filename or "").lower()
    if lowered_name.endswith(".xml"):
        return True
    return content.lstrip().startswith("<")


def classify_and_validate_upload_content(
    *,
    filename: str | None,
    content: str | None,
    iwxxm_version: str,
    endpoint_path: str,
    validation_orchestrator: ValidationOrchestrator | None,
) -> dict[str, str] | None:
    """
    Return a standardized XML rejection payload for TAC-only conversion endpoints.


    Parameters
    ----------
    filename : object
        Argument ``filename``.
    content : object
        Argument ``content``.
    iwxxm_version : object
        Argument ``iwxxm_version``.
    endpoint_path : object
        Argument ``endpoint_path``.
    validation_orchestrator : object
        Argument ``validation_orchestrator``.

    Returns
    -------
    object
        Return value.
    """
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


def normalize_code(value: str | None, max_length: int) -> str | None:
    """
    Normalize optional alphanumeric code-like fields.


    Parameters
    ----------
    value : object
        Argument ``value``.
    max_length : object
        Argument ``max_length``.

    Returns
    -------
    object
        Return value.
    """
    if not value:
        return None
    normalized = value.strip().upper()
    if not normalized:
        return None
    return normalized[:max_length]


def normalize_validation_level(value: str | None) -> str:
    """
    Normalize validation level to one of the supported API values.


    Parameters
    ----------
    value : object
        Argument ``value``.

    Returns
    -------
    object
        Return value.
    """
    allowed_levels = {"basic", "schema", "schematron", "icao_opmet", "comprehensive"}
    level = (value or "basic").strip().lower().replace("-", "_")
    return level if level in allowed_levels else "basic"


def _product_uses_metar_tac_layers(product: str | None) -> bool:
    """
    Internal helper ``_product_uses_metar_tac_layers``.

    Parameters
    ----------
    product : object
        Argument ``product``.

    Returns
    -------
    object
        Return value.
    """
    product_u = (product or "METAR").strip().upper()
    return product_u in {"METAR", "SPECI"}
