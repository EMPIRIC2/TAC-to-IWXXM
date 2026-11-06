<?xml version="1.0" encoding="UTF-8"?>
<collect:MeteorologicalBulletin
    xmlns:collect="http://def.wmo.int/collect/2014"
    xmlns:gml="http://www.opengis.net/gml/3.2"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    gml:id="uuid.01c7055f-7389-4fcc-a2ae-819cebda81c1">
    <collect:meteorologicalInformation>
<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:gml="http://www.opengis.net/gml/3.2"
    xmlns:aixm="http://www.aixm.aero/schema/5.1.1"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    gml:id="metar.nosig.sycj"
    reportStatus="NORMAL"
    permissibleUsage="OPERATIONAL"
    automatedStation="false">
  <iwxxm:issueTime>
    <gml:TimeInstant gml:id="t.issue">
      <gml:timePosition>2023-06-27T01:00:00Z</gml:timePosition>
    </gml:TimeInstant>
  </iwxxm:issueTime>
  <iwxxm:aerodrome>
    <aixm:AirportHeliport gml:id="ad.sycj">
      <aixm:timeSlice>
        <aixm:AirportHeliportTimeSlice gml:id="ad.ts.sycj">
          <gml:validTime/>
          <aixm:interpretation>SNAPSHOT</aixm:interpretation>
          <aixm:designator>SYCJ</aixm:designator>
          <aixm:locationIndicatorICAO>SYCJ</aixm:locationIndicatorICAO>
        </aixm:AirportHeliportTimeSlice>
      </aixm:timeSlice>
    </aixm:AirportHeliport>
  </iwxxm:aerodrome>
  <iwxxm:observationTime>
    <gml:TimeInstant gml:id="t.obs">
      <gml:timePosition>2023-06-27T01:00:00Z</gml:timePosition>
    </gml:TimeInstant>
  </iwxxm:observationTime>
  <iwxxm:observation>
    <iwxxm:MeteorologicalAerodromeObservation gml:id="obs.1" cloudAndVisibilityOK="false">
      <iwxxm:airTemperature uom="Cel">27.0</iwxxm:airTemperature>
      <iwxxm:dewpointTemperature uom="Cel">25.0</iwxxm:dewpointTemperature>
      <iwxxm:qnh uom="hPa">1012</iwxxm:qnh>
      <iwxxm:surfaceWind>
        <iwxxm:AerodromeSurfaceWind variableWindDirection="true">
          <iwxxm:meanWindSpeed uom="[kn_i]">2</iwxxm:meanWindSpeed>
        </iwxxm:AerodromeSurfaceWind>
      </iwxxm:surfaceWind>
      <iwxxm:visibility>
        <iwxxm:AerodromeHorizontalVisibility>
          <iwxxm:prevailingVisibility uom="m">9999</iwxxm:prevailingVisibility>
          <iwxxm:prevailingVisibilityOperator>ABOVE</iwxxm:prevailingVisibilityOperator>
        </iwxxm:AerodromeHorizontalVisibility>
      </iwxxm:visibility>
      <iwxxm:cloud>
        <iwxxm:AerodromeCloud>
          <iwxxm:layer>
            <iwxxm:CloudLayer>
              <iwxxm:amount xlink:href="http://codes.wmo.int/49-2/CloudAmountReportedAtAerodrome/FEW"/>
              <iwxxm:base uom="[ft_i]">1800</iwxxm:base>
            </iwxxm:CloudLayer>
          </iwxxm:layer>
        </iwxxm:AerodromeCloud>
      </iwxxm:cloud>
    </iwxxm:MeteorologicalAerodromeObservation>
  </iwxxm:observation>
  <iwxxm:trendForecast nilReason="http://codes.wmo.int/common/nil/noSignificantChange"/>
</iwxxm:METAR>
    </collect:meteorologicalInformation>
    <collect:bulletinIdentifier>A_LAGY31SYCJ270100_C_SYCJ_20260927010000.xml</collect:bulletinIdentifier>
</collect:MeteorologicalBulletin>