"""
Test Station Configuration

Curated list of ICAO stations for comprehensive IWXXM testing, selected to
maximize edge case coverage and geographic diversity.
"""

from typing import Dict, List

# Curated test stations organized by category
TEST_STATIONS: Dict[str, List[str]] = {
    "us_metar_edge_cases": [
        "KJFK",  # New York JFK - High-traffic, complex remarks (AO2, SLP, T-groups)
        "KORD",  # Chicago O'Hare - Midwest, wind shear, RVR, thunderstorms
        "KSFO",  # San Francisco - Coastal fog, complex TAF, marine layer
        "PANC",  # Anchorage - Arctic, extreme temps (-40°C), ice fog
        "PHNL",  # Honolulu - Tropical, volcanic ash proximity, trade winds
        "KDFW",  # Dallas/Fort Worth - Thunderstorm corridor, convective activity
        "KDEN",  # Denver - High elevation (5430 ft), mountain wave, blowing snow
        "KBOS",  # Boston Logan - Coastal, wind variability, nor'easter patterns
        "KMIA",  # Miami - Tropical, hurricane corridor, heavy convection
        "KSEA",  # Seattle - Pacific Northwest, persistent stratus, drizzle
    ],

    "international_diversity": [
        "EGLL",  # London Heathrow - European major hub, fog, variable vis
        "LFPG",  # Paris Charles de Gaulle - European, CAVOK usage patterns
        "EDDF",  # Frankfurt - DWD source, European reporting standards
        "LSZH",  # Zurich - Mountain aerodrome, complex terrain, foehn winds
        "YSSY",  # Sydney - Southern Hemisphere, Australian conventions
        "RJTT",  # Tokyo Narita - Asian-Pacific, typhoon corridor
        "FAOR",  # Johannesburg - African (high elevation 5558 ft), SAA standards
        "SBGR",  # São Paulo Guarulhos - South American, tropical convection
        "OMDB",  # Dubai - Desert, extreme heat, dust/sand storms, shamal winds
        "EIDW",  # Dublin - Atlantic, frequent precipitation, Celtic Sea patterns
    ],

    "extreme_conditions": [
        "CYQX",  # Gander, Newfoundland - Oceanic, severe icing, fog
        "BIKF",  # Reykjavik - Volcanic ash, extreme wind (>50kt common)
        "NZCH",  # Christchurch - Southern Hemisphere, antarctic air masses
        "PAFA",  # Fairbanks - Extreme arctic (-50°C), ice crystals, low vis
        "WSSS",  # Singapore Changi - Equatorial, heavy convection, CB activity
        "VHHH",  # Hong Kong - Mountainous terrain, typhoons, tropical
        "MMMX",  # Mexico City - Very high elevation (7350 ft), thin air
        "EKCH",  # Copenhagen - Baltic, frequent low stratus, fog
    ],

    "coastal_and_marine": [
        "KBWI",  # Baltimore - Coastal fog, marine layer
        "KPDX",  # Portland - River valley, marine influence
        "LIRF",  # Rome Fiumicino - Mediterranean, sea breeze
        "LPPT",  # Lisbon - Atlantic coast, Nortada winds
        "ZBAA",  # Beijing Capital - Continental, dust, pollution visibility
    ],

    "mountain_and_terrain": [
        "KATL",  # Atlanta - Piedmont, thunderstorm alley
        "KSNA",  # Orange County - Santa Ana winds, terrain challenges
        "PANC",  # Anchorage - Already in arctic, but also terrain
        "LIMC",  # Milan Malpensa - Po Valley, fog, Alps proximity
    ],

    "minimal_quick_test": [
        "KJFK",  # US major
        "EGLL",  # European major
        "YSSY",  # Australian major
        "RJTT",  # Asian major
    ]
}

# Station metadata for context (optional use)
STATION_METADATA: Dict[str, Dict[str, str]] = {
    "KJFK": {
        "name": "New York John F. Kennedy International",
        "country": "US",
        "elevation_ft": "13",
        "notes": "High-traffic, complex remarks, detailed runway info"
    },
    "PANC": {
        "name": "Anchorage Ted Stevens International",
        "country": "US",
        "elevation_ft": "152",
        "notes": "Arctic conditions, extreme temps, ice fog"
    },
    "EGLL": {
        "name": "London Heathrow",
        "country": "GB",
        "elevation_ft": "83",
        "notes": "European reporting, fog, wind shear"
    },
    "MMMX": {
        "name": "Mexico City International",
        "country": "MX",
        "elevation_ft": "7350",
        "notes": "Very high elevation, pressure altitude concerns"
    },
    "BIKF": {
        "name": "Reykjavik Keflavik International",
        "country": "IS",
        "elevation_ft": "171",
        "notes": "Volcanic ash, extreme winds, oceanic"
    },
}


def get_test_stations(category: str = "all") -> List[str]:
    """
    Get list of test stations by category.

    Args:
        category: Station category ("us_metar_edge_cases", "international_diversity",
                 "extreme_conditions", "coastal_and_marine", "mountain_and_terrain",
                 "minimal_quick_test", "all")

    Returns:
        List of ICAO station identifiers
    """
    if category == "all":
        # Return all unique stations (flatten and deduplicate)
        all_stations = []
        for stations in TEST_STATIONS.values():
            all_stations.extend(stations)
        return list(set(all_stations))

    return TEST_STATIONS.get(category, [])


def get_station_categories() -> List[str]:
    """Get list of available station categories."""
    return list(TEST_STATIONS.keys())


def get_station_metadata(icao: str) -> Dict[str, str]:
    """
    Get metadata for a specific station.

    Args:
        icao: ICAO station identifier

    Returns:
        Metadata dictionary (empty if not found)
    """
    return STATION_METADATA.get(icao, {})


def get_all_test_stations_with_metadata() -> Dict[str, Dict[str, str]]:
    """
    Get all test stations with their metadata.

    Returns:
        Dictionary mapping ICAO codes to metadata
    """
    all_icao = get_test_stations("all")
    return {
        icao: get_station_metadata(icao)
        for icao in all_icao
    }


def count_stations_by_category() -> Dict[str, int]:
    """
    Count stations in each category.

    Returns:
        Dictionary mapping category names to station counts
    """
    return {
        category: len(stations)
        for category, stations in TEST_STATIONS.items()
    }
