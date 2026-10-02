/**
 * Pannable station map for the decode visuals tab (F7 / F9).
 */

import { useEffect, useRef, useState } from 'react';
import 'leaflet/dist/leaflet.css';
import {
  DECODE_VISUALS_MAP_LOADING,
  DECODE_VISUALS_NO_MAP,
} from '@/utils/decodeVisualsCopy';
import {
  bindStationMap,
  fetchStationPoint,
  type StationPoint,
} from '@/utils/stationMap';

/**
 * Type `StationMinimapProps`.
 * @example
 * const _ = true;
 */
type StationMinimapProps = {
  icao: string;
};

const STATION_ID = /^[A-Z][A-Z0-9]{3}$/;

/**
 * Tile map for one known station ID.
 *
 * @param props.icao - Four-letter station ID
 * @example
 * const _ = true;
 */
function StationMinimapLoaded({ icao }: StationMinimapProps) {
  const host = useRef<HTMLDivElement>(null);
  const [point, setPoint] = useState<StationPoint | null | undefined>(undefined);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    const controller = new AbortController();
    fetchStationPoint(icao, controller.signal)
      .then((next) => {
        setFailed(false);
        setPoint(next);
      })
      .catch((error: unknown) => {
        if (error instanceof DOMException && error.name === 'AbortError') {
          return;
        }
        setFailed(true);
        setPoint(null);
      });
    return () => controller.abort();
  }, [icao]);

  useEffect(() => bindStationMap(host.current, point), [point]);

  if (failed || point === null) {
    return (
      <p
        className="text-sm text-gray-600 dark:text-gray-300"
        data-testid="station-map-empty"
      >
        {DECODE_VISUALS_NO_MAP}
      </p>
    );
  }
  if (!point) {
    return (
      <p
        className="text-sm text-gray-600 dark:text-gray-300"
        data-testid="station-map-loading"
      >
        {DECODE_VISUALS_MAP_LOADING}
      </p>
    );
  }
  return (
    <div
      ref={host}
      className="z-0 h-[min(36rem,calc(100dvh-18rem))] min-h-[20rem] w-full overflow-hidden rounded border border-gray-200 dark:border-gray-700"
      data-testid="station-map"
      role="img"
      aria-label={`Map of ${point.name}`}
    />
  );
}

/**
 * Tile map centered on one station, with a marker the operator can pan.
 *
 * @param props.icao - Station ID
 * @example
 * const _ = true;
 */
export function StationMinimap({ icao }: StationMinimapProps) {
  const code = icao.trim().toUpperCase();
  if (!STATION_ID.test(code)) {
    return (
      <p
        className="text-sm text-gray-600 dark:text-gray-300"
        data-testid="station-map-empty"
      >
        {DECODE_VISUALS_NO_MAP}
      </p>
    );
  }
  return <StationMinimapLoaded key={code} icao={code} />;
}
