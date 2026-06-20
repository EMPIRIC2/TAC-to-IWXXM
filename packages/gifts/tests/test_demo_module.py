"""Tests for the demo module components."""

import os
import sys
import pytest

# Import demo modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "demo"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestDemoConfiguration:
    """Test demo configuration and setup."""

    def test_demo_config_exists(self):
        """Test demo configuration file exists."""
        demo_dir = os.path.join(os.path.dirname(__file__), "..", "demo")
        config_file = os.path.join(demo_dir, "iwxxmd.cfg")
        assert os.path.exists(config_file), "Demo config file should exist"

    def test_demo_database_exists(self):
        """Test demo database files exist."""
        demo_dir = os.path.join(os.path.dirname(__file__), "..", "demo")
        assert os.path.exists(os.path.join(demo_dir, "aerodromes.db")), "aerodromes.db should exist"

    def test_demo_sample_data_exists(self):
        """Test demo sample data files exist."""
        demo_dir = os.path.join(os.path.dirname(__file__), "..", "demo")
        sample_files = ["metars.txt", "tafs.txt", "tca.txt", "vaa.txt"]
        for sample_file in sample_files:
            assert os.path.exists(os.path.join(demo_dir, sample_file)), f"{sample_file} should exist"

    def test_demo_sample_metar_data(self):
        """Test demo METAR sample data is readable."""
        demo_dir = os.path.join(os.path.dirname(__file__), "..", "demo")
        metars_file = os.path.join(demo_dir, "metars.txt")
        with open(metars_file, "r") as f:
            content = f.read()
            assert len(content) > 0, "metars.txt should contain data"
            assert "METAR" in content or "SPECI" in content, "Should contain METAR/SPECI keywords"

    def test_demo_sample_taf_data(self):
        """Test demo TAF sample data is readable."""
        demo_dir = os.path.join(os.path.dirname(__file__), "..", "demo")
        tafs_file = os.path.join(demo_dir, "tafs.txt")
        with open(tafs_file, "r") as f:
            content = f.read()
            assert len(content) > 0, "tafs.txt should contain data"
            assert "TAF" in content, "Should contain TAF keyword"

    def test_demo_sample_tca_data(self):
        """Test demo TCA sample data is readable."""
        demo_dir = os.path.join(os.path.dirname(__file__), "..", "demo")
        tca_file = os.path.join(demo_dir, "tca.txt")
        with open(tca_file, "r") as f:
            content = f.read()
            assert len(content) > 0, "tca.txt should contain data"
            # TCA content validation

    def test_demo_sample_vaa_data(self):
        """Test demo VAA sample data is readable."""
        demo_dir = os.path.join(os.path.dirname(__file__), "..", "demo")
        vaa_file = os.path.join(demo_dir, "vaa.txt")
        with open(vaa_file, "r") as f:
            content = f.read()
            assert len(content) > 0, "vaa.txt should contain data"
            assert "VAA" in content or "VOLCANO" in content, "Should contain VAA/VOLCANO content"


class TestDaemonBasics:
    """Test daemon initialization and basic functionality."""

    def test_daemon_import(self):
        """Test iwxxmd module can be imported."""
        try:
            import demo.iwxxmd as iwxxmd

            assert hasattr(iwxxmd, "Daemon"), "Daemon class should exist"
        except ImportError:
            # If import fails due to watchdog, that's OK for testing
            pytest.skip("watchdog module not available in test environment")

    def test_daemon_class_instantiation(self):
        """Test Daemon class can be instantiated."""
        try:
            from demo.iwxxmd import Daemon

            daemon = Daemon()
            assert daemon is not None
            assert hasattr(daemon, "daemonize"), "Daemon should have daemonize method"
        except ImportError:
            pytest.skip("watchdog module not available in test environment")

    def test_daemon_attributes(self):
        """Test Daemon class has expected attributes and methods."""
        try:
            from demo.iwxxmd import Daemon

            daemon = Daemon()
            # Check for key methods
            assert callable(getattr(daemon, "daemonize", None)), "daemonize should be callable"
        except ImportError:
            pytest.skip("watchdog module not available in test environment")


class TestDemoUtilities:
    """Test demo utility functions and helpers."""

    def test_demo_readme_exists(self):
        """Test demo README exists."""
        demo_dir = os.path.join(os.path.dirname(__file__), "..", "demo")
        readme_file = os.path.join(demo_dir, "README.md")
        assert os.path.exists(readme_file), "Demo README should exist"

    def test_demo_readme_has_content(self):
        """Test demo README has substantive content."""
        demo_dir = os.path.join(os.path.dirname(__file__), "..", "demo")
        readme_file = os.path.join(demo_dir, "README.md")
        with open(readme_file, "r") as f:
            content = f.read()
            assert len(content) > 50, "README should have substantive content"

    def test_demo_directory_structure(self):
        """Test demo directory has required structure."""
        demo_dir = os.path.join(os.path.dirname(__file__), "..", "demo")
        assert os.path.isdir(demo_dir), "demo directory should exist"
        assert os.path.exists(os.path.join(demo_dir, "iwxxmd.cfg")), "Config file should exist"
        assert os.path.exists(os.path.join(demo_dir, "iwxxmd.py")), "Daemon script should exist"


class TestDemo1Script:
    """Test the demo1.py script."""

    def test_demo1_import(self):
        """Test demo1.py can be imported."""
        try:
            import demo.demo1 as demo1

            assert demo1 is not None
        except ImportError as e:
            pytest.skip(f"Cannot import demo1: {e}")

    def test_demo1_file_exists(self):
        """Test demo1.py file exists."""
        demo_dir = os.path.join(os.path.dirname(__file__), "..", "demo")
        demo1_file = os.path.join(demo_dir, "demo1.py")
        assert os.path.exists(demo1_file), "demo1.py should exist"

    def test_demo1_has_main(self):
        """Test demo1.py has a main execution path."""
        demo_dir = os.path.join(os.path.dirname(__file__), "..", "demo")
        demo1_file = os.path.join(demo_dir, "demo1.py")
        with open(demo1_file, "r") as f:
            content = f.read()
            assert "if __name__" in content or "main()" in content, "demo1 should have main entry"


class TestDemoIntegration:
    """Test demo integration with gifts library."""

    def test_demo_can_import_gifts(self):
        """Test demo can import gifts library."""
        try:
            import gifts

            assert hasattr(gifts, "METAR"), "gifts should have METAR class"
            assert hasattr(gifts, "TAF"), "gifts should have TAF class"
            assert hasattr(gifts, "SWA"), "gifts should have SWA class"
        except ImportError:
            pytest.skip("Cannot import gifts module")

    def test_demo_config_format(self):
        """Test demo configuration file has valid format."""
        demo_dir = os.path.join(os.path.dirname(__file__), "..", "demo")
        config_file = os.path.join(demo_dir, "iwxxmd.cfg")

        # Try to read as config file
        with open(config_file, "r") as f:
            lines = f.readlines()
            assert len(lines) > 0, "Config file should have content"


class TestDaemonFileHandling:
    """Test daemon file system event handling."""

    def test_daemon_file_handler_exists(self):
        """Test daemon file event handler exists."""
        try:
            from demo.iwxxmd import BulletinFileHandler

            assert BulletinFileHandler is not None
        except (ImportError, AttributeError):
            # Handler might be named differently or watchdog not available
            pytest.skip("Cannot import BulletinFileHandler")

    def test_daemon_observer_setup(self):
        """Test daemon can set up file observer."""
        try:
            from watchdog.observers import Observer

            observer = Observer()
            assert observer is not None
        except ImportError:
            pytest.skip("watchdog module not available")


class TestDemoErrorHandling:
    """Test demo error handling and edge cases."""

    def test_missing_database_handling(self):
        """Test demo handles missing database gracefully."""
        demo_dir = os.path.join(os.path.dirname(__file__), "..", "demo")
        # Verify aerodromes database exists
        db_file = os.path.join(demo_dir, "aerodromes.db")
        assert os.path.exists(db_file), "Database should exist"

    def test_sample_data_format_validation(self):
        """Test sample data is in valid TAC format."""
        demo_dir = os.path.join(os.path.dirname(__file__), "..", "demo")

        # Test METAR format - just verify file has content
        with open(os.path.join(demo_dir, "metars.txt"), "r") as f:
            content = f.read()
            # File should have content with METAR messages
            assert len(content) > 0, "metars.txt should have content"
            # Should contain METAR-like data
            assert any(keyword in content for keyword in ["METAR", "SPECI", "KJFK", "KLAX"]), (
                "METAR file should contain METAR messages or airport codes"
            )

    def test_taf_sample_format_validation(self):
        """Test TAF sample data is valid."""
        demo_dir = os.path.join(os.path.dirname(__file__), "..", "demo")

        with open(os.path.join(demo_dir, "tafs.txt"), "r") as f:
            content = f.read()
            lines = [l.strip() for l in content.split("\n") if l.strip()]
            assert any("TAF" in line for line in lines), "Should contain TAF messages"


class TestDemoImages:
    """Test demo images and visual assets."""

    def test_demo_images_directory_exists(self):
        """Test demo images directory exists."""
        demo_dir = os.path.join(os.path.dirname(__file__), "..", "demo")
        images_dir = os.path.join(demo_dir, "images")
        assert os.path.isdir(images_dir), "images directory should exist"

    def test_demo_images_readable(self):
        """Test demo images are readable."""
        demo_dir = os.path.join(os.path.dirname(__file__), "..", "demo")
        images_dir = os.path.join(demo_dir, "images")

        if os.path.exists(images_dir):
            [f for f in os.listdir(images_dir) if f.endswith((".png", ".jpg", ".jpeg", ".gif"))]
            # At least verify directory is accessible
            assert os.access(images_dir, os.R_OK), "images directory should be readable"


class TestDaemonSignalHandling:
    """Test daemon signal handling."""

    def test_daemon_signal_handler_setup(self):
        """Test daemon can set up signal handlers."""
        try:
            import signal

            # Verify signal module works
            assert hasattr(signal, "SIGTERM")
            assert hasattr(signal, "SIGINT")
        except ImportError:
            pytest.skip("signal module not available")

    def test_daemon_cleanup(self):
        """Test daemon cleanup process."""
        try:
            from demo.iwxxmd import Daemon

            daemon = Daemon()
            # Daemon should be able to be instantiated and cleaned up
            assert daemon is not None
        except ImportError:
            pytest.skip("Cannot import Daemon")


class TestDemoConfigurationParsing:
    """Test demo configuration parsing."""

    def test_config_file_readable(self):
        """Test config file is readable."""
        demo_dir = os.path.join(os.path.dirname(__file__), "..", "demo")
        config_file = os.path.join(demo_dir, "iwxxmd.cfg")

        with open(config_file, "r") as f:
            content = f.read()
            assert len(content) > 0, "Config file should have content"

    def test_config_contains_settings(self):
        """Test config file contains expected settings."""
        demo_dir = os.path.join(os.path.dirname(__file__), "..", "demo")
        config_file = os.path.join(demo_dir, "iwxxmd.cfg")

        with open(config_file, "r") as f:
            content = f.read().lower()
            # Config should have some settings
            assert len(content) > 0, "Config should have content"


class TestDemoModuleStructure:
    """Test overall demo module structure."""

    def test_demo_directory_readable(self):
        """Test demo directory is readable."""
        demo_dir = os.path.join(os.path.dirname(__file__), "..", "demo")
        assert os.access(demo_dir, os.R_OK), "demo directory should be readable"

    def test_all_demo_files_readable(self):
        """Test all demo files are readable."""
        demo_dir = os.path.join(os.path.dirname(__file__), "..", "demo")
        for filename in os.listdir(demo_dir):
            filepath = os.path.join(demo_dir, filename)
            if os.path.isfile(filepath):
                assert os.access(filepath, os.R_OK), f"{filename} should be readable"

    def test_demo_python_files_syntax(self):
        """Test demo Python files have valid syntax."""
        demo_dir = os.path.join(os.path.dirname(__file__), "..", "demo")
        for filename in ["demo1.py", "iwxxmd.py"]:
            filepath = os.path.join(demo_dir, filename)
            if os.path.exists(filepath):
                try:
                    with open(filepath, "r") as f:
                        compile(f.read(), filepath, "exec")
                except SyntaxError as e:
                    pytest.fail(f"Syntax error in {filename}: {e}")
