#!/usr/bin/env python3
"""
Fetch airport data from OpenAIP API and cache locally.

This script downloads airport information from the OpenAIP API and stores it
in a JSON cache for use during METAR-to-IWXXM conversion.

Usage:
    python3 fetch_openaip_airports.py [--refresh] [--limit 10000]

Environment:
    OPENAIP_API_KEY: Required API key for OpenAIP (from .env)
"""
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def get_openaip_api_key() -> str:
    """Get OpenAIP API key from environment or .env file."""
    # Try environment variable first
    if api_key := os.getenv("OPENAIP_API_KEY"):
        return api_key

    # Try to load from .env file
    env_file = Path(__file__).parent.parent.parent / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.startswith("OPENAIP_API_KEY="):
                    return line.split("=", 1)[1].strip()

    raise ValueError(
        "OPENAIP_API_KEY not found in environment or .env file. "
        "Set it in .env or export OPENAIP_API_KEY=<your_key>"
    )


def fetch_from_openaip(api_key: str, limit: int = 10000) -> Dict[str, dict]:
    """
    Fetch all airports from OpenAIP API.
    
    Args:
        api_key: OpenAIP API key
        limit: Maximum number of airports to fetch (pagination)
    
    Returns:
        Dictionary keyed by ICAO code with airport data
    """
    try:
        import requests
    except ImportError:
        logger.error("requests library not found. Install with: pip install requests")
        sys.exit(1)

    airports = {}
    base_url = "https://api.openaip.net/api/airports"
    headers = {"Authorization": f"Bearer {api_key}"}

    # OpenAIP uses pagination with skip parameter
    skip = 0
    batch_size = 500
    total_fetched = 0

    while total_fetched < limit:
        params = {
            "limit": min(batch_size, limit - total_fetched),
            "skip": skip
        }

        logger.info(f"Fetching airports: skip={skip}, limit={params['limit']}")

        try:
            response = requests.get(base_url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Failed to fetch from OpenAIP: {e}")
            if total_fetched == 0:
                raise
            logger.info(f"Stopping fetch at {total_fetched} airports due to error")
            break

        data = response.json()
        items = data.get("items", [])

        if not items:
            logger.info(f"No more airports to fetch (got {len(items)} items)")
            break

        for airport in items:
            icao = airport.get("icaoCode")
            if icao:
                airports[icao] = {
                    "name": airport.get("name", ""),
                    "iata": airport.get("iataCode", ""),
                    "icao": icao,
                    "type": airport.get("type", -1),
                    "country": airport.get("country", ""),
                    "coordinates": {
                        "latitude": airport.get("lat"),
                        "longitude": airport.get("lon")
                    }
                }

        total_fetched += len(items)
        skip += len(items)

    logger.info(f"Successfully fetched {total_fetched} airports")
    return airports


def load_cached_openaip(cache_file: Path) -> Optional[Dict[str, dict]]:
    """Load OpenAIP data from cache file."""
    if not cache_file.exists():
        return None

    try:
        with open(cache_file) as f:
            data = json.load(f)
        logger.info(f"Loaded {len(data)} airports from cache")
        return data
    except Exception as e:
        logger.warning(f"Failed to load cache: {e}")
        return None


def save_cached_openaip(airports: Dict[str, dict], cache_file: Path) -> None:
    """Save OpenAIP data to cache file."""
    cache_file.parent.mkdir(parents=True, exist_ok=True)

    # Add metadata
    cache_data = {
        "_metadata": {
            "source": "OpenAIP",
            "fetched_at": datetime.utcnow().isoformat(),
            "total_airports": len(airports),
            "api_version": "1.0"
        },
        "airports": airports
    }

    with open(cache_file, "w") as f:
        json.dump(cache_data, f, indent=2)

    logger.info(f"Saved {len(airports)} airports to {cache_file}")


def merge_with_special_overrides(airports: Dict[str, dict]) -> Dict[str, dict]:
    """
    Merge OpenAIP data with special case overrides for known problematic airports.
    
    Returns:
        Merged airport dictionary with special cases overridden
    """
    # ENFB: Fornebu Airport (closed 1998) - OpenAIP erroneously has it as Statfjord B
    special_cases = {
        "ENFB": {
            "name": "FORNEBU AIRPORT",
            "iata": "FBU",
            "icao": "ENFB",
            "country": "NO",
            "type": 1,  # Small airport
            "coordinates": {
                "latitude": 59.89580,
                "longitude": 10.6172
            },
            "_override_reason": "OurAirports/OpenAIP confusion with Statfjord B (501km away)",
            "_status": "closed",
            "_closure_year": 1998
        }
    }

    for icao, override_data in special_cases.items():
        if icao in airports:
            airports[icao].update(override_data)
            logger.info(f"Applied special override for {icao}")
        else:
            airports[icao] = override_data
            logger.info(f"Added special case for {icao}")

    return airports


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Fetch and cache airport data from OpenAIP API"
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Force refresh from API even if cache exists"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10000,
        help="Maximum number of airports to fetch (default: 10000)"
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=Path(__file__).parent.parent / "src" / "data",
        help="Directory to store cache file"
    )

    args = parser.parse_args()
    cache_file = args.cache_dir / "openaip_cache.json"

    logger.info("OpenAIP Airport Cache Manager")
    logger.info(f"Cache file: {cache_file}")

    try:
        api_key = get_openaip_api_key()
        logger.info("✓ OpenAIP API key found")
    except ValueError as e:
        logger.error(f"✗ {e}")
        return 1

    # Try to load from cache first
    if not args.refresh:
        if airports := load_cached_openaip(cache_file):
            logger.info(f"Using cached data ({len(airports)} airports)")
            print(json.dumps(airports, indent=2))
            return 0

    # Fetch from API
    logger.info("Fetching from OpenAIP API...")
    try:
        airports = fetch_from_openaip(api_key, limit=args.limit)
    except Exception as e:
        logger.error(f"Failed to fetch from OpenAIP: {e}")
        return 1

    # Apply special overrides
    airports = merge_with_special_overrides(airports)

    # Save cache
    try:
        save_cached_openaip(airports, cache_file)
        logger.info("✓ Cache updated successfully")
    except Exception as e:
        logger.error(f"Failed to save cache: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
