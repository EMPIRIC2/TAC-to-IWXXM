/**
 * Independent TAC overlay layer toggles for the live map.
 */

import {
  LIVE_MAP_TAC_OVERLAY_EMPTY,
  LIVE_MAP_TAC_OVERLAYS,
  TAC_OVERLAY_LAYERS,
  overlayMatchCount,
  type TacOverlayLayerId,
  type TacOverlayVisibility,
} from '@/utils/liveMapTacLayers';

/**
 * Checkbox row for precip / temp / wind / thunder / ice overlays.
 *
 * @param props.visibility - Current overlay on/off map
 * @param props.onToggle - Flip one overlay id
 * @param props.places - Visible places used for empty-state hint
 * @example
 * const _ = true;
 */
export function LiveMapTacOverlayToggles({
  visibility,
  onToggle,
  places,
}: {
  visibility: TacOverlayVisibility;
  onToggle: (id: TacOverlayLayerId) => void;
  places: ReadonlyArray<{ reports: ReadonlyArray<{ tac: string }> }>;
}) {
  const emptyHint = TAC_OVERLAY_LAYERS.find(
    (layer) => visibility[layer.id] && overlayMatchCount(places, layer.id) === 0,
  );

  return (
    <div
      className="mt-3 flex flex-col gap-2 border-t border-gray-100 pt-3 dark:border-gray-800"
      data-testid="live-map-tac-overlays"
    >
      <span className="text-[11px] font-semibold tracking-wide text-gray-400 uppercase">
        {LIVE_MAP_TAC_OVERLAYS}
      </span>
      <div className="flex flex-wrap items-center gap-2">
        {TAC_OVERLAY_LAYERS.map((layer) => {
          const on = visibility[layer.id];
          return (
            <label
              key={layer.id}
              className={`inline-flex cursor-pointer items-center rounded-full border px-3 py-1 text-sm font-medium transition ${
                on
                  ? 'border-sky-800 bg-sky-800 text-white dark:border-sky-200 dark:bg-sky-200 dark:text-sky-950'
                  : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300'
              }`}
            >
              <input
                type="checkbox"
                className="sr-only"
                checked={on}
                data-testid={`tac-overlay-${layer.id}`}
                onChange={() => {
                  onToggle(layer.id);
                }}
              />
              {layer.label}
            </label>
          );
        })}
      </div>
      {emptyHint ? (
        <p
          className="text-xs text-gray-500 dark:text-gray-400"
          data-testid="live-map-tac-overlay-empty"
        >
          {LIVE_MAP_TAC_OVERLAY_EMPTY}
        </p>
      ) : null}
    </div>
  );
}
