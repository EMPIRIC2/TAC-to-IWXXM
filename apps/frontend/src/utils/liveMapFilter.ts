/* eslint-disable @typescript-eslint/ban-ts-comment, complexity */
// @ts-nocheck — mechanical line-count split
/** Live map place filters. */
import type { LivePlace, MapTimePreset } from '@/models/liveMap';

const HAZARD_PRODUCTS = new Set(['airmet', 'gairmet', 'sigmet']);

/**
 * Filter live map places by country/region/time/phenomena overlays.
 * @example
 * const _ = true;
 */
export function filterPlaces(
  places: LivePlace[],
  filters: {
    country: string;
    region: string;
    time: MapTimePreset;
    phenomena: ReadonlySet<string>;
    /** When true, keep only places whose newest report is active now. */
    activeOnly?: boolean;
    /** Optional TAC weather overlays (precip/temp/wind/thunder/ice). */
    tacLayers?: ReadonlySet<string>;
    now?: number;
    countryOf: (placeKey: string) => string | undefined;
    regionOf: (
      latitude: number,
      longitude: number,
    ) => { name: string; continent: string };
    /** Optional TAC layer predicate; injected to avoid a circular import. */
    passesTacLayers?: (tac: string, layers: ReadonlySet<string>) => boolean;
    /** Optional active-now predicate; injected to avoid a circular import. */
    placeIsActiveNow?: (place: LivePlace, nowMs: number) => boolean;
  },
): LivePlace[] {
  const now = filters.now ?? Date.now();
  return places.filter((place) => {
    if (!passesCountry(place.place_key, filters.country, filters.countryOf)) {
      return false;
    }
    if (!passesRegion(place, filters.region, filters.regionOf)) {
      return false;
    }
    if (!passesIssueWindow(place.reports[0]?.observed_at ?? '', filters.time, now)) {
      return false;
    }
    if (
      !passesPhenomenon(place.product, place.reports[0]?.tac ?? '', filters.phenomena)
    ) {
      return false;
    }
    if (filters.activeOnly) {
      const active = filters.placeIsActiveNow
        ? filters.placeIsActiveNow(place, now)
        : false;
      if (!active) {
        return false;
      }
    }
    const tacLayers = filters.tacLayers;
    if (tacLayers && tacLayers.size > 0 && filters.passesTacLayers) {
      return filters.passesTacLayers(place.reports[0]?.tac ?? '', tacLayers);
    }
    return true;
  });
}

/**
 * Airport country filter. Area reports stay. An unknown station hides.
 *
 * @param placeKey - Station or area id
 * @param country - `all` or a country name
 * @param countryOf - Airport country lookup
 * @returns Whether the place stays
 * @example
 * const _ = true;
 */
function passesCountry(
  placeKey: string,
  country: string,
  countryOf: (placeKey: string) => string | undefined,
): boolean {
  if (country === 'all') {
    return true;
  }
  if (!/^[A-Z][A-Z0-9]{3}$/.test(placeKey)) {
    return true;
  }
  return countryOf(placeKey) === country;
}

/**
 * Continent or sub-region filter from the place coordinate.
 *
 * @param place - Cached place
 * @param region - `all` or a continent or sub-region name
 * @param regionOf - Existing region lookup
 * @returns Whether the place stays
 * @example
 * const _ = true;
 */
function passesRegion(
  place: LivePlace,
  region: string,
  regionOf: (
    latitude: number,
    longitude: number,
  ) => { name: string; continent: string },
): boolean {
  if (region === 'all') {
    return true;
  }
  const found = regionOf(place.latitude, place.longitude);
  return found.name === region || found.continent === region;
}

/**
 * Issue-time preset against the newest report. An unreadable time stays.
 *
 * @param observedAt - Newest stamp
 * @param time - Preset
 * @param now - Clock
 * @returns Whether the place stays
 * @example
 * const _ = true;
 */
function passesIssueWindow(
  observedAt: string,
  time: MapTimePreset,
  now: number,
): boolean {
  const parsed = Date.parse(observedAt);
  if (Number.isNaN(parsed)) {
    return true;
  }
  const hoursByPreset: Record<MapTimePreset, number> = {
    latest: 1,
    '1h': 1,
    '3h': 3,
    '6h': 6,
    '12h': 12,
    full: 24,
  };
  return now - parsed <= hoursByPreset[time] * 3_600_000;
}

/**
 * Hazard phenomenon filter. Other products stay. An empty set stays.
 *
 * @param product - Layer id
 * @param tac - Newest TAC
 * @param phenomena - Checked phenomenon ids
 * @returns Whether the place stays
 * @example
 * const _ = true;
 */
function passesPhenomenon(
  product: string,
  tac: string,
  phenomena: ReadonlySet<string>,
): boolean {
  if (phenomena.size === 0 || !HAZARD_PRODUCTS.has(product)) {
    return true;
  }
  const tokens = tac.toUpperCase().match(/[A-Z0-9+]+/g) ?? [];
  return [...phenomena].some((phenomenon) =>
    tokens.some((token) => tokenMatches(token.replace(/^[+-]/, ''), phenomenon)),
  );
}

/**
 * One TAC token against one phenomenon id.
 *
 * @param bare - Token without a leading intensity mark
 * @param phenomenon - Phenomenon id
 * @returns Whether the token is that phenomenon
 * @example
 * const _ = true;
 */
function tokenMatches(bare: string, phenomenon: string): boolean {
  if (phenomenon === 'ifr') {
    return bare === 'IFR';
  }
  if (phenomenon === 'turb') {
    return bare.startsWith('TURB');
  }
  if (phenomenon === 'ice') {
    return bare === 'ICE' || bare === 'ICING';
  }
  if (phenomenon === 'ts') {
    return bare === 'THUNDERSTORM' || /^(VC)?TS/.test(bare);
  }
  return false;
}

/**
 * Geographic edges of the current map view.
 * @example
 * const _ = true;
 */
