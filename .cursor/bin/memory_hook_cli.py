#!/usr/bin/env python3
"""Engineering memory hook CLI entry. [Corpus: skill-integration]"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from memory_hook_lib import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
