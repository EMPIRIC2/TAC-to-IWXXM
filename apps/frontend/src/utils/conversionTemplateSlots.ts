/**
 * Slot list helpers for conversion templates (EV-080).
 */

import type { ConversionTemplateSlot } from './conversionProfilesApi';

/**
 * Move a slot from one index to another.
 *
 * @param slots - Ordered slots
 * @param fromIndex - Source index
 * @param toIndex - Destination index
 */
export function reorderConversionTemplateSlots(
  slots: ConversionTemplateSlot[],
  fromIndex: number,
  toIndex: number,
): ConversionTemplateSlot[] {
  if (
    fromIndex < 0 ||
    toIndex < 0 ||
    fromIndex >= slots.length ||
    toIndex >= slots.length ||
    fromIndex === toIndex
  ) {
    return slots;
  }
  const next = [...slots];
  const [item] = next.splice(fromIndex, 1);
  if (!item) {
    return slots;
  }
  next.splice(toIndex, 0, item);
  return next;
}
