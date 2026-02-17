"""Semantic validation rules for meteorological data consistency.

Validates that METAR data follows physical and meteorological principles,
independent of XML schema validation. Focuses on scientific accuracy.
"""

from dataclasses import dataclass
from typing import Optional, List
from enum import Enum


class IssueSeverity(str, Enum):
    """Severity levels for validation issues."""
    ERROR = "error"      # Data physically impossible
    WARNING = "warning"  # Unusual but possible
    INFO = "info"        # Note: Data seems inconsistent but could be valid


@dataclass
class ValidationIssue:
    """Represents a validation issue found in meteorological data."""
    
    rule_name: str
    severity: IssueSeverity
    message: str
    expected: str
    actual: str
    affected_field: str
    suggested_fix: Optional[str] = None
    
    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.rule_name}: {self.message}"


class TemperatureValidationRule:
    """Validate temperature and dewpoint relationships.
    
    In real-world meteorology, dewpoint temperature can NEVER exceed
    air temperature. This is fundamental thermodynamics.
    
    Dewpoint is the temperature to which air must be cooled (at constant
    pressure and humidity) to become saturated with water vapor. By definition,
    it cannot exceed the actual temperature.
    
    Physics Check: Td ≤ T (always)
    Spacing Check: Typically T - Td between 0°C and ~30°C
    """
    
    def __init__(self):
        """Initialize temperature validation rule."""
        self.rule_name = "temperature_dewpoint_relationship"
        self.min_dew_spread = 0.0    # °C, minimum T - Td
        self.max_dew_spread = 50.0   # °C, maximum realistic T - Td
    
    def validate(
        self,
        temperature: Optional[float],
        dewpoint: Optional[float]
    ) -> List[ValidationIssue]:
        """Validate temperature and dewpoint relationship.
        
        Args:
            temperature: Air temperature in °C
            dewpoint: Dewpoint temperature in °C
        
        Returns:
            List of validation issues (empty if valid)
        """
        issues = []
        
        # Skip validation if either value missing
        if temperature is None or dewpoint is None:
            return issues
        
        # Check 1: Dewpoint cannot exceed temperature (fundamental rule)
        if dewpoint > temperature:
            issues.append(ValidationIssue(
                rule_name=self.rule_name,
                severity=IssueSeverity.ERROR,
                message=f"Temperature ({temperature}°C) < Dewpoint ({dewpoint}°C): "
                       f"IMPOSSIBLE - dewpoint cannot exceed temperature",
                expected=f"Temperature ≥ Dewpoint",
                actual=f"T={temperature}°C, Td={dewpoint}°C",
                affected_field="temperature, dewpoint",
                suggested_fix=f"Data error: Swap values (T={dewpoint}°C, Td={temperature}°C)"
            ))
            return issues
        
        # Check 2: Reasonable spread between T and Td
        spread = temperature - dewpoint
        
        if spread < self.min_dew_spread:
            issues.append(ValidationIssue(
                rule_name=self.rule_name,
                severity=IssueSeverity.WARNING,
                message=f"Very small T-Td spread ({spread:.1f}°C): "
                       f"Indicates near-saturation (unusual but possible)",
                expected=f"T - Td typically ≥ {self.min_dew_spread}°C",
                actual=f"T-Td = {spread:.1f}°C",
                affected_field="temperature, dewpoint",
                suggested_fix="Verify data source for accuracy"
            ))
        
        if spread > self.max_dew_spread:
            issues.append(ValidationIssue(
                rule_name=self.rule_name,
                severity=IssueSeverity.WARNING,
                message=f"Very large T-Td spread ({spread:.1f}°C): "
                       f"Indicates very dry air (possible in deserts/upper atmosphere)",
                expected=f"T - Td typically ≤ {self.max_dew_spread}°C",
                actual=f"T-Td = {spread:.1f}°C",
                affected_field="temperature, dewpoint",
                suggested_fix="Verify high-altitude or desert station"
            ))
        
        return issues
    
    def calculate_relative_humidity(
        self,
        temperature: float,
        dewpoint: float
    ) -> float:
        """Calculate approximate relative humidity from T and Td.
        
        Uses Magnus formula approximation.
        
        Args:
            temperature: Air temperature in °C
            dewpoint: Dewpoint temperature in °C
        
        Returns:
            Relative humidity as percentage (0-100)
        """
        # Magnus formula coefficients
        a = 17.27
        b = 237.7  # °C
        
        alpha = ((a * temperature) / (b + temperature)) - ((a * dewpoint) / (b + dewpoint))
        rh = 100.0 * (2.71828 ** (-alpha))  # e^(-alpha)
        
        return max(0.0, min(100.0, rh))


class CloudLayerValidationRule:
    """Validate cloud layer ordering and consistency (Task 3.2).
    
    Cloud layers follow atmospheric physics:
    1. Bases increase with altitude (lower clouds below upper clouds)
    2. Coverage non-increasing upward (can't have 100% clouds, then clear sky)
    3. Clear sky rules (CLR/SKC) are mutually exclusive with other layers
    4. Altitudes within reasonable range (100m to 30km)
    5. Gap analysis between layers (detect unusual patterns)
    6. Coverage-altitude relationships (realistic for conditions)
    """
    
    # Coverage hierarchy (lower = more sky visible)
    COVERAGE_RANK = {
        "CLR": 0,    # Clear (SKC code equivalent)
        "SKC": 0,    # Sky Clear
        "FEW": 1,    # 1-2 oktas (12.5-25%)
        "SCT": 2,    # 3-4 oktas (37.5-50%)
        "BKN": 3,    # 5-7 oktas (62.5-87.5%)
        "OVC": 4,    # 8 oktas (100%)
    }
    
    # Altitude constraints (in meters)
    MIN_ALTITUDE_M = 100       # Minimum reported cloud base
    MAX_ALTITUDE_M = 30000     # Maximum reportable altitude (50,000 ft)
    TYPICAL_MAX_M = 6000       # Typical max for surface obs (~20,000 ft)
    
    # Gap analysis thresholds
    SMALL_GAP_M = 500          # Small gap between layers (< 500m)
    LARGE_GAP_M = 3000         # Large gap (> 3km)
    EXTREME_GAP_M = 8000       # Extreme gap (> 8km)
    
    def __init__(self):
        """Initialize cloud layer validation rule."""
        self.rule_name = "cloud_layer_consistency"
    
    def _check_altitude_validity(
        self,
        layers: List[dict]
    ) -> List[ValidationIssue]:
        """Check each layer's altitude is within valid range.
        
        Returns issues for out-of-range altitudes.
        """
        issues = []
        
        for i, layer in enumerate(layers):
            alt = layer.get("altitude_m")
            coverage = layer.get("coverage", "")
            
            if alt is None:
                continue
            
            # Check minimum altitude
            if alt < self.MIN_ALTITUDE_M and alt > 0:
                issues.append(ValidationIssue(
                    rule_name=self.rule_name,
                    severity=IssueSeverity.WARNING,
                    message=f"Layer {i}: Cloud altitude below minimum threshold "
                           f"({alt}m < {self.MIN_ALTITUDE_M}m)",
                    expected=f"Cloud base >= {self.MIN_ALTITUDE_M}m or 0 for ground",
                    actual=f"{alt}m for {coverage}",
                    affected_field=f"cloud_layers[{i}].altitude_m",
                    suggested_fix="Verify altitude measurement"
                ))
            
            # Check maximum altitude
            if alt > self.MAX_ALTITUDE_M:
                issues.append(ValidationIssue(
                    rule_name=self.rule_name,
                    severity=IssueSeverity.WARNING,
                    message=f"Layer {i}: Cloud altitude exceeds maximum "
                           f"({alt}m > {self.MAX_ALTITUDE_M}m)",
                    expected=f"Cloud base <= {self.MAX_ALTITUDE_M}m",
                    actual=f"{alt}m for {coverage}",
                    affected_field=f"cloud_layers[{i}].altitude_m",
                    suggested_fix="Verify altitude measurement or check data source"
                ))
            
            # Warn if unusual but possible (above typical max)
            if alt > self.TYPICAL_MAX_M and alt <= self.MAX_ALTITUDE_M:
                issues.append(ValidationIssue(
                    rule_name=self.rule_name,
                    severity=IssueSeverity.INFO,
                    message=f"Layer {i}: High altitude cloud ({alt}m above {self.TYPICAL_MAX_M}m)",
                    expected=f"Typical clouds below {self.TYPICAL_MAX_M}m",
                    actual=f"{alt}m for {coverage}",
                    affected_field=f"cloud_layers[{i}].altitude_m",
                    suggested_fix="Expected for high-altitude cirrus or upper-level reporting"
                ))
        
        return issues
    
    def _check_altitude_gaps(
        self,
        layers: List[dict]
    ) -> List[ValidationIssue]:
        """Analyze gaps between cloud layers for anomalies.
        
        Returns issues for unusual gap patterns.
        """
        issues = []
        
        layers_by_alt = sorted(layers, key=lambda x: x.get("altitude_m", 0))
        
        if len(layers_by_alt) < 2:
            return issues
        
        for i in range(len(layers_by_alt) - 1):
            current_alt = layers_by_alt[i].get("altitude_m", 0)
            next_alt = layers_by_alt[i + 1].get("altitude_m", 0)
            current_cov = layers_by_alt[i].get("coverage", "")
            next_cov = layers_by_alt[i + 1].get("coverage", "")
            
            if current_alt == 0 or next_alt == 0:
                continue
            
            gap = next_alt - current_alt
            
            # Check for extreme gaps (possible reporting error)
            if gap > self.EXTREME_GAP_M:
                issues.append(ValidationIssue(
                    rule_name=self.rule_name,
                    severity=IssueSeverity.WARNING,
                    message=f"Extreme gap between layers {i} and {i+1}: {gap}m",
                    expected=f"Typical gaps < {self.EXTREME_GAP_M}m",
                    actual=f"{current_cov} at {current_alt}m, "
                          f"{next_cov} at {next_alt}m (gap={gap}m)",
                    affected_field=f"cloud_layers[{i}:{i+1}]",
                    suggested_fix="Verify layer altitudes"
                ))
            
            # Info level for large but possible gaps
            elif gap > self.LARGE_GAP_M:
                issues.append(ValidationIssue(
                    rule_name=self.rule_name,
                    severity=IssueSeverity.INFO,
                    message=f"Large gap between layers {i} and {i+1}: {gap}m",
                    expected=f"Typical gaps < {self.LARGE_GAP_M}m",
                    actual=f"{current_cov} at {current_alt}m, "
                          f"{next_cov} at {next_alt}m",
                    affected_field=f"cloud_layers[{i}:{i+1}]",
                    suggested_fix="Clear air layer between clouds (normal for vertical structure)"
                ))
        
        return issues
    
    def _check_coverage_consistency(
        self,
        layers: List[dict]
    ) -> List[ValidationIssue]:
        """Validate coverage patterns are physically consistent.
        
        Returns issues for illogical coverage sequences.
        """
        issues = []
        
        layers_by_alt = sorted(layers, key=lambda x: x.get("altitude_m", 0))
        
        for i in range(len(layers_by_alt) - 1):
            current_cov = layers_by_alt[i].get("coverage", "")
            next_cov = layers_by_alt[i + 1].get("coverage", "")
            
            if current_cov not in self.COVERAGE_RANK or next_cov not in self.COVERAGE_RANK:
                continue
            
            current_rank = self.COVERAGE_RANK[current_cov]
            next_rank = self.COVERAGE_RANK[next_cov]
            
            # Rule: Coverage should not increase with altitude
            # (can't have FEW at 1000m, then OVC at 2000m)
            # FEW=rank 1, OVC=rank 4, so next_rank (4) > current_rank (1) = increases
            if next_rank > current_rank:
                issues.append(ValidationIssue(
                    rule_name=self.rule_name,
                    severity=IssueSeverity.WARNING,
                    message=f"Cloud coverage increases upward (layer {i} → {i+1}): "
                           f"{current_cov} → {next_cov}",
                    expected="Cloud coverage should decrease or stay same with altitude",
                    actual=f"Layer {i}: {current_cov} (rank {current_rank}), "
                          f"Layer {i+1}: {next_cov} (rank {next_rank})",
                    affected_field=f"cloud_layers[{i}:{i+1}]",
                    suggested_fix="Verify coverage observations match altitude structure"
                ))
        
        return issues
    
    def validate(
        self,
        cloud_layers: List[dict]
    ) -> List[ValidationIssue]:
        """Validate cloud layer sequence (Task 3.2 enhanced).
        
        Performs comprehensive checks:
        1. Clear sky exclusivity
        2. Altitude validity (within reasonable range)
        3. Altitude gap analysis
        4. Altitude strict ordering
        5. Coverage non-increasing upward
        
        Args:
            cloud_layers: List of dicts with keys: coverage, altitude_m
                Example: [
                    {"coverage": "BKN", "altitude_m": 800},
                    {"coverage": "OVC", "altitude_m": 2000}
                ]
        
        Returns:
            List of validation issues (empty if valid)
        """
        issues = []
        
        if not cloud_layers:
            return issues
        
        # Check 1: Clear sky exclusivity (highest priority)
        clear_layers = [l for l in cloud_layers if l.get("coverage") in ["CLR", "SKC"]]
        if clear_layers and len(cloud_layers) > 1:
            issues.append(ValidationIssue(
                rule_name=self.rule_name,
                severity=IssueSeverity.ERROR,
                message="CLR/SKC (clear sky) cannot coexist with other cloud layers",
                expected="If CLR or SKC present, must be only layer",
                actual=f"{len(cloud_layers)} layers including {len(clear_layers)} clear layer",
                affected_field="cloud_layers",
                suggested_fix="Remove redundant layers after CLR/SKC"
            ))
            return issues
        
        # Check 2: Altitude validity for each layer
        issues.extend(self._check_altitude_validity(cloud_layers))
        
        # Check 3: Gap analysis between layers
        issues.extend(self._check_altitude_gaps(cloud_layers))
        
        # Sort by altitude for remaining checks
        layers_by_alt = sorted(cloud_layers, key=lambda x: x.get("altitude_m", 0))
        
        # Check 4: Altitude strict ordering (no duplicates, increasing with height)
        for i in range(len(layers_by_alt) - 1):
            current_alt = layers_by_alt[i].get("altitude_m", 0)
            next_alt = layers_by_alt[i + 1].get("altitude_m", 0)
            
            if current_alt >= next_alt and current_alt > 0 and next_alt > 0:
                issues.append(ValidationIssue(
                    rule_name=self.rule_name,
                    severity=IssueSeverity.WARNING,
                    message=f"Cloud altitudes not strictly increasing: "
                           f"{current_alt}m >= {next_alt}m",
                    expected="Cloud bases strictly increase with height",
                    actual=f"Layer {i}: {current_alt}m, Layer {i+1}: {next_alt}m",
                    affected_field=f"cloud_layers[{i}:{i+1}]",
                    suggested_fix="Verify altitude measurements"
                ))
        
        # Check 5: Coverage consistency
        issues.extend(self._check_coverage_consistency(layers_by_alt))
        
        return issues


class VisibilityWeatherValidationRule:
    """Validate consistency between weather phenomena and visibility (Task 3.3).
    
    Different weather phenomena are associated with specific visibility ranges:
    - FG (Fog): Visibility < 1000m (defining characteristic)
    - BR (Mist): Visibility 1000-5000m  
    - RA (Rain): Visibility typically 2000-5000m
    - SN (Snow): Visibility < 2000m
    - TS (Thunderstorm): Highly variable but usually changed
    - HZ (Haze): Moderate visibility
    - DZ (Drizzle): Light precipitation
    
    Multiple phenomena compound effects on visibility.
    """
    
    # Expected visibility ranges for weather phenomena
    PHENOMENA_VISIBILITY = {
        "FG": {
            "min_m": 0,
            "max_m": 1000,
            "typical_m": "200-500",
            "description": "Fog: very restricted visibility",
            "severity_error_min": 0,
            "severity_error_max": 1050  # Above 1000m is not fog anymore
        },
        "BR": {
            "min_m": 500,
            "max_m": 5000,
            "typical_m": "2000-4000",
            "description": "Mist: light fog conditions",
            "severity_error_min": 250,
            "severity_error_max": 5500
        },
        "RA": {
            "min_m": 1000,
            "max_m": 10000,
            "typical_m": "2000-5000",
            "description": "Rain: moderate visibility reduction",
            "severity_error_min": 500,
            "severity_error_max": 15000
        },
        "SN": {
            "min_m": 100,
            "max_m": 5000,
            "typical_m": "500-2000",
            "description": "Snow: usually < 2000m",
            "severity_error_min": 50,
            "severity_error_max": 8000
        },
        "TS": {
            "min_m": 500,
            "max_m": 20000,
            "typical_m": "variable",
            "description": "Thunderstorm: highly variable",
            "severity_error_min": 300,
            "severity_error_max": 25000
        },
        "HZ": {
            "min_m": 1000,
            "max_m": 10000,
            "typical_m": "3000-8000",
            "description": "Haze: moderate visibility",
            "severity_error_min": 500,
            "severity_error_max": 15000
        },
        "DZ": {
            "min_m": 500,
            "max_m": 5000,
            "typical_m": "2000-4000",
            "description": "Drizzle: light precipitation",
            "severity_error_min": 300,
            "severity_error_max": 8000
        },
    }
    
    # Phenomenon combinations that compound visibility effects
    COMPOUNDS = {
        ("FG", "BR"): "Fog + Mist: expect very low visibility",
        ("SN", "BR"): "Snow + Mist: expect low visibility",
        ("RA", "BR"): "Rain + Mist: expect reduced visibility",
        ("TS", "RA"): "Thunderstorm + Rain: expect very variable visibility",
    }
    
    def __init__(self):
        """Initialize visibility-weather validation rule."""
        self.rule_name = "visibility_weather_consistency"
    
    def _check_single_phenomenon(
        self,
        phenomenon: str,
        visibility: int
    ) -> List[ValidationIssue]:
        """Check visibility for a single weather phenomenon.
        
        Returns list of issues.
        """
        issues = []
        
        if phenomenon not in self.PHENOMENA_VISIBILITY:
            return issues
        
        expected = self.PHENOMENA_VISIBILITY[phenomenon]
        min_vis = expected["min_m"]
        max_vis = expected["max_m"]
        error_min = expected.get("severity_error_min", min_vis)
        error_max = expected.get("severity_error_max", max_vis)
        
        # Check if visibility is out of critical range (ERROR)
        if visibility < error_min or visibility > error_max:
            severity = IssueSeverity.ERROR
            message_suffix = f" (critical - outside {error_min}-{error_max}m range)"
        # Check if visibility is unusual but possible (WARNING)
        elif visibility < min_vis or visibility > max_vis:
            severity = IssueSeverity.WARNING
            message_suffix = f" (unusual - outside {min_vis}-{max_vis}m range)"
        else:
            # Check if visibility is typical (INFO for edge cases)
            return issues
        
        direction = "low" if (visibility < min_vis or visibility < error_min) else "high"
        
        issues.append(ValidationIssue(
            rule_name=self.rule_name,
            severity=severity,
            message=f"{phenomenon} reported with unusually {direction} visibility: "
                   f"{visibility}m{message_suffix} ({expected['description']})",
            expected=f"{phenomenon}: {min_vis}-{max_vis}m "
                    f"(typical: {expected['typical_m']}m)",
            actual=f"Visibility: {visibility}m",
            affected_field="weather_phenomena, visibility",
            suggested_fix=f"Verify {phenomenon} code or visibility measurement"
        ))
        
        return issues
    
    def _check_phenomenon_combinations(
        self,
        phenomena: List[str],
        visibility: int
    ) -> List[ValidationIssue]:
        """Check visibility against combinations of phenomena.
        
        Multiple phenomena compound effects on visibility.
        """
        issues = []
        
        if len(phenomena) < 2:
            return issues
        
        # Check for notable combinations
        phenomena_set = set(phenomena)
        
        for (p1, p2), description in self.COMPOUNDS.items():
            if p1 in phenomena_set and p2 in phenomena_set:
                # For compounds, expect the MORE restrictive visibility
                vis1 = self.PHENOMENA_VISIBILITY[p1]
                vis2 = self.PHENOMENA_VISIBILITY[p2]
                
                # More restrictive = lower max and lower typical
                restrictive_max = min(vis1["max_m"], vis2["max_m"])
                
                if visibility > restrictive_max:
                    issues.append(ValidationIssue(
                        rule_name=self.rule_name,
                        severity=IssueSeverity.INFO,
                        message=f"Multiple phenomena ({p1} + {p2}): visibility higher than expected "
                               f"for combined effect ({visibility}m > typical {restrictive_max}m)",
                        expected=f"{description} - visibility typically < {restrictive_max}m",
                        actual=f"Visibility: {visibility}m",
                        affected_field="weather_phenomena",
                        suggested_fix="Verify if phenomena should be reported together"
                    ))
        
        return issues
    
    def validate(
        self,
        visibility_meters: Optional[int],
        weather_phenomena: Optional[List[str]] = None
    ) -> List[ValidationIssue]:
        """Validate visibility aligns with weather phenomena (Task 3.3 enhanced).
        
        Performs checks for:
        1. Individual phenomenon visibility ranges
        2. Multiple phenomenon combinations
        3. Visibility-phenomenon consistency
        
        Args:
            visibility_meters: Reported visibility in meters
            weather_phenomena: List of weather codes (e.g., ['RA', 'BR'])
        
        Returns:
            List of validation issues (empty if valid)
        """
        issues = []
        
        if not visibility_meters:
            return issues
        
        if not weather_phenomena:
            return issues
        
        # Filter to known phenomena only
        known_phenomena = [p for p in weather_phenomena if p in self.PHENOMENA_VISIBILITY]
        
        if not known_phenomena:
            return issues
        
        # Check each phenomenon individually
        for phenomenon in known_phenomena:
            issues.extend(self._check_single_phenomenon(phenomenon, visibility_meters))
        
        # Check phenomenon combinations
        issues.extend(self._check_phenomenon_combinations(known_phenomena, visibility_meters))
        
        return issues


class SemanticValidationEngine:
    """Main engine for running all semantic validation rules.
    
    Coordinates validation across multiple rules and provides
    comprehensive error reporting.
    """
    
    def __init__(self):
        """Initialize validation engine with all rules."""
        self.temperature_rule = TemperatureValidationRule()
        self.cloud_rule = CloudLayerValidationRule()
        self.visibility_rule = VisibilityWeatherValidationRule()
    
    def validate_metar_data(
        self,
        temperature: Optional[float] = None,
        dewpoint: Optional[float] = None,
        cloud_layers: Optional[List[dict]] = None,
        visibility_meters: Optional[int] = None,
        weather_phenomena: Optional[List[str]] = None,
    ) -> List[ValidationIssue]:
        """Run comprehensive semantic validation on METAR data.
        
        Args:
            temperature: Air temperature in °C
            dewpoint: Dewpoint temperature in °C
            cloud_layers: List of cloud layer dicts
            visibility_meters: Visibility in meters
            weather_phenomena: List of weather codes
        
        Returns:
            List of all validation issues found
        """
        all_issues = []
        
        # Run temperature validation
        all_issues.extend(
            self.temperature_rule.validate(temperature, dewpoint)
        )
        
        # Run cloud layer validation
        if cloud_layers:
            all_issues.extend(
                self.cloud_rule.validate(cloud_layers)
            )
        
        # Run visibility-weather validation
        if weather_phenomena:
            all_issues.extend(
                self.visibility_rule.validate(visibility_meters, weather_phenomena)
            )
        
        return all_issues
    
    def generate_report(
        self,
        issues: List[ValidationIssue],
        station_id: str = "UNKNOWN",
        raw_metar: str = ""
    ) -> dict:
        """Generate structured validation report.
        
        Args:
            issues: List of validation issues
            station_id: ICAO station identifier
            raw_metar: Raw METAR text
        
        Returns:
            Dictionary with report structure
        """
        error_count = sum(1 for i in issues if i.severity == IssueSeverity.ERROR)
        warning_count = sum(1 for i in issues if i.severity == IssueSeverity.WARNING)
        info_count = sum(1 for i in issues if i.severity == IssueSeverity.INFO)
        
        return {
            "station_id": station_id,
            "raw_metar": raw_metar,
            "is_valid": error_count == 0,
            "summary": {
                "total_issues": len(issues),
                "errors": error_count,
                "warnings": warning_count,
                "info": info_count
            },
            "issues": [
                {
                    "rule": issue.rule_name,
                    "severity": issue.severity.value,
                    "message": issue.message,
                    "expected": issue.expected,
                    "actual": issue.actual,
                    "field": issue.affected_field,
                    "suggested_fix": issue.suggested_fix
                }
                for issue in issues
            ]
        }
