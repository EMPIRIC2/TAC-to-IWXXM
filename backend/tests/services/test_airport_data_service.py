"""Unit tests for airport data auto-regeneration service."""
import pytest
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import time
import logging

logger = logging.getLogger(__name__)


@pytest.mark.unit
class TestAirportDataRegeneration:
    """Tests for airport data auto-regeneration."""
    
    def test_run_parser_success(self):
        """Test successful parser execution."""
        with patch('src.services.airport_data.subprocess.run') as mock_run:
            from src.services.airport_data import _run_parser
            
            mock_run.return_value = Mock(
                returncode=0,
                stdout="Loaded 1000 airports",
                stderr=""
            )
            
            mock_path = Mock()
            result = _run_parser(mock_path)
            
            assert result is True
            mock_run.assert_called_once()
    
    def test_run_parser_failure(self):
        """Test parser execution failure."""
        with patch('src.services.airport_data.subprocess.run') as mock_run:
            from src.services.airport_data import _run_parser
            
            mock_run.return_value = Mock(
                returncode=1,
                stdout="",
                stderr="Error parsing CSV"
            )
            
            mock_path = Mock()
            result = _run_parser(mock_path)
            
            assert result is False
    
    def test_run_parser_timeout(self):
        """Test parser timeout handling."""
        with patch('src.services.airport_data.subprocess.run') as mock_run:
            from src.services.airport_data import _run_parser
            
            mock_run.side_effect = subprocess.TimeoutExpired(
                cmd="python parser.py",
                timeout=30
            )
            
            mock_path = Mock()
            result = _run_parser(mock_path)
            
            assert result is False
    
    def test_run_parser_exception(self):
        """Test parser unexpected exception handling."""
        with patch('src.services.airport_data.subprocess.run') as mock_run:
            from src.services.airport_data import _run_parser
            
            mock_run.side_effect = Exception("Unexpected error")
            
            mock_path = Mock()
            result = _run_parser(mock_path)
            
            assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "unit"])
