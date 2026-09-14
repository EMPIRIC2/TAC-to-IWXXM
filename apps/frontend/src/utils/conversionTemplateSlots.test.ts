/**
 * Tests for conversion template slot helpers.
 */

import { describe, expect, it } from 'vitest';
import { reorderConversionTemplateSlots } from './conversionTemplateSlots';

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
