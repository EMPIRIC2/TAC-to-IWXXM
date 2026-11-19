"""Parameterizable conversion templates (EV-080 / #1146).

Slot-builder-first Conversion rule objects: typed captures map TAC groups to
IWXXM blocks. First-party builtins are view/fork sources; custom templates are
persisted by the API layer.
"""

from __future__ import annotations

# Imports/constants consumed by exec'd part bodies.
import re
from typing import Any, cast

from tac2iwxxm.models import (
    BridgePreview,
    ConversionTemplate,
    Slot,
    SlotMode,
    SlotType,
)

_WIND_RE = re.compile(r"^(\d{3})(\d{2,3})(?:G(\d{2,3}))?(KT|MPS)$", re.IGNORECASE)
