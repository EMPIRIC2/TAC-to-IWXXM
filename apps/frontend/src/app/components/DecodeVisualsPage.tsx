/**
 * Decode visuals tab: station map and wind cue (F7 / F9).
 */

import { useState, useSyncExternalStore } from 'react';
import { StationMinimap } from '@/app/components/StationMinimap';
import { WindCue } from '@/app/components/WindCue';
import { stationDisplayName } from '@/utils/decodeVisuals';
import {
  DECODE_VISUALS_EMPTY,
  DECODE_VISUALS_INTRO,
  DECODE_VISUALS_STATION_LABEL,
  DECODE_VISUALS_TITLE,
} from '@/utils/decodeVisualsCopy';
import { readDecodeVisuals, subscribeDecodeVisuals } from '@/utils/decodeVisualsStore';

const STATION_ID = /^[A-Z][A-Z0-9]{3}$/;

/**
 * Map and wind cue for the station last seen on Convert, or one typed here.
 *
 * @example
 * const _ = true;
 */
export function DecodeVisualsPage() {
  const published = useSyncExternalStore(
    subscribeDecodeVisuals,
    readDecodeVisuals,
    readDecodeVisuals,
  );
  const [draft, setDraft] = useState<string | null>(null);
  const station = (draft ?? published.station).trim().toUpperCase();
  const complete = STATION_ID.test(station);
  const heading = complete ? stationDisplayName(station) : '';

  return (
    <section
      className="mx-auto max-w-3xl space-y-4 px-4 py-6"
      data-testid="decode-visuals-page"
    >
      <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
        {DECODE_VISUALS_TITLE}
      </h1>
      <p className="text-sm text-gray-600 dark:text-gray-300">{DECODE_VISUALS_INTRO}</p>
      <label className="block text-sm text-gray-800 dark:text-gray-100">
        {DECODE_VISUALS_STATION_LABEL}
        <input
          className="mt-1 w-full max-w-xs rounded border border-gray-300 bg-white px-2 py-1 font-mono text-sm dark:border-gray-600 dark:bg-gray-900"
          value={draft ?? published.station}
          onChange={(event) => setDraft(event.target.value.toUpperCase())}
          data-testid="decode-visuals-station"
          aria-label={DECODE_VISUALS_STATION_LABEL}
          autoComplete="off"
          spellCheck={false}
        />
      </label>
      {complete ? (
        <>
          <p
            className="text-sm font-medium text-gray-900 dark:text-white"
            data-testid="decode-visuals-heading"
          >
            {heading}
          </p>
          <StationMinimap icao={station} />
          <WindCue segments={draft === null ? published.segments : []} />
        </>
      ) : (
        <p
          className="text-sm text-gray-600 dark:text-gray-300"
          data-testid="decode-visuals-empty"
        >
          {DECODE_VISUALS_EMPTY}
        </p>
      )}
    </section>
  );
}
