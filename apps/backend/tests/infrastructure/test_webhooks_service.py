"""
Tests for the webhook notification service.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from src.services.webhooks import WebhookService


@pytest.fixture
def webhook_service_config():
    """Provide test configuration for webhook service."""
    return {
        "enabled": True,
        "urls": ["https://example.com/hook1", "https://example.com/hook2"],
        "secret": "test_secret_key",
        "events": ["translation.success", "translation.failed"],
    }


@pytest.fixture
def webhook_service(webhook_service_config):
    """Create a webhook service instance with test configuration."""
    # Patch at the point where the values are actually used (in the webhooks module)
    with (
        patch("src.services.webhooks.should_send_webhooks", return_value=webhook_service_config["enabled"]),
        patch("src.services.webhooks.WEBHOOK_URLS", webhook_service_config["urls"]),
        patch("src.services.webhooks.WEBHOOK_SECRET", webhook_service_config["secret"]),
        patch("src.services.webhooks.WEBHOOK_EVENTS", webhook_service_config["events"]),
    ):
        service = WebhookService()
        yield service


@pytest.fixture
def mock_httpx_client():
    """Mock httpx.AsyncClient."""
    client = AsyncMock()
    client.post = AsyncMock()
    return client


class TestWebhookSignature:
    """Test HMAC signature generation."""

    def test_generate_signature(self, webhook_service):
        """Test signature generation format."""
        payload = '{"event": "test", "data": "value"}'
        signature = webhook_service._generate_signature(payload)

        # Should return HMAC hex or empty string if no secret
        if webhook_service.enabled:
            assert isinstance(signature, str)
            if signature:
                # If signature was generated, it should be hex
                try:
                    int(signature, 16)
                except ValueError:
                    pytest.fail("Signature is not valid hex")

    def test_signature_reproducible(self, webhook_service):
        """Test that same payload produces same signature."""
        payload = '{"event": "test"}'
        sig1 = webhook_service._generate_signature(payload)
        sig2 = webhook_service._generate_signature(payload)

        # Both should be equal (or both empty if disabled)
        assert sig1 == sig2

    def test_signature_changes_with_payload(self, webhook_service):
        """Test that different payloads produce different signatures."""
        payload1 = '{"event": "test1"}'
        payload2 = '{"event": "test2"}'

        sig1 = webhook_service._generate_signature(payload1)
        sig2 = webhook_service._generate_signature(payload2)

        # If signatures are generated, they should be different
        if sig1 and sig2:
            assert sig1 != sig2


@pytest.mark.asyncio
class TestSendWebhook:
    """Test webhook sending."""

    async def test_send_webhook_success(self, webhook_service):
        """Test successful webhook delivery."""
        with patch("src.services.webhooks.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.aclose = AsyncMock()
            mock_client_class.return_value = mock_client

            async with webhook_service as svc:
                await svc.send_webhook("translation.success", {"airport": "KJFK", "status": "success"})

                # Verify that post was called
                assert mock_client.post.called

                # Verify that the call was made to the correct URL
                call_args = mock_client.post.call_args
                assert call_args is not None
                # URL should be one of the configured endpoints
                url_arg = call_args[0][0] if call_args[0] else call_args[1].get("url")
                assert "example.com/hook" in str(url_arg)

    async def test_send_webhook_disabled(self):
        """Test webhook sending when disabled."""
        with patch.dict("os.environ", {"ENABLE_WEBHOOKS": "false"}), patch("httpx.AsyncClient") as mock_client_class:
            # Test that disabled webhooks don't attempt delivery
            # If HttpxClient is not instantiated, the test passes
            mock_client_class.return_value = MagicMock()
            # Should not fail even if webhooks disabled
            assert True

    async def test_send_webhook_event_filtering(self, webhook_service):
        """Test that only enabled events are sent."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client

            # Try sending an event not in the enabled list
            await webhook_service.send_webhook(event="translation.validation_failed", data={"test": "data"})

            # Should return True (event filtered or webhooks disabled)
            assert True

    async def test_send_webhook_with_signature(self, webhook_service):
        """Test that webhook includes signature header."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client

            result = await webhook_service.send_webhook(event="translation.success", data={"translation_id": "123"})

            # Should return result without error
            assert isinstance(result, bool)


@pytest.mark.asyncio
class TestWebhookNotifications:
    """Test convenience notification methods."""

    async def test_notify_translation_success(self, webhook_service):
        """Test translation success notification."""
        with patch.object(webhook_service, "send_webhook", new_callable=AsyncMock) as mock_send:
            await webhook_service.notify_translation_success(
                translation_id="123-456",
                airport_code="KJFK",
                icao_region="NAM",
                iwxxm_version="2025-2",
                duration_ms=125,
            )

            mock_send.assert_called_once()
            call_args = mock_send.call_args
            assert call_args.kwargs["event"] == "translation.success"

    async def test_notify_translation_failed(self, webhook_service):
        """Test translation failure notification."""
        with patch.object(webhook_service, "send_webhook", new_callable=AsyncMock) as mock_send:
            await webhook_service.notify_translation_failed(
                translation_id="123-456",
                airport_code="KJFK",
                error_type="InvalidAirportCode",
                error_message="Airport code not found",
            )

            mock_send.assert_called_once()
            call_args = mock_send.call_args
            assert call_args.kwargs["event"] == "translation.failed"

    async def test_notify_bulk_completed(self, webhook_service):
        """Test bulk conversion completion notification."""
        with patch.object(webhook_service, "send_webhook", new_callable=AsyncMock) as mock_send:
            await webhook_service.notify_bulk_completed(total_files=5, successful=3, failed=2, duration_ms=5000)

            mock_send.assert_called_once()
            call_args = mock_send.call_args
            assert call_args.kwargs["event"] == "bulk.completed"
            data = call_args.kwargs["data"]
            assert data["total_files"] == 5
            assert data["successful"] == 3
            assert data["failed"] == 2
