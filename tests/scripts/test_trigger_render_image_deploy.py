"""EV-080 coverage fills for scripts/deploy/trigger_render_image_deploy.py."""

from __future__ import annotations

import json
import urllib.error
from unittest.mock import patch

import pytest
import scripts.deploy.trigger_render_image_deploy as deploy_mod
from scripts.deploy.trigger_render_image_deploy import (
    build_deploy_hook_url,
    is_suspended_deploy_block,
    main,
    resolve_service_id,
    service_id_from_deploy_hook,
    trigger_image_deploy,
    trigger_via_hook,
    trigger_via_rest,
)


def test_build_deploy_hook_url_branches() -> None:
    hook = "https://api.render.com/deploy/srv-abc?key=secret"
    assert build_deploy_hook_url(hook, None) == hook
    url = build_deploy_hook_url(hook, "ghcr.io/org/img:tag")
    assert "imgURL=" in url
    with pytest.raises(ValueError, match="non-empty"):
        build_deploy_hook_url("  ", "img")


def test_service_id_from_deploy_hook() -> None:
    assert (
        service_id_from_deploy_hook("https://api.render.com/deploy/srv-x?k=1")
        == "srv-x"
    )
    assert service_id_from_deploy_hook("https://example.com/deploy/not-srv") is None
    assert service_id_from_deploy_hook("https://example.com/no-deploy") is None


def test_default_http_success_and_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    class Resp:
        status = 200

        def read(self) -> bytes:
            return b"ok"

        def __enter__(self):
            return self

        def __exit__(self, *args: object) -> None:
            return None

    monkeypatch.setattr(deploy_mod.urllib.request, "urlopen", lambda *a, **k: Resp())
    assert deploy_mod._default_http("http://x", "GET", None, None) == (200, "ok")

    def raise_http(*_a: object, **_k: object) -> None:
        err = urllib.error.HTTPError("http://x", 503, "fail", {}, None)
        err.read = lambda: b"body"  # type: ignore[method-assign]
        raise err

    monkeypatch.setattr(deploy_mod.urllib.request, "urlopen", raise_http)
    status, body = deploy_mod._default_http("http://x", "GET", None, None)
    assert status == 503
    assert body == "body"

    def raise_url(*_a: object, **_k: object) -> None:
        raise urllib.error.URLError("timeout")

    monkeypatch.setattr(deploy_mod.urllib.request, "urlopen", raise_url)
    assert deploy_mod._default_http("http://x", "GET", None, None)[0] == 0


def test_resolve_service_id_branches() -> None:
    assert (
        resolve_service_id(
            deploy_hook="https://api.render.com/deploy/srv-hook?k=1",
            service_id="srv-explicit",
            service_name=None,
            api_key=None,
            http=lambda *_: (200, "[]"),
        )
        == "srv-explicit"
    )

    assert (
        resolve_service_id(
            deploy_hook="https://api.render.com/deploy/srv-hook?k=1",
            service_id=None,
            service_name=None,
            api_key=None,
            http=lambda *_: (200, "[]"),
        )
        == "srv-hook"
    )

    payload = json.dumps([{"service": {"name": "api", "id": "srv-found"}}])
    assert (
        resolve_service_id(
            deploy_hook="https://example.com/nope",
            service_id=None,
            service_name="api",
            api_key="key",
            http=lambda *_: (200, payload),
        )
        == "srv-found"
    )

    flat_payload = json.dumps([{"name": "flat", "id": "srv-flat"}])
    assert (
        resolve_service_id(
            deploy_hook="https://example.com/nope",
            service_id=None,
            service_name="flat",
            api_key="key",
            http=lambda *_: (200, flat_payload),
        )
        == "srv-flat"
    )

    assert (
        resolve_service_id(
            deploy_hook="https://example.com/nope",
            service_id=None,
            service_name="api",
            api_key="key",
            http=lambda *_: (404, ""),
        )
        is None
    )
    assert (
        resolve_service_id(
            deploy_hook="https://example.com/nope",
            service_id=None,
            service_name="api",
            api_key="key",
            http=lambda *_: (200, "not-json"),
        )
        is None
    )
    assert (
        resolve_service_id(
            deploy_hook="https://example.com/nope",
            service_id=None,
            service_name="api",
            api_key="key",
            http=lambda *_: (200, json.dumps({"not": "list"})),
        )
        is None
    )
    assert (
        resolve_service_id(
            deploy_hook="https://example.com/nope",
            service_id=None,
            service_name="missing",
            api_key="key",
            http=lambda *_: (200, payload),
        )
        is None
    )
    assert (
        resolve_service_id(
            deploy_hook="https://example.com/nope",
            service_id=None,
            service_name="api",
            api_key=None,
            http=lambda *_: (200, payload),
        )
        is None
    )


def test_trigger_via_rest_and_hook() -> None:
    ok = trigger_via_rest(
        service_id="srv",
        image_url="img:1",
        api_key="k",
        http=lambda *_: (201, '{"id":"d"}'),
    )
    assert ok.ok is True
    assert ok.method == "rest_imageUrl"

    fail = trigger_via_rest(
        service_id="srv",
        image_url="img:1",
        api_key="k",
        http=lambda *_: (500, "err"),
    )
    assert fail.ok is False

    hook_ok = trigger_via_hook(
        deploy_hook="https://api.render.com/deploy/srv?k=1",
        image_url="img:1",
        http=lambda *_: (200, "ok"),
        retries=2,
    )
    assert hook_ok.ok is True

    calls: list[int] = []

    def flaky_http(
        url: str, method: str, headers: object, body: object
    ) -> tuple[int, str]:
        calls.append(1)
        return (500, "retry") if len(calls) == 1 else (200, "ok")

    with patch.object(deploy_mod.time, "sleep"):
        retried = trigger_via_hook(
            deploy_hook="https://api.render.com/deploy/srv?k=1",
            image_url=None,
            http=flaky_http,
            retries=2,
            backoff_seconds=0.01,
        )
    assert retried.ok is True
    assert retried.method == "hook_default"

    no_retry = trigger_via_hook(
        deploy_hook="https://api.render.com/deploy/srv?k=1",
        image_url="img",
        http=lambda *_: (404, "nope"),
        retries=1,
    )
    assert no_retry.ok is False
    assert no_retry.status_code == 404


def test_is_suspended_deploy_block() -> None:
    assert is_suspended_deploy_block(500, "service is suspended") is True
    assert is_suspended_deploy_block(200, "service is suspended") is False
    assert is_suspended_deploy_block(400, "cannot deploy suspended") is True
    assert is_suspended_deploy_block(400, "other") is False


def test_resolve_service_id_skips_non_dict_items() -> None:
    payload = json.dumps(
        ["not-a-dict", {"service": {"name": "api", "id": "srv-found"}}]
    )
    assert (
        resolve_service_id(
            deploy_hook="https://example.com/nope",
            service_id=None,
            service_name="api",
            api_key="key",
            http=lambda *_: (200, payload),
        )
        == "srv-found"
    )


def test_trigger_image_deploy_suspended_after_rest_without_fallback() -> None:
    def http(url: str, method: str, headers: object, body: object) -> tuple[int, str]:
        if "imgURL=" in url:
            return 500, "service is suspended"
        if method == "POST":
            return 400, "cannot deploy suspended"
        return 404, ""

    result = trigger_image_deploy(
        deploy_hook="https://api.render.com/deploy/srv-abc?k=1",
        image_url="img:1",
        api_key="key",
        http=http,
        hook_retries=1,
        allow_hook_without_imgurl=False,
        skip_if_suspended=True,
    )
    assert result.method == "skipped_suspended"


def test_trigger_image_deploy_rest_fail_no_suspended_no_fallback() -> None:
    def http(url: str, method: str, headers: object, body: object) -> tuple[int, str]:
        if "imgURL=" in url:
            return 500, "hook fail"
        if method == "POST":
            return 500, "rest fail"
        return 500, "default fail"

    result = trigger_image_deploy(
        deploy_hook="https://api.render.com/deploy/srv-abc?k=1",
        image_url="img:1",
        api_key="key",
        http=http,
        hook_retries=1,
        allow_hook_without_imgurl=False,
        skip_if_suspended=False,
    )
    assert result.ok is False
    assert "hook_imgURL+rest_imageUrl" in result.method


def test_trigger_image_deploy_suspended_on_default_hook_path() -> None:
    def http(url: str, method: str, headers: object, body: object) -> tuple[int, str]:
        if "imgURL=" in url:
            return 500, "fail"
        return 409, "service is suspended conflict"

    result = trigger_image_deploy(
        deploy_hook="https://api.render.com/deploy/srv-abc?k=1",
        image_url="img:1",
        api_key=None,
        http=http,
        hook_retries=1,
        allow_hook_without_imgurl=True,
        skip_if_suspended=True,
    )
    assert result.method == "skipped_suspended"
    ok_hook = trigger_image_deploy(
        deploy_hook="https://api.render.com/deploy/srv?k=1",
        image_url="img:1",
        http=lambda *_: (200, "ok"),
        hook_retries=1,
        allow_hook_without_imgurl=False,
    )
    assert ok_hook.ok is True

    def rest_then_fail(
        url: str, method: str, headers: object, body: object
    ) -> tuple[int, str]:
        if "imgURL=" in url:
            return 500, "hook fail"
        if method == "POST":
            return 201, "rest ok"
        return 404, ""

    rest_ok = trigger_image_deploy(
        deploy_hook="https://api.render.com/deploy/srv-abc?k=1",
        image_url="img:1",
        api_key="key",
        http=rest_then_fail,
        hook_retries=1,
        allow_hook_without_imgurl=False,
    )
    assert rest_ok.method == "rest_imageUrl"

    def all_fail(
        url: str, method: str, headers: object, body: object
    ) -> tuple[int, str]:
        if "imgURL=" in url:
            return 500, "service is suspended"
        if method == "POST":
            return 500, "cannot deploy suspended service"
        return 500, "default fail suspended"

    fallback = trigger_image_deploy(
        deploy_hook="https://api.render.com/deploy/srv-abc?k=1",
        image_url="img:1",
        api_key=None,
        http=lambda url, *_a: (200, "ok") if "imgURL=" not in url else (500, "x"),
        hook_retries=1,
        allow_hook_without_imgurl=True,
    )
    assert fallback.method == "hook_default_after_imgURL_fail"

    suspended = trigger_image_deploy(
        deploy_hook="https://api.render.com/deploy/srv-abc?k=1",
        image_url="img:1",
        api_key="key",
        http=all_fail,
        hook_retries=1,
        allow_hook_without_imgurl=False,
        skip_if_suspended=True,
    )
    assert suspended.method == "skipped_suspended"

    suspended_fallback = trigger_image_deploy(
        deploy_hook="https://api.render.com/deploy/srv-abc?k=1",
        image_url="img:1",
        api_key=None,
        http=lambda url, *_a: (
            (500, "suspended conflict")
            if "imgURL=" in url
            else (500, "cannot deploy suspended")
        ),
        hook_retries=1,
        allow_hook_without_imgurl=True,
        skip_if_suspended=True,
    )
    assert suspended_fallback.method == "skipped_suspended"

    hard_fail = trigger_image_deploy(
        deploy_hook="https://api.render.com/deploy/srv-abc?k=1",
        image_url="img:1",
        api_key=None,
        http=lambda *_: (500, "boom"),
        hook_retries=1,
        allow_hook_without_imgurl=False,
    )
    assert hard_fail.ok is False


def test_trigger_image_deploy_suspended_on_hook_after_fallback_not_suspended() -> None:
    """Cover 316-319: fallback fails without suspended; hook_result is suspended."""

    def http(url: str, method: str, headers: object, body: object) -> tuple[int, str]:
        if "imgURL=" in url:
            return 500, "service is suspended on imgurl path"
        return 500, "generic hook failure"

    result = trigger_image_deploy(
        deploy_hook="https://api.render.com/deploy/srv-abc?k=1",
        image_url="img:1",
        api_key=None,
        http=http,
        hook_retries=1,
        allow_hook_without_imgurl=True,
        skip_if_suspended=True,
    )
    assert result.method == "skipped_suspended"
    assert "suspended" in result.detail.lower()


def test_trigger_image_deploy_suspended_on_fallback_not_hook() -> None:
    """Cover 302-314: default hook fails with suspended after imgURL hook fails."""

    def http(url: str, method: str, headers: object, body: object) -> tuple[int, str]:
        if "imgURL=" in url:
            return 500, "imgurl hook failed"
        return 500, "cannot deploy suspended service"

    result = trigger_image_deploy(
        deploy_hook="https://api.render.com/deploy/srv-abc?k=1",
        image_url="img:1",
        api_key=None,
        http=http,
        hook_retries=1,
        allow_hook_without_imgurl=True,
        skip_if_suspended=True,
    )
    assert result.method == "skipped_suspended"


def test_main_cli(capsys: pytest.CaptureFixture[str]) -> None:
    args = [
        "--deploy-hook",
        "https://api.render.com/deploy/srv?k=1",
        "--image-url",
        "ghcr.io/x/y:tag",
    ]
    with patch.object(
        deploy_mod,
        "trigger_image_deploy",
        return_value=deploy_mod.TriggerResult(True, "hook", 200, "ok"),
    ):
        assert main(args) == 0
    assert '"ok": true' in capsys.readouterr().out.lower()

    with patch.object(
        deploy_mod,
        "trigger_image_deploy",
        return_value=deploy_mod.TriggerResult(False, "hook", 500, "fail"),
    ):
        assert main(args) == 1

    with (
        patch.dict(
            "os.environ",
            {
                "RENDER_SKIP_IF_SUSPENDED": "true",
                "RENDER_API_KEY": "k",
                "RENDER_SERVICE_ID": "srv",
            },
        ),
        patch.object(
            deploy_mod,
            "trigger_image_deploy",
            return_value=deploy_mod.TriggerResult(True, "skipped", 0, ""),
        ) as trig,
    ):
        assert main([*args, "--no-hook-without-imgurl"]) == 0
    trig.assert_called_once()
    call_kw = trig.call_args.kwargs
    assert call_kw["skip_if_suspended"] is True
    assert call_kw["allow_hook_without_imgurl"] is False
