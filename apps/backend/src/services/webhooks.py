"""
Webhook Notification Service for ICAO OPMET compliance.

Sends HTTP webhook notifications for translation events (User Decision 2).
"""

import asyncio
import hashlib
import hmac
import json
import logging
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional

import httpx

from ..config.icao_opmet import (
    WEBHOOK_EVENTS,
    WEBHOOK_SECRET,
    WEBHOOK_URLS,
    should_send_webhooks,
)

logger = logging.getLogger(__name__)


class WebhookService:
    """Service for sending webhook notifications."""

    def __init__(self):
        self.client = None
        self.enabled = should_send_webhooks()

    async def __aenter__(self):
        """Async context manager entry."""
        if self.enabled:
            self.client = httpx.AsyncClient(timeout=10.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.client:
            await self.client.aclose()

    def _generate_signature(self, payload: str) -> str:
        """
        Generate HMAC-SHA256 signature for webhook payload.

        Args:
            payload: JSON payload string

        Returns:
            Hex-encoded HMAC signature
        """
        if not WEBHOOK_SECRET:
            return ""

        signature = hmac.new(WEBHOOK_SECRET.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()

        return signature

    async def send_webhook(
        self,
        event: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Send webhook notification to all configured endpoints.

        Args:
            event: Event type (e.g., "translation.success")
            data: Event data payload
            metadata: Optional additional metadata

        Returns:
            True if all webhooks sent successfully, False otherwise
        """
        if not self.enabled:
            logger.debug("Webhooks disabled, skipping notification")
            return True

        if event not in WEBHOOK_EVENTS:
            logger.debug(f"Event {event} not in configured webhook events")
            return True

        if not WEBHOOK_URLS:
            logger.warning("No webhook URLs configured")
            return False

        # Prepare payload
        payload = {
            "event": event,
            "timestamp": datetime.now(UTC).replace(tzinfo=None).isoformat() + "Z",
            "data": data,
            "metadata": metadata or {},
            "source": {
                "centre": "NOAA-MDL",
                "service": "metar-to-iwxxm",
            },
        }

        payload_str = json.dumps(payload, default=str)
        signature = self._generate_signature(payload_str)

        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "METAR-to-IWXXM-Translation-Centre/1.0",
            "X-Webhook-Event": event,
            "X-Webhook-Timestamp": payload["timestamp"],
        }

        if signature:
            headers["X-Webhook-Signature"] = f"sha256={signature}"

        # Send to all webhook URLs
        tasks = [self._send_single_webhook(url, payload_str, headers) for url in WEBHOOK_URLS]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Check if all succeeded
        success = all(isinstance(result, bool) and result for result in results)

        return success

    async def _send_single_webhook(
        self,
        url: str,
        payload: str,
        headers: Dict[str, str],
    ) -> bool:
        """
        Send webhook to a single URL.

        Args:
            url: Webhook endpoint URL
            payload: JSON payload string
            headers: HTTP headers

        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.client:
                self.client = httpx.AsyncClient(timeout=10.0)

            response = await self.client.post(
                url,
                content=payload,
                headers=headers,
            )

            if response.status_code in [200, 201, 202, 204]:
                logger.info(f"Webhook sent successfully to {url} (status={response.status_code})")
                return True
            else:
                logger.warning(f"Webhook to {url} returned status {response.status_code}")
                return False

        except httpx.TimeoutException:
            logger.error(f"Webhook to {url} timed out")
            return False
        except httpx.RequestError as e:
            logger.error(f"Webhook to {url} failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending webhook to {url}: {e}", exc_info=True)
            return False

    async def notify_translation_completed(
        self,
        translation_id: str | None,
        airport_code: str,
        iwxxm_version: str,
        file_size_bytes: int,
        duration_ms: float | int,
    ):
        """
        Send notification for completed translation.

        Args:
            translation_id: Unique translation UUID
            airport_code: ICAO airport code
            iwxxm_version: IWXXM version used
            file_size_bytes: Size of generated IWXXM content
            duration_ms: Processing duration
        """
        if not translation_id:
            return
        await self.send_webhook(
            event="translation.completed",
            data={
                "translation_id": translation_id,
                "airport_code": airport_code,
                "iwxxm_version": iwxxm_version,
                "file_size_bytes": file_size_bytes,
                "duration_ms": int(round(duration_ms)),
            },
        )

    async def notify_translation_success(
        self,
        translation_id: str | None,
        airport_code: str,
        icao_region: str,
        iwxxm_version: str,
        duration_ms: float | int,
    ):
        """
        Send notification for successful translation.

        Args:
            translation_id: Unique translation UUID
            airport_code: ICAO airport code
            icao_region: ICAO region
            iwxxm_version: IWXXM version used
            duration_ms: Processing duration
        """
        if not translation_id:
            return
        await self.send_webhook(
            event="translation.success",
            data={
                "translation_id": translation_id,
                "airport_code": airport_code,
                "icao_region": icao_region,
                "iwxxm_version": iwxxm_version,
                "duration_ms": int(round(duration_ms)),
            },
        )

    async def notify_translation_failed(
        self,
        translation_id: str | None,
        airport_code: str,
        error_type: str,
        error_message: str,
    ):
        """
        Send notification for failed translation.

        Args:
            translation_id: Unique translation UUID
            airport_code: ICAO airport code
            error_type: Type of error
            error_message: Error message
        """
        if not translation_id:
            return
        await self.send_webhook(
            event="translation.failed",
            data={
                "translation_id": translation_id,
                "airport_code": airport_code,
                "error_type": error_type,
                "error_message": error_message,
            },
        )

    async def notify_validation_failed(
        self,
        translation_id: str,
        airport_code: str,
        failed_layers: List[str],
        error_details: Dict[str, Any],
    ):
        """
        Send notification for validation failure.

        Args:
            translation_id: Unique translation UUID
            airport_code: ICAO airport code
            failed_layers: List of failed validation layers
            error_details: Detailed validation errors
        """
        await self.send_webhook(
            event="validation.failed",
            data={
                "translation_id": translation_id,
                "airport_code": airport_code,
                "failed_layers": failed_layers,
                "error_count": len(error_details),
            },
            metadata={
                "error_details": error_details,
            },
        )

    async def notify_bulk_completed(
        self,
        total_files: int,
        successful: int,
        failed: int,
        duration_ms: int,
    ):
        """
        Send notification for bulk conversion completion.

        Args:
            total_files: Total number of files processed
            successful: Number of successful conversions
            failed: Number of failed conversions
            duration_ms: Total processing duration
        """
        await self.send_webhook(
            event="bulk.completed",
            data={
                "total_files": total_files,
                "successful": successful,
                "failed": failed,
                "success_rate": round(successful / total_files * 100, 2) if total_files > 0 else 0,
                "duration_ms": duration_ms,
            },
        )


# Singleton instance
webhook_service = WebhookService()
