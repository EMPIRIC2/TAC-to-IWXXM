"""Parse memory-only BYOC JSON into WIS2 / EDIS / F19 param models."""

from __future__ import annotations

from typing import Any

from dissemination.edis import EdisParams
from dissemination.f19_stubs import F19Params
from dissemination.wis2 import Wis2Params


def _str_param(params: dict[str, Any], *keys: str, default: str | None = None) -> str | None:
    """Return the first non-empty string among ``keys``."""
    for key in keys:
        raw = params.get(key)
        if raw is None:
            continue
        text = str(raw).strip()
        if text:
            return text
    return default


def _int_param(params: dict[str, Any], *keys: str, default: int) -> int:
    """Return the first parseable int among ``keys``, else ``default``."""
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
    """Return the first bool-like value among ``keys``, else ``default``."""
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
    """Build ``Wis2Params`` from free-form BYOC JSON."""
    host = _str_param(params, "mqtt_host", "broker", "host")
    topic = _str_param(params, "mqtt_topic", "topic")
    dataset = _str_param(params, "dataset_url", "dataset", "url")
    if not host or not topic or not dataset:
        raise ValueError(
            "wis2 params require mqtt_host (or broker), mqtt_topic (or topic), "
            "and dataset_url (or dataset)"
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
    """Build ``EdisParams`` from free-form BYOC JSON."""
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
    """Build ``F19Params`` for AMHS / SWIM / AFS staging stubs."""
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


__all__ = [
    "edis_params_from_request",
    "f19_params_from_request",
    "wis2_params_from_request",
]
