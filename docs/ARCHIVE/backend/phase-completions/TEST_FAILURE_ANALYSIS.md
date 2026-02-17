"""
COMPREHENSIVE TEST FAILURE ANALYSIS - FINDINGS & RECOMMENDATIONS
================================================================

SITUATION SUMMARY:
- 109 test cases with failures across 3 IWXXM amendments
- 701 total differences analyzed
- 118 cosmetic (16%) - safe to ignore (UUIDs, timestamps)
- 583 structural (84%) - need investigation

ROOT CAUSE IDENTIFIED:
All structural issues trace to ONE problem:
AirportHeliportTimeSlice is missing airport metadata:
  - name (44 occurrences)
  - locationIndicatorICAO (109 occurrences)  
  - designatorIATA (67 occurrences)
  - ARP / Aerodrome Reference Point (106 occurrences)

EVIDENCE:
1. Reference XMLs HAVE these fields
   Example from BGBW-282350Z.xml:
   <aixm:AirportHeliportTimeSlice>
     <gml:validTime/>
     <aixm:interpretation>SNAPSHOT</aixm:interpretation>
     <aixm:name>NARSARSUAQ AIRPORT</aixm:name>
     <aixm:locationIndicatorICAO>BGBW</aixm:locationIndicatorICAO>
     <aixm:designatorIATA>UAK</aixm:designatorIATA>
     <aixm:ARP>
       <aixm:ElevatedPoint>
         <gml:pos>61.16049957 -45.42599869</gml:pos>
         <aixm:elevation uom="M">34</aixm:elevation>
         <aixm:verticalDatum>EGM_96</aixm:verticalDatum>
       </aixm:ElevatedPoint>
     </aixm:ARP>
   </aixm:AirportHeliportTimeSlice>

2. GIFTs library CODE is ready to generate these fields
   File: /root/metar-to-IWXXM/GIFTs/gifts/common/Common.py (lines 45-89)
   The aerodrome() method populates:
   - token['name'] → <aixm:name>
   - token['str'] (ICAO) → <aixm:locationIndicatorICAO>
   - token['iataID'] → <aixm:designatorIATA>
   - token['position'] → <aixm:ARP> with coordinates + elevation

3. Backend IS using GIFTs
   File: /root/metar-to-IWXXM/backend/conversion.py
   Uses: metarDecoder.Annex3() → metarEncoder.Annex3()

CRITICAL QUESTIONS:
1. Does metarDecoder extract airport metadata from METAR?
   - METAR format: "METAR ICAO_CODE DATE_TIME DATA"
   - Contains: ICAO code, visibility, wind, temperature, etc.
   - Does NOT contain: airport name, IATA code, exact coordinates
   
2. Where does the encoder get airport NAME and IATA?
   - These should come from an airport database
   - We have: /root/metar-to-IWXXM/data/af-airports.csv (4,182 records)
   - Does GIFTs decode use it? Unknown
   
3. Where does ARP coordinates come from?
   - Must come from database lookup using ICAO code
   - Data exists in af-airports.csv (latitude_deg, longitude_deg)
   - Are these being looked up and passed? Unknown

NEXT STEPS (RECOMMENDED):

=== IMMEDIATE (15 minutes) ===
1. Check GIFTs input/output for airport lookup
   
   a) Look at: /root/metar-to-IWXXM/GIFTs/gifts/metar/Annex3.py
      - What does metarDecoder return format?
      - Does it have 'name', 'iataID', 'position' fields?
      
   b) Check: /root/metar-to-IWXXM/GIFTs/gifts/common/MetarConfig.py
      - How are airport lookups configured?
      - Is database lookup enabled?
      
2. Create small test script:
   ```python
   from gifts import metarDecoder
   decoded = metarDecoder.Annex3()("METAR BGBW 282350Z...")
   print("Decoded keys:", decoded.keys() if hasattr(decoded, 'keys') else dir(decoded))
   print("Has 'name'?", 'name' in decoded)
   print("Has 'iataID'?", 'iataID' in decoded)
   print("Has 'position'?", 'position' in decoded)
   ```

=== SHORT TERM (1 hour) ===
3. Determine if airport lookup is configured
   - GIFTs likely has airport lookup capability
   - Need to verify: is it enabled? is data path correct?
   
4. If lookup is disabled:
   - Enable airport database lookup in GIFTs configuration
   - Or: Add airport data augmentation layer to backend/conversion.py
   
5. If lookup is enabled but fails:
   - Debug why airport CSV lookup isn't working
   - Check path, format, lookup logic

=== VALIDATION PHASE (30 minutes) ===
6. After fix: Run full test suite
   - `pytest tests/test_conversion.py -v`
   - Should see dramatic improvement in test pass rate
   
7. Run Schematron on generated XMLs
   - Use Docker validator: SchematronValidatorDocker
   - Should pass Schematron validation if structure is correct
   
8. Update test expectations if needed
   - Some fields may still be legitimately optional
   - Schematron will clarify which are required vs optional

COSMETIC DIFFERENCES (Already Filtered):
These can be safely ignored in comparisons:
- UUIDs: #uuid.[a-f0-9\-]+ (generated per run)
- Timestamps: \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}

ACTION ITEMS:
[ ] Investigate GIFTs metarDecoder output structure
[ ] Check airport lookup configuration in GIFTs
[ ] Create test to see what's in decoded output
[ ] Enable/fix airport database lookups
[ ] Re-run test suite
[ ] Validate with Schematron
"""

print(__doc__)
