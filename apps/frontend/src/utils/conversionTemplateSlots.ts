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
 * @example
 * const _ = true;
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
  const item = next.splice(fromIndex, 1)[0] as ConversionTemplateSlot;
  next.splice(toIndex, 0, item);
  return next;
}

/**
 * Type `MoveSelectedSlotResult`.
 * @example
 * const _ = true;
 */
export type MoveSelectedSlotResult = {
  slots: ConversionTemplateSlot[];
  selectedSlotId: string | null;
};

/**
 * Reorder slots relative to the currently selected slot.
 *
 * @param slots - Ordered slots
 * @param selectedSlotId - Active slot id, or null to treat index 0 as selected
 * @param delta - Relative move (−1 up, +1 down)
 * @returns Updated slots + selection, or null when the move is a no-op
 * @example
 * const _ = true;
 */
export function moveSelectedConversionTemplateSlot(
  slots: ConversionTemplateSlot[],
  selectedSlotId: string | null,
  delta: number,
): MoveSelectedSlotResult | null {
  if (!slots.length) return null;
  const idx = selectedSlotId ? slots.findIndex((s) => s.id === selectedSlotId) : 0;
  if (idx < 0) return null;
  const nextIdx = idx + delta;
  if (nextIdx < 0 || nextIdx >= slots.length) return null;
  const reordered = reorderConversionTemplateSlots(slots, idx, nextIdx);
  return {
    slots: reordered,
    selectedSlotId: reordered[nextIdx]!.id,
  };
}
