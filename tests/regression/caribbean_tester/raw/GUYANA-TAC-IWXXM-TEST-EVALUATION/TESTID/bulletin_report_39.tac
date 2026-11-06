<?xml version="1.0" encoding="UTF-8"?>
<collect:MeteorologicalBulletin
    xmlns:collect="http://def.wmo.int/collect/2014"
    xmlns:gml="http://www.opengis.net/gml/3.2"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    gml:id="uuid.f85d4749-bdc9-48f0-854e-552e0757af3b">
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
      <gml:timePosition>2023-06-27T08:00:00Z</gml:timePosition>
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
      <gml:timePosition>2023-06-27T08:00:00Z</gml:timePosition>
    </gml:TimeInstant>
  </iwxxm:observationTime>
  <iwxxm:observation>
    <iwxxm:MeteorologicalAerodromeObservation gml:id="obs.1" cloudAndVisibilityOK="false">
      <iwxxm:airTemperature uom="Cel">24.0</iwxxm:airTemperature>
      <iwxxm:dewpointTemperature uom="Cel">24.0</iwxxm:dewpointTemperature>
      <iwxxm:qnh uom="hPa">1011</iwxxm:qnh>
      <iwxxm:surfaceWind>
        <iwxxm:AerodromeSurfaceWind variableWindDirection="false">
          <iwxxm:meanWindDirection uom="deg">0</iwxxm:meanWindDirection>
          <iwxxm:meanWindSpeed uom="[kn_i]">0</iwxxm:meanWindSpeed>
        </iwxxm:AerodromeSurfaceWind>
      </iwxxm:surfaceWind>
      <iwxxm:visibility>
        <iwxxm:AerodromeHorizontalVisibility>
          <iwxxm:prevailingVisibility uom="m">700</iwxxm:prevailingVisibility>
        </iwxxm:AerodromeHorizontalVisibility>
      </iwxxm:visibility>
      <iwxxm:presentWeather xlink:href="http://codes.wmo.int/306/4678/FU"/>
      <iwxxm:cloud>
        <iwxxm:AerodromeCloud>
          <iwxxm:layer>
            <iwxxm:CloudLayer>
              <iwxxm:amount xlink:href="http://codes.wmo.int/49-2/CloudAmountReportedAtAerodrome/BKN"/>
              <iwxxm:base uom="[ft_i]">200</iwxxm:base>
            </iwxxm:CloudLayer>
          </iwxxm:layer>
        </iwxxm:AerodromeCloud>
      </iwxxm:cloud>
    </iwxxm:MeteorologicalAerodromeObservation>
  </iwxxm:observation>
  <iwxxm:trendForecast nilReason="http://codes.wmo.int/common/nil/noSignificantChange"/>
</iwxxm:METAR>
    </collect:meteorologicalInformation>
    <collect:bulletinIdentifier>A_LAGY31SYCJ270800_C_SYCJ_20260927080000.xml</collect:bulletinIdentifier>
</collect:MeteorologicalBulletin>