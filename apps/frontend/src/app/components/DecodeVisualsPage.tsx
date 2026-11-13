/**
 * Full-page Live map: live TAC map, station search, and wind cue (F37 / F9).
 */

import { useSyncExternalStore } from 'react';
import { IcaoAutocomplete } from '@/app/components/IcaoAutocomplete';
import { LiveWorldMap } from '@/app/components/LiveWorldMap';
import { WindCue } from '@/app/components/WindCue';
import { stationDisplayName } from '@/utils/decodeVisuals';
import {
  DECODE_VISUALS_EMPTY,
  DECODE_VISUALS_INTRO,
  DECODE_VISUALS_SEARCH_PLACEHOLDER,
  DECODE_VISUALS_STATION_LABEL,
  DECODE_VISUALS_TITLE,
} from '@/utils/decodeVisualsCopy';
import {
  readDecodeVisuals,
  readStationDraft,
  subscribeDecodeVisuals,
  subscribeStationDraft,
  writeStationDraft,
} from '@/utils/decodeVisualsStore';
import type { LivePlace } from '@/utils/liveMap';
import { shellFrameClass, useLiveConvertLayout } from '@/utils/liveConvertLayout';

const STATION_ID = /^[A-Z][A-Z0-9]{3}$/;

interface DecodeVisualsPageProps {
  /** Send a map report into Convert (parity with Results → Map). */
  onOpenPlace?: (place: LivePlace) => void;
}

/**
 * Full-page live map with station search and wind cue.
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
  const draft = useSyncExternalStore(
    subscribeStationDraft,
    readStationDraft,
    readStationDraft,
  );
  const { layout } = useLiveConvertLayout();
  const station = (draft ?? published.station).trim().toUpperCase();
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
      <IcaoAutocomplete
        id="decode-visuals-station-input"
        label={DECODE_VISUALS_STATION_LABEL}
        value={draft ?? published.station}
        onChange={(value) => writeStationDraft(value.toUpperCase())}
        inputTestId="decode-visuals-station"
        placeholder={DECODE_VISUALS_SEARCH_PLACEHOLDER}
        className="max-w-xl"
      />
      <p
        className="text-sm text-gray-600 dark:text-gray-300"
        data-testid="decode-visuals-empty"
      >
        {DECODE_VISUALS_EMPTY}
      </p>
      <LiveWorldMap focusStation={complete ? station : ''} onOpenPlace={onOpenPlace} />
      {complete ? (
        <>
          <p
            className="text-sm font-medium text-gray-900 dark:text-white"
            data-testid="decode-visuals-heading"
          >
            {heading}
          </p>
          <WindCue segments={draft === null ? published.segments : []} />
        </>
      ) : null}
    </section>
  );
}
