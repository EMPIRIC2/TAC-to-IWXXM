"""Auto-split package: loads chunked sources into this namespace (API-stable)."""

from __future__ import annotations

from pathlib import Path

_pkg = Path(__file__).resolve().parent
_CHUNKS = _pkg / "_chunks"
__file__ = str(_pkg.parent / f"{_pkg.name}.py")
_src = "".join(p.read_text(encoding="utf-8") for p in sorted(_CHUNKS.glob("*.src")))
exec(compile(_src, __file__, "exec"), globals())
del _pkg, _CHUNKS, _src
