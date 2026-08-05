"""BUG-2026-08-03 — Render deploy hook imgURL 500 must fall back to REST.

Main CI Deploy failed on merge ``8bd111c`` when ``curl …&imgURL=`` returned HTTP 500
after GHCR push. Guard: resilient trigger script + CI must not use bare curl imgURL.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import yaml

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "deploy" / "trigger_render_image_deploy.py"
CI_CD = ROOT / ".github" / "workflows" / "ci-cd.yml"


def _load_mod():
    import sys

    name = "trigger_render_image_deploy"
    spec = importlib.util.spec_from_file_location(name, SCRIPT)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_bug_2026_08_03_build_deploy_hook_url_encodes_imgurl() -> None:
    mod = _load_mod()
    hook = "https://api.render.com/deploy/srv-abc123?key=secret"
    image = "ghcr.io/empiric2/tac-to-iwxxm/backend:20260803151459-8bd111c"
    url = mod.build_deploy_hook_url(hook, image)
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    assert qs["key"] == ["secret"]
    assert qs["imgURL"] == [image]
    # Must not naively append "&imgURL=" without encoding colons/slashes.
    assert "imgURL=" in url
    assert "ghcr.io%2Fempiric2" in url or "ghcr.io/empiric2" in qs["imgURL"][0]


def test_bug_2026_08_03_service_id_from_deploy_hook() -> None:
    mod = _load_mod()
    assert (
        mod.service_id_from_deploy_hook(
            "https://api.render.com/deploy/srv-d69v688gjchc73cn9kg0?key=x"
        )
        == "srv-d69v688gjchc73cn9kg0"
    )
    assert mod.service_id_from_deploy_hook("https://example.com/nope") is None


def test_bug_2026_08_03_hook_500_falls_back_to_rest() -> None:
    """Repro of main CI failure: hook imgURL → 500; REST imageUrl → success."""
    mod = _load_mod()
    calls: list[tuple[str, str]] = []

    def fake_http(
        url: str,
        method: str,
        headers: dict[str, str] | None,
        body: bytes | None,
    ) -> tuple[int, str]:
        calls.append((method, url))
        if "imgURL=" in url:
            return 500, "Internal Server Error"
        if method == "POST" and "/deploys" in url:
            assert body is not None
            assert b"imageUrl" in body
            assert headers is not None and "Bearer" in headers.get("Authorization", "")
            return 201, '{"id":"dep-test"}'
        return 404, "unexpected"

    result = mod.trigger_image_deploy(
        deploy_hook="https://api.render.com/deploy/srv-abc?key=k",
        image_url="ghcr.io/empiric2/tac-to-iwxxm/backend:tag",
        api_key="rnd_test",
        http=fake_http,
        hook_retries=1,
        allow_hook_without_imgurl=False,
    )
    assert result.ok is True
    assert result.method == "rest_imageUrl"
    assert result.status_code == 201
    assert any("imgURL=" in u for _, u in calls)
    assert any(m == "POST" and "/deploys" in u for m, u in calls)


def test_bug_2026_08_03_hook_500_falls_back_to_default_hook() -> None:
    mod = _load_mod()

    def fake_http(
        url: str,
        method: str,
        headers: dict[str, str] | None,
        body: bytes | None,
    ) -> tuple[int, str]:
        if "imgURL=" in url:
            return 500, "boom"
        return 200, "ok"

    result = mod.trigger_image_deploy(
        deploy_hook="https://api.render.com/deploy/srv-abc?key=k",
        image_url="ghcr.io/empiric2/tac-to-iwxxm/backend:tag",
        api_key=None,
        http=fake_http,
        hook_retries=1,
        allow_hook_without_imgurl=True,
    )
    assert result.ok is True
    assert result.method == "hook_default_after_imgURL_fail"


def test_bug_2026_08_04_suspended_render_skipped_when_enabled() -> None:
    """DOKS cutover: suspended Render must not fail Deploy after GHCR push."""
    mod = _load_mod()
    calls: list[tuple[str, str]] = []

    def fake_http(
        url: str,
        method: str,
        headers: dict[str, str] | None,
        body: bytes | None,
    ) -> tuple[int, str]:
        calls.append((method, url))
        if "imgURL=" in url:
            return 409, '{"conflict":"service is suspended"}'
        if method == "POST" and "/deploys" in url:
            return 400, '{"message":"cannot deploy suspended service"}'
        return 404, "unexpected"

    result = mod.trigger_image_deploy(
        deploy_hook="https://api.render.com/deploy/srv-abc?key=k",
        image_url="ghcr.io/empiric2/tac-to-iwxxm/backend:tag",
        api_key="rnd_test",
        http=fake_http,
        hook_retries=1,
        allow_hook_without_imgurl=False,
        skip_if_suspended=True,
    )
    assert result.ok is True
    assert result.method == "skipped_suspended"
    assert "suspended" in result.detail.lower()


def test_bug_2026_08_03_ci_uses_resilient_script_not_bare_curl() -> None:
    raw = CI_CD.read_text(encoding="utf-8")
    assert "trigger_render_image_deploy.py" in raw
    # Guard against regressing to the brittle one-liner that failed on 8bd111c.
    assert 'curl -fsSL "${DEPLOY_HOOK}&imgURL=' not in raw
    assert "&imgURL=${ENCODED_URL}" not in raw
    assert "--skip-if-suspended" in raw
    assert "RENDER_SKIP_IF_SUSPENDED" in raw
    assert "RENDER_DEPLOY_MODE: image" in raw

    doc = yaml.safe_load(raw)
    assert isinstance(doc, dict)
    deploy = (doc.get("jobs") or {}).get("deploy") or {}
    assert isinstance(deploy, dict)
    # Optional REST fallback secret must be wired when present.
    assert "RENDER_API_KEY" in raw
    assert "secrets.RENDER_API_KEY" in raw
