/**
 * Build Leaflet overlay markers from TAC parse + visibility. [Corpus: product] F37
 */

import L from 'leaflet';
import { shiftLatLng, WORLD_COPY_LNG_OFFSETS } from '@/utils/liveMap';
import {
  DEFAULT_OVERLAY_MAGNITUDE_SCALE,
  type LiveMapTempUnit,
  windVectorSizePx,
} from '@/utils/liveMapModes';
import {
  placeFeedsOverlay,
  windIntensityRadius,
  type TacOverlayLayerId,
  type TacOverlayVisibility,
} from '@/utils/liveMapTacLayers';
import { newestTac, parseTacOverlayFields } from '@/utils/liveMapTacParse';
import type { StationCluster } from '@/utils/liveMapStationCluster';
import {
  ICE_SVG,
  PRECIP_SVG,
  THUNDER_SVG,
  temperatureIconHtml,
  weatherIconHtml,
  windVectorIconHtml,
} from '@/utils/liveMapWeatherIcons';

/**
 * Options for overlay / temperature paint passes.
 *
 * @example
 * const _ = true;
 */
export type TacOverlayPaintOptions = {
  magnitudeScale?: number;
  tempUnit?: LiveMapTempUnit;
};

type OverlayPainter = (
  map: L.Map,
  cluster: StationCluster,
  at: L.LatLngExpression,
  options: TacOverlayPaintOptions,
) => L.Layer | null;

/**
 * DivIcon from HTML with a stable overlay class.
 *
 * @param html - Icon HTML
 * @param className - Extra class
 * @param size - Icon box
 * @returns Leaflet icon
 * @example
 * const _ = true;
 */
function divIcon(html: string, className: string, size: [number, number]): L.DivIcon {
  return L.divIcon({
    className: `live-map-tac-overlay ${className}`,
    html,
    iconSize: size,
    iconAnchor: [size[0] / 2, size[1] / 2],
  });
}

/**
 * Newest TAC on the first cluster member that feeds an overlay.
 *
 * @param cluster - Station cluster
 * @param id - Overlay id
 * @returns TAC text or empty
 * @example
 * const _ = true;
 */
function donorTac(cluster: StationCluster, id: TacOverlayLayerId): string {
  const member = cluster.members.find((place) => placeFeedsOverlay(place.reports, id));
  return member ? newestTac(member.reports) : '';
}

/**
 * Whether any cluster member feeds an overlay.
 *
 * @param cluster - Station cluster
 * @param id - Overlay id
 * @returns True when a marker should paint
 * @example
 * const _ = true;
 */
function clusterFeeds(cluster: StationCluster, id: TacOverlayLayerId): boolean {
  return cluster.members.some((place) => placeFeedsOverlay(place.reports, id));
}

/**
 * Non-interactive marker at a lat/lng.
 *
 * @param map - Leaflet map
 * @param at - Lat/lng
 * @param icon - DivIcon
 * @returns Layer
 * @example
 * const _ = true;
 */
function addIconMarker(map: L.Map, at: L.LatLngExpression, icon: L.DivIcon): L.Layer {
  return L.marker(at, {
    interactive: false,
    keyboard: false,
    icon,
  }).addTo(map);
}

const paintThunder: OverlayPainter = (map, cluster, at) => {
  if (!clusterFeeds(cluster, 'thunder')) {
    return null;
  }
  return addIconMarker(
    map,
    at,
    divIcon(weatherIconHtml(THUNDER_SVG), 'tac-overlay-icon-thunder', [24, 24]),
  );
};

const paintIce: OverlayPainter = (map, cluster, at) => {
  if (!clusterFeeds(cluster, 'ice')) {
    return null;
  }
  return addIconMarker(
    map,
    at,
    divIcon(weatherIconHtml(ICE_SVG), 'tac-overlay-icon-ice', [24, 24]),
  );
};

const paintPrecip: OverlayPainter = (map, cluster, at) => {
  if (!clusterFeeds(cluster, 'precip')) {
    return null;
  }
  return addIconMarker(
    map,
    at,
    divIcon(weatherIconHtml(PRECIP_SVG), 'tac-overlay-icon-precip', [24, 24]),
  );
};

const paintWindVector: OverlayPainter = (map, cluster, at, options) => {
  const parsed = parseTacOverlayFields(donorTac(cluster, 'windVector'));
  const degrees = parsed.wind?.directionDeg;
  if (
    !parsed.wind ||
    parsed.wind.variable ||
    degrees === null ||
    degrees === undefined
  ) {
    return null;
  }
  const { magnitudeScale = DEFAULT_OVERLAY_MAGNITUDE_SCALE } = options;
  const size = windVectorSizePx(parsed.wind.speedKt, magnitudeScale);
  return addIconMarker(
    map,
    at,
    divIcon(windVectorIconHtml(degrees, size), 'tac-overlay-icon-wind-vector', [
      size,
      size,
    ]),
  );
};

const paintWindIntensity: OverlayPainter = (map, cluster, at, options) => {
  const parsed = parseTacOverlayFields(donorTac(cluster, 'windIntensity'));
  if (!parsed.wind) {
    return null;
  }
  const { magnitudeScale = DEFAULT_OVERLAY_MAGNITUDE_SCALE } = options;
  return L.circleMarker(at, {
    radius: windIntensityRadius(parsed.wind.speedKt) * magnitudeScale,
    color: '#0f766e',
    fillColor: '#14b8a6',
    fillOpacity: 0.35,
    weight: 1,
    interactive: false,
    className: 'tac-overlay-icon-wind-intensity',
  }).addTo(map);
};

const OVERLAY_PAINTERS: ReadonlyArray<{
  id: TacOverlayLayerId;
  paint: OverlayPainter;
}> = [
  { id: 'thunder', paint: paintThunder },
  { id: 'ice', paint: paintIce },
  { id: 'precip', paint: paintPrecip },
  { id: 'windVector', paint: paintWindVector },
  { id: 'windIntensity', paint: paintWindIntensity },
];

/**
 * Paint enabled TAC overlays for one station cluster across world copies.
 *
 * @param map - Leaflet map
 * @param cluster - Same-station cluster
 * @param visibility - Overlay toggles
 * @param options - Magnitude scale for wind vectors / intensity
 * @returns Layers to remove on cleanup
 * @example
 * const _ = true;
 */
export function paintTacOverlays(
  map: L.Map,
  cluster: StationCluster,
  visibility: TacOverlayVisibility,
  options: TacOverlayPaintOptions = {},
): L.Layer[] {
  const layers: L.Layer[] = [];
  WORLD_COPY_LNG_OFFSETS.forEach((lngOffset) => {
    const at = shiftLatLng(cluster.latitude, cluster.longitude, lngOffset);
    OVERLAY_PAINTERS.forEach(({ id, paint }) => {
      if (!visibility[id]) {
        return;
      }
      const layer = paint(map, cluster, at, options);
      if (layer) {
        layers.push(layer);
      }
    });
  });
  return layers;
}

/**
 * Paint temperature badges for a station cluster (Temperatures mode).
 *
 * @param map - Leaflet map
 * @param cluster - Same-station cluster
 * @param unit - °C or °F
 * @returns Layers to remove on cleanup
 * @example
 * const _ = true;
 */
export function paintTemperatureMarkers(
  map: L.Map,
  cluster: StationCluster,
  unit: LiveMapTempUnit = 'C',
): L.Layer[] {
  const layers: L.Layer[] = [];
  let temperatureC: number | null = null;
  for (const place of cluster.members) {
    const parsed = parseTacOverlayFields(newestTac(place.reports));
    if (parsed.temperatureC !== null) {
      temperatureC = parsed.temperatureC;
      break;
    }
  }
  if (temperatureC === null) {
    return layers;
  }
  WORLD_COPY_LNG_OFFSETS.forEach((lngOffset) => {
    const at = shiftLatLng(cluster.latitude, cluster.longitude, lngOffset);
    layers.push(
      addIconMarker(
        map,
        at,
        divIcon(
          temperatureIconHtml(temperatureC, unit),
          'tac-overlay-icon-temp',
          [40, 18],
        ),
      ),
    );
  });
  return layers;
}
