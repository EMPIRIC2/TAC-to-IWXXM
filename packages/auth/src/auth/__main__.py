"""Package entrypoint wrapper for auth service."""

import runpy
from pathlib import Path

_root_main = Path(__file__).resolve().parents[1] / "__main__.py"
_namespace = runpy.run_path(str(_root_main))

app = _namespace["app"]

__all__ = ["app"]
