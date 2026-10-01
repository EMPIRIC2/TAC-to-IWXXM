/**
 * Operator layout for the live Convert panes.
 * Stored in this browser: decode density, XML wrapping, and pane widths.
 */

import { useEffect, useState } from 'react';

export const LIVE_CONVERT_LAYOUT_STORAGE_KEY = 'tac-to-iwxxm.live-convert.layout';

/** Same-tab notice so the shell and the workbench share one layout choice. */
export const LIVE_CONVERT_LAYOUT_EVENT = 'tac-live-convert-layout';

const MIN_PANE = 18;
const DEFAULT_WIDTHS: [number, number, number] = [34, 27, 39];

/**
 * Type `LiveConvertDensity`.
 * @example
 * const _ = true;
 */
export type LiveConvertDensity = 'detailed' | 'compact';

/**
 * Type `LiveConvertSpan`.
 * @example
 * const _ = true;
 */
export type LiveConvertSpan = 'roomy' | 'tight';

/**
 * Type `LiveConvertLayout`.
 * @example
 * const _ = true;
 */
export interface LiveConvertLayout {
  density: LiveConvertDensity;
  wrapXml: boolean;
  paneWidths: [number, number, number];
  span: LiveConvertSpan;
}

const DEFAULT_LAYOUT: LiveConvertLayout = {
  density: 'detailed',
  wrapXml: true,
  paneWidths: DEFAULT_WIDTHS,
  span: 'roomy',
};

/**
 * Keep three pane shares that each stay large enough to read.
 *
 * @param raw - Stored or dragged widths
 * @returns Shares that sum to 100
 * @example
 * const _ = true;
 */
export function normalizePaneWidths(raw: unknown): [number, number, number] {
  if (!Array.isArray(raw) || raw.length !== 3) {
    return DEFAULT_WIDTHS;
  }
  if (raw.some((value) => typeof value !== 'number' || !Number.isFinite(value))) {
    return DEFAULT_WIDTHS;
  }
  if (raw.some((value) => value < MIN_PANE)) {
    return DEFAULT_WIDTHS;
  }
  const widths = raw as [number, number, number];
  const sum = widths[0] + widths[1] + widths[2];
  return [(widths[0] / sum) * 100, (widths[1] / sum) * 100, (widths[2] / sum) * 100];
}

/**
 * Move the boundary between two panes. A move that would crush a pane is ignored.
 *
 * @param widths - Current shares
 * @param boundary - 0 between TAC and decode, 1 between decode and IWXXM
 * @param deltaPercent - Positive grows the left pane
 * @returns Next shares
 * @example
 * const _ = true;
 */
export function resizePanePair(
  widths: [number, number, number],
  boundary: 0 | 1,
  deltaPercent: number,
): [number, number, number] {
  const left = boundary === 0 ? widths[0] : widths[1];
  const right = boundary === 0 ? widths[1] : widths[2];
  const nextLeft = left + deltaPercent;
  const nextRight = right - deltaPercent;
  if (nextLeft < MIN_PANE || nextRight < MIN_PANE) {
    return widths;
  }
  const next: [number, number, number] = [widths[0], widths[1], widths[2]];
  if (boundary === 0) {
    next[0] = nextLeft;
    next[1] = nextRight;
  } else {
    next[1] = nextLeft;
    next[2] = nextRight;
  }
  return next;
}

/**
 * Read a stored layout. Unknown values use the defaults.
 *
 * @param raw - JSON string from localStorage
 * @returns Layout safe to render
 * @example
 * const _ = true;
 */
export function parseLiveConvertLayout(
  raw: string | null | undefined,
): LiveConvertLayout {
  if (!raw) {
    return DEFAULT_LAYOUT;
  }
  try {
    const parsed = JSON.parse(raw) as {
      density?: unknown;
      wrapXml?: unknown;
      paneWidths?: unknown;
      span?: unknown;
    };
    return {
      density: parsed.density === 'compact' ? 'compact' : 'detailed',
      wrapXml: parsed.wrapXml === false ? false : true,
      paneWidths: normalizePaneWidths(parsed.paneWidths),
      span: parsed.span === 'tight' ? 'tight' : 'roomy',
    };
  } catch {
    return DEFAULT_LAYOUT;
  }
}

/**
 * Read the saved Convert layout.
 *
 * @returns Stored layout or the defaults
 * @example
 * const _ = true;
 */
export function readLiveConvertLayout(): LiveConvertLayout {
  if (typeof window === 'undefined' || !window.localStorage) {
    return DEFAULT_LAYOUT;
  }
  try {
    return parseLiveConvertLayout(
      window.localStorage.getItem(LIVE_CONVERT_LAYOUT_STORAGE_KEY),
    );
  } catch {
    return DEFAULT_LAYOUT;
  }
}

/**
 * Save the Convert layout. Failures leave the on-screen choice in place.
 *
 * @param layout - Layout to store
 * @example
 * const _ = true;
 */
export function writeLiveConvertLayout(layout: LiveConvertLayout): void {
  if (typeof window === 'undefined' || !window.localStorage) {
    return;
  }
  try {
    window.localStorage.setItem(
      LIVE_CONVERT_LAYOUT_STORAGE_KEY,
      JSON.stringify(layout),
    );
    window.dispatchEvent(new Event(LIVE_CONVERT_LAYOUT_EVENT));
  } catch {
    // Quota or private mode: keep the choice for this visit only.
  }
}

/**
 * Load and update the Convert layout, writing each change to this browser.
 *
 * @returns Current layout and a patch function
 * @example
 * const _ = true;
 */
export function useLiveConvertLayout(): {
  layout: LiveConvertLayout;
  updateLayout: (patch: Partial<LiveConvertLayout>) => void;
} {
  const [layout, setLayout] = useState<LiveConvertLayout>(readLiveConvertLayout);
  useEffect(() => {
    const sync = () => setLayout(readLiveConvertLayout());
    window.addEventListener(LIVE_CONVERT_LAYOUT_EVENT, sync);
    return () => window.removeEventListener(LIVE_CONVERT_LAYOUT_EVENT, sync);
  }, []);
  const updateLayout = (patch: Partial<LiveConvertLayout>) => {
    setLayout((current) => {
      const next = { ...current, ...patch };
      writeLiveConvertLayout(next);
      return next;
    });
  };
  return { layout, updateLayout };
}

/**
 * True when the three Convert panes sit side by side.
 *
 * @returns Whether the wide pane layout is active
 * @example
 * const _ = true;
 */
export function useWideConvertPanes(): boolean {
  const query = '(min-width: 1280px)';
  const [wide, setWide] = useState(() => {
    if (typeof window === 'undefined' || !window.matchMedia) {
      return false;
    }
    return window.matchMedia(query).matches;
  });
  useEffect(() => {
    if (!window.matchMedia) {
      return;
    }
    const media = window.matchMedia(query);
    const onChange = () => setWide(media.matches);
    media.addEventListener('change', onChange);
    return () => media.removeEventListener('change', onChange);
  }, []);
  return wide;
}
