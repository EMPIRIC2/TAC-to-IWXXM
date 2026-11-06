#!/usr/bin/env python3
"""Fail when the CI logout fixture is missing or is not a non-production stub.

Default E2E must run logout against this fixture. The password is a committed
sentinel, not a live credential. [Corpus: tests]
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

FIXTURE_SENTINEL = "ci-logout-fixture"
_EMAIL_SUFFIX = "@example.invalid"


def fixture_error(env_value: str, repo_root: Path) -> str | None:
    """
    Return an error when the logout fixture is missing or not a stub.

    Parameters
    ----------
    env_value : str
        ``E2E_LOGOUT_FIXTURE`` value. Relative paths resolve from ``repo_root``.
    repo_root : Path
        Repository root used for relative fixture paths.

    Returns
    -------
    str or None
        Error text, or None when the fixture is a non-production stub.
    """
    raw = env_value.strip()
    if not raw:
        return "E2E_LOGOUT_FIXTURE is unset"
    fixture_path = Path(raw)
    if not fixture_path.is_absolute():
        fixture_path = repo_root / fixture_path
    if not fixture_path.is_file():
        return "logout fixture file is missing"
    try:
        parsed = json.loads(fixture_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return "logout fixture is not valid JSON"
    if not isinstance(parsed, dict):
        return "logout fixture must be a JSON object"
    email = parsed.get("email")
    secret = parsed.get("password")
    if not isinstance(email, str) or not email.endswith(_EMAIL_SUFFIX):
        return "logout fixture email must use the example.invalid domain"
    if not isinstance(secret, str) or secret != FIXTURE_SENTINEL:
        return "logout fixture password is not the non-production sentinel"
    return None


def main(argv: list[str] | None = None) -> int:
    """
    Exit 1 when the CI logout fixture is missing or unsafe.

    Parameters
    ----------
    argv : list of str or None
        ``argv[1]`` is the repository root. Defaults to the process arguments.

    Returns
    -------
    int
        Process status code.
    """
    args = list(sys.argv if argv is None else argv)
    root = Path(args[1] if len(args) > 1 else ".").resolve()
    error = fixture_error(os.environ.get("E2E_LOGOUT_FIXTURE", ""), root)
    if error is not None:
        print(error, file=sys.stderr)
        return 1
    print("non-production logout fixture ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
