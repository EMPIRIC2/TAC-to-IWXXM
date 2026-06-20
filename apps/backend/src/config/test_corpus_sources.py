"""
Test Corpus Sources Configuration

Defines external test corpora for IWXXM validation, including official WMO
translation pairs, NWS examples, and operational API snapshots.
"""

from pathlib import Path
from typing import Any, Dict, List

# Project root path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# External test corpus sources
TEST_CORPUS_SOURCES: Dict[str, Dict[str, Any]] = {
    "wmo_canonical_examples": {
        "type": "mirrored",
        "path": PROJECT_ROOT / "schemas" / "iwxxm" / "{version}" / "examples",
        "description": "Official WMO canonical examples from schemas.wmo.int",
        "products": ["METAR", "SPECI", "TAF", "SIGMET", "AIRMET", "TC_ADVISORY", "VA_ADVISORY", "SPACE_WEATHER", "WAFS", "VONA", "QVACI"],
        "priority": "canonical",
        "versions_covered": ["2023-1", "2025-2", "2025-2RC1", "2025-2RC2"],
        "enabled": True,
        "source_url": "https://schemas.wmo.int/iwxxm/{version}/examples/",
        "examples_count": {
            "2023-1": 50,
            "2025-2": 58
        },
        "validation_notes": "Highest priority - official WMO reference examples with TAC pairs"
    },
    "wmo_translation_pairs": {
        "type": "git_submodule",
        "path": PROJECT_ROOT / "data" / "iwxxm-translation",
        "description": "Official TAC↔IWXXM equivalence pairs from WMO",
        "products": ["METAR", "SPECI", "TAF"],
        "priority": "correctness",
        "versions_covered": ["2023-1", "2025-2"],
        "enabled": True,
        "url": "https://github.com/wmo-im/iwxxm-translation"
    },
    "wmo_iwxxm_examples": {
        "type": "git_submodule",
        "path": PROJECT_ROOT / "schemas" / "iwxxm" / "examples",
        "description": "TT-AvData canonical examples from IWXXM schema repo",
        "products": ["METAR", "SPECI", "TAF", "SIGMET"],
        "priority": "schematron",
        "versions_covered": ["2023-1", "2025-2"],
        "enabled": False,  # Superseded by wmo_canonical_examples
        "url": "https://github.com/wmo-im/iwxxm",
        "deprecation_note": "Use wmo_canonical_examples instead for versioned examples"
    },
    "nws_iwxxm_us": {
        "type": "snapshot_fetch",
        "url": "https://nws.weather.gov/schemas/iwxxm-us/3.0/examples/metars/",
        "snapshot_path": PROJECT_ROOT / "backend" / "test-data" / "external" / "nws-iwxxm-us",
        "description": "NWS operational METAR/SPECI with US extensions",
        "products": ["METAR", "SPECI"],
        "priority": "edge_cases",
        "update_frequency": "weekly",
        "enabled": True,
        "max_samples": 100,  # Limit snapshot size
        "validation_notes": "May contain IWXXM-US extensions not in base schema"
    },
    "aviationweather_api": {
        "type": "live_api_snapshot",
        "url": "https://aviationweather.gov/api/data/metar",
        "snapshot_path": PROJECT_ROOT / "backend" / "test-data" / "external" / "awc-snapshots",
        "description": "Live operational IWXXM from AviationWeather.gov",
        "products": ["METAR", "TAF"],
        "priority": "diversity",
        "update_frequency": "daily",
        "enabled": True,
        "max_samples": 50,  # Daily snapshot limit
        "api_params": {
            "format": "iwxxm",
            "hours": 3,  # Last 3 hours of data
        },
        "validation_notes": "Real-world operational data with full diversity"
    },
    "swim_registry_dwd": {
        "type": "snapshot_fetch",
        "url": "https://eur-registry.swim.aero/services/dwd-metar-iwxxm-10",
        "snapshot_path": PROJECT_ROOT / "backend" / "test-data" / "external" / "swim-dwd",
        "description": "DWD METAR IWXXM (European regional diversity)",
        "products": ["METAR"],
        "priority": "diversity",
        "update_frequency": "weekly",
        "enabled": False,  # Disabled by default (may require auth)
        "max_samples": 30,
        "validation_notes": "European stations, SWIM-wrapped format"
    }
}


def get_corpus_source(name: str) -> Dict[str, Any]:
    """
    Get configuration for a specific test corpus source.

    Args:
        name: Corpus source name (key from TEST_CORPUS_SOURCES)

    Returns:
        Configuration dictionary

    Raises:
        KeyError: If corpus source not found
    """
    if name not in TEST_CORPUS_SOURCES:
        raise KeyError(
            f"Unknown corpus source: {name}. "
            f"Available: {list(TEST_CORPUS_SOURCES.keys())}"
        )
    return TEST_CORPUS_SOURCES[name]


def get_enabled_corpus_sources() -> Dict[str, Dict[str, Any]]:
    """
    Get all enabled test corpus sources.

    Returns:
        Dictionary of enabled corpus sources
    """
    return {
        name: config
        for name, config in TEST_CORPUS_SOURCES.items()
        if config.get("enabled", False)
    }


def get_corpus_sources_by_type(source_type: str) -> Dict[str, Dict[str, Any]]:
    """
    Get corpus sources filtered by type.

    Args:
        source_type: Type filter ("git_submodule", "snapshot_fetch", "live_api_snapshot")

    Returns:
        Dictionary of corpus sources matching the type
    """
    return {
        name: config
        for name, config in TEST_CORPUS_SOURCES.items()
        if config.get("type") == source_type
    }


def get_corpus_sources_by_priority(priority: str) -> Dict[str, Dict[str, Any]]:
    """
    Get corpus sources filtered by priority.

    Args:
        priority: Priority filter ("correctness", "schematron", "edge_cases", "diversity")

    Returns:
        Dictionary of corpus sources matching the priority
    """
    return {
        name: config
        for name, config in TEST_CORPUS_SOURCES.items()
        if config.get("priority") == priority
    }


def get_corpus_path(name: str, version: str = None) -> Path:
    """
    Get the local path for a corpus source's data.

    Args:
        name: Corpus source name
        version: IWXXM version (required for mirrored sources with {version} placeholder)

    Returns:
        Path object to corpus data directory

    Raises:
        KeyError: If corpus source not found
        ValueError: If corpus type doesn't have a local path or version is missing
    """
    config = get_corpus_source(name)

    if config["type"] == "mirrored":
        path_template = str(config["path"])
        if "{version}" in path_template:
            if not version:
                raise ValueError(f"Version required for mirrored corpus: {name}")
            return Path(path_template.format(version=version))
        return config["path"]
    elif config["type"] == "git_submodule":
        return config["path"]
    elif config["type"] in ["snapshot_fetch", "live_api_snapshot"]:
        return config["snapshot_path"]
    else:
        raise ValueError(f"Unknown corpus type: {config['type']}")


def get_all_corpus_sources() -> List[str]:
    """Get list of all corpus source names."""
    return list(TEST_CORPUS_SOURCES.keys())
