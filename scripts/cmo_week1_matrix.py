#!/usr/bin/env python3
"""CLI wrapper for CMO Week 1 convert+validate matrix. [Corpus: tests]"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tests.cmo_week1.matrix_lib import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
