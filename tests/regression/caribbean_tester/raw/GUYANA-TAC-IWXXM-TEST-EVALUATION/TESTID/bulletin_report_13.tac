<?xml version="1.0" encoding="UTF-8"?>
<collect:MeteorologicalBulletin
    xmlns:collect="http://def.wmo.int/collect/2014"
    xmlns:gml="http://www.opengis.net/gml/3.2"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    gml:id="uuid.14b39be8-1837-4ab3-9f4c-0078bc0bf5cc">
    <collect:meteorologicalInformation>
<iwxxm:TAF xmlns:iwxxm="http://icao.int/iwxxm/2025-2"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:gml="http://www.opengis.net/gml/3.2"
    xmlns:aixm="http://www.aixm.aero/schema/5.1.1"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    gml:id="taf.basic.ttcp"
    reportStatus="NORMAL"
    permissibleUsage="OPERATIONAL">
  <iwxxm:issueTime>
    <gml:TimeInstant gml:id="t.issue">
      <gml:timePosition>2023-06-08T16:00:00Z</gml:timePosition>
    </gml:TimeInstant>
  </iwxxm:issueTime>
  <iwxxm:aerodrome>
    <aixm:AirportHeliport gml:id="ad.ttcp">
      <aixm:timeSlice>
        <aixm:AirportHeliportTimeSlice gml:id="ad.ts.ttcp">
          <gml:validTime/>
          <aixm:interpretation>SNAPSHOT</aixm:interpretation>
          <aixm:designator>TTCP</aixm:designator>
          <aixm:locationIndicatorICAO>TTCP</aixm:locationIndicatorICAO>
        </aixm:AirportHeliportTimeSlice>
      </aixm:timeSlice>
    </aixm:AirportHeliport>
  </iwxxm:aerodrome>
  <iwxxm:validPeriod>
    <gml:TimePeriod gml:id="t.valid">
      <gml:beginPosition>2023-06-08T18:00:00Z</gml:beginPosition>
      <gml:endPosition>2023-06-09T18:00:00Z</gml:endPosition>
    </gml:TimePeriod>
  </iwxxm:validPeriod>
  <iwxxm:baseForecast>
    <iwxxm:MeteorologicalAerodromeForecast gml:id="fcst.base.ttcp" cloudAndVisibilityOK="false">
      <iwxxm:phenomenonTime xlink:href="#uuid.00000000-0000-4000-8000-000000000001"/>
      <iwxxm:prevailingVisibility uom="m">10000</iwxxm:prevailingVisibility>
      <iwxxm:prevailingVisibilityOperator>ABOVE</iwxxm:prevailingVisibilityOperator>
      <iwxxm:surfaceWind>
        <iwxxm:AerodromeSurfaceWindForecast variableWindDirection="false">
          <iwxxm:meanWindDirection uom="deg">100</iwxxm:meanWindDirection>
          <iwxxm:meanWindSpeed uom="[kn_i]">14</iwxxm:meanWindSpeed>
        </iwxxm:AerodromeSurfaceWindForecast>
      </iwxxm:surfaceWind>
      <iwxxm:cloud>
        <iwxxm:AerodromeCloudForecast gml:id="cloud.base.ttcp">
          <iwxxm:layer>
            <iwxxm:CloudLayer>
              <iwxxm:amount xlink:href="http://codes.wmo.int/49-2/CloudAmountReportedAtAerodrome/SCT"/>
              <iwxxm:base uom="[ft_i]">2200</iwxxm:base>
            </iwxxm:CloudLayer>
          </iwxxm:layer>
        </iwxxm:AerodromeCloudForecast>
      </iwxxm:cloud>
    </iwxxm:MeteorologicalAerodromeForecast>
  </iwxxm:baseForecast>
  <iwxxm:changeForecast>
    <iwxxm:MeteorologicalAerodromeForecast gml:id="fcst.chg.1.ttcp" changeIndicator="BECOMING" cloudAndVisibilityOK="false">
      <iwxxm:phenomenonTime>
        <gml:TimePeriod gml:id="t.chg.1">
          <gml:beginPosition>2023-06-09T00:00:00Z</gml:beginPosition>
          <gml:endPosition>2023-06-09T02:00:00Z</gml:endPosition>
        </gml:TimePeriod>
      </iwxxm:phenomenonTime>
      <iwxxm:prevailingVisibility uom="m">6000</iwxxm:prevailingVisibility>
      <iwxxm:surfaceWind>
        <iwxxm:AerodromeSurfaceWindForecast variableWindDirection="false">
          <iwxxm:meanWindDirection uom="deg">80</iwxxm:meanWindDirection>
          <iwxxm:meanWindSpeed uom="[kn_i]">8</iwxxm:meanWindSpeed>
        </iwxxm:AerodromeSurfaceWindForecast>
      </iwxxm:surfaceWind>
      <iwxxm:weather xlink:href="http://codes.wmo.int/306/4678/SHRA"/>
      <iwxxm:cloud>
        <iwxxm:AerodromeCloudForecast gml:id="cloud.chg.1.ttcp">
          <iwxxm:layer>
            <iwxxm:CloudLayer>
              <iwxxm:amount xlink:href="http://codes.wmo.int/49-2/CloudAmountReportedAtAerodrome/FEW"/>
              <iwxxm:base uom="[ft_i]">1500</iwxxm:base>
            </iwxxm:CloudLayer>
          </iwxxm:layer>
          <iwxxm:layer>
            <iwxxm:CloudLayer>
              <iwxxm:amount xlink:href="http://codes.wmo.int/49-2/CloudAmountReportedAtAerodrome/SCT"/>
              <iwxxm:base uom="[ft_i]">4000</iwxxm:base>
            </iwxxm:CloudLayer>
          </iwxxm:layer>
          <iwxxm:layer>
            <iwxxm:CloudLayer>
              <iwxxm:amount xlink:href="http://codes.wmo.int/49-2/CloudAmountReportedAtAerodrome/FEW"/>
              <iwxxm:base uom="[ft_i]">1200</iwxxm:base>
              <iwxxm:cloudType xlink:href="http://codes.wmo.int/49-2/SigConvectiveCloudType/CB"/>
            </iwxxm:CloudLayer>
          </iwxxm:layer>
          <iwxxm:layer>
            <iwxxm:CloudLayer>
              <iwxxm:amount xlink:href="http://codes.wmo.int/49-2/CloudAmountReportedAtAerodrome/BKN"/>
              <iwxxm:base uom="[ft_i]">1500</iwxxm:base>
            </iwxxm:CloudLayer>
          </iwxxm:layer>
        </iwxxm:AerodromeCloudForecast>
      </iwxxm:cloud>
    </iwxxm:MeteorologicalAerodromeForecast>
  </iwxxm:changeForecast>
  <iwxxm:changeForecast>
    <iwxxm:MeteorologicalAerodromeForecast gml:id="fcst.chg.2.ttcp" changeIndicator="BECOMING" cloudAndVisibilityOK="false">
      <iwxxm:phenomenonTime>
        <gml:TimePeriod gml:id="t.chg.2">
          <gml:beginPosition>2023-06-09T12:00:00Z</gml:beginPosition>
          <gml:endPosition>2023-06-09T14:00:00Z</gml:endPosition>
        </gml:TimePeriod>
      </iwxxm:phenomenonTime>
      <iwxxm:surfaceWind>
        <iwxxm:AerodromeSurfaceWindForecast variableWindDirection="false">
          <iwxxm:meanWindDirection uom="deg">120</iwxxm:meanWindDirection>
          <iwxxm:meanWindSpeed uom="[kn_i]">15</iwxxm:meanWindSpeed>
        </iwxxm:AerodromeSurfaceWindForecast>
      </iwxxm:surfaceWind>
      <iwxxm:cloud>
        <iwxxm:AerodromeCloudForecast gml:id="cloud.chg.2.ttcp">
          <iwxxm:layer>
            <iwxxm:CloudLayer>
              <iwxxm:amount xlink:href="http://codes.wmo.int/49-2/CloudAmountReportedAtAerodrome/SCT"/>
              <iwxxm:base uom="[ft_i]">1600</iwxxm:base>
            </iwxxm:CloudLayer>
          </iwxxm:layer>
          <iwxxm:layer>
            <iwxxm:CloudLayer>
              <iwxxm:amount xlink:href="http://codes.wmo.int/49-2/CloudAmountReportedAtAerodrome/SCT"/>
              <iwxxm:base uom="[ft_i]">4500</iwxxm:base>
            </iwxxm:CloudLayer>
          </iwxxm:layer>
        </iwxxm:AerodromeCloudForecast>
      </iwxxm:cloud>
    </iwxxm:MeteorologicalAerodromeForecast>
  </iwxxm:changeForecast>
</iwxxm:TAF>
    </collect:meteorologicalInformation>
    <collect:bulletinIdentifier>A_LTCA31TTPP081600_C_TTPP_20260908160000.xml</collect:bulletinIdentifier>
</collect:MeteorologicalBulletin>