"""TAC lint, decode, and lint-issue-catalog routes (EV-037 TD-3b)."""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import Response
from tac2iwxxm import decode_tac as tac2iwxxm_decode_tac
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

router = APIRouter(prefix="/api/v1", tags=["Validation"])


@router.get(
    "/lint-issue-catalog",
    response_model=LintIssueCatalogResponse,
    responses={},
)
async def lint_issue_catalog(
    product: Optional[str] = None,
    family: Optional[str] = None,
    issue_type: Optional[str] = None,
    source_access: Optional[str] = None,
) -> Response:
    """Export TAC lint + IWXXM validation catalog for FE tooltips / catalog page."""
    from tac_validate.catalog_attribution import attribution_for
    from tac_validate.issue_catalog_meta import classify_issue_type

    from src.services.iwxxm_validation_catalog import iwxxm_validation_catalog_rows

    family_key = (family or "").strip().lower() or None
    if family_key is not None and family_key not in {"lint", "iwxxm"}:
        family_key = None
    issue_type_key = (issue_type or "").strip().lower() or None
    source_access_key = (source_access or "").strip().lower() or None

    issues: list[LintIssueCatalogEntryModel] = []

    if family_key in (None, "lint"):
        entries = tac_catalog_entries(product=product)
        for spec in entries:
            attr = attribution_for(spec.code)
            issues.append(
                LintIssueCatalogEntryModel(
                    code=spec.code,
                    severity=spec.severity,
                    message_template=spec.message_template,
                    product=spec.product,
                    tags=list(spec.tags),
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
                )
            )

    if family_key in (None, "iwxxm"):
        for row in iwxxm_validation_catalog_rows():
            issues.append(LintIssueCatalogEntryModel(**row))

    if issue_type_key or source_access_key:
        filtered: list[LintIssueCatalogEntryModel] = []
        for row in issues:
            if issue_type_key and (row.issue_type or "").lower() != issue_type_key:
                continue
            if source_access_key and (row.source_access or "").lower() != source_access_key:
                continue
            filtered.append(row)
        issues = filtered

    return api_surface.msgspec_json_response(LintIssueCatalogResponse(issues=issues))


@router.post(
    "/lint-tac",
    response_model=LintTacResponse,
    responses={
        415: {"description": "Unsupported Media Type — multipart/form-data required"},
    },
)
async def lint_tac(
    request: Request,
    manual_text: str = Form(default="", description="TAC or IWXXM XML to lint"),
    product: str = Form(
        default="METAR",
        description="Product type, or iwxxm for XML lint (default METAR)",
    ),
    files: Optional[List[UploadFile]] = File(None),
) -> Response:
    """Thin wrapper over ``packages/tac-validate`` (multipart/form-data only — Q8=A)."""
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
        415: {"description": "Unsupported Media Type — multipart/form-data required"},
        422: {"description": "Missing required product field"},
    },
)
async def decode_tac_endpoint(
    request: Request,
    product: str = Form(..., description="TAC product (required)"),
    manual_text: str = Form(default="", description="TAC text to decode"),
    files: Optional[List[UploadFile]] = File(None),
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
