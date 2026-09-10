"""Pydantic schemas for ConversionProfile catalog + rule packs (EV-933)."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MetarFamilyVariant(BaseModel):
    """Read-only METAR-family variant row projected from the profile catalog."""

    model_config = ConfigDict(extra="ignore")

    tac_lead: str
    api_product: str
    iwxxm_root: str
    rule_id: str | None = None
    rule_id_prefix: str | None = None
    minimal_observation: bool | None = None
    manobs: str | None = None
    notes: str | None = None


class ProfileCatalogEntry(BaseModel):
    """Read-only ConversionProfile catalog entry for the inspector."""

    model_config = ConfigDict(extra="ignore")

    id: str
    kind: str
    status: str | None = None
    priority: str | None = None
    products: list[str] = Field(default_factory=list)
    legacy_alias: str | None = None
    emit_key: str | None = None
    vendor_pins: dict[str, Any] = Field(default_factory=dict)
    implementation: dict[str, Any] = Field(default_factory=dict)
    deltas_vs_icao: list[str] = Field(default_factory=list)
    iwxxm_line: str | None = None
    metar_family_variants: list[MetarFamilyVariant] = Field(default_factory=list)
    rule_pack_count: int | None = Field(default=None, ge=0)
    overlay_count: int | None = Field(default=None, ge=0)


class ProfileCatalogResponse(BaseModel):
    """Catalog list response."""

    schema_version: int | str | None = None
    profiles: list[ProfileCatalogEntry]


class RulePackCreate(BaseModel):
    """Create body for a rule pack."""

    slug: str = Field(min_length=1, max_length=128)
    profile: str = Field(min_length=1, max_length=64)
    product: str = Field(min_length=1, max_length=32)
    stage: str = Field(min_length=1, max_length=64)
    severity: str = Field(min_length=1, max_length=32)
    when_expr: str = Field(default="", max_length=2048, alias="when")
    message: str = Field(default="", max_length=2048)
    standard_reference: str = Field(default="", max_length=512, alias="standardReference")

    model_config = ConfigDict(populate_by_name=True)


class RulePackUpdate(BaseModel):
    """Partial update for a rule pack."""

    slug: str | None = Field(default=None, max_length=128)
    profile: str | None = Field(default=None, max_length=64)
    product: str | None = Field(default=None, max_length=32)
    stage: str | None = Field(default=None, max_length=64)
    severity: str | None = Field(default=None, max_length=32)
    when_expr: str | None = Field(default=None, max_length=2048, alias="when")
    message: str | None = Field(default=None, max_length=2048)
    standard_reference: str | None = Field(default=None, max_length=512, alias="standardReference")

    model_config = ConfigDict(populate_by_name=True)


class RulePackOut(BaseModel):
    """Persisted rule pack (owner-scoped)."""

    model_config = ConfigDict(populate_by_name=True)

    id: UUID
    user_id: UUID
    slug: str
    profile: str
    product: str
    stage: str
    severity: str
    when_expr: str = Field(serialization_alias="when")
    message: str
    standard_reference: str = Field(serialization_alias="standardReference")
    created_at: datetime
    updated_at: datetime


class RulePackListResponse(BaseModel):
    """List of rule packs for the caller."""

    items: list[RulePackOut]


class OverlayCreate(BaseModel):
    """Create body for a signed overlay (server issues the signature)."""

    slug: str = Field(min_length=1, max_length=128)
    base_profile_id: str = Field(min_length=1, max_length=64, alias="baseProfileId")
    body: dict[str, Any] = Field(default_factory=dict)
    shared: bool = False

    model_config = ConfigDict(populate_by_name=True)


class OverlayUpdate(BaseModel):
    """Partial update for an overlay (re-signed on write)."""

    slug: str | None = Field(default=None, max_length=128)
    base_profile_id: str | None = Field(default=None, max_length=64, alias="baseProfileId")
    body: dict[str, Any] | None = None
    shared: bool | None = None

    model_config = ConfigDict(populate_by_name=True)


class OverlayOut(BaseModel):
    """Persisted signed overlay (owner-scoped)."""

    model_config = ConfigDict(populate_by_name=True)

    id: UUID
    user_id: UUID
    slug: str
    base_profile_id: str = Field(serialization_alias="baseProfileId")
    body: dict[str, Any]
    signature: str
    shared: bool
    created_at: datetime
    updated_at: datetime


class OverlayListResponse(BaseModel):
    """List of overlays for the caller."""

    items: list[OverlayOut]


class PresetCreate(BaseModel):
    """Create body for a saved semantic preset."""

    slug: str = Field(min_length=1, max_length=128)
    name: str = Field(min_length=1, max_length=128)
    semantic_profile: str = Field(min_length=1, max_length=64, alias="semanticProfile")
    iwxxm_version: str = Field(min_length=1, max_length=32, alias="iwxxmVersion")
    extensions: list[str] = Field(default_factory=list, max_length=16)
    report_variant: str | None = Field(default=None, max_length=64, alias="reportVariant")
    overlay_id: UUID | None = Field(default=None, alias="overlayId")
    shared: bool = False

    model_config = ConfigDict(populate_by_name=True)


class PresetUpdate(BaseModel):
    """Partial update for a saved semantic preset."""

    slug: str | None = Field(default=None, max_length=128)
    name: str | None = Field(default=None, max_length=128)
    semantic_profile: str | None = Field(default=None, max_length=64, alias="semanticProfile")
    iwxxm_version: str | None = Field(default=None, max_length=32, alias="iwxxmVersion")
    extensions: list[str] | None = Field(default=None, max_length=16)
    report_variant: str | None = Field(default=None, max_length=64, alias="reportVariant")
    overlay_id: UUID | None = Field(default=None, alias="overlayId")
    shared: bool | None = None

    model_config = ConfigDict(populate_by_name=True)


class PresetOut(BaseModel):
    """Persisted saved semantic preset."""

    model_config = ConfigDict(populate_by_name=True)

    id: UUID
    user_id: UUID
    slug: str
    name: str
    semantic_profile: str = Field(serialization_alias="semanticProfile")
    iwxxm_version: str = Field(serialization_alias="iwxxmVersion")
    extensions: list[str] = Field(default_factory=list)
    report_variant: str | None = Field(default=None, serialization_alias="reportVariant")
    overlay_id: UUID | None = Field(default=None, serialization_alias="overlayId")
    shared: bool
    created_at: datetime
    updated_at: datetime


class PresetListResponse(BaseModel):
    """List of semantic presets for the caller."""

    items: list[PresetOut]


class DisseminationTemplateCreate(BaseModel):
    """Create body for a saved dissemination template."""

    slug: str = Field(min_length=1, max_length=128)
    name: str = Field(min_length=1, max_length=128)
    sink_type: str = Field(min_length=1, max_length=32, alias="sinkType")
    product: str | None = Field(default=None, max_length=32)
    ddl: bool = False
    params: dict[str, Any] = Field(default_factory=dict)
    shared: bool = False

    model_config = ConfigDict(populate_by_name=True)


class DisseminationTemplateUpdate(BaseModel):
    """Partial update for a saved dissemination template."""

    slug: str | None = Field(default=None, max_length=128)
    name: str | None = Field(default=None, max_length=128)
    sink_type: str | None = Field(default=None, max_length=32, alias="sinkType")
    product: str | None = Field(default=None, max_length=32)
    ddl: bool | None = None
    params: dict[str, Any] | None = None
    shared: bool | None = None

    model_config = ConfigDict(populate_by_name=True)


class DisseminationTemplateOut(BaseModel):
    """Persisted saved dissemination template."""

    model_config = ConfigDict(populate_by_name=True)

    id: UUID
    user_id: UUID
    slug: str
    name: str
    sink_type: str = Field(serialization_alias="sinkType")
    product: str | None = None
    ddl: bool
    params: dict[str, Any] = Field(default_factory=dict)
    shared: bool
    created_at: datetime
    updated_at: datetime


class DisseminationTemplateListResponse(BaseModel):
    """List of saved dissemination templates for the caller."""

    items: list[DisseminationTemplateOut]
