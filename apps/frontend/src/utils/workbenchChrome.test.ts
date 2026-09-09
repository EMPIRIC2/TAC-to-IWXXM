/**
 * Workbench chrome viewport helpers — narrow collapse defaults.
 */

import { afterEach, describe, expect, it, vi } from 'vitest';

import {
  preferCollapsedWorkbenchChrome,
  subscribeNarrowWorkbenchChrome,
  WORKBENCH_NARROW_MQ,
} from './workbenchChrome';

function stubMatchMedia(initialMatches: boolean) {
  let matches = initialMatches;
  const listeners = new Set<() => void>();
  const matchMedia = vi.fn((query: string) => ({
    get matches() {
      return matches;
    },
    media: query,
    addEventListener: (_event: string, fn: () => void) => {
      listeners.add(fn);
    },
    removeEventListener: (_event: string, fn: () => void) => {
      listeners.delete(fn);
    },
    addListener: vi.fn(),
    removeListener: vi.fn(),
    dispatchEvent: vi.fn(),
    onchange: null,
  }));
  vi.stubGlobal('window', { matchMedia });
  return {
    matchMedia,
    setMatches: (next: boolean) => {
      matches = next;
    },
    fireChange: () => {
      listeners.forEach((fn) => fn());
    },
  };
}

describe('preferCollapsedWorkbenchChrome', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('returns false when window is unavailable', () => {
    vi.stubGlobal('window', undefined);
    expect(preferCollapsedWorkbenchChrome()).toBe(false);
  });

  it('follows the narrow media query', () => {
    const { matchMedia } = stubMatchMedia(true);
    expect(preferCollapsedWorkbenchChrome()).toBe(true);
    expect(matchMedia).toHaveBeenCalledWith(WORKBENCH_NARROW_MQ);
  });
});

describe('subscribeNarrowWorkbenchChrome', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('returns a no-op unsubscribe when matchMedia is missing', () => {
    vi.stubGlobal('window', {});
    const unsub = subscribeNarrowWorkbenchChrome(() => undefined);
    expect(() => unsub()).not.toThrow();
  });

  it('invokes onEnterNarrow only when crossing wide → narrow', () => {
    const { setMatches, fireChange } = stubMatchMedia(false);
    const onEnterNarrow = vi.fn();
    const unsub = subscribeNarrowWorkbenchChrome(onEnterNarrow);

    fireChange();
    expect(onEnterNarrow).not.toHaveBeenCalled();

    setMatches(true);
    fireChange();
    expect(onEnterNarrow).toHaveBeenCalledTimes(1);

    fireChange();
    expect(onEnterNarrow).toHaveBeenCalledTimes(1);

    setMatches(false);
    fireChange();
    setMatches(true);
    fireChange();
    expect(onEnterNarrow).toHaveBeenCalledTimes(2);

    unsub();
  });
});
