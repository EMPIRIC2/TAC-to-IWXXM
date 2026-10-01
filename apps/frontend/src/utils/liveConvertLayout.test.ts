/**
 * Saved Convert pane layout.
 */

import { act, renderHook } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import {
  LIVE_CONVERT_LAYOUT_STORAGE_KEY,
  normalizePaneWidths,
  parseLiveConvertLayout,
  readLiveConvertLayout,
  resizePanePair,
  useLiveConvertLayout,
  useWideConvertPanes,
  writeLiveConvertLayout,
} from './liveConvertLayout';

describe('liveConvertLayout', () => {
  afterEach(() => {
    window.localStorage.clear();
  });

  it('normalizes widths and ignores a crush', () => {
    expect(normalizePaneWidths(null)).toEqual([34, 27, 39]);
    expect(normalizePaneWidths([1, 2])).toEqual([34, 27, 39]);
    expect(normalizePaneWidths(['a', 40, 40])).toEqual([34, 27, 39]);
    expect(normalizePaneWidths([10, 45, 45])).toEqual([34, 27, 39]);
    expect(normalizePaneWidths([50, 25, 25])).toEqual([50, 25, 25]);
    const start: [number, number, number] = [34, 27, 39];
    expect(resizePanePair(start, 0, 2)).toEqual([36, 25, 39]);
    expect(resizePanePair(start, 0, -30)).toBe(start);
    expect(resizePanePair(start, 1, 2)).toEqual([34, 29, 37]);
    expect(resizePanePair(start, 1, -20)).toBe(start);
  });

  it('reads stored density and wrapping', () => {
    expect(parseLiveConvertLayout(null)).toMatchObject({
      density: 'detailed',
      wrapXml: true,
    });
    expect(parseLiveConvertLayout('{')).toMatchObject({ density: 'detailed' });
    expect(parseLiveConvertLayout('{"density":"other","wrapXml":true}')).toMatchObject({
      density: 'detailed',
      wrapXml: true,
    });
    expect(
      parseLiveConvertLayout(
        JSON.stringify({
          density: 'compact',
          wrapXml: false,
          paneWidths: [40, 30, 30],
        }),
      ),
    ).toEqual({
      density: 'compact',
      wrapXml: false,
      paneWidths: [40, 30, 30],
      span: 'roomy',
    });
    expect(parseLiveConvertLayout('{"span":"tight"}').span).toBe('tight');
    writeLiveConvertLayout({
      density: 'compact',
      wrapXml: false,
      paneWidths: [40, 30, 30],
      span: 'roomy',
    });
    expect(readLiveConvertLayout().density).toBe('compact');
    expect(window.localStorage.getItem(LIVE_CONVERT_LAYOUT_STORAGE_KEY)).toContain(
      'compact',
    );
  });

  it('falls back when storage is missing or throws', () => {
    const original = window.localStorage;
    Object.defineProperty(window, 'localStorage', {
      configurable: true,
      value: undefined,
    });
    expect(readLiveConvertLayout().density).toBe('detailed');
    writeLiveConvertLayout({
      density: 'compact',
      wrapXml: true,
      paneWidths: [34, 27, 39],
      span: 'roomy',
    });
    Object.defineProperty(window, 'localStorage', {
      configurable: true,
      value: original,
    });

    vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => {
      throw new Error('blocked');
    });
    expect(readLiveConvertLayout().wrapXml).toBe(true);
    vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
      throw new Error('quota');
    });
    writeLiveConvertLayout({
      density: 'detailed',
      wrapXml: true,
      paneWidths: [34, 27, 39],
      span: 'roomy',
    });
    vi.restoreAllMocks();
  });

  it('remembers a layout change and follows the wide breakpoint', () => {
    const { result } = renderHook(() => useLiveConvertLayout());
    act(() => result.current.updateLayout({ density: 'compact' }));
    expect(result.current.layout.density).toBe('compact');
    expect(readLiveConvertLayout().density).toBe('compact');

    const other = renderHook(() => useLiveConvertLayout());
    act(() => result.current.updateLayout({ span: 'tight' }));
    expect(other.result.current.layout.span).toBe('tight');
    other.unmount();

    let matches = false;
    let listener: (() => void) | null = null;
    const originalMatch = window.matchMedia;
    window.matchMedia = vi.fn(() => ({
      get matches() {
        return matches;
      },
      media: '(min-width: 1280px)',
      onchange: null,
      addListener: () => {},
      removeListener: () => {},
      addEventListener: (_type: string, fn: () => void) => {
        listener = fn;
      },
      removeEventListener: () => {
        listener = null;
      },
      dispatchEvent: () => true,
    })) as unknown as typeof window.matchMedia;

    const wide = renderHook(() => useWideConvertPanes());
    expect(wide.result.current).toBe(false);
    matches = true;
    act(() => listener?.());
    expect(wide.result.current).toBe(true);
    wide.unmount();

    const missing = window.matchMedia;
    Object.defineProperty(window, 'matchMedia', {
      configurable: true,
      value: undefined,
    });
    const narrow = renderHook(() => useWideConvertPanes());
    expect(narrow.result.current).toBe(false);
    narrow.unmount();
    window.matchMedia = missing;
    window.matchMedia = originalMatch;
  });
});
