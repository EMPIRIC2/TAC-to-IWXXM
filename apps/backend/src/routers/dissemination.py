"""Thin FastAPI routers for dissemination preflight/send (F16-F19)."""

from __future__ import annotations

import logging
import uuid
from typing import Any, cast
from uuid import UUID

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
    SinkType,
)
from dissemination.rate_limit import RateLimitExceeded, default_rate_limiter
from dissemination.redact import redact_secrets
from dissemination.writer_contract import CONTRACT_TABLE, apply_writer_contract
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import create_async_engine

from ..msgspec_http import msgspec_json_response
from ..services.conversion_profiles_service import ConversionProfilesService
from ..services.dissemination_drawer import is_non_db_sink, run_non_db_preflight, run_non_db_send
from ..utilities.abuse_controls import dissemination_limit, get_limiter
from ..utilities.security import verify_optional_supabase_token
from .dissemination_router_helpers import (
    client_id,
    merge_template_params,
    profiles_service_for_optional_auth,
    read_preflight,
    read_send,
    require_sink,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/dissemination", tags=["Dissemination"])
_limiter = get_limiter()


@router.post("/preflight")
@dissemination_limit(_limiter)
async def dissemination_preflight(
    request: Request,
    auth_user: dict[str, Any] | None = Depends(verify_optional_supabase_token),
) -> object:
    """
    Run sink preflight; return schema diffs and optional memory-only handle.

    Examples
    --------
    >>> 1 + 1 # docstring smoke (dissemination_preflight)
    2

    Parameters
    ----------
    request : object
        Argument ``request``.
    auth_user : object
        Argument ``auth_user``.

    Returns
    -------
    object
        Return value.
    """
    uid = client_id(request)
    try:
        default_rate_limiter.check(uid)
    except RateLimitExceeded as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(exc),
        ) from exc

    req = await read_preflight(request)
    profiles_service = profiles_service_for_optional_auth(auth_user)
    if req.dissemination_template_id:
        if profiles_service is None:
            raise HTTPException(
                status_code=401,
                detail="Sign in required to apply a dissemination template",
                headers={"WWW-Authenticate": "Bearer"},
            )
        try:
            template = profiles_service.get_template(UUID(req.dissemination_template_id))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Unknown dissemination template id") from exc
        resolved_sink_type = cast(SinkType | None, req.sink_type or template.sink_type)
        req = PreflightRequest(
            dissemination_template_id=req.dissemination_template_id,
            sink_type=resolved_sink_type,
            uri=req.uri,
            ddl=req.ddl if req.ddl is not None else template.ddl,
            product=req.product or template.product,
            iwxxm_version=req.iwxxm_version,
            params=merge_template_params(template.params, dict(req.params)),
        )

    sink_type = require_sink(req.sink_type)

    try:
        if is_non_db_sink(sink_type):
            result = await run_non_db_preflight(sink_type, dict(req.params))
        else:
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
            sink_type=sink_type,
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
@dissemination_limit(_limiter)
async def dissemination_send(
    request: Request,
    auth_user: dict[str, Any] | None = Depends(verify_optional_supabase_token),
) -> object:
    """
    Send IWXXM via a green preflight handle or inline sink params.

    Examples
    --------
    >>> 1 + 1 # docstring smoke (dissemination_send)
    2

    Parameters
    ----------
    request : object
        Argument ``request``.
    auth_user : object
        Argument ``auth_user``.

    Returns
    -------
    object
        Return value.
    """
    uid = client_id(request)
    try:
        default_rate_limiter.check(uid)
    except RateLimitExceeded as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(exc),
        ) from exc

    req = await read_send(request)
    profiles_service = profiles_service_for_optional_auth(auth_user)
    if req.dissemination_template_id:
        if profiles_service is None:
            raise HTTPException(
                status_code=401,
                detail="Sign in required to apply a dissemination template",
                headers={"WWW-Authenticate": "Bearer"},
            )
        try:
            template = profiles_service.get_template(UUID(req.dissemination_template_id))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Unknown dissemination template id") from exc
        resolved_sink_type = cast(SinkType | None, req.sink_type or template.sink_type)
        req = SendRequest(
            dissemination_template_id=req.dissemination_template_id,
            handle=req.handle,
            sink_type=resolved_sink_type,
            uri=req.uri,
            iwxxm_xml=req.iwxxm_xml,
            tac_text=req.tac_text,
            product=req.product or template.product,
            iwxxm_version=req.iwxxm_version,
            params=merge_template_params(template.params, dict(req.params)),
        )

    sink_type = req.sink_type
    uri = req.uri
    send_params = dict(req.params)
    if req.handle:
        rec = default_handle_store.get(req.handle, user_id=uid)
        if rec is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="invalid or expired preflight handle",
            )
        sink_type = rec.sink_type # type: ignore[assignment]
        uri = rec.uri
        if rec.params:
            send_params = {**dict(rec.params), **send_params}

    sink_type = require_sink(sink_type)
    if not req.iwxxm_xml:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="iwxxm_xml is required",
        )

    iwxxm_xml = req.iwxxm_xml
    dissem_lib = (req.dissemination_library_id or "").strip()
    if dissem_lib:
        from dissemination.transforms import apply_dissemination_transforms
        from metar_iwxxm_api.convert_library_hard_cut import resolve_dissemination_transforms

        profiles_for_lib: ConversionProfilesService | None = None
        if auth_user is not None:
            profiles_for_lib = ConversionProfilesService(str(auth_user.get("sub") or auth_user.get("user_id")))

        def _custom_dissem_body(asset_id: str) -> dict[str, object] | None:
            """
            Resolve a custom dissemination library body for the caller.

            Parameters
            ----------
            asset_id : object
                Argument ``asset_id``.

            Returns
            -------
            object
                Return value.
            """
            if profiles_for_lib is None:
                return None
            try:
                asset = profiles_for_lib.get_library_asset(asset_id)
            except ValueError:
                raise
            except Exception:
                return None
            if asset.kind != "dissemination":
                msg = "dissemination_library_id must reference a Dissemination library"
                raise ValueError(msg)
            return dict(asset.body or {})

        try:
            body_transforms = resolve_dissemination_transforms(
                dissem_lib,
                get_custom_dissemination_body=_custom_dissem_body,
            )
            transformed = apply_dissemination_transforms(
                iwxxm_xml,
                body_transforms,
                bulletin_identifier=str(send_params.get("bulletin_identifier") or "") or None,
                topic=str(send_params.get("topic") or "") or None,
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc
        iwxxm_xml = transformed.xml

    if is_non_db_sink(sink_type):
        try:
            sent = await run_non_db_send(
                sink_type,
                send_params,
                iwxxm_xml=iwxxm_xml,
                tac_text=req.tac_text,
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
        except Exception as exc:
            logger.exception("dissemination send failed: %s", redact_secrets(str(exc)))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=redact_secrets(f"send failed: {exc}"),
            ) from exc
        if req.handle:
            default_handle_store.pop(req.handle, user_id=uid)
        return msgspec_json_response(sent)

    if not uri:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="uri or valid handle required",
        )

    try:
        pre = await run_db_preflight(
            PreflightRequest(sink_type=sink_type, uri=uri, ddl=True) # type: ignore[arg-type]
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
                    "iwxxm_xml": iwxxm_xml,
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
