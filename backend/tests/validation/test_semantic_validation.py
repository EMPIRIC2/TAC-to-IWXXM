"""Tests for semantic validation rules - Task 3.1 & 3.2 & 3.3.

Tests validate meteorological consistency rules for METAR data.
"""

import pytest
from src.validation.semantic_rules import (
    ValidationIssue,
    IssueSeverity,
    TemperatureValidationRule,
    CloudLayerValidationRule,
    VisibilityWeatherValidationRule,
    SemanticValidationEngine,
)


class TestTemperatureValidationRule:
    """Test temperature and dewpoint validation (Task 3.1)."""
    
    @pytest.fixture
    def rule(self):
        """Provide temperature validation rule."""
        return TemperatureValidationRule()
    
    # Valid cases
    def test_valid_temperature_normal_spread(self, rule):
        """Test valid temperature with normal T-Td spread."""
        issues = rule.validate(temperature=15.0, dewpoint=10.0)
        # Should have no errors (spread is 5°C, which is normal)
        assert len([i for i in issues if i.severity == IssueSeverity.ERROR]) == 0
    
    def test_valid_temperature_saturated_air(self, rule):
        """Test valid temperature when air is nearly saturated (T ≈ Td)."""
        issues = rule.validate(temperature=12.0, dewpoint=12.0)
        # Should have no errors (T == Td is valid, indicates saturation/fog)
        assert len([i for i in issues if i.severity == IssueSeverity.ERROR]) == 0
    
    def test_valid_temperature_large_spread(self, rule):
        """Test valid temperature in dry conditions (large T-Td spread)."""
        issues = rule.validate(temperature=25.0, dewpoint=0.0)
        # Should have no errors (spread is 25°C, valid for dry climates)
        assert len([i for i in issues if i.severity == IssueSeverity.ERROR]) == 0
    
    def test_valid_temperature_negative_cold(self, rule):
        """Test valid temperature in cold conditions."""
        issues = rule.validate(temperature=-5.0, dewpoint=-10.0)
        # Should have no errors (valid for cold air)
        assert len([i for i in issues if i.severity == IssueSeverity.ERROR]) == 0
    
    # Invalid cases (critical error)
    def test_invalid_dewpoint_exceeds_temperature(self, rule):
        """Test INVALID case: Dewpoint > Temperature (physically impossible)."""
        issues = rule.validate(temperature=10.0, dewpoint=15.0)
        
        # Should have 1 critical error
        assert len(issues) >= 1
        assert any(i.severity == IssueSeverity.ERROR for i in issues)
        
        error = [i for i in issues if i.severity == IssueSeverity.ERROR][0]
        assert "impossible" in error.message.lower()
        assert "10" in error.actual  # Temperature value
        assert "15" in error.actual  # Dewpoint value
    
    def test_invalid_large_dewpoint_excess(self, rule):
        """Test INVALID case with large deg dewpoint excess."""
        issues = rule.validate(temperature=5.0, dewpoint=25.0)
        
        # Should have 1 critical error
        assert len([i for i in issues if i.severity == IssueSeverity.ERROR]) == 1
    
    # Warnings for unusual but possible cases
    def test_warning_extreme_dry_air(self, rule):
        """Test WARNING: Very dry air (large T-Td spread > 40°C)."""
        issues = rule.validate(temperature=30.0, dewpoint=-15.0)
        
        # Should not have errors, but might have warnings
        assert len([i for i in issues if i.severity == IssueSeverity.ERROR]) == 0
    
    # Missing data cases
    def test_missing_temperature(self, rule):
        """Test with missing temperature - should skip validation."""
        issues = rule.validate(temperature=None, dewpoint=10.0)
        assert len(issues) == 0
    
    def test_missing_dewpoint(self, rule):
        """Test with missing dewpoint - should skip validation."""
        issues = rule.validate(temperature=15.0, dewpoint=None)
        assert len(issues) == 0
    
    def test_missing_both(self, rule):
        """Test with both missing - should skip validation."""
        issues = rule.validate(temperature=None, dewpoint=None)
        assert len(issues) == 0
    
    # Relative humidity calculation
    def test_rh_calculation_saturated(self, rule):
        """Test RH calculation when T = Td (saturated air)."""
        rh = rule.calculate_relative_humidity(temperature=15.0, dewpoint=15.0)
        assert rh >= 95.0  # Should be near 100%
    
    def test_rh_calculation_dry(self, rule):
        """Test RH calculation in dry air."""
        rh = rule.calculate_relative_humidity(temperature=25.0, dewpoint=10.0)
        assert 35.0 <= rh <= 60.0  # Typical for dry conditions
    
    def test_rh_calculation_normal(self, rule):
        """Test RH calculation in normal conditions."""
        rh = rule.calculate_relative_humidity(temperature=20.0, dewpoint=15.0)
        assert 60.0 <= rh <= 80.0  # Typical for moderate conditions


class TestCloudLayerValidationRule:
    """Test cloud layer validation (Task 3.2)."""
    
    @pytest.fixture
    def rule(self):
        """Provide cloud layer validation rule."""
        return CloudLayerValidationRule()
    
    # Valid cloud layer arrangements
    def test_valid_single_layer(self, rule):
        """Test valid single cloud layer."""
        layers = [{"coverage": "BKN", "altitude_m": 1000}]
        issues = rule.validate(layers)
        assert len([i for i in issues if i.severity == IssueSeverity.ERROR]) == 0
    
    def test_valid_layered_increasing_altitude(self, rule):
        """Test valid multiple layers with increasing altitude."""
        layers = [
            {"coverage": "FEW", "altitude_m": 800},
            {"coverage": "SCT", "altitude_m": 2000},
            {"coverage": "OVC", "altitude_m": 5000}
        ]
        issues = rule.validate(layers)
        # Should have no critical errors
        assert len([i for i in issues if i.severity == IssueSeverity.ERROR]) == 0
    
    def test_valid_clear_sky_only(self, rule):
        """Test valid clear sky layer (CLR)."""
        layers = [{"coverage": "CLR", "altitude_m": 0}]
        issues = rule.validate(layers)
        assert len(issues) == 0
    
    def test_valid_sky_clear_equivalent(self, rule):
        """Test valid SKC (equivalent to CLR)."""
        layers = [{"coverage": "SKC", "altitude_m": 0}]
        issues = rule.validate(layers)
        assert len(issues) == 0
    
    # Invalid arrangements
    def test_invalid_clear_sky_with_other_layers(self, rule):
        """Test INVALID: CLR coexists with other layers."""
        layers = [
            {"coverage": "CLR", "altitude_m": 0},
            {"coverage": "FEW", "altitude_m": 1000}
        ]
        issues = rule.validate(layers)
        
        # Should have at least 1 error about clear sky exclusivity
        assert len([i for i in issues if i.severity == IssueSeverity.ERROR]) >= 1
    
    def test_invalid_skc_with_other_layers(self, rule):
        """Test INVALID: SKC coexists with other layers."""
        layers = [
            {"coverage": "SKC", "altitude_m": 0},
            {"coverage": "OVC", "altitude_m": 2000}
        ]
        issues = rule.validate(layers)
        assert len([i for i in issues if i.severity == IssueSeverity.ERROR]) >= 1
    
    # Empty input
    def test_empty_cloud_layers(self, rule):
        """Test with no cloud layers - skip validation."""
        issues = rule.validate([])
        assert len(issues) == 0


class TestVisibilityWeatherValidationRule:
    """Test visibility-weather consistency validation (Task 3.3)."""
    
    @pytest.fixture
    def rule(self):
        """Provide visibility-weather validation rule."""
        return VisibilityWeatherValidationRule()
    
    # Valid combinations
    def test_valid_fog_low_visibility(self, rule):
        """Test valid: Fog with visibility < 1000m."""
        issues = rule.validate(visibility_meters=500, weather_phenomena=["FG"])
        # Should have no critical errors
        assert len([i for i in issues if i.severity == IssueSeverity.ERROR]) == 0
    
    def test_valid_rain_moderate_visibility(self, rule):
        """Test valid: Rain with typical visibility range."""
        issues = rule.validate(visibility_meters=3000, weather_phenomena=["RA"])
        # Should have no errors
        assert len([i for i in issues if i.severity == IssueSeverity.ERROR]) == 0
    
    def test_valid_clear_no_weather(self, rule):
        """Test valid: Good visibility, no weather phenomena."""
        issues = rule.validate(visibility_meters=10000, weather_phenomena=[])
        assert len(issues) == 0
    
    # Invalid combinations
    def test_invalid_fog_high_visibility(self, rule):
        """Test INVALID: Fog reported with high visibility."""
        issues = rule.validate(visibility_meters=5000, weather_phenomena=["FG"])
        
        # Should have at least a warning/error
        assert len(issues) >= 1
        # Fog > 1000m is unusual
        assert any(i.severity in [IssueSeverity.ERROR, IssueSeverity.WARNING] 
                  for i in issues)
    
    def test_invalid_snow_no_low_visibility(self, rule):
        """Test INVALID: Snow with unusually high visibility."""
        issues = rule.validate(visibility_meters=8000, weather_phenomena=["SN"])
        
        # Should have warning about snow visibility
        assert len(issues) >= 1
    
    # Missing data
    def test_missing_visibility(self, rule):
        """Test with missing visibility - skip validation."""
        issues = rule.validate(visibility_meters=None, weather_phenomena=["RA"])
        assert len(issues) == 0
    
    def test_missing_weather_phenomena(self, rule):
        """Test with missing weather phenomena - skip validation."""
        issues = rule.validate(visibility_meters=5000, weather_phenomena=[])
        assert len(issues) == 0
    
    def test_unknown_weather_phenomenon(self, rule):
        """Test with unknown weather code - skip that phenomenon."""
        issues = rule.validate(
            visibility_meters=5000,
            weather_phenomena=["XX"]  # Unknown code
        )
        # Should skip unknown code, no issues
        assert len(issues) == 0


class TestSemanticValidationEngine:
    """Test the complete semantic validation engine."""
    
    @pytest.fixture
    def engine(self):
        """Provide validation engine."""
        return SemanticValidationEngine()
    
    def test_engine_temperature_validation(self, engine):
        """Test engine runs temperature validation."""
        issues = engine.validate_metar_data(
            temperature=10.0,
            dewpoint=15.0  # Invalid: Td > T
        )
        
        assert len([i for i in issues if i.severity == IssueSeverity.ERROR]) >= 1
    
    def test_engine_cloud_validation(self, engine):
        """Test engine runs cloud validation."""
        cloud_layers = [
            {"coverage": "CLR", "altitude_m": 0},
            {"coverage": "FEW", "altitude_m": 1000}  # Invalid: CLR with others
        ]
        
        issues = engine.validate_metar_data(cloud_layers=cloud_layers)
        assert len([i for i in issues if i.severity == IssueSeverity.ERROR]) >= 1
    
    def test_engine_visibility_validation(self, engine):
        """Test engine runs visibility validation."""
        issues = engine.validate_metar_data(
            visibility_meters=5000,
            weather_phenomena=["FG"]  # Invalid: Fog > 1000m
        )
        
        assert len(issues) >= 1
    
    def test_engine_all_validations(self, engine):
        """Test engine with all data at once."""
        issues = engine.validate_metar_data(
            temperature=15.0,
            dewpoint=10.0,  # Valid
            cloud_layers=[
                {"coverage": "BKN", "altitude_m": 1000},
                {"coverage": "OVC", "altitude_m": 3000}
            ],  # Valid
            visibility_meters=3000,
            weather_phenomena=["RA"]  # Valid
        )
        
        # All valid, so no errors
        assert len([i for i in issues if i.severity == IssueSeverity.ERROR]) == 0
    
    def test_engine_generate_report(self, engine):
        """Test engine generates proper report."""
        issues = engine.validate_metar_data(
            temperature=10.0,
            dewpoint=15.0  # Invalid
        )
        
        report = engine.generate_report(
            issues,
            station_id="KJFK",
            raw_metar="METAR KJFK..."
        )
        
        assert report["station_id"] == "KJFK"
        assert "METAR KJFK" in report["raw_metar"]
        assert report["is_valid"] == False
        assert report["summary"]["errors"] >= 1


class TestIntegrationWithTestData:
    """Integration tests using real test case data."""
    
    @pytest.fixture
    def engine(self):
        """Provide validation engine."""
        return SemanticValidationEngine()
    
    def test_validate_typical_metar(self, engine):
        """Test typical well-formed METAR data."""
        # METAR KJFK 151851Z 31008KT 10SM FEW250 M04/M17 A3034 RMK AO2 SLP279 T10441172
        issues = engine.validate_metar_data(
            temperature=-4.0,    # -04°C
            dewpoint=-17.0,      # -17°C  
            cloud_layers=[
                {"coverage": "FEW", "altitude_m": 7620}  # 250 × 30.48m
            ],
            visibility_meters=16000,  # 10 statute miles
            weather_phenomena=[]  # No weather
        )
        
        # Should pass all validation
        assert all(i.severity != IssueSeverity.ERROR for i in issues)
    
    def test_validate_metar_with_rain(self, engine):
        """Test METAR with rain."""
        # METAR FGSL 151300Z 18006KT 3000 RA SHRA BKN010 16/12 Q1012
        issues = engine.validate_metar_data(
            temperature=16.0,
            dewpoint=12.0,
            cloud_layers=[
                {"coverage": "BKN", "altitude_m": 300}  # 10 × 30m
            ],
            visibility_meters=3000,
            weather_phenomena=["RA", "SHRA"]  # Rain, rain showers
        )
        
        # Should pass - all consistent
        assert all(i.severity != IssueSeverity.ERROR for i in issues)
