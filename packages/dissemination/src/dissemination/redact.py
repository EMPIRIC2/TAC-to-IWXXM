"""Secret redaction for dissemination errors and logs (ADR-029)."""

from __future__ import annotations

import re
from urllib.parse import urlparse, urlunparse

_URI_USERINFO = re.compile(r"(://[^:/?#]+:)([^@/?#]+)(@)")
_PASSWORD_JSON = re.compile(r'(?i)("?(?:password|passwd|secret|token|api[_-]?key)"?\s*[:=]\s*")([^"]*)(")')


def redact_uri(uri: str) -> str:
    """
    Redact userinfo password in a connection URI.

    Parameters
    ----------
    uri :
        Possibly secret-bearing URI.

    Returns
    -------
    str
        URI with password replaced by ``***`` when present.
    """
    redacted = _URI_USERINFO.sub(r"\1***\3", uri)
    try:
        parsed = urlparse(redacted)
        if parsed.password:
            netloc = parsed.hostname or ""
            if parsed.port:
                netloc = f"{netloc}:{parsed.port}"
            if parsed.username:
                netloc = f"{parsed.username}:***@{netloc}"
            return urlunparse(parsed._replace(netloc=netloc))
    except Exception:
        pass
    return redacted


def redact_secrets(text: str) -> str:
    """Redact URI passwords and common secret JSON/key patterns from ``text``."""
    out = redact_uri(text)
    return _PASSWORD_JSON.sub(r"\1***\3", out)
