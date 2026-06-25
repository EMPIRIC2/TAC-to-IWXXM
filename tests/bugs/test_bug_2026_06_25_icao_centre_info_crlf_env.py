"""BUG-2026-06-25 — /api/v1/translation/centre-info 500 on CRLF .env values.

A CRLF-encoded ``.env`` leaves a trailing carriage return on every value
(e.g. ``SERVICE_ONLINE_SINCE='2026-01-01T00:00:00Z\\r'``). The router parsed it
with ``datetime.fromisoformat(value.replace("Z", "+00:00"))`` →
``ValueError: Invalid isoformat string: '2026-01-01T00:00:00+00:00\\r'`` (HTTP 500),
and ``ICAO_LOCATION_INDICATOR='TEST\\r'`` (len 5) broke the 4-char length check.

Fix: ``src.config.icao_opmet._clean_env`` strips surrounding whitespace (incl. CR)
when reading Translation Centre env vars.
"""

from __future__ import annotations

import importlib
import os
from datetime import datetime


def test_clean_env_strips_trailing_cr(monkeypatch) -> None:
    from src.config import icao_opmet as cfg

    monkeypatch.setenv("METAR_CRLF_PROBE", "value\r")
    assert cfg._clean_env("METAR_CRLF_PROBE") == "value"

    monkeypatch.setenv("METAR_CRLF_PROBE", "  \r\n")
    assert cfg._clean_env("METAR_CRLF_PROBE") is None

    monkeypatch.delenv("METAR_CRLF_PROBE", raising=False)
    assert cfg._clean_env("METAR_CRLF_PROBE") is None


def test_centre_info_tolerates_crlf_env() -> None:
    """Config values from a CRLF .env must be stripped and remain parseable."""
    from src.config import icao_opmet as cfg

    keys = [
        "SERVICE_ONLINE_SINCE",
        "ICAO_LOCATION_INDICATOR",
        "TRANSLATION_CENTRE_DESIGNATOR",
    ]
    saved = {k: os.environ.get(k) for k in keys}
    try:
        os.environ["SERVICE_ONLINE_SINCE"] = "2026-01-01T00:00:00Z\r"
        os.environ["ICAO_LOCATION_INDICATOR"] = "TEST\r"
        os.environ["TRANSLATION_CENTRE_DESIGNATOR"] = "TEST\r"
        importlib.reload(cfg)

        info = cfg.get_translation_centre_info()
        assert info["serviceOnlineSince"] == "2026-01-01T00:00:00Z"
        assert info["icaoLocationIndicator"] == "TEST"
        assert len(info["icaoLocationIndicator"]) == 4
        # The exact call the router makes must not raise.
        datetime.fromisoformat(info["serviceOnlineSince"].replace("Z", "+00:00"))
    finally:
        for key, value in saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        importlib.reload(cfg)
