"""TC-F17-001 - staging wis2box harness publish (T3.4 / UJ-028).

Requires the Compose wis2box profile (MQTT + HTTP dataset). Started by
``scripts/ci/run_wis2box_harness.sh`` or by the module fixture when Docker is available.
"""

from __future__ import annotations

import asyncio
import json
import os
import shutil
import subprocess
import urllib.error
import urllib.request
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import pytest
from dissemination.allowlist import parse_allowlist
from dissemination.transports import AiomqttClient, HttpxDatasetClient
from dissemination.wis2 import Wis2Params, wis2_preflight, wis2_publish

pytestmark = pytest.mark.integration

_ROOT = Path(__file__).resolve().parents[3]
_HTTP_PORT = int(os.environ.get("WIS2BOX_HTTP_HOST_PORT", "9080"))
_MQTT_PORT = int(os.environ.get("WIS2BOX_MQTT_HOST_PORT", "1883"))
_TOPIC = "origin/a/wis2/test-centre/data/core/weather/aviation/metar"


def _docker_available() -> bool:
    if not shutil.which("docker"):
        return False
    try:
        subprocess.run(
            ["docker", "info"],
            check=True,
            capture_output=True,
            timeout=15,
        )
        return True
    except (OSError, subprocess.SubprocessError, subprocess.TimeoutExpired):
        return False


def _harness_healthy() -> bool:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{_HTTP_PORT}/health", timeout=2) as resp:
            return resp.status == 200
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


@contextmanager
def _ensure_wis2box_harness() -> Iterator[None]:
    """Bring up Compose wis2box if not already healthy; leave external harness alone."""
    if _harness_healthy():
        yield
        return
    if not _docker_available():
        pytest.skip("Docker required for wis2box Compose harness (T3.4 / TC-F17-001)")

    compose = [
        "docker",
        "compose",
        "-f",
        str(_ROOT / "docker-compose.yml"),
        "-f",
        str(_ROOT / "docker-compose.wis2box.yml"),
        "--profile",
        "wis2box",
    ]
    subprocess.run(
        [*compose, "up", "-d", "--build", "--wait", "wis2box"],
        check=True,
        cwd=_ROOT,
        timeout=180,
    )
    try:
        if not _harness_healthy():
            pytest.fail("wis2box harness did not become healthy after compose up")
        yield
    finally:
        if os.environ.get("WIS2BOX_HARNESS_EXTERNAL") != "1":
            subprocess.run(
                [*compose, "stop", "wis2box"],
                check=False,
                cwd=_ROOT,
                timeout=60,
            )
            subprocess.run(
                [*compose, "rm", "-f", "wis2box"],
                check=False,
                cwd=_ROOT,
                timeout=60,
            )


@pytest.fixture
def wis2box_harness() -> Iterator[None]:
    with _ensure_wis2box_harness():
        yield


def _params() -> Wis2Params:
    return Wis2Params(
        mqtt_host="127.0.0.1",
        mqtt_port=_MQTT_PORT,
        mqtt_topic=_TOPIC,
        dataset_url=f"http://127.0.0.1:{_HTTP_PORT}/datasets/t34-metar.xml",
        centre_id="test-centre",
        use_tls=False,
    )


def _allowlist():
    # Literal loopback IP + CIDR for DNS-rebinding guard (ADR-029).
    return parse_allowlist("127.0.0.1,127.0.0.0/8,localhost,wis2box")


@pytest.mark.asyncio
async def test_wis2_harness_preflight_and_publish_retrievable(wis2box_harness: None) -> None:
    """MQTT notify + HTTP dataset retrievable against Compose harness (TC-F17-001)."""
    params = _params()
    allowlist = _allowlist()
    http = HttpxDatasetClient(timeout_s=10.0)
    mqtt = AiomqttClient(
        host=params.mqtt_host,
        port=params.mqtt_port,
        username=params.mqtt_username,
        password=params.mqtt_password,
    )

    received: asyncio.Queue[bytes] = asyncio.Queue()

    async def _subscribe() -> None:
        sub = AiomqttClient(
            host=params.mqtt_host,
            port=params.mqtt_port,
        )
        await sub.connect()
        try:
            await sub.subscribe(params.mqtt_topic)
            msg = await sub.recv(timeout_s=15.0)
            await received.put(msg)
        finally:
            await sub.disconnect()

    sub_task = asyncio.create_task(_subscribe())
    await asyncio.sleep(0.3)  # allow subscribe to land before publish

    pre = await wis2_preflight(params, allowlist=allowlist, mqtt=mqtt, http=http)
    assert pre.ok is True
    assert pre.connectivity_ok is True

    xml = b'<?xml version="1.0"?><iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/3.0">T34</iwxxm:METAR>'
    result = await wis2_publish(
        params,
        iwxxm_xml=xml,
        allowlist=allowlist,
        mqtt=mqtt,
        http=http,
    )
    assert result.ok is True
    assert result.dataset_url == params.dataset_url
    assert result.mqtt_topic == params.mqtt_topic

    got = await http.get_dataset(params.dataset_url)
    assert got == xml

    payload = await asyncio.wait_for(received.get(), timeout=15.0)
    await sub_task
    note = json.loads(payload.decode("utf-8"))
    assert note["type"] == "Feature"
    assert note["links"][0]["href"] == params.dataset_url
