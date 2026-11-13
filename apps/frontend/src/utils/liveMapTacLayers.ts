/**
 * TAC overlay layers for the live map (F37 deepen).
 *
 * precip / temp / wind / thunder / ice filters read the newest TAC at a place.
 * Station clusters collect matching reports for a file-style picker.
 */

/** TAC overlay ids operators can toggle on the map. */
export const LIVE_MAP_TAC_LAYERS = [
  { id: 'precip', label: 'Precipitation' },
  { id: 'temp', label: 'Temperature' },
  { id: 'wind', label: 'Wind' },
  { id: 'thunder', label: 'Thunder' },
  { id: 'ice', label: 'Ice' },
] as const;

/**
 * Id of one TAC overlay layer operators can toggle.
 * @example
 * const _ = true;
 */
export type LiveMapTacLayerId = (typeof LIVE_MAP_TAC_LAYERS)[number]['id'];

export const LIVE_MAP_TAC_LAYER_LABEL = 'TAC layers';
export const LIVE_MAP_STATION_CLUSTER_PICKER = 'Station files';
export const LIVE_MAP_STATION_CLUSTER_EMPTY = 'No reports in this cluster.';
export const LIVE_MAP_STATION_CLUSTER_HINT =
  'Choose a report to send to the converter.';

/**
 * One row in the station-cluster file picker.
 * @example
 * const _ = true;
 */
export type StationClusterPick = {
  icao: string;
  product: string;
  tac: string;
  observedAt: string;
};

/**
 * Weather / precip tokens (Code table 4678 style).
 *
 * @param bare - TAC token without intensity mark
 */
function isPrecip(bare: string): boolean {
  return /^(VC)?(SH|TS)?(DZ|RA|SN|SG|IC|PL|GR|GS|UP)+$/.test(bare) || bare === 'FZRA';
}

/**
 * Temperature / dewpoint group (including M for below zero).
 *
 * @param bare - TAC token
 */
function isTemp(bare: string): boolean {
  return /^M?\d{2}\/M?\d{2}$/.test(bare);
}

/**
 * Surface wind group (incl. VRB / gusts).
 *
 * @param bare - TAC token
 */
function isWind(bare: string): boolean {
  return /^(VRB|\d{3})\d{2}(G\d{2})?(KT|MPS|KMH)$/.test(bare);
}

/**
 * Thunderstorm tokens.
 *
 * @param bare - TAC token without intensity mark
 */
function isThunder(bare: string): boolean {
  return bare === 'THUNDERSTORM' || /^(VC)?TS/.test(bare);
}

/**
 * Icing tokens (hazard + METAR ice crystals).
 *
 * @param bare - TAC token without intensity mark
 */
function isIce(bare: string): boolean {
  return bare === 'ICE' || bare === 'ICING' || bare === 'IC' || bare === 'FZRA';
}

/**
 * Whether a TAC report matches one overlay id.
 *
 * @param tac - Newest TAC text
 * @param layer - Overlay id
 * @example
 * const _ = true;
 */
export function tacMatchesLayer(tac: string, layer: LiveMapTacLayerId): boolean {
  const tokens = tac.toUpperCase().match(/[A-Z0-9+/]+/g) ?? [];
  return tokens.some((token) => {
    const bare = token.replace(/^[+-]/, '');
    if (layer === 'precip') {
      return isPrecip(bare);
    }
    if (layer === 'temp') {
      return isTemp(bare);
    }
    if (layer === 'wind') {
      return isWind(bare);
    }
    if (layer === 'thunder') {
      return isThunder(bare);
    }
    if (layer === 'ice') {
      return isIce(bare);
    }
    return false;
  });
}

/**
 * Keep a place when its TAC hits at least one selected overlay.
 *
 * An empty set keeps every place (caller skips the filter).
 *
 * @param tac - Newest TAC
 * @param layers - Checked overlay ids
 * @example
 * const _ = true;
 */
export function passesTacLayers(tac: string, layers: ReadonlySet<string>): boolean {
  if (layers.size === 0) {
    return true;
  }
  return [...layers].some((layer) => tacMatchesLayer(tac, layer as LiveMapTacLayerId));
}

/**
 * Map one live place into a station-cluster picker row.
 *
 * Missing reports fall back to empty TAC / time strings.
 *
 * @param place - Live map place
 * @returns Picker row for the newest report
 * @example
 * const _ = true;
 */
export function placeToClusterPick(place: {
  place_key: string;
  product: string;
  reports: ReadonlyArray<{ tac?: string | null; observed_at?: string | null }>;
}): StationClusterPick {
  const report = place.reports[0];
  return {
    icao: place.place_key,
    product: place.product,
    tac: report?.tac ?? '',
    observedAt: report?.observed_at ?? '',
  };
}

/**
 * Build file-picker rows from places that already passed TAC overlays.
 *
 * @param rows - ICAO / product / TAC / time tuples
 * @returns Picker rows (blank TAC skipped)
 * @example
 * const _ = true;
 */
export function stationClusterFilePicker(
  rows: readonly {
    icao: string;
    product: string;
    tac: string;
    observedAt: string;
  }[],
): StationClusterPick[] {
  return rows
    .filter((row) => row.tac.trim().length > 0)
    .map((row) => ({
      icao: row.icao,
      product: row.product,
      tac: row.tac.trim(),
      observedAt: row.observedAt,
    }));
}

/**
 * Whether co-located places should open the cluster picker.
 *
 * @param count - Places sharing one grid cell
 * @param reportCount - Reports on the first place
 * @example
 * const _ = true;
 */
export function isMultiStationCluster(count: number, reportCount: number): boolean {
  return count > 1 || reportCount > 1;
}
