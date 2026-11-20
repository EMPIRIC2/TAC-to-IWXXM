"""Part 6 of ``conversion.py`` (line-cap split)."""

from __future__ import annotations

import datetime
from typing import Any

from dissemination.packaging import apply_exchange_packaging
from fastapi import Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import Response

from src.schemas.validation import (
    BulletinMetaModel,
    BulletinReportResultModel,
    ConvertBulletinResponse,
    LintFixModel,
    LintIssueModel,
)
from src.services.conversion_profiles_service import ConversionProfilesService
from src.utilities.conversion import ConversionError
from src.utilities.iwxxm_pass_through import NOT_XML_CODE, lint_iwxxm_pass_through
from src.utilities.security import verify_optional_supabase_token
from tac2iwxxm import BulletinSplitError, iwxxm_filename, parse_ahl

from .conversion_api_surface import api_surface
from .conversion_part_1 import (
    _form_text,
    _resolve_effective_iwxxm_version,
    router,
    tac_lint_fn,
)


@router.post(
    "/convert-bulletin",
    tags=["Conversion"],
    summary="Convert a WMO bulletin",
    response_model=ConvertBulletinResponse,
    responses={
        400: {"description": "Empty bulletin - no TAC reports after the abbreviated heading"},
        415: {"description": "Unsupported Media Type - multipart/form-data required"},
        422: {
            "description": (
                "Malformed abbreviated heading (INVALID_AHL) or missing required fields. "
                "Engine split failures may include an alias of bulletin_split_failed."
            )
        },
    },
)
async def convert_bulletin(
    request: Request,
    product: str = Form(..., description="TAC product, or iwxxm for XML pass-through"),
    files: list[UploadFile] | None = File(None),
    manual_text: str = Form(
        default="",
        description=(
            "Bulletin text: abbreviated heading TTAAii CCCC YYGGgg (optional BBB), "
            "then one or more TAC reports. Empty Bulletin ID / Issuing Center uses "
            "the heading TTAAii and CCCC."
        ),
    ),
    profile: str = Form(
        default="", description="Deprecated - use conversion_library_id (legacy alias: annex3 or iwxxm_us)"
    ),
    semantic_profile: str = Form(
        default="",
        description=(
            "Deprecated on Convert & Send. Prefer conversion_library_id. "
            "Still accepted on convert-bulletin until Dissemination library packaging lands."
        ),
    ),
    exchange_profile: str = Form(
        default="",
        description="Exchange packaging profile (e.g. GLOBAL_AFS); ignored on convert-only paths",
    ),
    conversion_library_id: str = Form(
        default="",
        description="Conversion library asset id (resolves engine profile when set)",
    ),
    dissemination_library_id: str = Form(
        default="",
        description=(
            "Dissemination library asset id. When set, ordered transforms "
            "(envelope / topic / checksum / bulletin re-wrap) apply on this "
            "Convert & Send path only."
        ),
    ),
    iwxxm_version: str = Form(default="", description="Target IWXXM version"),
    lint: bool = Form(default=True, description="Run tac-validate before each report convert"),
    extensions: list[str] = Form(
        default=[],
        description="Optional national extension tokens (e.g. IWXXM_CA for full Canadian validate stack)",
    ),
    propagate_residuals_to_remarks: bool | None = Form(
        default=None,
        description=(
            "When true, append decode residual token text into remarks / humanReadableText "
            "when the profile supports that path; annex3 documents no XML target. "
            "Omitted uses the profile default (annex3 / ICAO_2025 off)."
        ),
    ),
    include_national_remarks: bool = Form(
        default=True,
        description=(
            "When false, omit national remarks after RMK from IWXXM output even for "
            "profiles that normally keep remarks."
        ),
    ),
    bulletin_date: str = Form(
        default="",
        description=(
            "Optional calendar date (YYYY-MM-DD) used as the year and month for TAC day stamps. "
            "When omitted, the current UTC date is used. A day that cannot fall in that month "
            "fails conversion, and the message names the day and the month."
        ),
    ),
    auth_user: dict[str, Any] | None = Depends(verify_optional_supabase_token),
) -> Response:
    """
    Split a WMO AHL bulletin and convert each TAC report.

    Partial success is allowed: HTTP 200 when split succeeds even if some reports fail.
    Per-report ``issues`` / ``fixes`` follow lint-style identity.



    Parameters
    ----------
    request : object
        Argument ``request``.
    product : object
        Argument ``product``.
    files : object
        Argument ``files``.
    manual_text : object
        Argument ``manual_text``.
    profile : object
        Argument ``profile``.
    semantic_profile : object
        Argument ``semantic_profile``.
    exchange_profile : object
        Argument ``exchange_profile``.
    conversion_library_id : object
        Argument ``conversion_library_id``.
    dissemination_library_id : object
        Argument ``dissemination_library_id``.
    iwxxm_version : object
        Argument ``iwxxm_version``.
    lint : object
        Argument ``lint``.
    extensions : object
        Argument ``extensions``.
    propagate_residuals_to_remarks : object
        Argument ``propagate_residuals_to_remarks``.
    auth_user : object
        Argument ``auth_user``.

    Returns
    -------
    object
        Return value.
    """
    lib_raw = _form_text(conversion_library_id)
    if lib_raw.strip():
        from metar_iwxxm_api.convert_library_hard_cut import (
            resolve_engine_profile_from_conversion_library,
        )

        profiles_service: ConversionProfilesService | None = None
        if auth_user is not None:
            profiles_service = ConversionProfilesService(str(auth_user.get("sub") or auth_user.get("user_id")))

        def _custom_engine(asset_id: str) -> str | None:
            """
            Internal helper ``_custom_engine``.

            Parameters
            ----------
            asset_id : object
                Argument ``asset_id``.

            Returns
            -------
            object
                Return value.
            """
            if profiles_service is None:
                return None
            try:
                asset = profiles_service.get_library_asset(asset_id)
            except ValueError:
                raise
            except Exception:
                return None
            from metar_iwxxm_api.convert_library_hard_cut import assert_library_usable_on_convert

            assert_library_usable_on_convert(
                kind=asset.kind,
                expected_kind="conversion",
                access=asset.access,
                status=asset.status,
            )
            return asset.engine_profile_id

        try:
            _, semantic_profile = resolve_engine_profile_from_conversion_library(
                lib_raw,
                get_custom_engine_profile_id=_custom_engine,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        profile = ""

    wire = api_surface._resolve_request_profiles(
        route="/api/v1/convert-bulletin",
        profile=_form_text(profile),
        semantic_profile=_form_text(semantic_profile),
        exchange_profile=_form_text(exchange_profile),
        for_packaging=True,
    )
    emit_profile: str = str(wire.emit_key)
    profile = emit_profile
    iwxxm_version = _resolve_effective_iwxxm_version(
        iwxxm_version,
        semantic_canonical=wire.semantic_canonical,
        emit_profile=emit_profile,
    )
    api_surface._resolve_request_extensions(extensions, None)

    content_type = (request.headers.get("content-type") or "").lower()
    if "multipart/form-data" not in content_type:
        raise HTTPException(
            status_code=415,
            detail="POST /api/v1/convert-bulletin requires multipart/form-data",
        )

    bulletin_text = manual_text or ""
    if files:
        joined, err = await api_surface.read_upload_files_text(files)
        if err:
            raise HTTPException(status_code=400, detail={"code": "upload_rejected", "message": err})
        if joined:
            bulletin_text = joined

    if not bulletin_text.strip():
        raise HTTPException(
            status_code=400,
            detail={"code": "empty_bulletin", "message": "At least one of files or manual_text is required"},
        )

    product = api_surface.normalize_api_product(product, default=None)

    # F7.t: convert-bulletin with product=iwxxm treats the body as one XML document.
    if product == "IWXXM":
        iwxxm_lint = lint_iwxxm_pass_through(bulletin_text)
        issues = [
            LintIssueModel(
                severity=i.severity,
                code=i.code,
                message=i.message,
                location=i.location,
                start=i.start,
                end=i.end,
            )
            for i in iwxxm_lint.issues
        ]
        if not iwxxm_lint.ok:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": NOT_XML_CODE,
                    "message": issues[0].message if issues else "Expected IWXXM XML",
                    "issues": [i.model_dump() for i in issues],
                },
            )
        xml_body = bulletin_text.strip()
        return api_surface.msgspec_json_response(
            ConvertBulletinResponse(
                bulletin_meta=BulletinMetaModel(
                    ahl="",
                    report_count=1,
                    tt="",
                    aa="",
                    cccc="",
                    yygggg="",
                    bbb=None,
                ),
                results=[
                    BulletinReportResultModel(
                        report_index=0,
                        ok=True,
                        tac_input="",
                        xml=xml_body,
                        issues=[],
                        fixes=[],
                    )
                ],
            )
        )

    try:
        split = api_surface.tac2iwxxm_split_bulletin(bulletin_text, product=product)
    except BulletinSplitError as exc:
        raise api_surface.bulletin_split_http_error(exc) from exc

    if split.meta.report_count > api_surface.MAX_BULLETIN_REPORTS:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "too_many_reports",
                "message": (
                    f"Bulletin contains {split.meta.report_count} reports; limit is {api_surface.MAX_BULLETIN_REPORTS}"
                ),
            },
        )

    bulletin_identifier: str | None = None
    try:
        ahl_parts = parse_ahl(split.meta.ahl)
        yy = int(split.meta.yygggg[:2])
        hh = int(split.meta.yygggg[2:4])
        mm = int(split.meta.yygggg[4:6])
        issued_at = datetime.datetime.now(datetime.UTC).replace(day=yy, hour=hh, minute=mm, second=0, microsecond=0)
        bulletin_identifier = iwxxm_filename(ahl_parts, issued_at=issued_at)
    except (TypeError, ValueError):
        bulletin_identifier = None

    results: list[BulletinReportResultModel] = []
    dissem_lib = _form_text(dissemination_library_id).strip()
    dissem_profiles: ConversionProfilesService | None = None
    if dissem_lib and auth_user is not None:
        dissem_profiles = ConversionProfilesService(str(auth_user.get("sub") or auth_user.get("user_id")))

    def _custom_dissem_body(asset_id: str) -> dict[str, object] | None:
        """
        Internal helper ``_custom_dissem_body``.

        Parameters
        ----------
        asset_id : object
            Argument ``asset_id``.

        Returns
        -------
        object
            Return value.
        """
        if dissem_profiles is None:
            return None
        try:
            asset = dissem_profiles.get_library_asset(asset_id)
        except ValueError:
            raise
        except Exception:
            return None
        from metar_iwxxm_api.convert_library_hard_cut import assert_library_usable_on_convert

        assert_library_usable_on_convert(
            kind=asset.kind,
            expected_kind="dissemination",
            access=asset.access,
            status=asset.status,
        )
        return dict(asset.body or {})

    for index, tac in enumerate(split.reports):
        issues: list[LintIssueModel] = []
        fixes: list[LintFixModel] = []
        xml_out: str | None = None
        ok = True

        if lint:
            lint_report = tac_lint_fn(
                tac,
                product=product,
                profile=profile,
            )
            issues.extend(
                LintIssueModel(
                    severity=i.severity,
                    code=i.code,
                    message=i.message,
                    location=i.location,
                    start=getattr(i, "start", None),
                    end=getattr(i, "end", None),
                )
                for i in lint_report.issues
            )
            fixes.extend(
                LintFixModel(code=f.code, message=f.message, replacement=f.replacement) for f in lint_report.fixes
            )
            if not lint_report.ok:
                ok = False

        if ok:
            try:
                xml_out, _ = api_surface.convert_metar_tac_with_metadata(
                    tac,
                    iwxxm_version=iwxxm_version,
                    reference_time=bulletin_date or None,
                    validate=False,
                    product=product,
                    profile=emit_profile,
                    report_status=split.meta.report_status,
                    propagate_residuals_to_remarks=propagate_residuals_to_remarks,
                    include_national_remarks=include_national_remarks,
                )
            except ConversionError as exc:
                ok = False
                xml_out = None
                issues.append(
                    LintIssueModel(
                        severity="error",
                        code="parse_failed",
                        message=str(exc),
                        location=None,
                    )
                )

        if ok and xml_out and wire.exchange_profile:
            xml_out = apply_exchange_packaging(
                xml_out,
                exchange_profile=wire.exchange_profile,
                bulletin_identifier=bulletin_identifier,
            )

        if ok and xml_out and dissem_lib:
            from dissemination.transforms import apply_dissemination_transforms
            from metar_iwxxm_api.convert_library_hard_cut import resolve_dissemination_transforms

            try:
                body_transforms = resolve_dissemination_transforms(
                    dissem_lib,
                    get_custom_dissemination_body=_custom_dissem_body,
                )
                transformed = apply_dissemination_transforms(
                    xml_out,
                    body_transforms,
                    bulletin_identifier=bulletin_identifier,
                )
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc
            xml_out = transformed.xml

        results.append(
            BulletinReportResultModel(
                report_index=index,
                ok=ok and xml_out is not None,
                tac_input=tac,
                xml=xml_out if ok else None,
                issues=issues,
                fixes=fixes,
            )
        )

    return api_surface.msgspec_json_response(
        ConvertBulletinResponse(
            bulletin_meta=BulletinMetaModel(
                ahl=split.meta.ahl,
                report_count=split.meta.report_count,
                tt=split.meta.tt,
                aa=split.meta.aa,
                cccc=split.meta.cccc,
                yygggg=split.meta.yygggg,
                bbb=split.meta.bbb,
                report_status=split.meta.report_status,
            ),
            exchange_profile=wire.exchange_profile,
            results=results,
        )
    )
