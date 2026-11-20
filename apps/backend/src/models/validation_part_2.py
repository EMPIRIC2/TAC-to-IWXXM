"""Part 2 of ``validation.py`` (line-cap split)."""

from __future__ import annotations

from pydantic import BaseModel, Field

from .validation_part_1 import LintFixModel, LintIssueModel


class LintIssueCatalogEntryModel(BaseModel):
    """
    One registry row exported by GET /api/v1/lint-issue-catalog.


    Attributes
    ----------
    _ : object
        See implementation.
    """

    code: str
    severity: str
    message_template: str
    product: str | None = None
    tags: list[str] = Field(default_factory=list)
    source_id: str | None = None
    source_url: str | None = None
    source_attribution: str | None = None
    # Additive EV-061 / #1014 (optional; older clients ignore).
    family: str | None = Field(
        default=None,
        description="lint (TAC registry) or iwxxm (validation checks)",
    )
    source_type: str | None = Field(
        default=None,
        description="tier1, tier2, or tier3 source policy",
    )
    status: str | None = Field(
        default=None,
        description="verified, legacy_alias, or semantic_only",
    )
    semantic_identifier: str | None = Field(
        default=None,
        description="Vocabulary concept path when href is a verified landing",
    )
    last_verified: str | None = Field(
        default=None,
        description="ISO date of last HTTP check for operator source_url",
    )
    replacement_url: str | None = Field(
        default=None,
        description="Verified landing when source_url is a legacy alias",
    )
    # Additive EV-062 / #1017 (optional; older clients ignore).
    issue_type: str | None = Field(
        default=None,
        description="Closed vocabulary: presence, structure, content, consistency, iwxxm_schema, other",
    )
    source_locator: str | None = Field(
        default=None,
        description="Section/table/page locator for the cited source",
    )
    source_access: str | None = Field(
        default=None,
        description="Operator access tier: public, paywall, login, semantic_only",
    )
    # Additive EV-1120 / #1121 (optional; older clients ignore).
    semantic_profiles: list[str] = Field(
        default_factory=list,
        description=("Canonical semantic profile ids this row applies to; empty = shared/global"),
    )
    exchange_profiles: list[str] = Field(
        default_factory=list,
        description=("Canonical exchange profile ids for packaging-tagged rows; empty = shared"),
    )


class LintIssueCatalogResponse(BaseModel):
    """
    Response for GET /api/v1/lint-issue-catalog.


    Attributes
    ----------
    _ : object
        See implementation.
    """

    issues: list[LintIssueCatalogEntryModel] = Field(default_factory=list)


class DecodeSegmentModel(BaseModel):
    """
    HTTP DTO for one TAC decode/annotate segment.


    Attributes
    ----------
    _ : object
        See implementation.
    """

    start: int
    end: int
    code: str
    explanation: str


class DecodeResidualModel(BaseModel):
    """
    HTTP DTO for an undecoded TAC span (explicit residuals - G4).


    Attributes
    ----------
    _ : object
        See implementation.
    """

    start: int
    end: int
    text: str


class DecodeTacResponse(BaseModel):
    """
    Response for POST /api/v1/decode-tac.


    Attributes
    ----------
    _ : object
        See implementation.
    """

    product: str
    segments: list[DecodeSegmentModel] = Field(default_factory=list)
    residuals: list[DecodeResidualModel] = Field(default_factory=list)
    summary: str = Field(
        default="",
        description="Deterministic plain-language paragraph of the report",
    )


class PackageIssueModel(BaseModel):
    """
    HTTP DTO for an iwxxm-validate package finding (additive on /validate).


    Attributes
    ----------
    _ : object
        See implementation.
    """

    layer: str
    severity: str
    message: str
    location: str | None = None
    code: str | None = None
    start: int | None = Field(default=None, description="Inclusive offset when known")
    end: int | None = Field(default=None, description="Exclusive offset when known")


class PackageStageModel(BaseModel):
    """
    Per-stage CA_ECCC validation outcome (additive on /validate).


    Attributes
    ----------
    _ : object
        See implementation.
    """

    stage: str
    label: str
    ok: bool
    issues: list[PackageIssueModel] = Field(default_factory=list)


class ValidateIssueModel(BaseModel):
    """
    HTTP DTO for a validation orchestrator finding on /validate.


    Attributes
    ----------
    _ : object
        See implementation.
    """

    layer: str
    level: str
    message: str
    location: str | None = None
    code: str | None = None
    start: int | None = Field(default=None, description="Inclusive offset when known")
    end: int | None = Field(default=None, description="Exclusive offset when known")


class ValidateLayerIssueModel(BaseModel):
    """
    Per-layer issue entry nested under ``issues_by_layer``.


    Attributes
    ----------
    _ : object
        See implementation.
    """

    level: str
    message: str
    location: str | None = None
    code: str | None = None


class ValidateResponse(BaseModel):
    """
    Response for POST /api/v1/validate (validation layers + package_* extras).


    Attributes
    ----------
    _ : object
        See implementation.
    """

    is_valid: bool
    version: str
    profile: str = "annex3"
    layers_run: list[str] = Field(default_factory=list)
    layers_passed: list[str] = Field(default_factory=list)
    layers_failed: list[str] = Field(default_factory=list)
    total_issues: int = 0
    issues: list[ValidateIssueModel] = Field(default_factory=list)
    issues_by_layer: dict[str, list[ValidateLayerIssueModel]] = Field(default_factory=dict)
    stopped_at_layer: str | None = None
    package_ok: bool = True
    package_issues: list[PackageIssueModel] = Field(default_factory=list)
    package_stages: list[PackageStageModel] | None = Field(
        default=None,
        description=(
            "Optional per-stage breakdown from iwxxm-validate when profile=ca_eccc and extensions include IWXXM_CA"
        ),
    )
    extensions: list[str] | None = Field(
        default=None,
        description="Resolved national extension tokens from the request (when supplied)",
    )
    segments: list[DecodeSegmentModel] | None = Field(
        default=None,
        description=(
            "Optional item-by-item decode rows (code and explanation) when a readable decode exists. "
            "Omitted when there is no decode."
        ),
    )
    summary: str | None = Field(
        default=None,
        description=(
            "Optional plain-language paragraph of the decoded report when a readable decode exists. "
            "Omitted when there is no decode."
        ),
    )


class BulletinMetaModel(BaseModel):
    """
    Abbreviated heading fields for one converted bulletin.


    Attributes
    ----------
    _ : object
        See implementation.
    """

    ahl: str
    report_count: int
    tt: str
    aa: str
    cccc: str
    yygggg: str
    bbb: str | None = None
    report_status: str | None = None


class BulletinReportResultModel(BaseModel):
    """
    Per-report convert-bulletin result (partial success allowed).


    Attributes
    ----------
    _ : object
        See implementation.
    """

    report_index: int
    ok: bool
    tac_input: str
    xml: str | None = None
    issues: list[LintIssueModel] = Field(default_factory=list)
    fixes: list[LintFixModel] = Field(default_factory=list)


class ConvertBulletinResponse(BaseModel):
    """
    Response for POST /api/v1/convert-bulletin.


    Attributes
    ----------
    _ : object
        See implementation.
    """

    bulletin_meta: BulletinMetaModel
    exchange_profile: str | None = Field(
        default=None,
        description="Resolved exchange packaging profile (default GLOBAL_AFS on this route)",
    )
    results: list[BulletinReportResultModel] = Field(default_factory=list)
