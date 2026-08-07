/**
 * Unit tests for operator work-queue helpers (TC-EV042-003).
 *
 * [Corpus: product §F7] [Corpus: tests]
 */
import { describe, expect, it } from 'vitest';
import {
  clampQueueIndex,
  nextQueueIndex,
  prevQueueIndex,
  toggleQueueSelection,
} from './operatorWorkQueue';

describe('operatorWorkQueue', () => {
  it('clamps focus index within bounds', () => {
    expect(clampQueueIndex(-1, 3)).toBe(0);
    expect(clampQueueIndex(99, 3)).toBe(2);
    expect(clampQueueIndex(1, 0)).toBe(0);
  });

  it('moves next/prev without wrapping past ends', () => {
    expect(nextQueueIndex(0, 3)).toBe(1);
    expect(nextQueueIndex(2, 3)).toBe(2);
    expect(prevQueueIndex(2, 3)).toBe(1);
    expect(prevQueueIndex(0, 3)).toBe(0);
  });

  it('toggles multi-select membership immutably', () => {
    const empty = new Set<string>();
    const one = toggleQueueSelection(empty, 'a');
    expect([...one]).toEqual(['a']);
    expect(empty.size).toBe(0);
    const none = toggleQueueSelection(one, 'a');
    expect(none.size).toBe(0);
  });
});
