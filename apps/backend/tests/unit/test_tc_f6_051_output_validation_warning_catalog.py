"""TC-F6-051: OUTPUT_VALIDATION_WARNING is in the operator issue catalog.

[Corpus: product §F6] [Corpus: api] [Corpus: tests §TC-F6-051]
"""

from __future__ import annotations

import re

from src.services.iwxxm_validation_catalog import iwxxm_validation_catalog_rows

_INTERNAL = re.compile(r"(?i)(\[Corpus:|docs/sessions/|ADR-\d+|EV-\d+|#\d{3,}|TC-EV|UJ-\d+|F\d{1,2}\.[a-z])")


def test_tc_f6_051_output_validation_warning_catalog_text() -> None:
    """The catalog describes the warning in plain language."""
    row = next(item for item in iwxxm_validation_catalog_rows() if item["code"] == "OUTPUT_VALIDATION_WARNING")
    text = str(row["message_template"])
    attribution = str(row["source_attribution"])
    assert row["severity"] == "warning"
    assert "validation" in text.lower()
    assert "publish" in text.lower()
    assert _INTERNAL.search(text) is None
    assert _INTERNAL.search(attribution) is None
    assert _INTERNAL.search(str(row["source_locator"])) is None
