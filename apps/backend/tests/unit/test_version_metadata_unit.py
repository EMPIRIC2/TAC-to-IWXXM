"""Unit tests for IWXXM version metadata helpers."""

from src.config import version_metadata as vm


def test_get_version_metadata_known_and_unknown() -> None:
    known = vm.get_version_metadata("2025-2")
    unknown = vm.get_version_metadata("2099-9")

    assert known is not None
    assert known.version == "2025-2"
    assert unknown is None


def test_version_metadata_repr_contains_short_namespace() -> None:
    metadata = vm.get_version_metadata("2016")

    assert metadata is not None
    text = repr(metadata)
    assert "version=2016" in text
    assert "ns=2.1" in text


def test_normalize_version_aliases_and_canonical_values() -> None:
    assert vm.normalize_version(" 2025 ") == "2025-2"
    assert vm.normalize_version("2025-1") == "2025-2"
    assert vm.normalize_version("3.0") == "2018"
    assert vm.normalize_version("2.1") == "2016"
    assert vm.normalize_version("2023-1") == "2023-1"
    assert vm.normalize_version("unknown") == "unknown"


def test_get_supported_versions_reflects_registry_keys() -> None:
    supported = vm.get_supported_versions()

    assert set(supported) == set(vm.VERSION_METADATA.keys())
    assert "2025-2" in supported
