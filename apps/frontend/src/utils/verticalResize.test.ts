import { describe, expect, it } from 'vitest';

import {
  VERTICAL_RESIZE_MAX_PX,
  VERTICAL_RESIZE_MIN_PX,
  clampVerticalResizeHeight,
} from './verticalResize';

describe('clampVerticalResizeHeight', () => {
  it('grows and shrinks within bounds', () => {
    expect(clampVerticalResizeHeight(240, 40)).toBe(280);
    expect(clampVerticalResizeHeight(240, -40)).toBe(200);
  });

  it('clamps to min and max', () => {
    expect(clampVerticalResizeHeight(VERTICAL_RESIZE_MIN_PX, -50)).toBe(
      VERTICAL_RESIZE_MIN_PX,
    );
    expect(clampVerticalResizeHeight(VERTICAL_RESIZE_MAX_PX, 50)).toBe(
      VERTICAL_RESIZE_MAX_PX,
    );
  });
});
