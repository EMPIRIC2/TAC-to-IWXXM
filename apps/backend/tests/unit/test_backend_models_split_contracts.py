"""Contract tests for backend models package + line-cap split facades.

Covers evolve-auto success / mutation / failure / validation permutations for
the models/schemas bridge and conversion orchestration entrypoints.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from src.models.conversion import ConversionResponse, ConversionResponseMetadata, ConversionResult
from src.models.conversion_profiles import (
    LibraryAssetCreate,
    LibraryKindLiteral,
    PresetCreate,
    PresetUpdate,
)
from src.models.orm import Base, TranslationStatisticsModel
from src.models.validation import ValidationLevel, ValidationSeverity
from src.routers import conversion as conversion_router
from src.schemas import conversion as conversion_schemas
from src.schemas import conversion_profiles as profiles_schemas
from src.schemas import validation as validation_schemas


def test_schemas_bridge_reexports_conversion_models() -> None:
    """schemas.conversion re-exports models.conversion public types."""
    assert conversion_schemas.ConversionResponse is ConversionResponse
    assert conversion_schemas.ConversionResponseMetadata is ConversionResponseMetadata
    assert validation_schemas.ValidationSeverity is ValidationSeverity
    assert ValidationSeverity is ValidationLevel
    assert profiles_schemas.LibraryKindLiteral is LibraryKindLiteral


def test_orm_models_live_under_models_package() -> None:
    """SQLAlchemy ORM symbols remain importable from src.models."""
    assert TranslationStatisticsModel.__tablename__ == "translation_statistics"
    assert Base is not None


def test_conversion_response_metadata_accepts_known_and_extra_keys() -> None:
    """Nested convert metadata uses a model with extra=allow (validation success)."""
    meta = ConversionResponseMetadata(
        bulletin_id="EGLL01",
        product="metar",
        custom_flag=True,  # type: ignore[call-arg]
    )
    assert meta.bulletin_id == "EGLL01"
    assert meta.model_extra is not None
    payload = ConversionResponse(
        results=[
            ConversionResult(
                name="manual_input.txt",
                content="<xml/>",
                source="manual",
                size_bytes=6,
            )
        ],
        errors=[],
        issues=[],
        total_processed=1,
        successful=1,
        failed=0,
        metadata=meta,
    )
    assert payload.successful == 1
    dumped = payload.model_dump()
    assert dumped["metadata"]["bulletin_id"] == "EGLL01"


def test_conversion_response_rejects_invalid_counts() -> None:
    """Validation failure: negative counters are rejected (422-class)."""
    with pytest.raises(ValidationError):
        ConversionResponse(
            results=[],
            errors=[],
            issues=[],
            total_processed=-1,
            successful=0,
            failed=0,
        )


def test_preset_create_and_update_validation_matrix() -> None:
    """Mutation x validation: create/update pass and fail for profile presets."""
    created = PresetCreate(
        slug="ops-default",
        name="ops-default",
        semantic_profile="annex3",
        iwxxm_version="2025-2",
    )
    assert created.name == "ops-default"

    with pytest.raises(ValidationError):
        PresetCreate(
            slug="",
            name="x",
            semantic_profile="annex3",
            iwxxm_version="2025-2",
        )

    updated = PresetUpdate(name="renamed")
    assert updated.name == "renamed"

    with pytest.raises(ValidationError):
        PresetUpdate(name="x" * 200)


def test_library_asset_create_success_and_failure() -> None:
    """Mutation create success/fail for library assets."""
    asset = LibraryAssetCreate(
        kind="conversion",
        slug="lib-1",
        name="Library 1",
        engine_profile_id="annex3",
        attached_national_line="none",
        body={},
    )
    assert asset.slug == "lib-1"
    assert asset.kind in LibraryKindLiteral.__args__  # type: ignore[attr-defined]
    with pytest.raises(ValidationError):
        LibraryAssetCreate(
            kind="not-a-kind",  # type: ignore[arg-type]
            slug="x",
            name="x",
            engine_profile_id="annex3",
            attached_national_line="none",
            body={},
        )


def test_conversion_router_exports_convert_entrypoint() -> None:
    """Success path: conversion facade still exposes convert coroutine."""
    assert callable(conversion_router.convert)


def test_convert_continue_entrypoint_importable() -> None:
    """Failure/success seam: convert continuation module imports after line-cap split."""
    from src.routers.conversion_convert_continue import convert_continue

    assert callable(convert_continue)


def test_src_line_count_gate() -> None:
    """Every apps/backend/src Python module stays ≤500 lines."""
    from pathlib import Path

    root = Path(__file__).resolve().parents[2] / "src"
    over = []
    for path in root.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        n = text.count("\n") + (0 if text.endswith("\n") or not text else 1)
        if n > 500:
            over.append(f"{n} {path.relative_to(root)}")
    assert over == [], "files over 500 lines:\n" + "\n".join(over)


def test_api_module_imports() -> None:
    """Success path: FastAPI app module loads after the split."""
    from src.api import app

    assert app is not None
    assert len(app.routes) >= 20
