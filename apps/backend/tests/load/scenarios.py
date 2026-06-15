"""Locust user scenarios for backend API load testing."""

from __future__ import annotations

import random
from typing import Dict

from locust import HttpUser, between, task

from tests.load.auth import AuthProvider, build_auth_provider
from tests.load.config import LoadProfile, load_profile

SAMPLE_METARS = [
    "METAR KJFK 161200Z 12012KT 10SM FEW250 22/14 A3015 RMK AO2 SLP210",
    "METAR EGLL 161200Z 27015KT 9999 FEW040 18/12 Q1015",
    "METAR RJTT 161200Z 09008KT 10SM FEW030 20/15 A2995",
    "METAR YSSY 161200Z 20018KT 9999 SCT025 24/17 Q1010",
]


class BaseMetarUser(HttpUser):
    """Shared setup and helpers for all Locust users."""

    wait_time = between(0.5, 2.5)
    abstract = True
    host = load_profile().host

    profile: LoadProfile
    auth_provider: AuthProvider

    def on_start(self) -> None:
        self.profile = load_profile()
        self.auth_provider = build_auth_provider(self.profile)

    def request_context(self, scenario: str, endpoint: str) -> Dict[str, str]:
        """Context labels consumed by metrics hooks."""
        return {
            "profile": self.profile.name,
            "auth_mode": self.profile.auth_mode,
            "scenario": scenario,
            "endpoint": endpoint,
        }

    def protected_headers(self) -> Dict[str, str]:
        """Return headers for protected endpoints."""
        return self.auth_provider.headers()


class PublicApiUser(BaseMetarUser):
    """Public endpoint traffic for baseline health and routing latency."""

    weight = 3

    @task(5)
    def health(self) -> None:
        self.client.get(
            "/health",
            name="GET /health",
            context=self.request_context("public", "/health"),
        )

    @task(2)
    def versions(self) -> None:
        self.client.get(
            "/api/v1/versions",
            name="GET /api/v1/versions",
            context=self.request_context("public", "/api/v1/versions"),
        )

    @task(2)
    def schema_status(self) -> None:
        self.client.get(
            "/api/v1/schema-status",
            name="GET /api/v1/schema-status",
            context=self.request_context("public", "/api/v1/schema-status"),
        )

    @task(2)
    def centre_info(self) -> None:
        self.client.get(
            "/api/v1/translation/centre-info",
            name="GET /api/v1/translation/centre-info",
            context=self.request_context("public", "/api/v1/translation/centre-info"),
        )

    @task(1)
    def airport_region(self) -> None:
        code = random.choice(["KJFK", "EGLL", "RJTT", "YSSY"])
        self.client.get(
            f"/api/v1/translation/airport-region/{code}",
            name="GET /api/v1/translation/airport-region/{code}",
            context=self.request_context("public", "/api/v1/translation/airport-region/{code}"),
        )


class ConversionApiUser(BaseMetarUser):
    """Conversion workflow using authenticated endpoint."""

    weight = 5

    @task(5)
    def convert_single(self) -> None:
        metar = random.choice(SAMPLE_METARS)
        headers = self.protected_headers()
        context = self.request_context("convert", "/api/v1/convert")

        with self.client.post(
            "/api/v1/convert",
            name="POST /api/v1/convert",
            data={
                "manual_text": metar,
                "iwxxm_version": self.profile.target_iwxxm_version,
                "validate_output": "false",
                "validation_level": "basic",
            },
            headers=headers,
            context=context,
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"Unexpected status {response.status_code}")

    @task(1)
    def convert_with_validation(self) -> None:
        metar = random.choice(SAMPLE_METARS)
        headers = self.protected_headers()
        context = self.request_context("convert", "/api/v1/convert?validate_output=true")

        with self.client.post(
            "/api/v1/convert",
            name="POST /api/v1/convert (validated)",
            data={
                "manual_text": metar,
                "iwxxm_version": self.profile.target_iwxxm_version,
                "validate_output": "true",
                "validation_level": "comprehensive",
            },
            headers=headers,
            context=context,
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"Unexpected status {response.status_code}")


class ValidationApiUser(BaseMetarUser):
    """Validation endpoint workflow for TAC inputs."""

    weight = 3

    @task(3)
    def validate_single(self) -> None:
        metar = random.choice(SAMPLE_METARS)
        headers = {"Content-Type": "application/json", **self.protected_headers()}
        context = self.request_context("validation", "/api/v1/validation/validate")
        layers = [
            layer.strip()
            for layer in self.profile.validation_layers.split(",")
            if layer.strip()
        ]

        with self.client.post(
            "/api/v1/validation/validate",
            name="POST /api/v1/validation/validate",
            json={
                "content": metar,
                "content_type": "tac",
                "layers": layers,
                "iwxxm_version": self.profile.target_iwxxm_version,
            },
            headers=headers,
            context=context,
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"Unexpected status {response.status_code}")

    @task(1)
    def validate_batch(self) -> None:
        headers = {"Content-Type": "application/json", **self.protected_headers()}
        context = self.request_context("validation", "/api/v1/validation/validate-multi")

        with self.client.post(
            "/api/v1/validation/validate-multi",
            name="POST /api/v1/validation/validate-multi",
            json={
                "items": [
                    {"content": SAMPLE_METARS[0], "content_type": "tac"},
                    {"content": SAMPLE_METARS[1], "content_type": "tac"},
                ],
                "layers": ["airport_icao", "tac_syntax"],
            },
            headers=headers,
            context=context,
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"Unexpected status {response.status_code}")


class EvaluationApiUser(BaseMetarUser):
    """Optional evaluation workflow (disabled by default)."""

    weight = 1

    @task(1)
    def create_and_poll_job(self) -> None:
        if not self.profile.evaluation_enabled:
            return

        headers = {"Content-Type": "application/json", **self.protected_headers()}
        create_context = self.request_context("evaluation", "/api/v1/evaluation/jobs")

        with self.client.post(
            "/api/v1/evaluation/jobs",
            name="POST /api/v1/evaluation/jobs",
            json={
                "mode": "single",
                "station_ids": ["KJFK"],
                "hours": 2,
                "large_airports_only": True,
                "scheduled_service_only": True,
            },
            headers=headers,
            context=create_context,
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"Unexpected status {response.status_code}")
                return

            payload = response.json()
            job_id = payload.get("job_id")
            if not job_id:
                response.failure("No job_id returned")
                return

        poll_context = self.request_context("evaluation", "/api/v1/evaluation/jobs/{job_id}")
        self.client.get(
            f"/api/v1/evaluation/jobs/{job_id}",
            name="GET /api/v1/evaluation/jobs/{job_id}",
            headers=self.protected_headers(),
            context=poll_context,
        )
