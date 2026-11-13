/**
 * Compact station report card for the live map popup.
 */

import { useEffect, useState } from 'react';
import { airports } from '@/utils/airportsData';
import {
  formatObservedAt,
  LIVE_MAP_ISSUE_COPY,
  LIVE_MAP_SEND_TO_CONVERTER,
  LIVE_MAP_TAC,
  pinColor,
  placeTitle,
  productLabel,
  type LivePlace,
} from '@/utils/liveMap';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from './ui/collapsible';

/**
 * Compact station id for the map card header (ICAO key when present).
 *
 * @param placeKey - Station or area id
 * @param airportName - Optional airport display name
 * @returns Short station label for the dense card
 * @example
 * stationCardLabel('KJFK', 'Kennedy');
 */
function stationCardLabel(placeKey: string, airportName: string | undefined): string {
  if (/^[A-Z][A-Z0-9]{3}$/.test(placeKey)) {
    return placeKey;
  }
  return placeTitle(placeKey, airportName);
}

/**
 * Station text inside the map card.
 *
 * Compact header (product + station + issue-time select), TAC collapsed by
 * default, and Send to converter via the existing onLoad handoff.
 *
 * @param place - Cached place
 * @param layout - Side by side on a wide map, stacked on a narrow one
 * @param onShowing - Remembers the copy on the card
 * @param onLoad - Loads that copy into the converter
 * @example
 * <StationPopup place={place} />
 */
export function StationPopup({
  place,
  layout = 'side',
  onShowing,
  onLoad,
}: {
  place: LivePlace;
  layout?: 'side' | 'stack';
  onShowing?: (tac: string) => void;
  onLoad?: (tac: string) => void;
}) {
  const [index, setIndex] = useState(0);
  const [tacOpen, setTacOpen] = useState(false);
  const report = place.reports[index];
  useEffect(() => {
    if (report) {
      onShowing?.(report.tac);
    }
  }, [onShowing, report]);
  if (!report) {
    return null;
  }
  const airportName = airports.findWhere({ icao: place.place_key })?.name;
  const station = stationCardLabel(place.place_key, airportName);
  return (
    <div
      data-testid="live-map-detail"
      className="max-h-48 overflow-y-auto text-sm text-gray-900"
    >
      <div
        data-testid="live-map-card"
        data-layout={layout}
        className="flex flex-col gap-2"
      >
        <div className="flex min-w-0 flex-wrap items-center gap-x-2 gap-y-1">
          <p className="text-sm font-semibold" data-testid="live-map-product">
            <span
              aria-hidden="true"
              className="mr-1.5 inline-block h-2.5 w-2.5 rounded-full align-middle"
              style={{ backgroundColor: pinColor(place.product) }}
            />
            {productLabel(place.product)}
          </p>
          <p className="font-medium" data-testid="live-map-station">
            {station}
          </p>
          {place.reports.length > 1 ? (
            <select
              className="h-7 min-w-[9rem] max-w-full rounded-md border border-gray-200 bg-white px-1.5 text-xs text-gray-900"
              data-testid="live-map-issue-time"
              aria-label={LIVE_MAP_ISSUE_COPY}
              value={String(index)}
              onClick={(event) => {
                event.stopPropagation();
              }}
              onChange={(event) => {
                event.stopPropagation();
                setIndex(Number(event.target.value));
              }}
            >
              {place.reports.map((copy, copyIndex) => (
                <option
                  key={`${copy.observed_at}-${copyIndex}`}
                  value={String(copyIndex)}
                >
                  {formatObservedAt(copy.observed_at)}
                </option>
              ))}
            </select>
          ) : (
            <p className="text-xs text-gray-600" data-testid="live-map-issued">
              {formatObservedAt(report.observed_at)}
            </p>
          )}
        </div>
        <Collapsible
          className="min-w-0"
          data-testid="live-map-tac-section"
          open={tacOpen}
          onOpenChange={setTacOpen}
        >
          <CollapsibleTrigger
            className="cursor-pointer text-xs font-medium text-gray-800"
            data-testid="live-map-tac-toggle"
          >
            {LIVE_MAP_TAC}
          </CollapsibleTrigger>
          <CollapsibleContent>
            <pre
              className="mt-1 max-h-28 overflow-y-auto rounded-md bg-gray-50 p-2 whitespace-pre-wrap font-mono text-xs text-gray-800"
              data-testid="live-map-tac"
            >
              {report.tac}
            </pre>
          </CollapsibleContent>
        </Collapsible>
        <button
          type="button"
          className="self-start rounded-md bg-gray-900 px-2.5 py-1 text-xs font-medium text-white hover:bg-gray-800"
          data-testid="live-map-send-to-converter"
          onClick={(event) => {
            event.stopPropagation();
            onLoad?.(report.tac);
          }}
        >
          {LIVE_MAP_SEND_TO_CONVERTER}
        </button>
      </div>
    </div>
  );
}
