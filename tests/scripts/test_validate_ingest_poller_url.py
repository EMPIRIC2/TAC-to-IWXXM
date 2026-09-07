"""Coverage for scripts/deploy/validate_ingest_poller_url.py."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
import scripts.deploy.validate_ingest_poller_url as poller_cli


@pytest.mark.unit
def test_print_fixture(capsys: pytest.CaptureFixture[str]) -> None:
    with patch("sys.argv", ["prog", "--print-fixture"]):
        assert poller_cli.main() == 0
    assert "raw.githubusercontent.com" in capsys.readouterr().out


@pytest.mark.unit
def test_invalid_url(capsys: pytest.CaptureFixture[str]) -> None:
    with patch("sys.argv", ["prog", "http://bad"]):
        assert poller_cli.main() == 2
    assert "ERROR:" in capsys.readouterr().err


@pytest.mark.unit
def test_ok_without_probe(capsys: pytest.CaptureFixture[str]) -> None:
    url = "https://example.com/feed.json"
    with patch("sys.argv", ["prog", url]):
        assert poller_cli.main() == 0
    assert f"OK: {url}" in capsys.readouterr().out


@pytest.mark.unit
def test_probe_dict_items(capsys: pytest.CaptureFixture[str]) -> None:
    url = "https://example.com/feed.json"
    payload = json.dumps({"items": [{"id": 1}, {"id": 2}]}).encode()
    resp = MagicMock()
    resp.read.return_value = payload
    resp.__enter__ = MagicMock(return_value=resp)
    resp.__exit__ = MagicMock(return_value=False)
    with (
        patch("sys.argv", ["prog", url, "--probe"]),
        patch("scripts.deploy.validate_ingest_poller_url.urlopen", return_value=resp),
    ):
        assert poller_cli.main() == 0
    assert "probe items=2" in capsys.readouterr().out


@pytest.mark.unit
def test_probe_list_payload(capsys: pytest.CaptureFixture[str]) -> None:
    url = "https://example.com/feed.json"
    payload = json.dumps([{"id": 1}]).encode()
    resp = MagicMock()
    resp.read.return_value = payload
    resp.__enter__ = MagicMock(return_value=resp)
    resp.__exit__ = MagicMock(return_value=False)
    with (
        patch("sys.argv", ["prog", url, "--probe"]),
        patch("scripts.deploy.validate_ingest_poller_url.urlopen", return_value=resp),
    ):
        assert poller_cli.main() == 0
    assert "probe items=1" in capsys.readouterr().out


@pytest.mark.unit
def test_probe_invalid_shape(capsys: pytest.CaptureFixture[str]) -> None:
    url = "https://example.com/feed.json"
    payload = json.dumps({"nope": []}).encode()
    resp = MagicMock()
    resp.read.return_value = payload
    resp.__enter__ = MagicMock(return_value=resp)
    resp.__exit__ = MagicMock(return_value=False)
    with (
        patch("sys.argv", ["prog", url, "--probe"]),
        patch("scripts.deploy.validate_ingest_poller_url.urlopen", return_value=resp),
    ):
        assert poller_cli.main() == 2
    assert "feed must be JSON list" in capsys.readouterr().err


@pytest.mark.unit
def test_probe_dict_items_not_list(capsys: pytest.CaptureFixture[str]) -> None:
    url = "https://example.com/feed.json"
    payload = json.dumps({"items": "not-a-list"}).encode()
    resp = MagicMock()
    resp.read.return_value = payload
    resp.__enter__ = MagicMock(return_value=resp)
    resp.__exit__ = MagicMock(return_value=False)
    with (
        patch("sys.argv", ["prog", url, "--probe"]),
        patch("scripts.deploy.validate_ingest_poller_url.urlopen", return_value=resp),
    ):
        assert poller_cli.main() == 0
    assert "probe items=?" in capsys.readouterr().out


@pytest.mark.unit
def test_probe_json_decode_error(capsys: pytest.CaptureFixture[str]) -> None:
    url = "https://example.com/feed.json"
    resp = MagicMock()
    resp.read.return_value = b"not-json"
    resp.__enter__ = MagicMock(return_value=resp)
    resp.__exit__ = MagicMock(return_value=False)
    with (
        patch("sys.argv", ["prog", url, "--probe"]),
        patch("scripts.deploy.validate_ingest_poller_url.urlopen", return_value=resp),
    ):
        assert poller_cli.main() == 2
    assert "probe failed" in capsys.readouterr().err

    from urllib.error import URLError

    url = "https://example.com/feed.json"
    with (
        patch("sys.argv", ["prog", url, "--probe"]),
        patch(
            "scripts.deploy.validate_ingest_poller_url.urlopen",
            side_effect=URLError("down"),
        ),
    ):
        assert poller_cli.main() == 2
    assert "probe failed" in capsys.readouterr().err
