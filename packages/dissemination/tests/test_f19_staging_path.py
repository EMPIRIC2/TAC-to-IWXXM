"""TC-F19-001..003 — staging/test path green per F19 adapter (T5.3 / E14-09).

One case per AMHS / SWIM / AFS adapter with mocked (no-live) transport via the
staging stubs. Live F19 demos remain optional at cycle close (S-EV014-M2).
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from dissemination.allowlist import parse_allowlist
from dissemination.f19_stubs import F19Params, get_staging_sink


@pytest.fixture(autouse=True)
def _public_dns_for_example_hosts():
    with patch(
        "dissemination.allowlist.socket.getaddrinfo",
        return_value=[(None, None, None, None, ("8.8.8.8", 0))],
    ):
        yield


@pytest.mark.parametrize(
    ("tc_id", "sink_type"),
    [
        ("TC-F19-001", "amhs"),
        ("TC-F19-002", "swim"),
        ("TC-F19-003", "afs"),
    ],
)
@pytest.mark.asyncio
async def test_f19_staging_preflight_and_send_green(tc_id: str, sink_type: str) -> None:
    """Staging path: allowlisted preflight + send without live protocol egress."""
    del tc_id  # retained in parametrize id for test-plan traceability
    adapter = get_staging_sink(sink_type)
    params = F19Params(
        sink_type=sink_type,  # type: ignore[arg-type]
        host="f19-staging.example.test",
        port=443,
        username="byoc-user",
        password="byoc-secret",
        endpoint="/v1/submit",
    )
    allowlist = parse_allowlist("f19-staging.example.test")

    pre = await adapter.preflight(params=params, allowlist=allowlist)
    assert pre.ok is True
    assert pre.connectivity_ok is True

    send = await adapter.send(
        params=params,
        allowlist=allowlist,
        iwxxm_xml=b'<?xml version="1.0"?><iwxxm:METAR/>',
    )
    assert send.ok is True
    assert send.kv_upload_key is not None
    assert sink_type in send.kv_upload_key
    assert "staging" in send.kv_upload_key.lower() or (send.detail is not None and "staging" in send.detail.lower())
