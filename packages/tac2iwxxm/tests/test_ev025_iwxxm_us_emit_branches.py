"""Branch coverage for iwxxm-us emit helpers (S032 / EV-025 push gate).

Exercises soft/edge paths not hit by TAC goldens so ``test-unit-tac2iwxxm``
stays at the 95% fail-under threshold.
"""

from __future__ import annotations

from tac2iwxxm.profiles import iwxxm_us as us


def test_lightning_sector_all_quadrants_and_empty_cloud_character() -> None:
    xml = us._observed_lightning_xml(
        {
            "qualitative_distance_href": "http://example/dist",
            "frequency_href": "http://example/freq",
            "type_href": "http://example/type",
            "sector": {"in_all_quadrants": True},
        }
    )
    assert 'inAllQuadrants="true"' in xml
    compass = us._observed_lightning_xml(
        {
            "sector": {"ccw_deg": 10.0, "cw_deg": 90.0},
        }
    )
    assert "extremeCCWDirection" in compass
    assert us._cloud_character_elem("lowCloudCharacter", None, None) == ""


def test_convective_sector_all_quadrants_and_hail_without_diameter() -> None:
    xml = us._convective_cloud_xml(
        {
            "cloud_type_href": "http://example/cb",
            "sector": {"in_all_quadrants": True},
            "direction_of_motion_deg": 180,
        }
    )
    assert 'inAllQuadrants="true"' in xml
    compass = us._convective_cloud_xml(
        {
            "cloud_type_href": "http://example/cb",
            "qualitative_distance_href": "http://example/dist",
            "sector": {"ccw_deg": 0.0, "cw_deg": 45.0},
        }
    )
    assert "extremeCWDirection" in compass
    assert us._hailstone_size_addendum_inner({"hailstone_size": {"size_operator": "ABOVE"}}) == ""


def test_second_location_vis_only_and_measure_nil_float() -> None:
    xml = us._second_location_addendum_inner(
        {
            "observed_at_second_location": {
                "visibility_ft": 1200,
                "visibility_below_sensor_minimum": True,
            }
        }
    )
    assert "visibilityBelowSensorMinimum" in xml
    assert "1200" in xml
    assert 'nilReason="missing"' in us._measure_or_nil("maxTemperature", None, uom="Cel")
    assert "12.5" in us._measure_or_nil("maxTemperature", 12.5, uom="Cel")
    assert "7" in us._measure_or_nil("minTemperature", "7", uom="Cel")


def test_max_min_processed_recent_skip_non_dicts() -> None:
    mm = us._max_min_temperatures_addendum_inner({"max_min_temperatures": ["skip", {"max_c": 10, "min_c": None}]})
    assert "maxMinTemperatures" in mm
    assert 'nilReason="missing"' in mm
    pq = us._processed_quantity_addendum_inner(
        {
            "processed_quantities": [
                "skip",
                {
                    "processed_weather_element_href": "http://e",
                    "value_type_href": "http://t",
                    "processed_value": None,
                    "qualifier": "TRACE",
                },
            ]
        }
    )
    assert "processedQuantity" in pq
    assert "TRACE" in pq
    recent = us._recent_weather_addendum_inner(
        {
            "day": 15,
            "hour": 18,
            "recent_weather_us": [
                "skip",
                {
                    "phenomenon_href": "http://wx",
                    "begin_hour": 17,
                    "end_hour": 18,
                    "begin_minute": 5,
                },
            ],
        }
    )
    assert "RecentWeather" in recent
    assert "2023-06-15T17:05:00Z" in recent


def test_variable_rvr_sensor_flags() -> None:
    below = us._variable_rvr_extension(
        {
            "rvr": {
                "variable": True,
                "min_m": 200,
                "max_m": 600,
                "below_sensor_minimum": True,
            }
        }
    )
    above = us._variable_rvr_extension(
        {
            "rvr": {
                "variable": True,
                "min_m": 200,
                "max_m": 2000,
                "above_sensor_maximum": True,
            }
        }
    )
    assert "belowSensorMinimum" in below
    assert "aboveSensorMaximum" in above


def test_sector_tower_var_vis_and_nil_cloud_character() -> None:
    vis = us._visibility_us_extension(
        {
            "sector_visibility": {
                "visibility_m": 800,
                "direction_deg": 90,
                "below_sensor_minimum": True,
            },
            "tower_visibility": {"visibility_m": 500, "less_than": True},
            "variable_visibility": {
                "minimum_m": 400,
                "maximum_m": 900,
                "below_minimum": True,
            },
        }
    )
    assert "SectorVisibility" in vis
    assert "TowerVisibility" in vis
    assert "VariableVisibility" in vis
    assert 'nilReason="missing"' in us._cloud_character_elem("lowCloudCharacter", None, "missing")
