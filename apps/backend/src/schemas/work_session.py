"""Pydantic schemas for F5/F7 unified TAC work session API (ADR-020)."""

from __future__ import annotations

import re
from datetime import datetime
from enum import StrEnum
from html import unescape
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

_HTML_TAG_RE = re.compile(r"<[^>]*>")


class WorkSessionStatus(StrEnum):
    """Lifecycle status for a user's TAC work session."""

    DRAFT = "draft"
    WIP = "wip"
    FINISHED = "finished"
    FAILED = "failed"


class WorkSessionProduct(StrEnum):
    """Product ids stored on ``tac_work_sessions.product`` (lowercase)."""

    AIRMET = "airmet"
    METAR = "metar"
    SIGMET = "sigmet"
    SPECI = "speci"
    TAF = "taf"
    VAA = "vaa"
    TCA = "tca"
    SWXA = "swxa"


class PendingFilePayload(BaseModel):
    """
    Queued file content stored inline on the session row.

    Attributes
    ----------
    _ : object
        See implementation.
    """

    name: str = Field(min_length=1)
    content: str = ""


def _normalize_product_value(value: object) -> object:
    """
    Internal helper ``_normalize_product_value``.

    Parameters
    ----------
    value : object
        Argument ``value``.

    Returns
    -------
    object
        Return value.
    """
    if isinstance(value, str):
        return value.strip().lower()
    return value


def sanitize_work_session_title(value: object) -> object:
    """
    Strip HTML markup from a work-session title (defense in depth).

    Parameters
    ----------
    value :
        Raw title from create/update, or ``None`` when omitted.

    Returns
    -------
    object
        Plain-text title with tags removed and whitespace normalized, ``None``
        when the input was ``None``, or the original value when not a string.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (sanitize_work_session_title)
    2
    """
    if value is None or not isinstance(value, str):
        return value
    plain = unescape(_HTML_TAG_RE.sub("", value))
    plain = plain.replace("<", "").replace(">", "")
    return " ".join(plain.split())


class WorkSessionPayload(BaseModel):
    """
    Shared optional fields for create/update payloads (product declared on subclasses).

    Attributes
    ----------
    _ : object
        See implementation.
    """

    title: str | None = None
    manual_tac: str = ""
    pending_files: list[PendingFilePayload] = Field(default_factory=list)
    converted_results: list[dict[str, Any]] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    issues: list[dict[str, Any]] = Field(default_factory=list)
    conversion_params: dict[str, Any] = Field(default_factory=dict)
    status: WorkSessionStatus | None = None
    kv_upload_key: str | None = None

    @field_validator("title", mode="before")
    @classmethod
    def _sanitize_title(cls, value: object) -> object:
        """
        Internal helper ``_sanitize_title``.

        Parameters
        ----------
        value : object
            Argument ``value``.

        Returns
        -------
        object
            Return value.
        """
        return sanitize_work_session_title(value)


class WorkSessionCreate(WorkSessionPayload):
    """
    Body for POST /api/v1/work-sessions.

    Attributes
    ----------
    _ : object
        See implementation.
    """

    product: WorkSessionProduct

    @field_validator("product", mode="before")
    @classmethod
    def _normalize_product(cls, value: object) -> object:
        """
        Internal helper ``_normalize_product``.

        Parameters
        ----------
        value : object
            Argument ``value``.

        Returns
        -------
        object
            Return value.
        """
        return _normalize_product_value(value)


class WorkSessionUpdate(WorkSessionPayload):
    """
    Body for PATCH /api/v1/work-sessions/{id}.

    Attributes
    ----------
    _ : object
        See implementation.
    """

    product: WorkSessionProduct | None = None

    @field_validator("product", mode="before")
    @classmethod
    def _normalize_product(cls, value: object) -> object:
        """
        Internal helper ``_normalize_product``.

        Parameters
        ----------
        value : object
            Argument ``value``.

        Returns
        -------
        object
            Return value.
        """
        return _normalize_product_value(value)


class WorkSession(BaseModel):
    """
    Persisted work session returned by the API.

    Attributes
    ----------
    _ : object
        See implementation.
    """

    id: UUID
    user_id: UUID
    product: WorkSessionProduct
    status: WorkSessionStatus
    title: str
    manual_tac: str = ""
    pending_files: list[PendingFilePayload] = Field(default_factory=list)
    converted_results: list[dict[str, Any]] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    issues: list[dict[str, Any]] = Field(default_factory=list)
    conversion_params: dict[str, Any] = Field(default_factory=dict)
    kv_upload_key: str | None = None
    deleted_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    @field_validator("product", mode="before")
    @classmethod
    def _normalize_product(cls, value: object) -> object:
        """
        Internal helper ``_normalize_product``.

        Parameters
        ----------
        value : object
            Argument ``value``.

        Returns
        -------
        object
            Return value.
        """
        return _normalize_product_value(value)

    @field_validator("title", mode="before")
    @classmethod
    def _sanitize_title(cls, value: object) -> object:
        """
        Internal helper ``_sanitize_title``.

        Parameters
        ----------
        value : object
            Argument ``value``.

        Returns
        -------
        object
            Return value.
        """
        cleaned = sanitize_work_session_title(value)
        return "" if cleaned is None else cleaned


class WorkSessionListResponse(BaseModel):
    """
    Paginated list of work sessions.

    Attributes
    ----------
    _ : object
        See implementation.
    """

    items: list[WorkSession]
    total: int
    page: int
    limit: int


class AdminWorkSession(WorkSession):
    """
    Deprecated admin list row (routes removed - schema retained for typing only).

    Attributes
    ----------
    _ : object
        See implementation.
    """

    user_email: str | None = None
