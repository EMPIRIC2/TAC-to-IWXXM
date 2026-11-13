"""Dispatch public drawer preflight/send for non-DB sinks (WIS2 / EDIS / F19).

DB sinks stay on ``run_db_preflight`` + writer-contract in the router. This module
parses memory-only BYOC params and calls package adapters. Secrets are never logged.
"""

from __future__ import annotations

from typing import Any

from dissemination.allowlist import Allowlist, load_allowlist_from_env
from dissemination.edis import SmtpClient, edis_preflight, edis_submit
from dissemination.f19_stubs import get_staging_sink
from dissemination.models import PreflightResponse, SendResponse, SinkType
from dissemination.transports import AiomqttClient, AiosmtpClient, HttpxDatasetClient
from dissemination.wis2 import (
    HttpDatasetClient,
    MqttClient,
    wis2_preflight,
    wis2_publish,
)

from .dissemination_drawer_params import (
    edis_params_from_request,
    f19_params_from_request,
    wis2_params_from_request,
)

NON_DB_SINKS: frozenset[str] = frozenset({"wis2", "edis", "amhs", "swim", "afs"})
DB_SINKS: frozenset[str] = frozenset({"postgres", "mysql", "sqlserver", "sqlite"})


def is_db_sink(sink_type: str) -> bool:
    """Return True when ``sink_type`` is a SQL drawer sink."""
    return sink_type in DB_SINKS


def is_non_db_sink(sink_type: str) -> bool:
    """Return True when ``sink_type`` is WIS2, EDIS, or an F19 stub sink."""
    return sink_type in NON_DB_SINKS


def default_allowlist() -> Allowlist:
    """Load the process egress allowlist (fail-closed when empty)."""
    return load_allowlist_from_env()


async def run_non_db_preflight(
    sink_type: str,
    params: dict[str, Any],
    *,
    allowlist: Allowlist | None = None,
    mqtt: MqttClient | None = None,
    http: HttpDatasetClient | None = None,
    smtp: SmtpClient | None = None,
) -> PreflightResponse:
    """Run WIS2 / EDIS / F19 preflight for the public drawer."""
    allow = allowlist if allowlist is not None else default_allowlist()
    if sink_type == "wis2":
        wis2 = wis2_params_from_request(params)
        mqtt_client = mqtt or AiomqttClient(
            host=wis2.mqtt_host,
            port=wis2.mqtt_port,
            username=wis2.mqtt_username,
            password=wis2.mqtt_password,
        )
        http_client = http or HttpxDatasetClient()
        return await wis2_preflight(wis2, allowlist=allow, mqtt=mqtt_client, http=http_client)
    if sink_type == "edis":
        edis = edis_params_from_request(params)
        smtp_client = smtp or AiosmtpClient(
            hostname=edis.smtp_host,
            port=edis.smtp_port,
            use_tls=edis.use_tls,
        )
        return await edis_preflight(edis, allowlist=allow, smtp=smtp_client)
    if sink_type in {"amhs", "swim", "afs"}:
        f19 = f19_params_from_request(sink_type, params)
        adapter = get_staging_sink(sink_type)
        return await adapter.preflight(params=f19, allowlist=allow)
    raise ValueError(f"unsupported non-DB sink: {sink_type!r}")


async def run_non_db_send(
    sink_type: str,
    params: dict[str, Any],
    *,
    iwxxm_xml: str,
    tac_text: str | None = None,
    allowlist: Allowlist | None = None,
    mqtt: MqttClient | None = None,
    http: HttpDatasetClient | None = None,
    smtp: SmtpClient | None = None,
) -> SendResponse:
    """Deliver IWXXM through WIS2 / EDIS / F19 after allowlist checks."""
    allow = allowlist if allowlist is not None else default_allowlist()
    if sink_type == "wis2":
        wis2 = wis2_params_from_request(params)
        mqtt_client = mqtt or AiomqttClient(
            host=wis2.mqtt_host,
            port=wis2.mqtt_port,
            username=wis2.mqtt_username,
            password=wis2.mqtt_password,
        )
        http_client = http or HttpxDatasetClient()
        result = await wis2_publish(
            wis2,
            iwxxm_xml=iwxxm_xml,
            allowlist=allow,
            mqtt=mqtt_client,
            http=http_client,
        )
        return SendResponse(ok=result.ok, kv_upload_key=None, detail=result.detail or "wis2 published")
    if sink_type == "edis":
        edis = edis_params_from_request(params)
        smtp_client = smtp or AiosmtpClient(
            hostname=edis.smtp_host,
            port=edis.smtp_port,
            use_tls=edis.use_tls,
        )
        result = await edis_submit(
            edis,
            tac_body=tac_text or iwxxm_xml,
            allowlist=allow,
            smtp=smtp_client,
        )
        detail = result.detail or "edis submitted"
        return SendResponse(ok=result.ok, kv_upload_key=None, detail=detail)
    if sink_type in {"amhs", "swim", "afs"}:
        f19 = f19_params_from_request(sink_type, params)
        adapter = get_staging_sink(sink_type)
        return await adapter.send(
            params=f19,
            allowlist=allow,
            iwxxm_xml=iwxxm_xml,
            tac_text=tac_text,
        )
    raise ValueError(f"unsupported non-DB sink: {sink_type!r}")


def assert_known_sink(sink_type: str | None) -> SinkType:
    """Validate ``sink_type`` is a known drawer sink."""
    if sink_type is None:
        raise ValueError("missing")
    if sink_type in DB_SINKS or sink_type in NON_DB_SINKS:
        return sink_type  # type: ignore[return-value]
    raise ValueError(f"unknown:{sink_type}")


__all__ = [
    "DB_SINKS",
    "NON_DB_SINKS",
    "assert_known_sink",
    "default_allowlist",
    "edis_params_from_request",
    "f19_params_from_request",
    "is_db_sink",
    "is_non_db_sink",
    "run_non_db_preflight",
    "run_non_db_send",
    "wis2_params_from_request",
]
