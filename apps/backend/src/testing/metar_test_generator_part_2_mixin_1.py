"""Mixin extracted from ``metar_test_generator_part_2.py``::METARTestGenerator."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, cast

from .metar_test_generator_part_1 import CoverageReport, METARTestCase, logger


class _METARTestGeneratorMethodsMixin:
    """Methods mixin for ``METARTestGenerator``."""

    def _save_to_cache(self, test_cases: list[METARTestCase], cache_file: Path) -> None:
        """
        Internal helper ``_save_to_cache``.

        Parameters
        ----------
        test_cases : object
            Argument ``test_cases``.
        cache_file : object
            Argument ``cache_file``.
        """
        data = {
            "generated_at": datetime.now().isoformat(),
            "count": len(test_cases),
            "test_cases": [
                {
                    "station_id": tc.station_id,
                    "raw_metar": tc.raw_metar,
                    "latitude": tc.latitude,
                    "longitude": tc.longitude,
                    "country": tc.country,
                    "elevation": tc.elevation,
                    "weather_phenomena": tc.weather_phenomena,
                    "cloud_types": tc.cloud_types,
                    "cloud_amounts": tc.cloud_amounts,
                    "visibility": tc.visibility,
                    "temperature": tc.temperature,
                    "region": tc.region,
                    "source": tc.source,
                }
                for tc in test_cases
            ],
        }

        with open(cache_file, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved {len(test_cases)} test cases to {cache_file}")

    def _load_from_cache(self, cache_file: Path) -> list[METARTestCase]:
        """
        Internal helper ``_load_from_cache``.

        Parameters
        ----------
        cache_file : object
            Argument ``cache_file``.

        Returns
        -------
        object
            Return value.
        """
        with open(cache_file) as f:
            raw = cast(dict[str, Any], json.load(f))

        test_cases: list[METARTestCase] = []
        for tc_data in cast(list[dict[str, Any]], raw.get("test_cases", [])):
            test_case = METARTestCase(
                station_id=tc_data["station_id"],
                raw_metar=tc_data["raw_metar"],
                latitude=tc_data.get("latitude"),
                longitude=tc_data.get("longitude"),
                country=tc_data.get("country"),
                elevation=tc_data.get("elevation"),
                weather_phenomena=tc_data.get("weather_phenomena", []),
                cloud_types=tc_data.get("cloud_types", []),
                cloud_amounts=tc_data.get("cloud_amounts", []),
                visibility=tc_data.get("visibility"),
                temperature=tc_data.get("temperature"),
                region=tc_data.get("region"),
                source=tc_data.get("source", "cache"),
            )
            test_cases.append(test_case)
            self.coverage.add_test_case(test_case)

        logger.info(f"Loaded {len(test_cases)} test cases from cache")
        return test_cases

    def get_coverage_report(self) -> CoverageReport:
        """
        Get current coverage report.


        Returns
        -------
        object
            Return value.
        """
        return self.coverage

    def save_coverage_report(self, output_file: Path | None = None) -> None:
        """
        Save coverage report to JSON file.


        Parameters
        ----------
        output_file : object
            Argument ``output_file``.
        """
        if output_file is None:
            output_file = self.cache_dir / "coverage_report.json"

        with open(output_file, "w") as f:
            json.dump(self.coverage.to_dict(), f, indent=2)

        logger.info(f"Saved coverage report to {output_file}")
