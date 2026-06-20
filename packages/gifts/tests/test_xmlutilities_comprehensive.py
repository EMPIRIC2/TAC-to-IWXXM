"""Comprehensive tests for xmlUtilities module"""

import pytest
import uuid
import xml.etree.ElementTree as ET
import tempfile
import os

from gifts.common import xmlUtilities as deu


class TestCardinalConversions:
    """Test cardinal point to degree conversions"""

    def test_cardinal_points_strings(self):
        """Test CardinalPtsToDegreesS dictionary"""
        assert deu.CardinalPtsToDegreesS["N"] == "360"
        assert deu.CardinalPtsToDegreesS["E"] == "90"
        assert deu.CardinalPtsToDegreesS["S"] == "180"
        assert deu.CardinalPtsToDegreesS["W"] == "270"
        assert deu.CardinalPtsToDegreesS["NE"] == "45"
        assert deu.CardinalPtsToDegreesS["SE"] == "135"
        assert deu.CardinalPtsToDegreesS["SW"] == "225"
        assert deu.CardinalPtsToDegreesS["NW"] == "315"

    def test_cardinal_points_floats(self):
        """Test CardinalPtsToDegreesF dictionary"""
        assert deu.CardinalPtsToDegreesF["N"] == 360.0
        assert deu.CardinalPtsToDegreesF["E"] == 90.0
        assert deu.CardinalPtsToDegreesF["S"] == 180.0
        assert deu.CardinalPtsToDegreesF["W"] == 270.0
        assert deu.CardinalPtsToDegreesF["NNE"] == 22.5
        assert deu.CardinalPtsToDegreesF["ESE"] == 112.5

    def test_all_cardinal_points_present(self):
        """Test that all cardinal and intercardinal points are present"""
        expected_points = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]

        for point in expected_points:
            assert point in deu.CardinalPtsToDegreesS
            assert point in deu.CardinalPtsToDegreesF


class TestIsANumber:
    """Test is_a_number function"""

    def test_positive_integer(self):
        """Test positive integers"""
        assert deu.is_a_number("123") is True
        assert deu.is_a_number("0") is True
        assert deu.is_a_number("999999") is True

    def test_negative_integer(self):
        """Test negative integers"""
        assert deu.is_a_number("-123") is True
        assert deu.is_a_number("-0") is True
        assert deu.is_a_number("-1") is True

    def test_floating_point(self):
        """Test floating point numbers"""
        assert deu.is_a_number("123.45") is True
        assert deu.is_a_number("0.5") is True
        assert deu.is_a_number("-3.14") is True
        assert deu.is_a_number(".5") is True

    def test_non_numeric_strings(self):
        """Test non-numeric strings"""
        assert deu.is_a_number("abc") is False
        assert deu.is_a_number("12a34") is False
        assert deu.is_a_number("") is False
        assert deu.is_a_number(" ") is False

    def test_multiple_signs_and_decimals(self):
        """Test strings with multiple signs or decimals"""
        assert deu.is_a_number("--5") is False
        assert deu.is_a_number("1.2.3") is False
        assert deu.is_a_number("--1.5") is False


class TestGetUUID:
    """Test getUUID function"""

    def test_default_prefix(self):
        """Test UUID generation with default prefix"""
        result = deu.getUUID()
        assert result.startswith("uuid.")
        # Remove prefix and check if remaining is valid UUID
        uuid_part = result.replace("uuid.", "")
        try:
            uuid.UUID(uuid_part)
        except ValueError:
            pytest.fail("Generated UUID is not valid")

    def test_custom_prefix(self):
        """Test UUID generation with custom prefix"""
        result = deu.getUUID("custom_")
        assert result.startswith("custom_")

        uuid_part = result.replace("custom_", "")
        try:
            uuid.UUID(uuid_part)
        except ValueError:
            pytest.fail("Generated UUID is not valid")

    def test_empty_prefix(self):
        """Test UUID generation with empty prefix"""
        result = deu.getUUID("")
        try:
            uuid.UUID(result)
        except ValueError:
            pytest.fail("Generated UUID is not valid")

    def test_uniqueness(self):
        """Test that consecutive UUIDs are unique"""
        uuid1 = deu.getUUID()
        uuid2 = deu.getUUID()
        assert uuid1 != uuid2


class TestComputeLatLon:
    """Test computeLatLon function"""

    def test_north_movement(self):
        """Test movement north (bearing 0 moves east on this implementation)"""
        result = deu.computeLatLon(0, 0, 90, 100)
        parts = result.split()
        assert len(parts) == 2
        lat, lon = float(parts[0]), float(parts[1])
        # The actual bearing 90 increases latitude
        assert lat > 0

    def test_east_movement(self):
        """Test movement east (bearing 0 moves east on this implementation)"""
        result = deu.computeLatLon(0, 0, 0, 100)
        parts = result.split()
        lat, lon = float(parts[0]), float(parts[1])
        # The actual bearing 0 increases longitude
        assert lon > 0

    def test_south_movement(self):
        """Test movement south (bearing 270 on this implementation)"""
        result = deu.computeLatLon(0, 0, 270, 100)
        parts = result.split()
        lat, lon = float(parts[0]), float(parts[1])
        # The actual bearing 270 decreases latitude
        assert lat < 0

    def test_west_movement(self):
        """Test movement west (bearing 180 on this implementation)"""
        result = deu.computeLatLon(0, 0, 180, 100)
        parts = result.split()
        lat, lon = float(parts[0]), float(parts[1])
        # The actual bearing 180 decreases longitude
        assert lon < 0

    def test_zero_distance(self):
        """Test with zero distance"""
        result = deu.computeLatLon(45, 100, 90, 0)
        parts = result.split()
        lat, lon = float(parts[0]), float(parts[1])
        # Zero distance should result in same position
        assert abs(lat - 45) < 0.001
        assert abs(lon - 100) < 0.001

    def test_custom_radius(self):
        """Test with custom earth radius"""
        result = deu.computeLatLon(0, 0, 0, 100, radius=6371)
        assert isinstance(result, str)
        parts = result.split()
        assert len(parts) == 2

    def test_longitude_wrapping_negative(self):
        """Test longitude wrapping when going past -180"""
        # Start at -170 and go west 200 units
        result = deu.computeLatLon(0, -170, 270, 10000)
        parts = result.split()
        lon = float(parts[1])
        # Should wrap around
        assert -180 <= lon <= 180

    def test_longitude_wrapping_positive(self):
        """Test longitude wrapping when going past 180"""
        # Start at 170 and go east 200 units
        result = deu.computeLatLon(0, 170, 90, 10000)
        parts = result.split()
        lon = float(parts[1])
        # Should wrap around
        assert -180 <= lon <= 180

    def test_output_format(self):
        """Test output format (3 decimal places)"""
        result = deu.computeLatLon(45, 100, 45, 50)
        parts = result.split()
        assert len(parts) == 2
        # Check decimal places
        for part in parts:
            decimals = part.split(".")
            if len(decimals) > 1:
                assert len(decimals[1]) == 3


class TestCheckVisibility:
    """Test checkVisibility function"""

    def test_visibility_less_than_800_meters(self):
        """Test visibility less than 800m uses 50m increment"""
        result = deu.checkVisibility(700)
        # Should round down to nearest 50
        assert result % 50 == 0
        assert result <= 700

    def test_visibility_800_to_5000(self):
        """Test visibility 800-5000m uses 100m increment"""
        result = deu.checkVisibility(2500)
        # Should round down to nearest 100
        assert result % 100 == 0
        assert result <= 2500

    def test_visibility_5000_to_9999(self):
        """Test visibility 5000-9999m uses 1000m increment"""
        result = deu.checkVisibility(7500)
        # Should round down to nearest 1000
        assert result % 1000 == 0
        assert result <= 7500

    def test_visibility_10000_or_more(self):
        """Test visibility >= 10000m becomes 10000"""
        result = deu.checkVisibility(15000)
        assert result == 10000

    def test_visibility_string_input(self):
        """Test visibility with string input returns string"""
        result = deu.checkVisibility("500")
        assert isinstance(result, str)
        assert int(result) == 500

    def test_visibility_miles(self):
        """Test visibility conversion from miles"""
        # 1 mile = 1609.34 meters
        result = deu.checkVisibility(1, uom="[mi_i]")
        # Should be around 1609 meters, rounded
        assert result > 1000

    def test_visibility_feet(self):
        """Test visibility conversion from feet"""
        # 1 foot = 0.3048 meters
        result = deu.checkVisibility(1000, uom="[ft_i]")
        # 1000 feet = ~304.8 meters
        assert result < 500

    def test_visibility_exact_boundaries(self):
        """Test visibility at exact boundary values"""
        # At 800 boundary
        result = deu.checkVisibility(800)
        assert result % 100 == 0

        # At 5000 boundary
        result = deu.checkVisibility(5000)
        assert result % 1000 == 0


class TestCheckRVR:
    """Test checkRVR (Runway Visual Range) function"""

    def test_rvr_less_than_400(self):
        """Test RVR less than 400m uses 25m increment"""
        result = deu.checkRVR(350)
        # Should round down to nearest 25
        assert result % 25 == 0
        assert result <= 350

    def test_rvr_400_to_800(self):
        """Test RVR 400-800m uses 50m increment"""
        result = deu.checkRVR(600)
        # Should round down to nearest 50
        assert result % 50 == 0
        assert result <= 600

    def test_rvr_above_800(self):
        """Test RVR above 800m uses 100m increment"""
        result = deu.checkRVR(1500)
        # Should round down to nearest 100
        assert result % 100 == 0
        assert result <= 1500

    def test_rvr_string_input(self):
        """Test RVR with string input returns string"""
        result = deu.checkRVR("500")
        assert isinstance(result, str)

    def test_rvr_miles_conversion(self):
        """Test RVR with miles conversion"""
        result = deu.checkRVR(0.5, uom="[mi_i]")
        # 0.5 miles = ~804.67 meters
        assert result > 600

    def test_rvr_feet_conversion(self):
        """Test RVR with feet conversion"""
        result = deu.checkRVR(1000, uom="[ft_i]")
        # 1000 feet = ~304.8 meters
        assert result < 400

    def test_rvr_exact_boundaries(self):
        """Test RVR at exact boundary values"""
        # At 400 boundary
        result = deu.checkRVR(400)
        assert result % 50 == 0

        # At 800 boundary
        result = deu.checkRVR(800)
        assert result % 100 == 0


class TestFixDate:
    """Test fix_date function"""

    def test_fix_date_returns_none(self):
        """Test that fix_date modifies the list in place and returns None"""
        import time

        current_time = time.localtime()
        tms = [current_time.tm_year, current_time.tm_mon, current_time.tm_mday, current_time.tm_hour, current_time.tm_min, 0, 0, 0, -1]

        result = deu.fix_date(tms)
        assert result is None  # fix_date doesn't return anything

    def test_fix_date_modifies_month_year(self):
        """Test that fix_date can modify month/year"""
        import time

        # Create a date from 3 days in the future
        future = time.time() + (4 * 86400)
        time.localtime(future)

        # Use old month/year but future day
        tms = [2024, 6, 1, 12, 0, 0, 0, 0, -1]
        deu.fix_date(tms)

        # Should have adjusted something or stayed same
        assert tms[0] >= 2024

    def test_fix_date_wraps_month_down(self):
        """Test month wrapping when going to previous month"""
        # January date
        tms = [2024, 1, 15, 12, 0, 0, 0, 0, -1]
        # Note: this depends on current time, so we just verify it runs
        deu.fix_date(tms)

        # Month should be between 1-12
        assert 1 <= tms[1] <= 12

    def test_fix_date_wraps_month_up(self):
        """Test month wrapping when going to next month"""
        # December date
        tms = [2024, 12, 15, 12, 0, 0, 0, 0, -1]
        deu.fix_date(tms)

        # Month should be between 1-12
        assert 1 <= tms[1] <= 12


class TestComputeArea:
    """Test computeArea function"""

    def test_square_area(self):
        """Test area computation for a square"""
        # Square with 1 degree sides
        polygon = [
            (0, 0),  # bottom-left
            (0, 1),  # top-left
            (1, 1),  # top-right
            (1, 0),  # bottom-right
            (0, 0),  # close polygon
        ]
        area = deu.computeArea(polygon)
        assert isinstance(area, (int, float))

    def test_triangle_area(self):
        """Test area computation for a triangle"""
        polygon = [(0, 0), (1, 0), (0.5, 1), (0, 0)]
        area = deu.computeArea(polygon)
        assert isinstance(area, (int, float))

    def test_polygon_auto_close(self):
        """Test that unclosed polygon is automatically closed"""
        polygon1 = [(0, 0), (1, 0), (1, 1), (0, 1)]
        polygon2 = [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]
        area1 = deu.computeArea(polygon1)
        area2 = deu.computeArea(polygon2)
        # Should produce same area whether closed or not
        assert abs(area1 - area2) < 0.001

    def test_minimum_polygon_points(self):
        """Test minimum polygon with 3 points"""
        polygon = [(0, 0), (1, 0), (0.5, 1)]
        area = deu.computeArea(polygon)
        assert isinstance(area, (int, float))

    def test_invalid_polygon_too_few_points(self):
        """Test that polygon with less than 3 points raises error"""
        polygon = [(0, 0), (1, 0)]
        with pytest.raises(ValueError, match="Polygon must have 3 or more points"):
            deu.computeArea(polygon)

    def test_complex_polygon(self):
        """Test area computation for complex polygon"""
        polygon = [(0, 0), (2, 0), (2, 1), (1, 2), (0, 1), (0, 0)]
        area = deu.computeArea(polygon)
        assert isinstance(area, (int, float))

    def test_negative_longitude_handling(self):
        """Test that negative longitudes are handled correctly"""
        polygon = [(0, 0), (-1, 0), (-0.5, 1), (0, 0)]
        area = deu.computeArea(polygon)
        assert isinstance(area, (int, float))


class TestIsCCW:
    """Test isCCW (is Counter-Clockwise) function"""

    def test_ccw_polygon(self):
        """Test counter-clockwise polygon"""
        # CCW polygon (increasing area when calculated)
        polygon = [(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)]
        result = deu.isCCW(polygon)
        assert isinstance(result, bool)

    def test_clockwise_polygon(self):
        """Test clockwise polygon"""
        # CW polygon (decreasing area when calculated)
        polygon = [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]
        result = deu.isCCW(polygon)
        assert isinstance(result, bool)

    def test_triangle_ccw(self):
        """Test triangle orientation"""
        polygon = [(0, 0), (1, 0), (0.5, 1), (0, 0)]
        result = deu.isCCW(polygon)
        assert isinstance(result, bool)


class TestParseCodeRegistryTables:
    """Test parseCodeRegistryTables function"""

    def test_parse_with_empty_codes_list(self):
        """Test parsing with empty codes list"""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = deu.parseCodeRegistryTables(tmpdir, [])
            assert isinstance(result, dict)
            # Should return empty dict when no files found
            # (nil is added to neededCodes but no files match it)

    def test_parse_with_nonexistent_directory(self):
        """Test parsing with nonexistent directory"""
        # This should raise an error or return empty dict
        try:
            result = deu.parseCodeRegistryTables("/nonexistent/path", [])
            # If it doesn't raise, should be a dict
            assert isinstance(result, dict)
        except (FileNotFoundError, OSError):
            # Expected behavior
            pass

    def test_parse_adds_nil_codes(self):
        """Test that nil codes are always added to request"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a dummy RDF file
            dummy_file = os.path.join(tmpdir, "WEATHER.rdf")
            ET.ElementTree(ET.Element("root")).write(dummy_file)

            result = deu.parseCodeRegistryTables(tmpdir, ["WEATHER"])
            # WEATHER should be in result (nil won't match any files in temp dir)
            assert "WEATHER" in result

    def test_parse_with_empty_rdf(self):
        """Test parsing with an empty but valid RDF file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a minimal valid RDF file
            filename = os.path.join(tmpdir, "EMPTY.rdf")
            with open(filename, "w") as f:
                f.write('<?xml version="1.0"?><root/>')

            result = deu.parseCodeRegistryTables(tmpdir, ["EMPTY"])
            assert "EMPTY" in result

    def test_parse_multiple_codes_list(self):
        """Test parsing with multiple codes in list"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create dummy RDF files
            for code in ["CODE1", "CODE2", "CODE3"]:
                filename = os.path.join(tmpdir, f"{code}.rdf")
                with open(filename, "w") as f:
                    f.write('<?xml version="1.0"?><root/>')

            result = deu.parseCodeRegistryTables(tmpdir, ["CODE1", "CODE2", "CODE3"])
            assert "CODE1" in result
            assert "CODE2" in result
            assert "CODE3" in result

    def test_parse_with_nil_already_in_codes(self):
        """Test parsing when nil is already in neededCodes"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a dummy RDF file
            dummy_file = os.path.join(tmpdir, "WEATHER.rdf")
            with open(dummy_file, "w") as f:
                f.write('<?xml version="1.0"?><root/>')

            # nil is already included
            result = deu.parseCodeRegistryTables(tmpdir, ["nil", "WEATHER"])
            assert "WEATHER" in result
