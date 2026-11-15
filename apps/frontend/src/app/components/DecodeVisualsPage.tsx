/**
 * Full-page Live map: live TAC map and wind cue from Convert context (F37 / F9).
 */

import { useSyncExternalStore } from 'react';
import { LiveWorldMap } from '@/app/components/LiveWorldMap';
import { WindCue } from '@/app/components/WindCue';
import { stationDisplayName } from '@/utils/decodeVisuals';
import {
  DECODE_VISUALS_INTRO,
  DECODE_VISUALS_NO_STATION,
  DECODE_VISUALS_TITLE,
} from '@/utils/decodeVisualsCopy';
import { readDecodeVisuals, subscribeDecodeVisuals } from '@/utils/decodeVisualsStore';
import type { LivePlace } from '@/utils/liveMap';
import { shellFrameClass, useLiveConvertLayout } from '@/utils/liveConvertLayout';

const STATION_ID = /^[A-Z][A-Z0-9]{3}$/;

interface DecodeVisualsPageProps {
  /** Send a map report into Convert. */
  onOpenPlace?: (place: LivePlace) => void;
}

/**
 * Full-page live map with wind cue from the Convert / decode station.
 *
 * @param props.onOpenPlace - Optional Send-to-converter handoff
 * @example
 * const _ = true;
 */
export function DecodeVisualsPage({ onOpenPlace }: DecodeVisualsPageProps = {}) {
  const published = useSyncExternalStore(
    subscribeDecodeVisuals,
    readDecodeVisuals,
    readDecodeVisuals,
  );
  const { layout } = useLiveConvertLayout();
  const station = published.station.trim().toUpperCase();
  const complete = STATION_ID.test(station);
  const heading = complete ? stationDisplayName(station) : '';

  return (
    <section
      className={`mx-auto flex min-h-[calc(100dvh-4rem)] w-full flex-col gap-4 px-4 py-6 ${shellFrameClass(layout.span)}`}
      data-testid="decode-visuals-page"
    >
      <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
        {DECODE_VISUALS_TITLE}
      </h1>
      <p className="text-sm text-gray-600 dark:text-gray-300">{DECODE_VISUALS_INTRO}</p>
      {!complete ? (
        <p
          className="text-sm text-gray-600 dark:text-gray-300"
          data-testid="decode-visuals-empty"
        >
          {DECODE_VISUALS_NO_STATION}
        </p>
      ) : null}
      <LiveWorldMap focusStation={complete ? station : ''} onOpenPlace={onOpenPlace} />
      {complete ? (
        <>
          <p
            className="text-sm font-medium text-gray-900 dark:text-white"
            data-testid="decode-visuals-heading"
          >
            {heading}
          </p>
          <WindCue segments={published.segments} />
        </>
      ) : null}
    </section>
  );
}
