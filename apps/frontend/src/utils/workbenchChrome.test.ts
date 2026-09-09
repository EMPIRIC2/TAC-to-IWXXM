/**
 * Workbench chrome viewport helpers — narrow collapse defaults.
 */

import { afterEach, describe, expect, it, vi } from 'vitest';

import { preferCollapsedWorkbenchChrome, WORKBENCH_NARROW_MQ } from './workbenchChrome';

describe('preferCollapsedWorkbenchChrome', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('returns false when window is unavailable', () => {
    vi.stubGlobal('window', undefined);
    expect(preferCollapsedWorkbenchChrome()).toBe(false);
  });

  it('follows the narrow media query', () => {
    const matchMedia = vi.fn((query: string) => ({
      matches: query === WORKBENCH_NARROW_MQ,
      media: query,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
    }));
    vi.stubGlobal('window', { matchMedia });
    expect(preferCollapsedWorkbenchChrome()).toBe(true);
    expect(matchMedia).toHaveBeenCalledWith(WORKBENCH_NARROW_MQ);
  });
});
