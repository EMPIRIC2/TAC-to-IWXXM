/**
 * Tests for conversion template slot helpers.
 */

import { describe, expect, it } from 'vitest';
import {
  moveSelectedConversionTemplateSlot,
  reorderConversionTemplateSlots,
} from './conversionTemplateSlots';

describe('reorderConversionTemplateSlots', () => {
  it('moves an item and no-ops on bad indexes', () => {
    const slots = [
      { id: 'a', label: 'a', type: 'digits' },
      { id: 'b', label: 'b', type: 'digits' },
    ];
    expect(reorderConversionTemplateSlots(slots, 0, 1).map((s) => s.id)).toEqual([
      'b',
      'a',
    ]);
    expect(reorderConversionTemplateSlots(slots, -1, 0)).toBe(slots);
  });
});

describe('moveSelectedConversionTemplateSlot', () => {
  const slots = [
    { id: 'a', label: 'a', type: 'digits' },
    { id: 'b', label: 'b', type: 'digits' },
  ];

  it('returns null for empty slots or unknown selection', () => {
    expect(moveSelectedConversionTemplateSlot([], 'a', 1)).toBeNull();
    expect(moveSelectedConversionTemplateSlot(slots, 'missing', 1)).toBeNull();
  });

  it('defaults to index 0 when selection is null', () => {
    const moved = moveSelectedConversionTemplateSlot(slots, null, 1);
    expect(moved?.slots.map((s) => s.id)).toEqual(['b', 'a']);
    expect(moved?.selectedSlotId).toBe('a');
  });

  it('no-ops at list boundaries', () => {
    expect(moveSelectedConversionTemplateSlot(slots, 'a', -1)).toBeNull();
    expect(moveSelectedConversionTemplateSlot(slots, 'b', 1)).toBeNull();
  });

  it('moves a selected slot and keeps selection on the moved id', () => {
    const moved = moveSelectedConversionTemplateSlot(slots, 'b', -1);
    expect(moved?.slots.map((s) => s.id)).toEqual(['b', 'a']);
    expect(moved?.selectedSlotId).toBe('b');
  });
});
