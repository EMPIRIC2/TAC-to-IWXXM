#!/usr/bin/env python3
"""Trigger Render image deploys with deploy-hook → REST fallback.

BUG-2026-08-03: ``curl …&imgURL=`` against a Render deploy hook can return HTTP 500
even after GHCR push succeeds. Prefer the hook (with retries); on 5xx fall back to
``POST /v1/services/{id}/deploys`` with ``imageUrl`` when ``RENDER_API_KEY`` is set;
as a last resort, fire the hook without ``imgURL`` (service default / ``main-latest``).

CLI::

    python scripts/deploy/trigger_render_image_deploy.py \\
      --deploy-hook "$RENDER_BACKEND_DEPLOY_HOOK" \\
      --image-url "ghcr.io/empiric2/tac-to-iwxxm/backend:TAG" \\
      --service-name metar-to-iwxxm-api
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

RENDER_API_BASE = "https://api.render.com/v1"
HttpMethod = Literal["GET", "POST"]
HttpCaller = Callable[
    [str, HttpMethod, dict[str, str] | None, bytes | None], tuple[int, str]
]


@dataclass(frozen=True)
class TriggerResult:
    """Outcome of a deploy trigger attempt."""

    ok: bool
    method: str
    status_code: int
    detail: str


def build_deploy_hook_url(deploy_hook: str, image_url: str | None = None) -> str:
    """Append a URL-encoded ``imgURL`` query param to a Render deploy hook.

    Parameters
    ----------
    deploy_hook
        Hook URL that already includes ``?key=…``.
    image_url
        Full registry reference (``host/repo/name:tag``). When ``None``, return
        the hook unchanged.

    Returns
    -------
    str
        Hook URL ready for GET/POST.
    """
    hook = deploy_hook.strip()
    if not hook:
        raise ValueError("deploy_hook must be non-empty")
    if image_url is None:
        return hook

    parsed = urlparse(hook)
    query = parse_qs(parsed.query, keep_blank_values=True)
    query["imgURL"] = [image_url]
    new_query = urlencode(query, doseq=True)
    return urlunparse(parsed._replace(query=new_query))


def service_id_from_deploy_hook(deploy_hook: str) -> str | None:
    """Extract ``srv-…`` from ``https://api.render.com/deploy/srv-…?key=…``."""
    path = urlparse(deploy_hook.strip()).path.rstrip("/")
    if "/deploy/" not in path:
        return None
    candidate = path.rsplit("/", 1)[-1]
    if candidate.startswith("srv-"):
        return candidate
    return None


def _default_http(
    url: str,
    method: HttpMethod,
    headers: dict[str, str] | None,
    body: bytes | None,
) -> tuple[int, str]:
    req = urllib.request.Request(url, data=body, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return int(resp.status), resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        body_txt = exc.read().decode("utf-8", errors="replace")
        return int(exc.code), body_txt
    except urllib.error.URLError as exc:
        return 0, str(exc.reason if hasattr(exc, "reason") else exc)


def resolve_service_id(
    *,
    deploy_hook: str,
    service_id: str | None,
    service_name: str | None,
    api_key: str | None,
    http: HttpCaller,
) -> str | None:
    """Resolve a Render service id from explicit id, hook path, or name lookup."""
    if service_id:
        return service_id
    from_hook = service_id_from_deploy_hook(deploy_hook)
    if from_hook:
        return from_hook
    if not (api_key and service_name):
        return None
    status, text = http(
        f"{RENDER_API_BASE}/services?limit=100&name={urllib.parse.quote(service_name)}",
        "GET",
        {"Authorization": f"Bearer {api_key}", "Accept": "application/json"},
        None,
    )
    if status != 200:
        return None
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, list):
        return None
    for item in payload:
        if not isinstance(item, dict):
            continue
        raw_svc = item.get("service")
        svc: dict[str, object]
        if isinstance(raw_svc, dict):
            svc = raw_svc
        else:
            svc = item
        if svc.get("name") == service_name:
            sid = svc.get("id")
            return sid if isinstance(sid, str) else None
    return None


def trigger_via_rest(
    *,
    service_id: str,
    image_url: str,
    api_key: str,
    http: HttpCaller,
) -> TriggerResult:
    """POST ``/services/{id}/deploys`` with ``imageUrl``."""
    body = json.dumps({"imageUrl": image_url}).encode("utf-8")
    status, text = http(
        f"{RENDER_API_BASE}/services/{service_id}/deploys",
        "POST",
        {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        body,
    )
    ok = status in (200, 201, 202)
    return TriggerResult(
        ok=ok, method="rest_imageUrl", status_code=status, detail=text[:500]
    )


def trigger_via_hook(
    *,
    deploy_hook: str,
    image_url: str | None,
    http: HttpCaller,
    retries: int = 3,
    backoff_seconds: float = 2.0,
) -> TriggerResult:
    """GET deploy hook, optionally with ``imgURL``, with retries on 5xx/0."""
    url = build_deploy_hook_url(deploy_hook, image_url)
    method_label = "hook_imgURL" if image_url else "hook_default"
    last = TriggerResult(ok=False, method=method_label, status_code=0, detail="")
    for attempt in range(1, max(1, retries) + 1):
        status, text = http(url, "GET", None, None)
        last = TriggerResult(
            ok=200 <= status < 300,
            method=method_label,
            status_code=status,
            detail=text[:500],
        )
        if last.ok:
            return last
        # Retry transient failures only.
        if status and status < 500 and status != 0:
            return last
        if attempt < retries:
            time.sleep(backoff_seconds * attempt)
    return last


def trigger_image_deploy(
    *,
    deploy_hook: str,
    image_url: str,
    api_key: str | None = None,
    service_id: str | None = None,
    service_name: str | None = None,
    http: HttpCaller | None = None,
    hook_retries: int = 3,
    allow_hook_without_imgurl: bool = True,
) -> TriggerResult:
    """Try hook+imgURL, then REST imageUrl, then hook without imgURL."""
    caller = http or _default_http

    hook_result = trigger_via_hook(
        deploy_hook=deploy_hook,
        image_url=image_url,
        http=caller,
        retries=hook_retries,
    )
    if hook_result.ok:
        return hook_result

    key = (api_key or "").strip() or None
    sid = resolve_service_id(
        deploy_hook=deploy_hook,
        service_id=service_id,
        service_name=service_name,
        api_key=key,
        http=caller,
    )
    if key and sid:
        rest = trigger_via_rest(
            service_id=sid,
            image_url=image_url,
            api_key=key,
            http=caller,
        )
        if rest.ok:
            return rest
        hook_result = TriggerResult(
            ok=False,
            method=f"{hook_result.method}+{rest.method}",
            status_code=rest.status_code or hook_result.status_code,
            detail=(
                f"hook={hook_result.status_code}:{hook_result.detail} | "
                f"rest={rest.status_code}:{rest.detail}"
            )[:800],
        )

    if allow_hook_without_imgurl:
        fallback = trigger_via_hook(
            deploy_hook=deploy_hook,
            image_url=None,
            http=caller,
            retries=2,
        )
        if fallback.ok:
            return TriggerResult(
                ok=True,
                method="hook_default_after_imgURL_fail",
                status_code=fallback.status_code,
                detail=(
                    f"imgURL path failed ({hook_result.status_code}); "
                    f"default hook succeeded (ensure service image tracks main-latest). "
                    f"{fallback.detail}"
                )[:800],
            )

    return hook_result


def main(argv: list[str] | None = None) -> int:
    """CLI entry for CI Deploy steps."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--deploy-hook", required=True, help="Render deploy hook URL")
    parser.add_argument("--image-url", required=True, help="Full GHCR image reference")
    parser.add_argument(
        "--service-name",
        default=None,
        help="Render service name (lookup when hook lacks srv- id)",
    )
    parser.add_argument("--service-id", default=None, help="Explicit Render service id")
    parser.add_argument(
        "--api-key",
        default=None,
        help="RENDER_API_KEY (default: env RENDER_API_KEY)",
    )
    parser.add_argument(
        "--no-hook-without-imgurl",
        action="store_true",
        help="Do not fall back to hook without imgURL",
    )
    args = parser.parse_args(argv)

    result = trigger_image_deploy(
        deploy_hook=args.deploy_hook,
        image_url=args.image_url,
        api_key=args.api_key or os.environ.get("RENDER_API_KEY"),
        service_id=args.service_id or os.environ.get("RENDER_SERVICE_ID"),
        service_name=args.service_name,
        allow_hook_without_imgurl=not args.no_hook_without_imgurl,
    )
    print(
        json.dumps(
            {
                "ok": result.ok,
                "method": result.method,
                "status_code": result.status_code,
                "detail": result.detail,
            },
            indent=2,
        )
    )
    return 0 if result.ok else 1


if __name__ == "__main__":
    sys.exit(main())
