/**
 * Labeled ICAO-region sketch for a station (F7 / F9).
 */

import {
  regionBoxes,
  regionForStation,
  stationDisplayName,
} from '@/utils/decodeVisuals';
import {
  DECODE_VISUALS_NO_REGION,
  DECODE_VISUALS_REGION_CAPTION,
} from '@/utils/decodeVisualsCopy';

/**
 * Type `RegionSchematicProps`.
 * @example
 * const _ = true;
 */
type RegionSchematicProps = {
  icao: string;
  /** When true, the visible caption includes the airport name or code. */
  showStationName?: boolean;
};

/**
 * Region sketch with a text equivalent. Missing prefixes stay an empty sentence.
 *
 * @param props.icao - Station code
 * @param props.showStationName - Include the station heading in the caption
 * @example
 * const _ = true;
 */
export function RegionSchematic({
  icao,
  showStationName = false,
}: RegionSchematicProps) {
  const region = regionForStation(icao);
  const station = showStationName ? stationDisplayName(icao) : '';
  const caption = region
    ? station
      ? `${DECODE_VISUALS_REGION_CAPTION}: ${region.label}. Station ${station}.`
      : `${DECODE_VISUALS_REGION_CAPTION}: ${region.label}.`
    : DECODE_VISUALS_NO_REGION;

  return (
    <figure className="space-y-2" data-testid="region-schematic">
      {region ? (
        <svg
          viewBox="0 0 320 160"
          role="img"
          aria-label={caption}
          className="h-40 w-full max-w-md rounded border border-gray-200 bg-slate-50 dark:border-gray-700 dark:bg-slate-900"
          data-testid="region-schematic-svg"
        >
          {regionBoxes().map((box) => {
            const active = box.prefix === region.prefix;
            return (
              <g key={box.prefix}>
                <rect
                  x={box.x}
                  y={box.y}
                  width={box.w}
                  height={box.h}
                  rx={4}
                  fill={active ? '#0369a1' : '#e2e8f0'}
                  stroke={active ? '#0c4a6e' : '#94a3b8'}
                />
                <text
                  x={box.x + 4}
                  y={box.y + 16}
                  fontSize={9}
                  fill={active ? '#f8fafc' : '#334155'}
                >
                  {box.label}
                </text>
              </g>
            );
          })}
        </svg>
      ) : null}
      <figcaption
        className="text-sm text-gray-700 dark:text-gray-200"
        data-testid="region-schematic-text"
      >
        {caption}
      </figcaption>
    </figure>
  );
}
