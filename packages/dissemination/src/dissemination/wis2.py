"""WIS2 sink adapter — MQTT notification + HTTP dataset (F17 / E14-09).

Transports are injected (Protocols) so unit tests mock MQTT/HTTP without a live
broker. Compose wis2box wiring lands in T3.3–T3.4; live BYOC remains cycle-close.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Protocol
from urllib.parse import urlparse
from uuid import uuid4

from dissemination.allowlist import Allowlist, EgressDenied, validate_egress_host
from dissemination.models import PreflightResponse
from dissemination.redact import redact_secrets


class MqttClient(Protocol):
    """Minimal async MQTT client used by the WIS2 sink."""

    async def connect(self) -> None: ...

    async def publish(self, topic: str, payload: bytes) -> None: ...

    async def disconnect(self) -> None: ...


class HttpDatasetClient(Protocol):
    """Minimal async HTTP client for dataset PUT/GET/ping."""

    async def ping(self, url: str) -> bool: ...

    async def put_dataset(self, url: str, body: bytes, content_type: str) -> int: ...

    async def get_dataset(self, url: str) -> bytes: ...


@dataclass(frozen=True, slots=True)
class Wis2Params:
    """BYOC WIS2 endpoint parameters (memory-only; never logged raw)."""

    mqtt_host: str
    mqtt_topic: str
    dataset_url: str
    mqtt_port: int = 8883
    centre_id: str | None = None
    mqtt_username: str | None = None
    mqtt_password: str | None = None
    use_tls: bool = True


@dataclass(frozen=True, slots=True)
class Wis2PublishResult:
    """Result of a WIS2 publish (MQTT notify + HTTP dataset)."""

    ok: bool
    dataset_url: str
    mqtt_topic: str
    detail: str | None = None


def _dataset_hostname(dataset_url: str) -> str:
    host = urlparse(dataset_url).hostname
    if not host:
        raise ValueError("dataset_url must include a hostname")
    return host


def _validate_wis2_egress(params: Wis2Params, allowlist: Allowlist) -> None:
    validate_egress_host(params.mqtt_host, allowlist=allowlist)
    validate_egress_host(_dataset_hostname(params.dataset_url), allowlist=allowlist)


def _redact_exc(exc: BaseException, params: Wis2Params) -> str:
    text = redact_secrets(str(exc))
    if params.mqtt_password:
        text = text.replace(params.mqtt_password, "REDACTED")
    if params.mqtt_username:
        text = text.replace(params.mqtt_username, "REDACTED")
    return text


def build_wis2_notification(
    params: Wis2Params,
    *,
    content_type: str = "application/xml",
) -> dict[str, object]:
    """
    Build a minimal WIS Notification Message–shaped JSON dict.

    Parameters
    ----------
    params :
        WIS2 BYOC parameters (topic + canonical dataset URL).
    content_type :
        Media type for the canonical link.

    Returns
    -------
    dict[str, object]
        JSON-serializable notification (no credentials).
    """
    centre = params.centre_id or "unknown"
    data_id = f"wis2/{centre}/{uuid4().hex}"
    return {
        "type": "Feature",
        "conformsTo": ["http://wis.wmo.int/spec/wnm/1/conf/core"],
        "properties": {
            "data_id": data_id,
            "pubtime": None,
        },
        "links": [
            {
                "rel": "canonical",
                "type": content_type,
                "href": params.dataset_url,
            }
        ],
    }


async def wis2_preflight(
    params: Wis2Params,
    *,
    allowlist: Allowlist,
    mqtt: MqttClient,
    http: HttpDatasetClient,
) -> PreflightResponse:
    """
    Check allowlist + MQTT connect + HTTP dataset reachability.

    Raises
    ------
    EgressDenied
        When MQTT or dataset hosts are not allowlisted.
    ValueError
        When transport checks fail (secrets redacted).
    """
    _validate_wis2_egress(params, allowlist)
    try:
        await mqtt.connect()
        try:
            reachable = await http.ping(params.dataset_url)
        finally:
            await mqtt.disconnect()
    except Exception as exc:
        raise ValueError(_redact_exc(exc, params)) from exc

    if not reachable:
        return PreflightResponse(
            ok=False,
            connectivity_ok=False,
            diffs=[],
            detail="dataset HTTP ping failed",
        )
    return PreflightResponse(
        ok=True,
        connectivity_ok=True,
        diffs=[],
        detail=None,
    )


async def wis2_publish(
    params: Wis2Params,
    *,
    iwxxm_xml: bytes | str,
    allowlist: Allowlist,
    mqtt: MqttClient,
    http: HttpDatasetClient,
    content_type: str = "application/xml",
) -> Wis2PublishResult:
    """
    PUT IWXXM dataset over HTTP, then publish MQTT notification with canonical link.

    Raises
    ------
    EgressDenied
        When MQTT or dataset hosts are not allowlisted.
    ValueError
        When transport fails (secrets redacted).
    """
    _validate_wis2_egress(params, allowlist)
    body = iwxxm_xml.encode("utf-8") if isinstance(iwxxm_xml, str) else iwxxm_xml
    try:
        status = await http.put_dataset(params.dataset_url, body, content_type)
        if status >= 400:
            raise ValueError(f"dataset PUT failed with HTTP {status}")
        notification = build_wis2_notification(params, content_type=content_type)
        payload = json.dumps(notification, separators=(",", ":")).encode("utf-8")
        await mqtt.connect()
        try:
            await mqtt.publish(params.mqtt_topic, payload)
        finally:
            await mqtt.disconnect()
    except EgressDenied:
        raise
    except Exception as exc:
        if isinstance(exc, ValueError) and "dataset PUT failed" in str(exc):
            raise
        raise ValueError(_redact_exc(exc, params)) from exc

    return Wis2PublishResult(
        ok=True,
        dataset_url=params.dataset_url,
        mqtt_topic=params.mqtt_topic,
        detail=None,
    )


__all__ = [
    "HttpDatasetClient",
    "MqttClient",
    "Wis2Params",
    "Wis2PublishResult",
    "build_wis2_notification",
    "wis2_preflight",
    "wis2_publish",
]
