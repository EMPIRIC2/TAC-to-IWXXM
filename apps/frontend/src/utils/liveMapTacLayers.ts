/**
 * Toggleable TAC overlay layer state for the live map. [Corpus: product] F37
 */

import {
  newestTac,
  parseTacOverlayFields,
  type TacOverlayParse,
} from '@/utils/liveMapTacParse';

export const LIVE_MAP_TAC_OVERLAYS = 'TAC overlays';
export const LIVE_MAP_TAC_OVERLAY_EMPTY =
  'No matching weather in the loaded reports for this overlay.';
export const LIVE_MAP_CLUSTER_PICK = 'Report at this station';
export const LIVE_MAP_CLUSTER_COUNT = 'reports at this station';

export const TAC_OVERLAY_LAYERS = [
  { id: 'precip', label: 'Precipitation' },
  { id: 'temp', label: 'Temperature' },
  { id: 'windVector', label: 'Wind vectors' },
  { id: 'windIntensity', label: 'Wind intensity' },
  { id: 'thunder', label: 'Thunderstorms' },
  { id: 'ice', label: 'Ice' },
] as const;

export type TacOverlayLayerId = (typeof TAC_OVERLAY_LAYERS)[number]['id'];

export type TacOverlayVisibility = Record<TacOverlayLayerId, boolean>;

/**
 * All TAC overlays start off so product layers stay the calm default.
 *
 * @returns Visibility map
 * @example
 * defaultTacOverlayVisibility();
 */
export function defaultTacOverlayVisibility(): TacOverlayVisibility {
  return {
    precip: false,
    temp: false,
    windVector: false,
    windIntensity: false,
    thunder: false,
    ice: false,
  };
}

/**
 * Flip one overlay without touching the others.
 *
 * @param current - Current visibility
 * @param id - Overlay id
 * @returns Next visibility
 * @example
 * toggleTacOverlay(defaultTacOverlayVisibility(), 'thunder');
 */
export function toggleTacOverlay(
  current: TacOverlayVisibility,
  id: TacOverlayLayerId,
): TacOverlayVisibility {
  return { ...current, [id]: !current[id] };
}

/**
 * Whether a parsed TAC contributes to one overlay.
 *
 * @param parsed - Parsed overlay fields
 * @param id - Overlay id
 * @returns True when a marker should paint
 * @example
 * overlayApplies(parseTacOverlayFields('TSRA'), 'thunder');
 */
export function overlayApplies(
  parsed: TacOverlayParse,
  id: TacOverlayLayerId,
): boolean {
  if (id === 'precip') {
    return parsed.precipCodes.length > 0;
  }
  if (id === 'temp') {
    return parsed.temperatureC !== null;
  }
  if (id === 'windVector') {
    return parsed.wind !== null && !parsed.wind.variable && parsed.wind.directionDeg !== null;
  }
  if (id === 'windIntensity') {
    return parsed.wind !== null;
  }
  if (id === 'thunder') {
    return parsed.hasThunder;
  }
  return parsed.hasIce;
}

/**
 * Whether a place's newest TAC feeds an overlay.
 *
 * @param reports - Place reports
 * @param id - Overlay id
 * @returns True when the overlay should mark this station
 * @example
 * placeFeedsOverlay([{ tac: 'TSRA', observed_at: 'x' }], 'thunder');
 */
export function placeFeedsOverlay(
  reports: ReadonlyArray<{ tac: string }>,
  id: TacOverlayLayerId,
): boolean {
  return overlayApplies(parseTacOverlayFields(newestTac(reports)), id);
}

/**
 * Count places that would paint for one overlay.
 *
 * @param places - Visible places
 * @param id - Overlay id
 * @returns Matching place count
 * @example
 * overlayMatchCount([], 'ice');
 */
export function overlayMatchCount(
  places: ReadonlyArray<{ reports: ReadonlyArray<{ tac: string }> }>,
  id: TacOverlayLayerId,
): number {
  return places.filter((place) => placeFeedsOverlay(place.reports, id)).length;
}

/**
 * Wind intensity band for marker sizing (calm → gale).
 *
 * @param speedKt - Knots
 * @returns Band id
 * @example
 * windIntensityBand(25);
 */
export function windIntensityBand(
  speedKt: number,
): 'calm' | 'light' | 'moderate' | 'strong' | 'gale' {
  if (speedKt < 5) {
    return 'calm';
  }
  if (speedKt < 15) {
    return 'light';
  }
  if (speedKt < 25) {
    return 'moderate';
  }
  if (speedKt < 35) {
    return 'strong';
  }
  return 'gale';
}

/**
 * Pixel radius for a wind-intensity disc.
 *
 * @param speedKt - Knots
 * @returns Leaflet circleMarker radius
 * @example
 * windIntensityRadius(12);
 */
export function windIntensityRadius(speedKt: number): number {
  const band = windIntensityBand(speedKt);
  if (band === 'calm') {
    return 4;
  }
  if (band === 'light') {
    return 6;
  }
  if (band === 'moderate') {
    return 8;
  }
  if (band === 'strong') {
    return 10;
  }
  return 12;
}
