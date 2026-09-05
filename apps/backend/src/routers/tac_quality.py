"""TAC lint, decode, and lint-issue-catalog routes (EV-037 TD-3b)."""

from __future__ import annotations

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import Response
from tac_validate import lint as tac_lint_fn
from tac_validate.issue_registry import catalog_entries as tac_catalog_entries

from src import api as api_surface
from src.schemas.validation import (
    DecodeResidualModel,
    DecodeSegmentModel,
    DecodeTacResponse,
    LintFixModel,
    LintIssueCatalogEntryModel,
    LintIssueCatalogResponse,
    LintIssueModel,
    LintTacResponse,
)
from src.utilities.iwxxm_pass_through import lint_iwxxm_pass_through
from tac2iwxxm import decode_tac as tac2iwxxm_decode_tac

router = APIRouter(prefix="/api/v1", tags=["Validation"])


@router.get(
    "/lint-issue-catalog",
    response_model=LintIssueCatalogResponse,
    responses={},
)
async def lint_issue_catalog(
    product: str | None = None,
    family: str | None = None,
    issue_type: str | None = None,
    source_access: str | None = None,
    semantic_profile: str | None = None,
    exchange_profile: str | None = None,
) -> Response:
    """Export TAC lint + IWXXM validation catalog for FE tooltips / catalog page."""
    from dissemination.exchange_registry import resolve_exchange_profile
    from tac_validate.catalog_attribution import attribution_for
    from tac_validate.issue_catalog_meta import classify_issue_type

    from src.services.iwxxm_validation_catalog import iwxxm_validation_catalog_rows
    from src.services.lint_catalog_profile_filter import (
        exchange_profiles_from_tags,
        row_matches_profile,
        semantic_profiles_from_tags,
    )
    from src.utilities.profile_wire import resolve_route_profiles

    family_key = (family or "").strip().lower() or None
    if family_key is not None and family_key not in {"lint", "iwxxm"}:
        family_key = None
    issue_type_key = (issue_type or "").strip().lower() or None
    source_access_key = (source_access or "").strip().lower() or None

    semantic_raw = (semantic_profile or "").strip()
    exchange_raw = (exchange_profile or "").strip()
    semantic_canonical: str | None = None
    exchange_canonical: str | None = None
    if semantic_raw:
        semantic_canonical = resolve_route_profiles(
            semantic_profile=semantic_raw,
            for_packaging=False,
        ).semantic_canonical
    if exchange_raw:
        resolved_ex = resolve_exchange_profile(exchange_raw)
        if resolved_ex is None:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "invalid_exchange_profile",
                    "message": f"Unknown exchange profile {exchange_raw!r}",
                },
            )
        exchange_canonical = resolved_ex.wire_id

    issues: list[LintIssueCatalogEntryModel] = []

    if family_key in (None, "lint"):
        entries = tac_catalog_entries(product=product)
        for spec in entries:
            attr = attribution_for(spec.code)
            tags = list(spec.tags)
            issues.append(
                LintIssueCatalogEntryModel(
                    code=spec.code,
                    severity=spec.severity,
                    message_template=spec.message_template,
                    product=spec.product,
                    tags=tags,
                    source_id=attr.get("source_id"),
                    source_url=attr.get("source_url"),
                    source_attribution=attr.get("source_attribution"),
                    family=attr.get("family") or "lint",
                    source_type=attr.get("source_type"),
                    status=attr.get("status"),
                    semantic_identifier=attr.get("semantic_identifier"),
                    last_verified=attr.get("last_verified"),
                    replacement_url=attr.get("replacement_url"),
                    issue_type=classify_issue_type(
                        code=spec.code,
                        tags=spec.tags,
                        family="lint",
                    ),
                    source_locator=attr.get("source_locator"),
                    source_access=attr.get("source_access"),
                    semantic_profiles=semantic_profiles_from_tags(tags),
                    exchange_profiles=exchange_profiles_from_tags(tags),
                )
            )

    if family_key in (None, "iwxxm"):
        for row in iwxxm_validation_catalog_rows():
            tags = list(row.get("tags") or [])
            issues.append(
                LintIssueCatalogEntryModel(
                    code=str(row["code"]),
                    severity=str(row["severity"]),
                    message_template=str(row["message_template"]),
                    product=row.get("product"),
                    tags=tags,
                    source_id=row.get("source_id"),
                    source_url=row.get("source_url"),
                    source_attribution=row.get("source_attribution"),
                    family=row.get("family"),
                    source_type=row.get("source_type"),
                    status=row.get("status"),
                    semantic_identifier=row.get("semantic_identifier"),
                    last_verified=row.get("last_verified"),
                    replacement_url=row.get("replacement_url"),
                    issue_type=row.get("issue_type"),
                    source_locator=row.get("source_locator"),
                    source_access=row.get("source_access"),
                    semantic_profiles=semantic_profiles_from_tags(tags),
                    exchange_profiles=exchange_profiles_from_tags(tags),
                )
            )
    if issue_type_key or source_access_key:
        filtered: list[LintIssueCatalogEntryModel] = []
        for row in issues:
            if issue_type_key and (row.issue_type or "").lower() != issue_type_key:
                continue
            if source_access_key and (row.source_access or "").lower() != source_access_key:
                continue
            filtered.append(row)
        issues = filtered

    if semantic_canonical is not None:
        issues = [row for row in issues if row_matches_profile(row.semantic_profiles, selected=semantic_canonical)]
    if exchange_canonical is not None:
        issues = [row for row in issues if row_matches_profile(row.exchange_profiles, selected=exchange_canonical)]

    return api_surface.msgspec_json_response(LintIssueCatalogResponse(issues=issues))


@router.post(
    "/lint-tac",
    response_model=LintTacResponse,
    responses={
        415: {"description": "Unsupported Media Type - multipart/form-data required"},
    },
)
async def lint_tac(
    request: Request,
    manual_text: str = Form(default="", description="TAC or IWXXM XML to lint"),
    product: str = Form(
        default="METAR",
        description="Product type, or iwxxm for XML lint (default METAR)",
    ),
    files: list[UploadFile] | None = File(None),
) -> Response:
    """Thin wrapper over ``packages/tac-validate`` (multipart/form-data only - Q8=A)."""
    content_type = (request.headers.get("content-type") or "").lower()
    if "multipart/form-data" not in content_type:
        raise HTTPException(
            status_code=415,
            detail="POST /api/v1/lint-tac requires multipart/form-data",
        )

    tac_text = manual_text or ""
    if files:
        joined, err = await api_surface.read_upload_files_text(files)
        if err:
            raise HTTPException(status_code=400, detail={"code": "upload_rejected", "message": err})
        if joined:
            tac_text = joined

    product_u = api_surface.normalize_api_product(product, default="METAR")
    if product_u == "IWXXM":
        report = lint_iwxxm_pass_through(tac_text)
        return api_surface.msgspec_json_response(
            LintTacResponse(
                ok=report.ok,
                product=report.product,
                issues=[
                    LintIssueModel(
                        severity=i.severity,
                        code=i.code,
                        message=i.message,
                        location=i.location,
                        start=i.start,
                        end=i.end,
                    )
                    for i in report.issues
                ],
                fixes=[],
            )
        )
    report = tac_lint_fn(tac_text, product=product_u)
    return api_surface.msgspec_json_response(
        LintTacResponse(
            ok=report.ok,
            product=report.product,
            issues=[
                LintIssueModel(
                    severity=i.severity,
                    code=i.code,
                    message=i.message,
                    location=i.location,
                    start=getattr(i, "start", None),
                    end=getattr(i, "end", None),
                )
                for i in report.issues
            ],
            fixes=[LintFixModel(code=f.code, message=f.message, replacement=f.replacement) for f in report.fixes],
        )
    )


@router.post(
    "/decode-tac",
    tags=["Conversion"],
    response_model=DecodeTacResponse,
    responses={
        415: {"description": "Unsupported Media Type - multipart/form-data required"},
        422: {"description": "Missing required product field"},
    },
)
async def decode_tac_endpoint(
    request: Request,
    product: str = Form(..., description="TAC product (required)"),
    manual_text: str = Form(default="", description="TAC text to decode"),
    files: list[UploadFile] | None = File(None),
) -> Response:
    """Decode TAC into annotated segments and a plain-language summary."""
    content_type = (request.headers.get("content-type") or "").lower()
    if "multipart/form-data" not in content_type:
        raise HTTPException(
            status_code=415,
            detail="POST /api/v1/decode-tac requires multipart/form-data",
        )

    tac_text = manual_text or ""
    if files:
        joined, err = await api_surface.read_upload_files_text(files)
        if err:
            raise HTTPException(status_code=400, detail={"code": "upload_rejected", "message": err})
        if joined:
            tac_text = joined

    product_u = api_surface.normalize_api_product(product, default=None)
    result = tac2iwxxm_decode_tac(tac_text, product=product_u)
    return api_surface.msgspec_json_response(
        DecodeTacResponse(
            product=result.product,
            segments=[
                DecodeSegmentModel(
                    start=s.start,
                    end=s.end,
                    code=s.code,
                    explanation=s.explanation,
                )
                for s in result.segments
            ],
            residuals=[DecodeResidualModel(start=r.start, end=r.end, text=r.text) for r in result.residuals],
            summary=result.summary,
        )
    )
