"""Part 2 of ``conversion_profiles.py`` (line-cap split)."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .conversion_profiles_part_1 import ConversionTemplateSlot, LibraryKindLiteral


class ConversionTemplateOut(BaseModel):
    """
    Persisted or first-party conversion template projection.


    Attributes
    ----------
    _ : object
        See implementation.
    """

    model_config = ConfigDict(populate_by_name=True)

    id: str
    user_id: UUID | None = None
    slug: str
    name: str
    access: str
    iwxxm_block: str = Field(serialization_alias="iwxxmBlock")
    slots: list[ConversionTemplateSlot] = Field(default_factory=list)
    sample: str = ""
    comments: str | None = None
    fork_of: str | None = Field(default=None, serialization_alias="forkOf")
    shared: bool = False
    profiles: list[str] = Field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ConversionTemplateListResponse(BaseModel):
    """
    First-party + custom conversion templates visible to the caller.


    Attributes
    ----------
    _ : object
        See implementation.
    """

    items: list[ConversionTemplateOut]


class ConversionTemplatePreviewRequest(BaseModel):
    """
    Bridge preview request.


    Attributes
    ----------
    _ : object
        See implementation.
    """

    model_config = ConfigDict(populate_by_name=True)

    template_id: str = Field(min_length=1, max_length=128, alias="templateId")
    focus_group: str = Field(default="", max_length=256, alias="focusGroup")
    full_tac: str | None = Field(default=None, max_length=8192, alias="fullTac")
    slots: list[ConversionTemplateSlot] | None = None
    iwxxm_block: str | None = Field(default=None, max_length=128, alias="iwxxmBlock")


class ConversionTemplatePreviewResponse(BaseModel):
    """
    Bridge preview response.


    Attributes
    ----------
    _ : object
        See implementation.
    """

    model_config = ConfigDict(populate_by_name=True)

    template_id: str = Field(serialization_alias="templateId")
    focus_group: str = Field(serialization_alias="focusGroup")
    matched: bool
    captures: list[dict[str, str]] = Field(default_factory=list)
    xml_block: str = Field(default="", serialization_alias="xmlBlock")
    compiled_pattern: str = Field(default="", serialization_alias="compiledPattern")
    skipped: list[dict[str, str]] = Field(default_factory=list)


class LibraryAssetOut(BaseModel):
    """
    First-party or custom library asset (five Libraries).


    Attributes
    ----------
    _ : object
        See implementation.
    """

    model_config = ConfigDict(populate_by_name=True)

    id: str
    kind: LibraryKindLiteral
    name: str
    access: Literal["first_party", "custom"]
    engine_profile_id: str = Field(serialization_alias="engineProfileId")
    attached_national_line: str = Field(serialization_alias="attachedNationalLine")
    body: dict[str, Any] = Field(default_factory=dict)
    fork_of: str | None = Field(default=None, serialization_alias="forkOf")
    user_id: UUID | None = Field(default=None, serialization_alias="userId")
    slug: str | None = None
    shared: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None
    yaml_body: str | None = Field(default=None, serialization_alias="yamlBody")
    status: Literal["draft", "activated"] = "draft"
    schema_version: int = Field(default=1, serialization_alias="schemaVersion")


class LibraryAssetListResponse(BaseModel):
    """
    Library assets visible to the caller.


    Attributes
    ----------
    _ : object
        See implementation.
    """

    items: list[LibraryAssetOut]


class LibraryAssetCreate(BaseModel):
    """
    Create a custom library asset (optionally forked).


    Attributes
    ----------
    _ : object
        See implementation.
    """

    model_config = ConfigDict(populate_by_name=True)

    slug: str = Field(min_length=1, max_length=128)
    name: str = Field(min_length=1, max_length=256)
    kind: LibraryKindLiteral
    engine_profile_id: str = Field(min_length=1, max_length=64, alias="engineProfileId")
    attached_national_line: str = Field(min_length=1, max_length=64, alias="attachedNationalLine")
    body: dict[str, Any] = Field(default_factory=dict)
    fork_of: str | None = Field(default=None, alias="forkOf")
    shared: bool = False
    yaml_body: str | None = Field(default=None, alias="yamlBody")
    status: Literal["draft", "activated"] = "draft"
    schema_version: int = Field(default=1, ge=1, alias="schemaVersion")


class LibraryAssetUpdate(BaseModel):
    """
    Partial update for a custom library asset (or fork-on-edit first-party).


    Attributes
    ----------
    _ : object
        See implementation.
    """

    model_config = ConfigDict(populate_by_name=True)

    slug: str | None = Field(default=None, max_length=128)
    name: str | None = Field(default=None, max_length=256)
    body: dict[str, Any] | None = None
    shared: bool | None = None
    yaml_body: str | None = Field(default=None, alias="yamlBody")
    status: Literal["draft", "activated"] | None = None
    schema_version: int | None = Field(default=None, ge=1, alias="schemaVersion")


class LibraryYamlValidateRequest(BaseModel):
    """
    Validate library YAML without persisting.


    Attributes
    ----------
    _ : object
        See implementation.
    """

    model_config = ConfigDict(populate_by_name=True)

    yaml_body: str = Field(min_length=0, alias="yamlBody")
    kind: LibraryKindLiteral
    lifecycle: Literal["draft", "activated"] = "draft"


class LibraryYamlValidateResponse(BaseModel):
    """
    Regex + schema diagnostics for a library YAML document.


    Attributes
    ----------
    _ : object
        See implementation.
    """

    valid_yaml: bool
    yaml_error: str | None = None
    kind: LibraryKindLiteral | None = None
    name: str | None = None
    lifecycle: Literal["draft", "activated"] = "draft"
    fail_count: int = 0
    warn_count: int = 0
    can_activate: bool = False
    diagnostics: list[dict[str, Any]] = Field(default_factory=list)


class LibraryRulePreviewRequest(BaseModel):
    """
    AC11 rule association preview for a TAC group.


    Attributes
    ----------
    _ : object
        See implementation.
    """

    model_config = ConfigDict(populate_by_name=True)

    library_id: str = Field(min_length=1, max_length=128, alias="libraryId")
    focus_group: str = Field(min_length=1, max_length=256, alias="focusGroup")


class LibraryRulePreviewResponse(BaseModel):
    """
    Matched conversion rule for a TAC group.


    Attributes
    ----------
    _ : object
        See implementation.
    """

    model_config = ConfigDict(populate_by_name=True)

    library_id: str = Field(serialization_alias="libraryId")
    focus_group: str = Field(serialization_alias="focusGroup")
    rule_id: str = Field(serialization_alias="ruleId")
    rule_name: str = Field(serialization_alias="ruleName")
    matched: bool = True
