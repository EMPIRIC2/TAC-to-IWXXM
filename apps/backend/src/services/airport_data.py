"""Airport data management and auto-regeneration."""

from __future__ import annotations

import logging
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


def check_and_regenerate_airports() -> bool:
    """
    Check if airports.json needs regeneration and regenerate if needed.

    Compares modification times of af-airports.csv and airports.json.
    If CSV is newer, runs parse_airports_csv.py to regenerate.

    Returns:
        True if regeneration occurred, False otherwise
    """
    try:
        backend_root = Path(__file__).parent.parent.parent
        project_root = backend_root.parent

        csv_path = project_root / "data" / "af-airports.csv"
        backend_json = backend_root / "src" / "data" / "airports.json"
        script_path = project_root / "scripts" / "parse_airports_csv.py"

        if not csv_path.exists():
            logger.warning(f"Airport CSV not found at {csv_path}")
            return False

        if not script_path.exists():
            logger.warning(f"Parser script not found at {script_path}")
            return False

        if not backend_json.exists():
            logger.info("airports.json not found, regenerating...")
            return _run_parser(script_path)

        csv_mtime = csv_path.stat().st_mtime
        json_mtime = backend_json.stat().st_mtime

        if csv_mtime > json_mtime:
            logger.info("af-airports.csv is newer than airports.json, regenerating...")
            return _run_parser(script_path)

        logger.debug("airports.json is up to date")
        return False

    except Exception as e:
        logger.error(f"Error checking airport data: {e}", exc_info=True)
        return False


def _run_parser(script_path: Path) -> bool:
    """Run the parse_airports_csv.py script."""
    try:
        logger.info(f"Running {script_path}...")

        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            logger.info("Airport data regeneration successful")
            logger.debug(f"Parser output: {result.stdout}")
            return True
        else:
            logger.error(f"Parser failed with code {result.returncode}")
            logger.error(f"Parser stderr: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        logger.error("Parser script timed out after 30 seconds")
        return False
    except Exception as e:
        logger.error(f"Error running parser: {e}", exc_info=True)
        return False
