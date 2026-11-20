/**
 * Catalog of operator-visible string exports for guard scans.
 */
import type { OperatorVisibleCopyEntry } from '@/models/operatorCopy';
import { DECODE_VISUALS_NO_STATION } from '@/utils/decodeVisualsCopy';
import {
  LIVE_MAP_DISPLAY_MODES,
  LIVE_MAP_MODE_GROUP,
  LIVE_MAP_OVERLAY_SCALE,
  LIVE_MAP_SHOW_LATEST,
  LIVE_MAP_TEMP_C,
  LIVE_MAP_TEMP_F,
  LIVE_MAP_TEMP_UNIT,
} from '@/utils/liveMapModes';
import { LIVE_MAP_ACTIVE_EMPTY, LIVE_MAP_FILTER_ACTIVE } from '@/utils/liveMapValidity';
import * as C from './operatorVisibleCopyConsts';
import { OPERATOR_VISIBLE_COPY_PART1 } from './operatorVisibleCopy.part1';
import { OPERATOR_VISIBLE_COPY_PART2 } from './operatorVisibleCopy.part2';
import { OPERATOR_VISIBLE_COPY_PART3 } from './operatorVisibleCopy.part3';

export type { OperatorVisibleCopyEntry } from '@/models/operatorCopy';

/**
 * Collect operator-visible copy entries for guard scans.
 * @example
 * const _ = true;
 */
export function collectOperatorVisibleCopy(): OperatorVisibleCopyEntry[] {
  const entries: OperatorVisibleCopyEntry[] = [
    ...OPERATOR_VISIBLE_COPY_PART1,
    ...OPERATOR_VISIBLE_COPY_PART2,
    ...OPERATOR_VISIBLE_COPY_PART3,
    { id: 'decode-visuals.no-station', text: DECODE_VISUALS_NO_STATION },
    { id: 'live-map.filter-active', text: LIVE_MAP_FILTER_ACTIVE },
    { id: 'live-map.active-empty', text: LIVE_MAP_ACTIVE_EMPTY },
    { id: 'live-map.mode-group', text: LIVE_MAP_MODE_GROUP },
    ...LIVE_MAP_DISPLAY_MODES.map((mode) => ({
      id: `live-map.mode.${mode.id}`,
      text: mode.label,
    })),
    { id: 'live-map.show-latest', text: LIVE_MAP_SHOW_LATEST },
    { id: 'live-map.overlay-scale', text: LIVE_MAP_OVERLAY_SCALE },
    { id: 'live-map.temp-unit', text: LIVE_MAP_TEMP_UNIT },
    { id: 'live-map.temp-c', text: LIVE_MAP_TEMP_C },
    { id: 'live-map.temp-f', text: LIVE_MAP_TEMP_F },
  ];

  for (const item of C.STORAGE_INVENTORY) {
    entries.push({
      id: `privacy.inventory.${item.kind}`,
      text: item.purpose,
    });
  }

  for (const example of C.EXAMPLES) {
    entries.push({
      id: `examples.${example.id}.label`,
      text: example.label,
    });
  }

  return entries;
}
