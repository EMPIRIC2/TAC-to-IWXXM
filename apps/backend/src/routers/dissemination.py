"""Thin FastAPI routers for dissemination preflight/send (F16–F19 / ADR-030)."""

from __future__ import annotations

import logging
import uuid
from typing import Any

import msgspec
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import create_async_engine

from dissemination.db_preflight import (
    EgressDenied,
    dialect_for_sink,
    normalize_sqlalchemy_uri,
    run_db_preflight,
)
from dissemination.handles import default_handle_store
from dissemination.models import (
    PreflightRequest,
    PreflightResponse,
    SendRequest,
    SendResponse,
)
from dissemination.rate_limit import RateLimitExceeded, default_rate_limiter
from dissemination.redact import redact_secrets
from dissemination.writer_contract import CONTRACT_TABLE, apply_writer_contract

from ..msgspec_http import msgspec_json_response
from ..utilities.security import verify_supabase_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/dissemination", tags=["Dissemination"])

_DB_SINKS = frozenset({"postgres", "mysql", "sqlserver", "sqlite"})
_decoder_preflight = msgspec.json.Decoder(PreflightRequest)
_decoder_send = msgspec.json.Decoder(SendRequest)


def _user_id(user: dict[str, Any]) -> str:
    return str(user.get("sub") or user.get("user_id") or "anonymous")


async def _read_struct(request: Request, decoder: msgspec.json.Decoder) -> Any:
    raw = await request.body()
    try:
        return decoder.decode(raw)
    except msgspec.DecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=redact_secrets(f"invalid request body: {exc}"),
        ) from exc


@router.post("/preflight")
async def dissemination_preflight(
    request: Request,
    user: dict[str, Any] = Depends(verify_supabase_token),
):
    """Run sink preflight; return schema diffs and optional memory-only handle."""
    uid = _user_id(user)
    try:
        default_rate_limiter.check(uid)
    except RateLimitExceeded as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(exc),
        ) from exc

    req: PreflightRequest = await _read_struct(request, _decoder_preflight)

    if req.sink_type not in _DB_SINKS:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=f"sink_type {req.sink_type!r} not implemented in this milestone",
        )

    try:
        result = await run_db_preflight(req)
    except EgressDenied as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=redact_secrets(str(exc)),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=redact_secrets(str(exc)),
        ) from exc
    except Exception as exc:
        logger.exception("dissemination preflight failed: %s", redact_secrets(str(exc)))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="preflight failed",
        ) from exc

    handle = None
    if result.ok:
        handle = default_handle_store.create(
            user_id=uid,
            sink_type=req.sink_type,
            uri=req.uri,
            params=dict(req.params),
        )
    resp = PreflightResponse(
        ok=result.ok,
        connectivity_ok=result.connectivity_ok,
        diffs=result.diffs,
        handle=handle,
        detail=result.detail,
    )
    return msgspec_json_response(resp)


@router.post("/send")
async def dissemination_send(
    request: Request,
    user: dict[str, Any] = Depends(verify_supabase_token),
):
    """Send IWXXM via a green preflight handle or inline sink params."""
    uid = _user_id(user)
    try:
        default_rate_limiter.check(uid)
    except RateLimitExceeded as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(exc),
        ) from exc

    req: SendRequest = await _read_struct(request, _decoder_send)

    sink_type = req.sink_type
    uri = req.uri
    if req.handle:
        rec = default_handle_store.get(req.handle, user_id=uid)
        if rec is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="invalid or expired preflight handle",
            )
        sink_type = rec.sink_type  # type: ignore[assignment]
        uri = rec.uri

    if sink_type not in _DB_SINKS:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=f"sink_type {sink_type!r} not implemented in this milestone",
        )
    if not uri:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="uri or valid handle required",
        )
    if not req.iwxxm_xml:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="iwxxm_xml is required",
        )

    # Re-check allowlist / contract before write.
    try:
        pre = await run_db_preflight(
            PreflightRequest(sink_type=sink_type, uri=uri, ddl=True)  # type: ignore[arg-type]
        )
    except EgressDenied as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=redact_secrets(str(exc)),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=redact_secrets(str(exc)),
        ) from exc

    if not pre.ok:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="writer-contract not green; run preflight with ddl=true",
        )

    dialect = dialect_for_sink(sink_type)
    sa_uri = normalize_sqlalchemy_uri(uri, sink_type)
    engine = create_async_engine(sa_uri)
    upload_key = f"kv_{uuid.uuid4().hex}"
    try:
        await apply_writer_contract(engine, dialect=dialect)
        from sqlalchemy import text

        insert_sql = text(
            f"INSERT INTO {CONTRACT_TABLE} "
            "(id, product, icao, observation_time, iwxxm_version, iwxxm_xml, "
            "tac_text, upload_key) "
            "VALUES (:id, :product, :icao, :observation_time, :iwxxm_version, "
            ":iwxxm_xml, :tac_text, :upload_key)"
        )
        async with engine.begin() as conn:
            await conn.execute(
                insert_sql,
                {
                    "id": str(uuid.uuid4()),
                    "product": req.product or "metar",
                    "icao": None,
                    "observation_time": None,
                    "iwxxm_version": req.iwxxm_version or "2025-2",
                    "iwxxm_xml": req.iwxxm_xml,
                    "tac_text": req.tac_text,
                    "upload_key": upload_key,
                },
            )
    except Exception as exc:
        logger.exception("dissemination send failed: %s", redact_secrets(str(exc)))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=redact_secrets(f"send failed: {exc}"),
        ) from exc
    finally:
        await engine.dispose()

    if req.handle:
        default_handle_store.pop(req.handle, user_id=uid)

    return msgspec_json_response(SendResponse(ok=True, kv_upload_key=upload_key, detail="uploaded"))
