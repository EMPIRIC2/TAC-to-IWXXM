# METAR to IWXXM Conversion - Architecture Overview

## System Design (Sprint 1 + Sprint 2)

### Layered Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    TEST GENERATION & EXECUTION                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ tests/test_dynamic_metar_generation.py (200+ parameterized) │   │
│  │ ├─ TestDynamicMETARConversion (IWXXM 2023-1 & 2025-2)       │   │
│  │ ├─ TestRegionalCoverage (7 regions)                        │   │
│  │ └─ TestPhenomenonCoverage (8 weather types)               │   │
│  └─────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ scripts/generate_test_data.py (standalone generator)        │   │
│  │ ├─ API configuration validation                            │   │
│  │ ├─ Test case generation                                    │   │
│  │ ├─ Coverage reporting                                      │   │
│  │ └─ Failure analysis                                        │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                    TEST DATA GENERATION LAYER                        │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ METARTestGenerator (src/testing/metar_test_generator.py)    │   │
│  │ ├─ diverse_sample() - 7 world regions                      │   │
│  │ ├─ regional_sample() - specific region                     │   │
│  │ ├─ phenomenon_coverage() - target weather                  │   │
│  │ ├─ Feature extraction (regex-based)                        │   │
│  │ └─ Caching (JSON, 1-hour TTL)                              │   │
│  └─────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Coverage Tracking                                           │   │
│  │ ├─ Stations, countries, regions                            │   │
│  │ ├─ Weather phenomena, cloud types                          │   │
│  │ └─ Complexity distribution                                 │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                  DATA ENRICHMENT & RECONCILIATION                    │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ AirportReconciliationService                               │   │
│  │ ├─ Priority: OpenAIP > GIFTs > AviationWeather            │   │
│  │ ├─ Conflict detection & resolution                        │   │
│  │ ├─ Confidence scoring                                     │   │
│  │ └─ Multi-source data merge                                │   │
│  └─────────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────┬──────────────────────┬──────────────────┐ │
│  │ OpenAIPClient        │ WMOCodelistsClient   │ ViaAviationWx    │ │
│  │ ├─ Airport data      │ ├─ Weather validation│ ├─ Known from    │ │
│  │ ├─ Coordinates       │ │  phenomena         │ │  API responses │ │
│  │ ├─ Elevation         │ │  ├─ RA, SN, TS...  │ ├─ Station names │ │
│  │ ├─ IATA codes        │ │  ├─ FG, BR, etc.   │ └─ Latest data   │ │
│  │ └─ 40K+ airports     │ │  └─ Validations    │                  │ │
│  └──────────────────────┴──────────────────────┴──────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                      DATA ACCESS LAYER                               │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ AviationWeatherClient                                        │  │
│  │ ├─ async fetch_metar_batch(stations)                        │  │
│  │ ├─ async fetch_metars_by_bbox(bbox, hours)  ← NEW          │  │
│  │ ├─ async fetch_random_sample(count, regions) ← NEW         │  │
│  │ `─ sync wrappers for convenience  ← NEW                     │  │
│  │   ├─ CachedAviationWeatherClient (MD5 keyed, 1hr TTL)      │  │
│  │   └─ Supports JSON & raw formats                           │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                      LIVE DATA SOURCES                               │
│  ┌──────────────────┬──────────────────┬──────────────────────────┐ │
│  │ AviationWeather  │ OpenAIP Database │ WMO Codelists           │ │
│  │ .gov API         │ (Local Cache)    │ (codes.wmo.int)         │ │
│  ├──────────────────┼──────────────────┼──────────────────────────┤ │
│  │ • Base URL:      │ • Format:        │ • Registry:             │ │
│  │   /api/data/metar│   GeoJSON        │   https://codes.wmo.int │ │
│  │ • Query: bbox    │ • Coverage:      │ • Concepts:             │ │
│  │ • Returns: JSON  │   ~40,000        │   - Weather phenomena   │ │
│  │ • Auth: None req │ • Schema:        │   - Cloud types         │ │
│  │ • Rate limit:    │   GeoJSON        │   - Cloud amounts       │ │
│  │   respectful     │   FeatureCol     │ • Format: RDF/XML       │ │
│  │ • Updated: 3h    │                  │ • Online cache: 1 week  │ │
│  └──────────────────┴──────────────────┴──────────────────────────┘ │
│  Local: data/af-airports.csv (GIFTs)                              │ │
│  ├─ 100K+ airport records                                         │ │
│  ├─ ICAO codes, names, coords, elevation                          │ │
│  └─ Primary for African airports                                  │ │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Complete Test Generation Flow

```
┌─ python3 scripts/generate_test_data.py ─┐
│                                          │
├─→ Load Environment Variables             │
│   ├─ OPENAIP_API_KEY (optional)         │
│   ├─ WMO_ONLINE_VALIDATION              │
│   └─ ENABLE_LIVE_API_TESTS              │
│                                          │
├─→ Initialize METARTestGenerator         │
│   ├─→ Create AviationWeatherClient      │
│   ├─→ Create OpenAIPClient              │
│   ├─→ Create WMOCodelistsClient         │
│   └─→ Create AirportReconciliationSvc  │
│                                          │
├─→ Generate diverse_sample(200 cases)    │
│   │                                      │
│   ├─→ For each of 7 world regions:      │
│   │   │                                  │
│   │   ├─→ fetch_metars_by_bbox_sync()   │
│   │   │   ├─ Query AviationWeather API  │
│   │   │   └─ Get 400+ METARs per region │
│   │   │                                  │
│   │   ├─→ Sample if > regional quota    │
│   │   │                                  │
│   │   ├─→ For each METAR:               │
│   │   │   │                              │
│   │   │   ├─→ Parse features            │
│   │   │   │   ├─ Extract weather codes  │
│   │   │   │   ├─ Extract cloud types    │
│   │   │   │   └─ Extract visibility     │
│   │   │   │                              │
│   │   │   ├─→ Enrich with metadata      │
│   │   │   │   ├─ Get Airport from svc   │
│   │   │   │   ├─ Classify region        │
│   │   │   │   └─ Set coordinates        │
│   │   │   │                              │
│   │   │   ├─→ Create METARTestCase      │
│   │   │   │                              │
│   │   │   └─→ Add to coverage tracking  │
│   │   │                                  │
│   │   └─→ Cache regional results        │
│   │                                      │
│   └─→ Return 200 diverse test cases     │
│       (or use cache if available)       │
│                                          │
├─→ Generate regional_sample per region   │
│   └─→ Similar flow but single region    │
│                                          │
├─→ Generate phenomenon_coverage          │
│   │                                      │
│   └─→ Search all regions for:           │
│       ├─ RA (Rain)                      │
│       ├─ SN (Snow)                      │
│       ├─ TS (Thunderstorm)              │
│       ├─ FG (Fog)                       │
│       ├─ BR (Mist)                      │
│       ├─ CB (Cumulonimbus)              │
│       ├─ TCU (Towering Cumulus)         │
│       └─ NSW (No Significant Weather)   │
│                                          │
├─→ Generate Coverage Report              │
│   ├─ Save as coverage_report.json       │
│   └─ Display statistics in console      │
│                                          │
└─→ Exit (or run tests)                   │
```

### Test Execution Flow

```
┌─ pytest tests/test_dynamic_metar_generation.py ─┐
│                                                   │
├─→ Collect fixtures                              │
│   └─ test_cases (200+ parameterized tests)      │
│                                                   │
├─→ For each test_case (e.g., KDCA, KJFK, etc.): │
│   │                                              │
│   ├─→ convert_metar_tac_with_metadata()         │
│   │   (Use case-specific version: 2023-1 or)    │
│   │   (2025-2)                                   │
│   │                                              │
│   ├─→ Assert:                                    │
│   │   ├─ IWXXM XML not empty                    │
│   │   ├─ Station ID in output                   │
│   │   ├─ Validation passed (optional)           │
│   │   └─ Version string present                 │
│   │                                              │
│   ├─→ On failure:                               │
│   │   └─ Save failure report to JSON            │
│   │       test-reports/dynamic-test-failures/   │
│   │                                              │
│   └─→ Update coverage statistics                │
│                                                   │
├─→ Generate Coverage Report                      │
│   ├─ Unique stations tested                     │
│   ├─ Success/failure rates                      │
│   ├─ Phenomena distribution                     │
│   └─ Regional performance                       │
│                                                   │
└─→ Exit with results                             │
```

## Component Integration Points

### When AirportReconciliationService Gets Data

```
reconciliation.get_airport("KDCA")
├─ Check OpenAIP (highest priority)
│  ├─ Loaded from data/open-aip/ (GeoJSON)
│  ├─ Search by ICAO code
│  └─ Return Airport object with metadata
├─ If not found, check GIFTs database
│  ├─ Load from data/af-airports.csv
│  ├─ Search by icao_code column
│  └─ Return airport data dict
├─ If not found, check AviationWeather (minimal)
│  └─ Use only coordinates from API
└─ Reconcile conflicts if multiple sources have data
   ├─ Priority-based resolution
   ├─ Confidence scoring
   └─ Return ReconciledAirport object
```

### When METARTestGenerator Creates Test Cases

```
test_generator.diverse_sample(count=200)
├─ For each region (7 total):
│  ├─ aviation_weather_client.fetch_metars_by_bbox_sync()
│  │  └─ Live API call → 400+ raw METARs
│  └─ For each METAR:
│     ├─ Extract from metar_data dict:
│     │  ├─ icaoId → station_id
│     │  ├─ rawOb → raw_metar
│     │  ├─ lat, lon → coordinates
│     │  └─ elev → elevation_m
│     ├─ _parse_metar_features(raw_metar)
│     │  ├─ Regex: look for RA, SN, TS, FG... → weather_phenomena
│     │  ├─ Regex: look for FEW, SCT, BKN, OVC → cloud_amounts
│     │  ├─ Regex: look for CB, TCU → cloud_types
│     │  └─ Calculate complexity_score()
│     ├─ reconciliation.get_airport(station_id)
│     │  ├─ Get enriched metadata (country, better coords, etc.)
│     │  └─ Store in METARTestCase
│     └─ Store in coverage tracking
└─ Cache results to JSON file
```

## Data Structures

### METARTestCase

```python
@dataclass
class METARTestCase:
    # Identifiers
    station_id: str                        # ICAO code (e.g., "KDCA")
    raw_metar: str                         # Full TAC (e.g., "METAR KDCA...")
    
    # Location
    latitude: Optional[float]              # Degrees (-90 to 90)
    longitude: Optional[float]             # Degrees (-180 to 180)
    country: Optional[str]                 # ISO country code (e.g., "US")
    elevation: Optional[float]             # Meters above sea level
    
    # Meteorology
    weather_phenomena: List[str]           # [RA, SN, TS, etc.]
    cloud_types: List[str]                 # [CB, TCU, etc.]
    cloud_amounts: List[str]               # [FEW, SCT, BKN, OVC, etc.]
    visibility: Optional[str]              # Presence indicator
    temperature: Optional[float]           # Degrees C
    
    # Metadata
    region: Optional[str]                  # World region
    timestamp: Optional[datetime]          # When created
    source: str                            # "aviation_weather" or "cache"
    
    # Methods
    has_weather() → bool                   # weather_phenomena non-empty?
    has_clouds() → bool                    # cloud_amounts non-empty?
    complexity_score() → int               # 0-10+ (higher = more complex)
```

### CoverageReport

```python
@dataclass
class CoverageReport:
    total_cases: int                       # Total test cases
    unique_stations: Set[str]              # {KDCA, KJFK, ...}
    countries: Set[str]                    # {US, CA, GB, ...}
    regions: Set[str]                      # {north_america, europe, ...}
    
    weather_phenomena: Set[str]            # {RA, SN, TS, FG, BR, CB, TCU}
    cloud_types: Set[str]                  # {CB, TCU}
    cloud_amounts: Set[str]                # {FEW, SCT, BKN, OVC, CLR, SKC}
    
    # Distribution
    simple_cases: int                      # Complexity 0-2
    medium_cases: int                      # Complexity 3-6
    complex_cases: int                     # Complexity 7+
    
    # Methods
    add_test_case(METARTestCase) → None   # Update tracking
    to_dict() → Dict                       # For JSON export
```

## Caching Strategy

### Cache Directory Structure

```
test-data/generated-tests/
├─ coverage_report.json
│  └─ Coverage statistics in JSON format
│
├─ diverse_sample_200_3h.json
│  └─ 200 METARs from 7 regions, 3-hour lookback
│
├─ regional_north_america_30_3h.json
├─ regional_europe_30_3h.json
├─ regional_asia_pacific_30_3h.json
├─ regional_south_america_30_3h.json
├─ regional_africa_30_3h.json
├─ regional_middle_east_30_3h.json
└─ regional_australia_30_3h.json
```

### Cache Keys

Generated using MD5 of:
```
(method_name, param1, param2, ..., hours, format_type)
```

Example:
```
bbox query: MD5("bbox", (-10, 35, 40, 70), 3, "json")
sample query: MD5("sample", 100, 3)
```

### TTL

- AviationWeather cache: **1 hour** (3600s) by default
- Manual override: `use_cache=False` bypasses

## Error Handling

### API Failures

```
try fetch_metars_by_bbox()
├─ HTTP 200 + valid JSON → Return data
├─ HTTP 404 → Return empty list
├─ HTTP 5xx → Raise AviationWeatherAPIError
├─ Network timeout → Raise RequestError
└─ JSON parse error → Continue to next region

Result: Graceful degradation, partial coverage acceptable
```

### Metadata Enrichment Failures

```
try reconciliation.get_airport(station_id)
├─ Found in OpenAIP → Return full data
├─ Found in GIFTs → Return available fields
├─ Found in API → Use only coordinates
└─ Not found → Return None

Result: Test case created with API data as fallback
```

## Performance Characteristics

### First Run (All API Calls)

```
7 regions × 400 METARs × 3 API calls (with retries)
├─ Network latency: ~2-5 seconds per call
├─ JSON parsing: ~1-2 seconds per response
├─ Airport enrichment: ~5-10 seconds total
└─ Total: 30-60 seconds
```

### Cached Runs

```
Load JSON files from disk
├─ File I/O: <100ms
├─ JSON parse: ~500ms
└─ Total: <1 second
```

### Test Execution (200 tests)

```
For each METAR:
├─ Convert to IWXXM: 100-500ms
├─ Save failure report (if failed): ~50ms
└─ 200 test cases: 1-5 minutes
```

## Security Considerations

### API Keys

- **OpenAIP key**: Optional, stored in .env (from user attachment)
- **WMO**: No auth required (public registry)
- **AviationWeather**: No auth required (no rate limiting for research use)

### Data Privacy

- Test data is public (weather is public information)
- Failure reports saved locally only
- No data transmitted outside of direct API calls

### Cache Security

- Cache files are local JSON (plain text)
- No sensitive data cached
- Can be safely committed to version control (or .gitignore if preferred)

## Summary

This architecture provides:

1. **Scalability**: 200+ tests with one command, easily extensible
2. **Reproducibility**: Cached data ensures same tests across runs
3. **Coverage**: 7 world regions, 8+ phenomena, 79+ stations
4. **Integration**: Leverages all Sprint 1 components
5. **Maintainability**: Clean separation of concerns
6. **Extensibility**: Ready for Sprint 3 semantic validation
