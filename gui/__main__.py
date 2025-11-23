"""Entry point for launching the FastAPI GUI with uvicorn.

Usage:
	python -m gui  (from repository root)
"""

from __future__ import annotations

import uvicorn
from .app import app


def main() -> None:
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":  # pragma: no cover
    main()
