"""Unit tests for iwxxm_validation.py schemas – 0% coverage target."""

from src.schemas.iwxxm_validation import (
    SUPPORTED_IWXXM_VERSIONS,
    VALID_METEOROLOGICAL_FEATURES,
    VALID_NIL_REASONS,
    VALID_VOLCANIC_CODES,
    IWXXMVersion,
    MeteorologicalFeature,
    NilReason,
    VolcanicAviationColourCode,
    extract_iwxxm_namespace_version,
    get_namespace_version,
    is_supported_iwxxm_version,
    is_valid_meteorological_feature,
    is_valid_nil_reason,
    is_valid_volcanic_code,
)


class TestMeteorologicalFeature:
    def test_cloud_value(self):
        assert MeteorologicalFeature.CLOUD == "CLOUD"

    def test_all_are_strings(self):
        for feat in MeteorologicalFeature:
            assert isinstance(feat.value, str)


class TestVolcanicAviationColourCode:
    def test_values(self):
        assert VolcanicAviationColourCode.GREEN == "GREEN"
        assert VolcanicAviationColourCode.RED == "RED"
        assert VolcanicAviationColourCode.UNASSIGNED == "UNASSIGNED"


class TestNilReason:
    def test_missing(self):
        assert NilReason.MISSING == "missing"

    def test_unknown(self):
        assert NilReason.UNKNOWN == "unknown"


class TestIWXXMVersion:
    def test_supported_versions(self):
        versions = {v.value for v in IWXXMVersion}
        assert "2023-1" in versions
        assert "2025-2" in versions

    def test_sets_populated(self):
        assert len(VALID_METEOROLOGICAL_FEATURES) >= 5
        assert len(VALID_VOLCANIC_CODES) >= 4
        assert len(VALID_NIL_REASONS) >= 5
        assert len(SUPPORTED_IWXXM_VERSIONS) >= 3


class TestValidationHelpers:
    def test_is_valid_meteorological_feature_true(self):
        assert is_valid_meteorological_feature("CLOUD") is True
        assert is_valid_meteorological_feature("STORM") is True

    def test_is_valid_meteorological_feature_false(self):
        assert is_valid_meteorological_feature("NOT_A_FEATURE") is False
        assert is_valid_meteorological_feature("") is False

    def test_is_valid_volcanic_code_true(self):
        assert is_valid_volcanic_code("GREEN") is True
        assert is_valid_volcanic_code("RED") is True

    def test_is_valid_volcanic_code_false(self):
        assert is_valid_volcanic_code("PURPLE") is False
        assert is_valid_volcanic_code("") is False

    def test_valid_meteorological_features_set_contents(self):
        assert "AIRFRAME_ICING" in VALID_METEOROLOGICAL_FEATURES
        assert "DUSTSTORM" in VALID_METEOROLOGICAL_FEATURES

    def test_valid_nil_reasons_set_contents(self):
        assert "missing" in VALID_NIL_REASONS
        assert "unknown" in VALID_NIL_REASONS
        assert "inapplicable" in VALID_NIL_REASONS

    def test_is_valid_nil_reason_true_and_false(self):
        assert is_valid_nil_reason("missing") is True
        assert is_valid_nil_reason("not-a-nil-reason") is False

    def test_is_supported_iwxxm_version_true_and_false(self):
        assert is_supported_iwxxm_version("2025-2") is True
        assert is_supported_iwxxm_version("2099-1") is False

    def test_extract_iwxxm_namespace_version_success(self):
        assert extract_iwxxm_namespace_version("http://icao.int/iwxxm/2023-1") == "2023-1"

    def test_extract_iwxxm_namespace_version_invalid_prefix(self):
        try:
            extract_iwxxm_namespace_version("http://example.org/not-iwxxm/2023-1")
        except ValueError as exc:
            assert "Invalid IWXXM namespace" in str(exc)
        else:
            raise AssertionError("Expected ValueError")

    def test_extract_iwxxm_namespace_version_unsupported(self):
        try:
            extract_iwxxm_namespace_version("http://icao.int/iwxxm/2099-1")
        except ValueError as exc:
            assert "Unsupported IWXXM version" in str(exc)
        else:
            raise AssertionError("Expected ValueError")

    def test_get_namespace_version_success(self):
        xml = '<root xmlns:iwxxm="http://icao.int/iwxxm/2025-2" />'
        assert get_namespace_version(xml) == "2025-2"

    def test_get_namespace_version_legacy_3_0_success(self):
        xml = '<root xmlns:iwxxm="http://icao.int/iwxxm/3.0" />'
        assert get_namespace_version(xml) == "3.0"

    def test_get_namespace_version_missing_namespace_raises(self):
        try:
            get_namespace_version("<root/>")
        except ValueError as exc:
            assert "namespace not found" in str(exc)
        else:
            raise AssertionError("Expected ValueError")

    def test_get_namespace_version_unsupported_raises(self):
        xml = '<root xmlns:iwxxm="http://icao.int/iwxxm/2099-1" />'
        try:
            get_namespace_version(xml)
        except ValueError as exc:
            assert "Unsupported IWXXM version" in str(exc)
        else:
            raise AssertionError("Expected ValueError")
