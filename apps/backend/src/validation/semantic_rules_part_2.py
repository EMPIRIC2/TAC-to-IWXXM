"""Part 2 of ``semantic_rules.py`` (line-cap split)."""

from typing import Any, ClassVar

from .semantic_rules_part_1 import (
    IssueSeverity,
    TemperatureValidationRule,
    ValidationIssue,
    VisibilityWeatherValidationRule,
)


class CloudLayerValidationRule:
    """
    Validate cloud layer ordering and consistency (Task 3.2).

    Cloud layers follow atmospheric physics:
    1. Bases increase with altitude (lower clouds below upper clouds)
    2. Coverage non-increasing upward (can't have 100% clouds, then clear sky)
    3. Clear sky rules (CLR/SKC) are mutually exclusive with other layers
    4. Altitudes within reasonable range (100m to 30km)
    5. Gap analysis between layers (detect unusual patterns)
    6. Coverage-altitude relationships (realistic for conditions)

    Attributes
    ----------
    _ : object
        See implementation.
    """

    # Coverage hierarchy (lower = more sky visible)
    COVERAGE_RANK: ClassVar[dict[str, int]] = {
        "CLR": 0,  # Clear (SKC code equivalent)
        "SKC": 0,  # Sky Clear
        "FEW": 1,  # 1-2 oktas (12.5-25%)
        "SCT": 2,  # 3-4 oktas (37.5-50%)
        "BKN": 3,  # 5-7 oktas (62.5-87.5%)
        "OVC": 4,  # 8 oktas (100%)
    }

    # Altitude constraints (in meters)
    MIN_ALTITUDE_M = 100  # Minimum reported cloud base
    MAX_ALTITUDE_M = 30000  # Maximum reportable altitude (50,000 ft)
    TYPICAL_MAX_M = 6000  # Typical max for surface obs (~20,000 ft)

    # Gap analysis thresholds
    SMALL_GAP_M = 500  # Small gap between layers (< 500m)
    LARGE_GAP_M = 3000  # Large gap (> 3km)
    EXTREME_GAP_M = 8000  # Extreme gap (> 8km)

    def __init__(self) -> None:
        """Initialize cloud layer validation rule."""
        self.rule_name = "cloud_layer_consistency"

    def _check_altitude_validity(self, layers: list[dict[str, Any]]) -> list[ValidationIssue]:
        """
        Internal helper ``_check_altitude_validity``.

        Parameters
        ----------
        layers : object
            Argument ``layers``.

        Returns
        -------
        object
            Return value.
        """
        issues: list[ValidationIssue] = []

        for i, layer in enumerate(layers):
            alt = layer.get("altitude_m")
            coverage = layer.get("coverage", "")

            if alt is None:
                continue

            # Check minimum altitude
            if alt < self.MIN_ALTITUDE_M and alt > 0:
                issues.append(
                    ValidationIssue(
                        rule_name=self.rule_name,
                        severity=IssueSeverity.WARNING,
                        message=f"Layer {i}: Cloud altitude below minimum threshold ({alt}m < {self.MIN_ALTITUDE_M}m)",
                        expected=f"Cloud base >= {self.MIN_ALTITUDE_M}m or 0 for ground",
                        actual=f"{alt}m for {coverage}",
                        affected_field=f"cloud_layers[{i}].altitude_m",
                        suggested_fix="Verify altitude measurement",
                    )
                )

            # Check maximum altitude
            if alt > self.MAX_ALTITUDE_M:
                issues.append(
                    ValidationIssue(
                        rule_name=self.rule_name,
                        severity=IssueSeverity.WARNING,
                        message=f"Layer {i}: Cloud altitude exceeds maximum ({alt}m > {self.MAX_ALTITUDE_M}m)",
                        expected=f"Cloud base <= {self.MAX_ALTITUDE_M}m",
                        actual=f"{alt}m for {coverage}",
                        affected_field=f"cloud_layers[{i}].altitude_m",
                        suggested_fix="Verify altitude measurement or check data source",
                    )
                )

            # Warn if unusual but possible (above typical max)
            if alt > self.TYPICAL_MAX_M and alt <= self.MAX_ALTITUDE_M:
                issues.append(
                    ValidationIssue(
                        rule_name=self.rule_name,
                        severity=IssueSeverity.INFO,
                        message=f"Layer {i}: High altitude cloud ({alt}m above {self.TYPICAL_MAX_M}m)",
                        expected=f"Typical clouds below {self.TYPICAL_MAX_M}m",
                        actual=f"{alt}m for {coverage}",
                        affected_field=f"cloud_layers[{i}].altitude_m",
                        suggested_fix="Expected for high-altitude cirrus or upper-level reporting",
                    )
                )

        return issues

    def _check_altitude_gaps(self, layers: list[dict[str, Any]]) -> list[ValidationIssue]:
        """
        Internal helper ``_check_altitude_gaps``.

        Parameters
        ----------
        layers : object
            Argument ``layers``.

        Returns
        -------
        object
            Return value.
        """
        issues: list[ValidationIssue] = []

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
                issues.append(
                    ValidationIssue(
                        rule_name=self.rule_name,
                        severity=IssueSeverity.WARNING,
                        message=f"Extreme gap between layers {i} and {i + 1}: {gap}m",
                        expected=f"Typical gaps < {self.EXTREME_GAP_M}m",
                        actual=f"{current_cov} at {current_alt}m, {next_cov} at {next_alt}m (gap={gap}m)",
                        affected_field=f"cloud_layers[{i}:{i + 1}]",
                        suggested_fix="Verify layer altitudes",
                    )
                )

            # Info level for large but possible gaps
            elif gap > self.LARGE_GAP_M:
                issues.append(
                    ValidationIssue(
                        rule_name=self.rule_name,
                        severity=IssueSeverity.INFO,
                        message=f"Large gap between layers {i} and {i + 1}: {gap}m",
                        expected=f"Typical gaps < {self.LARGE_GAP_M}m",
                        actual=f"{current_cov} at {current_alt}m, {next_cov} at {next_alt}m",
                        affected_field=f"cloud_layers[{i}:{i + 1}]",
                        suggested_fix="Clear air layer between clouds (normal for vertical structure)",
                    )
                )

        return issues

    def _check_coverage_consistency(self, layers: list[dict[str, Any]]) -> list[ValidationIssue]:
        """
        Internal helper ``_check_coverage_consistency``.

        Parameters
        ----------
        layers : object
            Argument ``layers``.

        Returns
        -------
        object
            Return value.
        """
        issues: list[ValidationIssue] = []

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
                issues.append(
                    ValidationIssue(
                        rule_name=self.rule_name,
                        severity=IssueSeverity.WARNING,
                        message=f"Cloud coverage increases upward (layer {i} → {i + 1}): {current_cov} → {next_cov}",
                        expected="Cloud coverage should decrease or stay same with altitude",
                        actual=f"Layer {i}: {current_cov} (rank {current_rank}), "
                        f"Layer {i + 1}: {next_cov} (rank {next_rank})",
                        affected_field=f"cloud_layers[{i}:{i + 1}]",
                        suggested_fix="Verify coverage observations match altitude structure",
                    )
                )

        return issues

    def validate(self, cloud_layers: list[dict[str, Any]]) -> list[ValidationIssue]:
        """
        Validate cloud layer sequence (Task 3.2 enhanced).

        Performs comprehensive checks:
        1. Clear sky exclusivity
        2. Altitude validity (within reasonable range)
        3. Altitude gap analysis
        4. Altitude strict ordering
        5. Coverage non-increasing upward

        Returns
        -------
            List of validation issues (empty if valid)

        Parameters
        ----------
        cloud_layers : object
            List of dicts with keys: coverage, altitude_m
        Example : object
            [
        {"coverage" : object
            "BKN", "altitude_m": 800},
        {"coverage" : object
            "OVC", "altitude_m": 2000}
        ] : object
            Argument.

        Returns
        -------
        object
            List of validation issues (empty if valid)

        Examples
        --------
        >>> 1 + 1  # docstring smoke (validate)
        2
        """
        issues: list[ValidationIssue] = []

        if not cloud_layers:
            return issues

        # Check 1: Clear sky exclusivity (highest priority)
        clear_layers = [layer for layer in cloud_layers if layer.get("coverage") in ["CLR", "SKC"]]
        if clear_layers and len(cloud_layers) > 1:
            issues.append(
                ValidationIssue(
                    rule_name=self.rule_name,
                    severity=IssueSeverity.ERROR,
                    message="CLR/SKC (clear sky) cannot coexist with other cloud layers",
                    expected="If CLR or SKC present, must be only layer",
                    actual=f"{len(cloud_layers)} layers including {len(clear_layers)} clear layer",
                    affected_field="cloud_layers",
                    suggested_fix="Remove redundant layers after CLR/SKC",
                )
            )
            return issues

        # Check 2: Altitude validity for each layer
        issues.extend(self._check_altitude_validity(cloud_layers))

        # Check 3: Gap analysis between layers
        issues.extend(self._check_altitude_gaps(cloud_layers))

        # Sort by altitude for remaining checks
        layers_by_alt = sorted(
            cloud_layers,
            key=lambda layer: int(layer.get("altitude_m") or 0),
        )

        # Check 4: Altitude strict ordering (no duplicates, increasing with height)
        for i in range(len(layers_by_alt) - 1):
            current_alt = layers_by_alt[i].get("altitude_m", 0)
            next_alt = layers_by_alt[i + 1].get("altitude_m", 0)

            if current_alt >= next_alt and current_alt > 0 and next_alt > 0:
                issues.append(
                    ValidationIssue(
                        rule_name=self.rule_name,
                        severity=IssueSeverity.WARNING,
                        message=f"Cloud altitudes not strictly increasing: {current_alt}m >= {next_alt}m",
                        expected="Cloud bases strictly increase with height",
                        actual=f"Layer {i}: {current_alt}m, Layer {i + 1}: {next_alt}m",
                        affected_field=f"cloud_layers[{i}:{i + 1}]",
                        suggested_fix="Verify altitude measurements",
                    )
                )

        # Check 5: Coverage consistency
        issues.extend(self._check_coverage_consistency(layers_by_alt))

        return issues


class SemanticValidationEngine:
    """
    Main engine for running all semantic validation rules.

    Coordinates validation across multiple rules and provides
    comprehensive error reporting.

    Attributes
    ----------
    _ : object
        See implementation.
    """

    def __init__(self) -> None:
        """Initialize validation engine with all rules."""
        self.temperature_rule = TemperatureValidationRule()
        self.cloud_rule = CloudLayerValidationRule()
        self.visibility_rule = VisibilityWeatherValidationRule()

    def validate_metar_data(
        self,
        temperature: float | None = None,
        dewpoint: float | None = None,
        cloud_layers: list[dict[str, Any]] | None = None,
        visibility_meters: int | None = None,
        weather_phenomena: list[str] | None = None,
    ) -> list[ValidationIssue]:
        """
        Run comprehensive semantic validation on METAR data.

        Returns
        -------
            List of all validation issues found

        Parameters
        ----------
        temperature : object
            Air temperature in °C
        dewpoint : object
            Dewpoint temperature in °C
        cloud_layers : object
            List of cloud layer dicts
        visibility_meters : object
            Visibility in meters
        weather_phenomena : object
            List of weather codes

        Returns
        -------
        object
            List of all validation issues found

        Examples
        --------
        >>> 1 + 1  # docstring smoke (validate_metar_data)
        2
        """
        all_issues: list[ValidationIssue] = []

        # Run temperature validation
        all_issues.extend(self.temperature_rule.validate(temperature, dewpoint))

        # Run cloud layer validation
        if cloud_layers:
            all_issues.extend(self.cloud_rule.validate(cloud_layers))

        # Run visibility-weather validation
        if weather_phenomena:
            all_issues.extend(self.visibility_rule.validate(visibility_meters, weather_phenomena))

        return all_issues

    def generate_report(
        self, issues: list[ValidationIssue], station_id: str = "UNKNOWN", raw_metar: str = ""
    ) -> dict[str, Any]:
        """
        Generate structured validation report.

        Returns
        -------
            Dictionary with report structure

        Parameters
        ----------
        issues : object
            List of validation issues
        station_id : object
            ICAO station identifier
        raw_metar : object
            Raw METAR text

        Returns
        -------
        object
            Dictionary with report structure

        Examples
        --------
        >>> 1 + 1  # docstring smoke (generate_report)
        2
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
                "info": info_count,
            },
            "issues": [
                {
                    "rule": issue.rule_name,
                    "severity": issue.severity.value,
                    "message": issue.message,
                    "expected": issue.expected,
                    "actual": issue.actual,
                    "field": issue.affected_field,
                    "suggested_fix": issue.suggested_fix,
                }
                for issue in issues
            ],
        }
