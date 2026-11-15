"""HTTP helpers extracted from api.py (line-cap refactor)."""

from __future__ import annotations

import logging
import re
from collections.abc import Awaitable, Callable
from typing import Any, cast

from fastapi import FastAPI
from starlette.types import Message, Receive, Scope, Send

logger = logging.getLogger("src.api")


class ConvertRequestLoggingMiddleware:
    """
    Log request/response details for convert flow, including OPTIONS preflight.

    Attributes
    ----------
    _ : object
        See implementation.
    """

    def __init__(self, app: Callable[[Scope, Receive, Send], Awaitable[None]]) -> None:
        """
        Internal helper ``__init__``.

        Parameters
        ----------
        app : object
            Argument ``app``.
        """
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        Internal helper ``__call__``.

        Parameters
        ----------
        scope : object
            Argument ``scope``.
        receive : object
            Argument ``receive``.
        send : object
            Argument ``send``.
        """
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        method = scope.get("method", "")

        if path != "/api/v1/convert":
            await self.app(scope, receive, send)
            return

        headers = {key.decode("latin1").lower(): value.decode("latin1") for key, value in scope.get("headers", [])}

        logger.info(
            "[PREFLIGHT] %s %s origin=%s acr_method=%s acr_headers=%s content_type=%s",
            method,
            path,
            headers.get("origin", "none"),
            headers.get("access-control-request-method", "none"),
            headers.get("access-control-request-headers", "none"),
            headers.get("content-type", "none"),
        )

        async def send_wrapper(message: Message) -> None:
            """
            Log preflight response status before forwarding ASGI messages.

            Examples
            --------
            >>> 1 + 1  # docstring smoke (send_wrapper)
            2

            Parameters
            ----------
            message : object
                Argument ``message``.
            """
            if message.get("type") == "http.response.start":
                status_code = message.get("status")
                logger.info(
                    "[PREFLIGHT] %s %s -> status=%s",
                    method,
                    path,
                    status_code,
                )
            await send(message)

        await self.app(scope, receive, send_wrapper)


_NUMPY_SECTION = re.compile(
    "\n(?:Examples|Parameters|Returns|Raises|Attributes|Notes|Warnings|See Also|References)\n-+"
)


def _operator_description(text: str) -> str:
    """Keep the prose before a NumPy section or a form feed.

    Parameters
    ----------
    text : str
        OpenAPI description copied from a docstring.

    Returns
    -------
    str
        Operator-facing description.
    """
    head = text.split("\f", 1)[0]
    match = _NUMPY_SECTION.search(head)
    if match:
        head = head[: match.start()]
    return head.strip()


def _trim_operator_descriptions(node: object) -> None:
    """Apply :func:`_operator_description` to every OpenAPI description."""
    if isinstance(node, dict):
        mapping = cast(dict[str, Any], node)
        description = mapping.get("description")
        if isinstance(description, str):
            trimmed = _operator_description(description)
            if trimmed != description:
                mapping["description"] = trimmed
        for value in mapping.values():
            _trim_operator_descriptions(value)
    elif isinstance(node, list):
        items = cast(list[Any], node)
        for item in items:
            _trim_operator_descriptions(item)


def make_custom_openapi(app: FastAPI) -> Callable[[], dict[str, Any]]:
    """Return an OpenAPI factory bound to ``app`` (avoids import cycles)."""

    def custom_openapi() -> dict[str, Any]:
        """Build OpenAPI schema without security schemes for public API docs."""
        if app.openapi_schema:
            return app.openapi_schema

        from fastapi.openapi.utils import get_openapi

        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
            tags=app.openapi_tags,
        )
        _trim_operator_descriptions(openapi_schema)
        components = openapi_schema.setdefault("components", {})
        components.pop("securitySchemes", None)
        openapi_schema.pop("security", None)
        app.openapi_schema = openapi_schema
        return openapi_schema

    return custom_openapi
