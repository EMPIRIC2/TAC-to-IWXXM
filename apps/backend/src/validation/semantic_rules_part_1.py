"""Part 1 of ``semantic_rules.py`` (line-cap split)."""

from dataclasses import dataclass
from enum import StrEnum
from typing import ClassVar


class IssueSeverity(StrEnum):
    """Severity levels for validation issues."""

    ERROR = "error"  # Data physically impossible
    WARNING = "warning"  # Unusual but possible
    INFO = "info"  # Note: Data seems inconsistent but could be valid


@dataclass
class ValidationIssue:
    """
    Represents a validation issue found in meteorological data.

    Attributes
    ----------
    _ : object
        See implementation.
    """

    rule_name: str
    severity: IssueSeverity
    message: str
    expected: str
    actual: str
    affected_field: str
    suggested_fix: str | None = None

    def __str__(self) -> str:
        """
        Internal helper ``__str__``.

        Returns
        -------
        object
            Return value.
        """
        return f"[{self.severity.upper()}] {self.rule_name}: {self.message}"


class TemperatureValidationRule:
    """
    Validate temperature and dewpoint relationships.

    In real-world meteorology, dewpoint temperature can NEVER exceed
    air temperature. This is fundamental thermodynamics.

    Dewpoint is the temperature to which air must be cooled (at constant
    pressure and humidity) to become saturated with water vapor. By definition,
    it cannot exceed the actual temperature.

    Physics Check: Td ≤ T (always)
    Spacing Check: Typically T - Td between 0°C and ~30°C

    Attributes
    ----------
    _ : object
        See implementation.
    """

    def __init__(self) -> None:
        """Initialize temperature validation rule."""
        self.rule_name = "temperature_dewpoint_relationship"
        self.min_dew_spread = 0.0  # °C, minimum T - Td
        self.max_dew_spread = 50.0  # °C, maximum realistic T - Td

    def validate(self, temperature: float | None, dewpoint: float | None) -> list[ValidationIssue]:
        """
        Validate temperature and dewpoint relationship.

        Returns
        -------
            List of validation issues (empty if valid)

        Parameters
        ----------
        temperature : object
            Air temperature in °C
        dewpoint : object
            Dewpoint temperature in °C

        Returns
        -------
        object
            List of validation issues (empty if valid)
        """
        issues: list[ValidationIssue] = []

        # Skip validation if either value missing
        if temperature is None or dewpoint is None:
            return issues

        # Check 1: Dewpoint cannot exceed temperature (fundamental rule)
        if dewpoint > temperature:
            issues.append(
                ValidationIssue(
                    rule_name=self.rule_name,
                    severity=IssueSeverity.ERROR,
                    message=f"Temperature ({temperature}°C) < Dewpoint ({dewpoint}°C): "
                    f"IMPOSSIBLE - dewpoint cannot exceed temperature",
                    expected="Temperature ≥ Dewpoint",
                    actual=f"T={temperature}°C, Td={dewpoint}°C",
                    affected_field="temperature, dewpoint",
                    suggested_fix=f"Data error: Swap values (T={dewpoint}°C, Td={temperature}°C)",
                )
            )
            return issues

        # Check 2: Reasonable spread between T and Td
        spread = temperature - dewpoint

        if spread < self.min_dew_spread:
            issues.append(
                ValidationIssue(
                    rule_name=self.rule_name,
                    severity=IssueSeverity.WARNING,
                    message=f"Very small T-Td spread ({spread:.1f}°C): "
                    f"Indicates near-saturation (unusual but possible)",
                    expected=f"T - Td typically ≥ {self.min_dew_spread}°C",
                    actual=f"T-Td = {spread:.1f}°C",
                    affected_field="temperature, dewpoint",
                    suggested_fix="Verify data source for accuracy",
                )
            )

        if spread > self.max_dew_spread:
            issues.append(
                ValidationIssue(
                    rule_name=self.rule_name,
                    severity=IssueSeverity.WARNING,
                    message=f"Very large T-Td spread ({spread:.1f}°C): "
                    f"Indicates very dry air (possible in deserts/upper atmosphere)",
                    expected=f"T - Td typically ≤ {self.max_dew_spread}°C",
                    actual=f"T-Td = {spread:.1f}°C",
                    affected_field="temperature, dewpoint",
                    suggested_fix="Verify high-altitude or desert station",
                )
            )

        return issues

    def calculate_relative_humidity(self, temperature: float, dewpoint: float) -> float:
        """
        Calculate approximate relative humidity from T and Td.

        Uses Magnus formula approximation.

        Returns
        -------
            Relative humidity as percentage (0-100)

        Parameters
        ----------
        temperature : object
            Air temperature in °C
        dewpoint : object
            Dewpoint temperature in °C

        Returns
        -------
        object
            Relative humidity as percentage (0-100)
        """
        # Magnus formula coefficients
        a = 17.27
        b = 237.7  # °C

        alpha = ((a * temperature) / (b + temperature)) - ((a * dewpoint) / (b + dewpoint))
        rh = 100.0 * (2.71828 ** (-alpha))  # e^(-alpha)

        return max(0.0, min(100.0, rh))


class VisibilityWeatherValidationRule:
    """
    Validate consistency between weather phenomena and visibility (Task 3.3).

    Different weather phenomena are associated with specific visibility ranges:
    - FG (Fog): Visibility < 1000m (defining characteristic)
    - BR (Mist): Visibility 1000-5000m
    - RA (Rain): Visibility typically 2000-5000m
    - SN (Snow): Visibility < 2000m
    - TS (Thunderstorm): Highly variable but usually changed
    - HZ (Haze): Moderate visibility
    - DZ (Drizzle): Light precipitation

    Multiple phenomena compound effects on visibility.

    Attributes
    ----------
    _ : object
        See implementation.
    """

    # Expected visibility ranges for weather phenomena
    PHENOMENA_VISIBILITY: ClassVar[dict[str, dict[str, int | str]]] = {
        "FG": {
            "min_m": 0,
            "max_m": 1000,
            "typical_m": "200-500",
            "description": "Fog: very restricted visibility",
            "severity_error_min": 0,
            "severity_error_max": 1050,  # Above 1000m is not fog anymore
        },
        "BR": {
            "min_m": 500,
            "max_m": 5000,
            "typical_m": "2000-4000",
            "description": "Mist: light fog conditions",
            "severity_error_min": 250,
            "severity_error_max": 5500,
        },
        "RA": {
            "min_m": 1000,
            "max_m": 10000,
            "typical_m": "2000-5000",
            "description": "Rain: moderate visibility reduction",
            "severity_error_min": 500,
            "severity_error_max": 15000,
        },
        "SN": {
            "min_m": 100,
            "max_m": 5000,
            "typical_m": "500-2000",
            "description": "Snow: usually < 2000m",
            "severity_error_min": 50,
            "severity_error_max": 8000,
        },
        "TS": {
            "min_m": 500,
            "max_m": 20000,
            "typical_m": "variable",
            "description": "Thunderstorm: highly variable",
            "severity_error_min": 300,
            "severity_error_max": 25000,
        },
        "HZ": {
            "min_m": 1000,
            "max_m": 10000,
            "typical_m": "3000-8000",
            "description": "Haze: moderate visibility",
            "severity_error_min": 500,
            "severity_error_max": 15000,
        },
        "DZ": {
            "min_m": 500,
            "max_m": 5000,
            "typical_m": "2000-4000",
            "description": "Drizzle: light precipitation",
            "severity_error_min": 300,
            "severity_error_max": 8000,
        },
    }

    # Phenomenon combinations that compound visibility effects
    COMPOUNDS: ClassVar[dict[tuple[str, str], str]] = {
        ("FG", "BR"): "Fog + Mist: expect very low visibility",
        ("SN", "BR"): "Snow + Mist: expect low visibility",
        ("RA", "BR"): "Rain + Mist: expect reduced visibility",
        ("TS", "RA"): "Thunderstorm + Rain: expect very variable visibility",
    }

    def __init__(self) -> None:
        """Initialize visibility-weather validation rule."""
        self.rule_name = "visibility_weather_consistency"

    def _check_single_phenomenon(self, phenomenon: str, visibility: int) -> list[ValidationIssue]:
        """
        Internal helper ``_check_single_phenomenon``.

        Parameters
        ----------
        phenomenon : object
            Argument ``phenomenon``.
        visibility : object
            Argument ``visibility``.

        Returns
        -------
        object
            Return value.
        """
        issues: list[ValidationIssue] = []

        if phenomenon not in self.PHENOMENA_VISIBILITY:
            return issues

        expected = self.PHENOMENA_VISIBILITY[phenomenon]
        min_vis = int(expected["min_m"])
        max_vis = int(expected["max_m"])
        error_min = int(expected.get("severity_error_min", min_vis))
        error_max = int(expected.get("severity_error_max", max_vis))

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

        issues.append(
            ValidationIssue(
                rule_name=self.rule_name,
                severity=severity,
                message=f"{phenomenon} reported with unusually {direction} visibility: "
                f"{visibility}m{message_suffix} ({expected['description']})",
                expected=f"{phenomenon}: {min_vis}-{max_vis}m (typical: {expected['typical_m']}m)",
                actual=f"Visibility: {visibility}m",
                affected_field="weather_phenomena, visibility",
                suggested_fix=f"Verify {phenomenon} code or visibility measurement",
            )
        )

        return issues

    def _check_phenomenon_combinations(self, phenomena: list[str], visibility: int) -> list[ValidationIssue]:
        """
        Internal helper ``_check_phenomenon_combinations``.

        Parameters
        ----------
        phenomena : object
            Argument ``phenomena``.
        visibility : object
            Argument ``visibility``.

        Returns
        -------
        object
            Return value.
        """
        issues: list[ValidationIssue] = []

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
                restrictive_max = min(int(vis1["max_m"]), int(vis2["max_m"]))

                if visibility > restrictive_max:
                    issues.append(
                        ValidationIssue(
                            rule_name=self.rule_name,
                            severity=IssueSeverity.INFO,
                            message=f"Multiple phenomena ({p1} + {p2}): visibility higher than expected "
                            f"for combined effect ({visibility}m > typical {restrictive_max}m)",
                            expected=f"{description} - visibility typically < {restrictive_max}m",
                            actual=f"Visibility: {visibility}m",
                            affected_field="weather_phenomena",
                            suggested_fix="Verify if phenomena should be reported together",
                        )
                    )

        return issues

    def validate(
        self, visibility_meters: int | None, weather_phenomena: list[str] | None = None
    ) -> list[ValidationIssue]:
        """
        Validate visibility aligns with weather phenomena (Task 3.3 enhanced).

        Performs checks for:
        1. Individual phenomenon visibility ranges
        2. Multiple phenomenon combinations
        3. Visibility-phenomenon consistency

        Returns
        -------
            List of validation issues (empty if valid)

        Parameters
        ----------
        visibility_meters : object
            Reported visibility in meters
        weather_phenomena : object
            List of weather codes (e.g., ['RA', 'BR'])

        Returns
        -------
        object
            List of validation issues (empty if valid)
        """
        issues: list[ValidationIssue] = []

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
