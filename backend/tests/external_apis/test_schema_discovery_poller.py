"""
Tests for Schema Discovery Poller

Tests version detection, RC identification, and discovery polling logic.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.services.schema_discovery_poller import (
    SchemaDiscoveryPoller,
    discover_schemas,
    extract_version_from_url,
    VERSION_PATTERN,
    RC_PATTERN
)


class TestVersionPatterns:
    """Test version regex patterns."""
    
    def test_version_pattern_matches_stable(self):
        """Test VERSION_PATTERN matches stable releases."""
        test_cases = ["2025-2", "2023-1", "2026-1", "2024-2"]
        for version in test_cases:
            assert VERSION_PATTERN.search(version), f"Failed to match: {version}"
    
    def test_version_pattern_matches_rc(self):
        """Test VERSION_PATTERN matches RC versions."""
        test_cases = ["2025-2RC1", "2025-2RC2", "2026-1RC1"]
        for version in test_cases:
            assert VERSION_PATTERN.search(version), f"Failed to match: {version}"
    
    def test_rc_pattern_identifies_rc(self):
        """Test RC_PATTERN correctly identifies RC versions."""
        assert RC_PATTERN.match("2025-2RC1")
        assert RC_PATTERN.match("2025-2RC2")
        assert not RC_PATTERN.match("2025-2")
        assert not RC_PATTERN.match("2023-1")
    
    def test_version_pattern_rejects_invalid(self):
        """Test VERSION_PATTERN rejects invalid formats."""
        invalid_cases = ["2025-3", "2024-0", "202-1", "20251", "v2025-2"]
        for version in invalid_cases:
            match = VERSION_PATTERN.search(version)
            if match and match.group(0) == version:
                pytest.fail(f"Should not match invalid: {version}")


class TestExtractVersionFromUrl:
    """Test URL version extraction."""
    
    def test_extract_from_schema_url(self):
        """Test extracting version from schema URLs."""
        test_cases = [
            ("https://schemas.wmo.int/iwxxm/2025-2/iwxxm.xsd", "2025-2"),
            ("https://schemas.wmo.int/iwxxm/2025-2RC1/iwxxm.xsd", "2025-2RC1"),
            ("https://schemas.wmo.int/iwxxm/2023-1/rule/iwxxm.sch", "2023-1"),
        ]
        for url, expected in test_cases:
            result = extract_version_from_url(url)
            assert result == expected, f"Expected {expected}, got {result} for {url}"
    
    def test_extract_returns_none_for_invalid(self):
        """Test extraction returns None for URLs without version."""
        invalid_urls = [
            "https://schemas.wmo.int/iwxxm/",
            "https://example.com/test.xsd",
            "not-a-url"
        ]
        for url in invalid_urls:
            result = extract_version_from_url(url)
            assert result is None, f"Should return None for: {url}"


class TestSchemaDiscoveryPoller:
    """Test SchemaDiscoveryPoller class."""
    
    @pytest.fixture
    def poller(self):
        """Create poller instance for testing."""
        return SchemaDiscoveryPoller(
            poll_urls=["https://test.example.com/iwxxm/"],
            timeout_seconds=10
        )
    
    def test_poller_initialization(self, poller):
        """Test poller initializes correctly."""
        assert poller.timeout_seconds == 10
        assert len(poller.poll_urls) == 1
        assert len(poller.discovered_versions) == 0
    
    def test_is_rc_version(self, poller):
        """Test RC version detection."""
        assert poller._is_rc_version("2025-2RC1")
        assert poller._is_rc_version("2025-2RC2")
        assert not poller._is_rc_version("2025-2")
        assert not poller._is_rc_version("2023-1")
    
    def test_extract_versions_from_html(self, poller):
        """Test version extraction from HTML directory listing."""
        html_content = """
        <!DOCTYPE html>
        <html>
        <body>
            <a href="2025-2/">2025-2/</a>
            <a href="2025-2RC1/">2025-2RC1/</a>
            <a href="2023-1/">2023-1/</a>
            <a href="2021-2/">2021-2/</a>
        </body>
        </html>
        """
        versions = poller._extract_versions_from_html(html_content)
        
        assert "2025-2" in versions
        assert "2025-2RC1" in versions
        assert "2023-1" in versions
        assert "2021-2" in versions
    
    @pytest.mark.asyncio
    async def test_poll_once_with_mock_response(self, poller):
        """Test polling with mocked HTTP response."""
        mock_html = """
        <html><body>
        <a href="2025-2/">2025-2/</a>
        <a href="2025-2RC1/">2025-2RC1/</a>
        </body></html>
        """
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = AsyncMock()
            mock_response.text = mock_html
            mock_response.raise_for_status = Mock()
            
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            result = await poller.poll_once()
            
            assert "new_stable" in result
            assert "new_rc" in result
            assert "2025-2" in result["new_stable"]
            assert "2025-2RC1" in result["new_rc"]
    
    def test_get_discovered_versions_by_channel(self, poller):
        """Test filtering discovered versions by channel."""
        poller.discovered_versions = {"2025-2", "2025-2RC1", "2023-1"}
        
        stable = poller.get_discovered_versions(channel="stable")
        assert "2025-2" in stable
        assert "2023-1" in stable
        assert "2025-2RC1" not in stable
        
        rc = poller.get_discovered_versions(channel="rc")
        assert "2025-2RC1" in rc
        assert "2025-2" not in rc
        
        all_versions = poller.get_discovered_versions(channel=None)
        assert len(all_versions) == 3


@pytest.mark.unit
class TestDiscoveryConvenienceFunctions:
    """Test convenience wrapper functions."""
    
    @pytest.mark.asyncio
    async def test_discover_schemas_creates_poller(self):
        """Test discover_schemas() creates and uses poller."""
        with patch.object(SchemaDiscoveryPoller, 'poll_once', new_callable=AsyncMock) as mock_poll:
            mock_poll.return_value = {"new_stable": [], "new_rc": []}
            result = await discover_schemas()
            assert "new_stable" in result
            assert "new_rc" in result
