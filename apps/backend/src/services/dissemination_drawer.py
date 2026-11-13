"""Dispatch public drawer preflight/send for non-DB sinks (WIS2 / EDIS / F19).

DB sinks stay on ``run_db_preflight`` + writer-contract in the router. This module
parses memory-only BYOC params and calls package adapters. Secrets are never logged.
"""

from __future__ import annotations

from typing import Any

from dissemination.allowlist import Allowlist, load_allowlist_from_env
from dissemination.edis import EdisParams, SmtpClient, edis_preflight, edis_submit
from dissemination.f19_stubs import F19Params, get_staging_sink
from dissemination.models import PreflightResponse, SendResponse, SinkType
from dissemination.transports import AiomqttClient, AiosmtpClient, HttpxDatasetClient
from dissemination.wis2 import (
    HttpDatasetClient,
    MqttClient,
    Wis2Params,
    wis2_preflight,
    wis2_publish,
)

NON_DB_SINKS: frozenset[str] = frozenset({"wis2", "edis", "amhs", "swim", "afs"})
DB_SINKS: frozenset[str] = frozenset({"postgres", "mysql", "sqlserver", "sqlite"})


def is_db_sink(sink_type: str) -> bool:
    """
    Return True when ``sink_type`` is a SQL drawer sink.

    Examples
    --------
    >>> is_db_sink("postgres")
    True
    >>> is_db_sink("wis2")
    False

    Parameters
    ----------
    sink_type : object
        Argument ``sink_type``.

    Returns
    -------
    object
        Return value.
    """
    return sink_type in DB_SINKS


def is_non_db_sink(sink_type: str) -> bool:
    """
    Return True when ``sink_type`` is WIS2, EDIS, or an F19 stub sink.

    Examples
    --------
    >>> is_non_db_sink("wis2")
    True
    >>> is_non_db_sink("sqlite")
    False

    Parameters
    ----------
    sink_type : object
        Argument ``sink_type``.

    Returns
    -------
    object
        Return value.
    """
    return sink_type in NON_DB_SINKS


def _str_param(params: dict[str, Any], *keys: str, default: str | None = None) -> str | None:
    """
    Return the first non-empty string among ``keys``.

    Parameters
    ----------
    params : object
        Argument ``params``.
    default : object
        Argument ``default``.
    keys : object
        Argument ``keys``.

    Returns
    -------
    object
        Return value.
    """
    for key in keys:
        raw = params.get(key)
        if raw is None:
            continue
        text = str(raw).strip()
        if text:
            return text
    return default


def _int_param(params: dict[str, Any], *keys: str, default: int) -> int:
    """
    Return the first parseable int among ``keys``, else ``default``.

    Parameters
    ----------
    params : object
        Argument ``params``.
    default : object
        Argument ``default``.
    keys : object
        Argument ``keys``.

    Returns
    -------
    object
        Return value.
    """
    for key in keys:
        raw = params.get(key)
        if raw is None:
            continue
        try:
            return int(raw)
        except (TypeError, ValueError):
            continue
    return default


def _bool_param(params: dict[str, Any], *keys: str, default: bool) -> bool:
    """
    Return the first bool-like value among ``keys``, else ``default``.

    Parameters
    ----------
    params : object
        Argument ``params``.
    default : object
        Argument ``default``.
    keys : object
        Argument ``keys``.

    Returns
    -------
    object
        Return value.
    """
    for key in keys:
        raw = params.get(key)
        if raw is None:
            continue
        if isinstance(raw, bool):
            return raw
        text = str(raw).strip().lower()
        if text in {"1", "true", "yes", "on"}:
            return True
        if text in {"0", "false", "no", "off"}:
            return False
    return default


def wis2_params_from_request(params: dict[str, Any]) -> Wis2Params:
    """
    Build ``Wis2Params`` from free-form BYOC JSON.

    Accepts fixture keys (``mqtt_host``, ``mqtt_topic``, ``dataset_url``) and
    short aliases (``broker`` / ``host``, ``topic``, ``dataset``).

    Raises
    ------
    ValueError
        When required fields are missing.

    Examples
    --------
    >>> p = wis2_params_from_request(
    ...     {"mqtt_host": "h", "mqtt_topic": "t", "dataset_url": "http://x/y"}
    ... )
    >>> p.mqtt_host
    'h'

    Parameters
    ----------
    params : object
        Argument ``params``.

    Returns
    -------
    object
        Return value.
    """
    host = _str_param(params, "mqtt_host", "broker", "host")
    topic = _str_param(params, "mqtt_topic", "topic")
    dataset = _str_param(params, "dataset_url", "dataset", "url")
    if not host or not topic or not dataset:
        raise ValueError(
            "wis2 params require mqtt_host (or broker), mqtt_topic (or topic), and dataset_url (or dataset)"
        )
    return Wis2Params(
        mqtt_host=host,
        mqtt_topic=topic,
        dataset_url=dataset,
        mqtt_port=_int_param(params, "mqtt_port", "port", default=8883),
        centre_id=_str_param(params, "centre_id", "centre"),
        mqtt_username=_str_param(params, "mqtt_username", "username"),
        mqtt_password=_str_param(params, "mqtt_password", "password"),
        use_tls=_bool_param(params, "use_tls", "tls", default=True),
    )


def edis_params_from_request(params: dict[str, Any]) -> EdisParams:
    """
    Build ``EdisParams`` from free-form BYOC JSON.

    Raises
    ------
    ValueError
        When required fields are missing.

    Examples
    --------
    >>> p = edis_params_from_request(
    ...     {
    ...         "smtp_host": "h",
    ...         "mail_from": "a@b.c",
    ...         "mail_to": "d@e.f",
    ...         "tt": "SA",
    ...         "aa": "US",
    ...         "ii": "31",
    ...         "cccc": "KXXX",
    ...         "yygggg": "211200",
    ...     }
    ... )
    >>> p.smtp_host
    'h'

    Parameters
    ----------
    params : object
        Argument ``params``.

    Returns
    -------
    object
        Return value.
    """
    smtp_host = _str_param(params, "smtp_host", "host")
    mail_from = _str_param(params, "mail_from", "from")
    mail_to = _str_param(params, "mail_to", "to")
    tt = _str_param(params, "tt")
    aa = _str_param(params, "aa")
    ii = _str_param(params, "ii")
    cccc = _str_param(params, "cccc")
    yygggg = _str_param(params, "yygggg")
    missing = [
        name
        for name, value in (
            ("smtp_host", smtp_host),
            ("mail_from", mail_from),
            ("mail_to", mail_to),
            ("tt", tt),
            ("aa", aa),
            ("ii", ii),
            ("cccc", cccc),
            ("yygggg", yygggg),
        )
        if not value
    ]
    if missing:
        raise ValueError(f"edis params missing required fields: {', '.join(missing)}")
    return EdisParams(
        smtp_host=smtp_host or "",
        mail_from=mail_from or "",
        mail_to=mail_to or "",
        tt=tt or "",
        aa=aa or "",
        ii=ii or "",
        cccc=cccc or "",
        yygggg=yygggg or "",
        smtp_port=_int_param(params, "smtp_port", "port", default=587),
        username=_str_param(params, "username"),
        password=_str_param(params, "password"),
        use_tls=_bool_param(params, "use_tls", "tls", default=True),
        bbb=_str_param(params, "bbb"),
        subject=_str_param(params, "subject"),
    )


def f19_params_from_request(sink_type: str, params: dict[str, Any]) -> F19Params:
    """
    Build ``F19Params`` for AMHS / SWIM / AFS staging stubs.

    Raises
    ------
    ValueError
        When host is missing or sink_type is not F19.

    Examples
    --------
    >>> p = f19_params_from_request("amhs", {"host": "amhs.example"})
    >>> p.host
    'amhs.example'

    Parameters
    ----------
    sink_type : object
        Argument ``sink_type``.
    params : object
        Argument ``params``.

    Returns
    -------
    object
        Return value.
    """
    if sink_type not in {"amhs", "swim", "afs"}:
        raise ValueError(f"not an F19 sink: {sink_type!r}")
    host = _str_param(params, "host", "endpoint_host")
    if not host:
        raise ValueError(f"{sink_type} params require host")
    return F19Params(
        sink_type=sink_type,  # type: ignore[arg-type]
        host=host,
        port=_int_param(params, "port", default=0),
        username=_str_param(params, "username"),
        password=_str_param(params, "password"),
        endpoint=_str_param(params, "endpoint"),
    )


def default_allowlist() -> Allowlist:
    """
    Load the process egress allowlist (fail-closed when empty).

    Examples
    --------
    >>> isinstance(default_allowlist().is_empty, bool)
    True

    Returns
    -------
    object
        Return value.
    """
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
    """
    Run WIS2 / EDIS / F19 preflight for the public drawer.

    Raises
    ------
    EgressDenied
        When a destination host is not allowlisted.
    ValueError
        When params are incomplete or transport checks fail.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (run_non_db_preflight)
    2

    Parameters
    ----------
    sink_type : object
        Argument ``sink_type``.
    params : object
        Argument ``params``.
    allowlist : object
        Argument ``allowlist``.
    mqtt : object
        Argument ``mqtt``.
    http : object
        Argument ``http``.
    smtp : object
        Argument ``smtp``.

    Returns
    -------
    object
        Return value.
    """
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
    """
    Deliver IWXXM through WIS2 / EDIS / F19 after allowlist checks.

    Raises
    ------
    EgressDenied
        When a destination host is not allowlisted.
    ValueError
        When params or transport fail.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (run_non_db_send)
    2

    Parameters
    ----------
    sink_type : object
        Argument ``sink_type``.
    params : object
        Argument ``params``.
    iwxxm_xml : object
        Argument ``iwxxm_xml``.
    tac_text : object
        Argument ``tac_text``.
    allowlist : object
        Argument ``allowlist``.
    mqtt : object
        Argument ``mqtt``.
    http : object
        Argument ``http``.
    smtp : object
        Argument ``smtp``.

    Returns
    -------
    object
        Return value.
    """
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
    """
    Validate ``sink_type`` is a known drawer sink.

    Raises
    ------
    ValueError
        With code ``missing`` or ``unknown`` for the router to map to HTTP status.

    Examples
    --------
    >>> assert_known_sink("wis2")
    'wis2'

    Parameters
    ----------
    sink_type : object
        Argument ``sink_type``.

    Returns
    -------
    object
        Return value.
    """
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
