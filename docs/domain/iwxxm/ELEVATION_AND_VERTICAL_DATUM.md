# Elevation and Vertical Datum System

## Overview

The METAR-to-IWXXM conversion system now includes accurate elevation and vertical datum data for 9,590+ airports worldwide. Each airport's elevation is referenced to the appropriate vertical datum based on the country's national geodetic system.

## Coordinate Reference Systems

### Horizontal Position
All horizontal positions use **EPSG:4326 (WGS84)**:
- **srsName**: `http://www.opengis.net/def/crs/EPSG/0/4326`
- **Format**: Latitude, Longitude (decimal degrees, 8 decimal places)
- **Accuracy**: ~1 centimeter (per ICAO Annex 3)

### Vertical Datums

Different countries use different vertical reference systems for elevation. The system automatically selects the correct vertical datum based on the airport's country:

| Country/Region | Vertical Datum | IWXXM Code | Description |
|---------------|---------------|------------|-------------|
| **Global Default** | EGM96 | `EGM_96` | Earth Gravitational Model 1996 |
| USA | NAVD88 | `NAVD88` | North American Vertical Datum 1988 |
| Canada | CGVD2013 | `OTHER:CGVD2013` | Canadian Geodetic Vertical Datum 2013 |
| Mexico | NAVD88 | `NAVD88` | North American Vertical Datum 1988 |
| Greenland | EGM96 | `EGM_96` | Earth Gravitational Model 1996 |
| Australia | AHD | `AHD` | Australian Height Datum |
| New Zealand | NZVD2016 | `OTHER:NZVD2016` | New Zealand Vertical Datum 2016 |
| United Kingdom | ODN | `OTHER:ODN` | Ordnance Datum Newlyn |
| Germany | DHHN92 | `OTHER:DHHN92` | Deutsches Haupthöhennetz 1992 |
| France | NGF-IGN69 | `OTHER:NGF_IGN69` | Nivellement Général de la France |
| Europe (multi) | EVRF2007 | `OTHER:EVRF2007` | European Vertical Reference Frame 2007 |
| Russia | Baltic 1977 | `OTHER:BALTIC_1977` | Baltic Datum 1977 |

**Note**: IWXXM natively supports three datums (`EGM_96`, `NAVD88`, `AHD`). Others use the `OTHER:` prefix.

## Data Sources

### Airport Database
- **Source**: OurAirports.com (global airport database)
- **Coverage**: 9,590 airports with ICAO codes
- **Data**: Name, IATA code, coordinates, elevation (feet)
- **Update Frequency**: Manual updates via script

### Vertical Datum Mapping
- **File**: `backend/src/data/vertical_datum_map.json`
- **Contains**:
  - Country-level default datums (45 countries)
  - Airport-specific overrides (for exceptions)
  - Datum metadata and descriptions

### Elevation Service
- **Location**: `backend/src/utilities/elevation_service.py`
- **Features**:
  - Automatic datum selection by country
  - Airport-specific overrides
  - Elevation conversion (feet → meters)
  - Runtime configuration of GIFTs encoder

## Example Output

### BGBW (Greenland) - EGM96
```xml
<aixm:ElevatedPoint srsDimension="2" 
                    srsName="http://www.opengis.net/def/crs/EPSG/0/4326" 
                    axisLabels="Lat Long">
  <gml:pos>61.16050000 -45.42599900</gml:pos>
  <aixm:elevation uom="M">34</aixm:elevation>
  <aixm:verticalDatum>EGM_96</aixm:verticalDatum>
</aixm:ElevatedPoint>
```

### KJFK (USA) - NAVD88
```xml
<aixm:ElevatedPoint srsDimension="2" 
                    srsName="http://www.opengis.net/def/crs/EPSG/0/4326" 
                    axisLabels="Lat Long">
  <gml:pos>40.63944700 -73.77931700</gml:pos>
  <aixm:elevation uom="M">4</aixm:elevation>
  <aixm:verticalDatum>NAVD88</aixm:verticalDatum>
</aixm:ElevatedPoint>
```

### EGLL (UK) - ODN
```xml
<aixm:ElevatedPoint srsDimension="2" 
                    srsName="http://www.opengis.net/def/crs/EPSG/0/4326" 
                    axisLabels="Lat Long">
  <gml:pos>51.47074800 -0.45990900</gml:pos>
  <aixm:elevation uom="M">25</aixm:elevation>
  <aixm:verticalDatum>OTHER:ODN</aixm:verticalDatum>
</aixm:ElevatedPoint>
```

## Configuration

### Adding Country Defaults

Edit `backend/src/data/vertical_datum_map.json`:

```json
{
  "country_defaults": {
    "XX": "EGM96",  // Add 2-letter ISO country code
    ...
  }
}
```

### Adding Airport-Specific Overrides

For airports that use non-standard datums:

```json
{
  "airport_overrides": {
    "ICAO": {
      "vertical_datum": "EGM_96",
      "elevation_m": 123,
      "source": "National AIP",
      "notes": "Special handling required"
    }
  }
}
```

### Updating Airport Database

Run the update script to refresh from OurAirports:

```bash
cd backend
python3 scripts/update_airports_db.py
```

This will:
1. Download latest airport data
2. Apply vertical datum mappings
3. Convert elevations to meters
4. Generate `src/data/airports.json`

## Accuracy Considerations

### Elevation Precision
- **Source**: OurAirports (varies by airport)
- **Conversion**: Feet to meters (×0.3048)
- **Rounding**: To nearest meter
- **Accuracy**: ±1-5 meters typical

### Recommended Practice
For critical aviation applications, verify elevation and datum from authoritative sources:
- **ICAO AIP** (Aeronautical Information Publication)
- **FAA NASR** (US airports)
- **EuroControl** (European airports)
- **National AIS** (country-specific)

Use airport-specific overrides when more accurate data is available.

## References

- **ICAO Annex 3**: Meteorological Service for International Air Navigation
- **ICAO Annex 15**: Aeronautical Information Services
- **WMO Manual on IWXXM**: Technical Regulations
- **OGC Standards**: http://www.opengis.net/def/crs/EPSG/0/
- **OurAirports**: https://ourairports.com/data/

## Testing

Run comprehensive datum tests:

```bash
# Test multiple airports across different countries
curl -X POST "http://localhost:8002/api/v1/convert" \
  -F "manual_text=METAR KJFK 121151Z 09014KT 10SM BKN250 04/M03 A2990" \
  -F "iwxxm_version=2023-1"
```

Expected vertical datums:
- **BGBW** (Greenland): EGM_96
- **KJFK** (USA): NAVD88
- **EGLL** (UK): OTHER:ODN
- **YSSY** (Australia): AHD

## Future Enhancements

1. **API Integration**: Fetch real-time elevation from authoritative sources
2. **Datum Transformation**: Convert between vertical datums when needed
3. **Quality Indicators**: Provide confidence/accuracy metadata
4. **AIXM 5.1 Compliance**: Full support for temporal aspects of vertical datums

## Support

For questions about vertical datum assignment or elevation accuracy:
- Check `vertical_datum_map.json` for country mappings
- Review `elevation_service.py` for lookup logic
- Consult ICAO AIP for authoritative airport data
