"""TC-DX-001..004: package façade discoverability (EV-layout-dx).

Spec: docs/test-plan.md TC-DX-001..004; docs/engineering/package-dx.md.
"""

from __future__ import annotations

import iwxxm_validate


def test_tc_dx_001_validate_in_package_all() -> None:
    """I want to validate IWXXM XML → ``from iwxxm_validate import validate``."""
    from iwxxm_validate import validate

    assert validate is iwxxm_validate.validate
    assert "validate" in iwxxm_validate.__all__


def test_tc_dx_002_canonical_xml_primary_and_c14n_aliases() -> None:
    """I want Quality Metrics compare ignoring formatting → clear primary names."""
    from iwxxm_validate import (
        c14n_equal,
        c14n_xml,
        canonical_xml_equal,
        to_canonical_xml,
    )

    pretty = "<a>\n  <b x='1'/>\n</a>"
    compact = "<a><b x='1'/></a>"
    assert to_canonical_xml(pretty) == to_canonical_xml(compact)
    assert canonical_xml_equal(pretty, compact) is True
    assert c14n_xml is to_canonical_xml
    assert c14n_equal is canonical_xml_equal
    assert "to_canonical_xml" in iwxxm_validate.__all__
    assert "canonical_xml_equal" in iwxxm_validate.__all__
    assert "c14n_xml" in iwxxm_validate.__all__
    assert "c14n_equal" in iwxxm_validate.__all__


def test_tc_dx_003_rust_available_in_package_all() -> None:
    """I want to know whether the Rust native engine is available."""
    from iwxxm_validate import rust_available

    assert callable(rust_available)
    assert "rust_available" in iwxxm_validate.__all__


def test_tc_dx_004_validate_for_quality_metrics_in_package_all() -> None:
    """I want validation tuned for Quality Metrics reporting."""
    from iwxxm_validate import validate_for_quality_metrics

    assert callable(validate_for_quality_metrics)
    assert "validate_for_quality_metrics" in iwxxm_validate.__all__
