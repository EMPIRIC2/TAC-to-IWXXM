/**
 * Cluster → report picker for same-station live map pins.
 */

import { useMemo, useState } from 'react';
import type { LivePlace } from '@/utils/liveMap';
import {
  clusterReportChoices,
  placeWithReportIndex,
  type StationCluster,
} from '@/utils/liveMapStationCluster';
import { LIVE_MAP_CLUSTER_PICK } from '@/utils/liveMapTacLayers';
import { StationPopup } from './StationPopup';

/**
 * Let the operator pick a report when several share one station point.
 *
 * @param props.cluster - Same-station members
 * @param props.layout - Card layout
 * @param props.onShowing - Remembers the TAC on the card
 * @param props.onLoad - Loads TAC into the converter
 * @example
 * <StationClusterPopup cluster={cluster} />
 */
export function StationClusterPopup({
  cluster,
  layout = 'side',
  onShowing,
  onLoad,
}: {
  cluster: StationCluster;
  layout?: 'side' | 'stack';
  onShowing?: (tac: string) => void;
  onLoad?: (tac: string) => void;
}) {
  const choices = useMemo(() => clusterReportChoices(cluster), [cluster]);
  const [selectedId, setSelectedId] = useState(choices[0]?.id ?? '');
  const choice = choices.find((row) => row.id === selectedId) ?? choices[0];
  if (!choice) {
    return (
      <p className="text-sm text-gray-600" data-testid="live-map-cluster-empty">
        No reports at this station.
      </p>
    );
  }
  const narrowed = placeWithReportIndex(choice.place, choice.reportIndex);
  if (!narrowed) {
    return (
      <p className="text-sm text-gray-600" data-testid="live-map-cluster-empty">
        No reports at this station.
      </p>
    );
  }
  return (
    <div className="flex flex-col gap-2" data-testid="live-map-cluster">
      {choices.length > 1 ? (
        <label className="flex flex-col gap-1 text-[11px] font-semibold tracking-wide text-gray-500 uppercase">
          {LIVE_MAP_CLUSTER_PICK}
          <select
            className="h-8 max-w-full rounded-md border border-gray-200 bg-white px-1.5 text-xs font-medium normal-case text-gray-900"
            data-testid="live-map-cluster-pick"
            aria-label={LIVE_MAP_CLUSTER_PICK}
            value={choice.id}
            onClick={(event) => {
              event.stopPropagation();
            }}
            onChange={(event) => {
              event.stopPropagation();
              setSelectedId(event.target.value);
            }}
          >
            {choices.map((row) => (
              <option key={row.id} value={row.id}>
                {row.label}
              </option>
            ))}
          </select>
        </label>
      ) : null}
      <StationPopup
        place={narrowed as LivePlace}
        layout={layout}
        onShowing={onShowing}
        onLoad={onLoad}
      />
    </div>
  );
}
