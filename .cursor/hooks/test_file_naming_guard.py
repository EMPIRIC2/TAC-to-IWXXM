"""Cursor afterFileEdit / Write hook: warn on planning-id test filenames.

Fails open (exit 0) but prints a clear ERROR so agents rename before commit.
CI hard-fails via ``scripts/ci/check_test_file_naming.py``.

[Corpus: tests]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def _find_repo_root(start: Path) -> Path | None:
    p = start if start.is_dir() else start.parent
    for candidate in [p, *p.parents]:
        if (candidate / ".git").exists() or (candidate / ".git").is_file():
            return candidate
    return None


def _load_policy(repo: Path):
    sys.path.insert(0, str(repo))
    import scripts.ci.check_test_file_naming as policy

    return policy


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        print("{}")
        return 0

    raw = payload.get("filePath") or payload.get("file_path") or ""
    if not raw:
        print("{}")
        return 0

    file_path = Path(raw)
    repo = _find_repo_root(file_path)
    if repo is None:
        print("{}")
        return 0

    try:
        rel = file_path.resolve().relative_to(repo.resolve())
    except ValueError:
        print("{}")
        return 0

    rel_str = str(rel).replace("\\", "/")
    try:
        policy = _load_policy(repo)
    except Exception:
        # Fail open in the editor when the policy module cannot load.
        print("{}")
        return 0

    verdict = policy.classify_path(rel_str, is_new=True)
    if verdict.allowed:
        print("{}")
        return 0

    msg = (
        f"ERROR: banned planning-id test filename stem: {rel_str}. "
        "Rename to test_<subject>_<scenario>.py; cite EV/TC/M in a docstring "
        "or marker. Keep WMO AHL fc_* fixtures. See "
        "packages/tac-validate/tests/NAMING.md."
    )
    print(json.dumps({"user_message": msg}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
