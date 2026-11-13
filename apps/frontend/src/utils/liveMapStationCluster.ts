/**
 * Same-station clustering for live map pins. [Corpus: product] F37
 */

import { formatObservedAt, productLabel, type LivePlace } from '@/utils/liveMap';
import { LIVE_MAP_CLUSTER_COUNT } from '@/utils/liveMapTacLayers';

/**
 * One originating station with every loaded point product at that key.
 * @example
 * const _ = true;
 */
export type StationCluster = {
  stationKey: string;
  latitude: number;
  longitude: number;
  members: LivePlace[];
};

/**
 * One selectable report row inside a same-station popup.
 * @example
 * const _ = true;
 */
export type ClusterReportChoice = {
  id: string;
  place: LivePlace;
  reportIndex: number;
  label: string;
};

/**
 * True when the place draws as a station point (not an area shape).
 *
 * @param place - Cached place
 * @returns Whether it belongs in a station cluster
 * @example
 * const _ = true;
 */
export function isStationPointPlace(place: LivePlace): boolean {
  const kind = place.geometry?.kind;
  return !kind || kind === 'point';
}

/**
 * Group point places that share an originating station into one cluster.
 *
 * Area shapes are omitted — callers still draw those separately.
 *
 * @param places - Visible places
 * @returns Clusters keyed by station
 * @example
 * const _ = true;
 */
export function clusterByStation(places: readonly LivePlace[]): StationCluster[] {
  const buckets = new Map<string, LivePlace[]>();
  for (const place of places) {
    if (!isStationPointPlace(place)) {
      continue;
    }
    const group = buckets.get(place.place_key) ?? [];
    group.push(place);
    buckets.set(place.place_key, group);
  }
  return [...buckets.entries()].map(([stationKey, members]) => {
    const anchor = members[0] as LivePlace;
    return {
      stationKey,
      latitude: anchor.latitude,
      longitude: anchor.longitude,
      members,
    };
  });
}

/**
 * Flatten every report in a cluster into picker rows (newest first per place).
 *
 * @param cluster - Station cluster
 * @returns Ordered choices
 * @example
 * const _ = true;
 */
export function clusterReportChoices(cluster: StationCluster): ClusterReportChoice[] {
  const rows: ClusterReportChoice[] = [];
  for (const place of cluster.members) {
    place.reports.forEach((report, reportIndex) => {
      rows.push({
        id: `${place.place_key}-${place.product}-${report.observed_at}-${reportIndex}`,
        place,
        reportIndex,
        label: `${productLabel(place.product)} · ${formatObservedAt(report.observed_at)}`,
      });
    });
  }
  return rows;
}

/**
 * Accessible summary for a multi-report cluster marker.
 *
 * @param cluster - Station cluster
 * @returns Aria label
 * @example
 * const _ = true;
 */
export function clusterAriaLabel(cluster: StationCluster): string {
  const count = clusterReportChoices(cluster).length;
  if (count <= 1) {
    return cluster.stationKey;
  }
  return `${cluster.stationKey}, ${count} ${LIVE_MAP_CLUSTER_COUNT}`;
}

/**
 * Narrow a place to the single report the operator picked.
 *
 * @param place - Source place
 * @param reportIndex - Report index
 * @returns Place with one report, or null when missing
 * @example
 * const _ = true;
 */
export function placeWithReportIndex(
  place: LivePlace,
  reportIndex: number,
): LivePlace | null {
  const report = place.reports[reportIndex];
  if (!report) {
    return null;
  }
  return { ...place, reports: [report] };
}
