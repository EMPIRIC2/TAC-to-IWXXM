/**
 * Region sketch and wind cue for decoded reports (F7 / F9).
 *
 * Positions are a labeled sketch of ICAO prefix regions, not a surveyed map.
 */

import { airports } from '@/utils/airportsData';
import {
  DECODE_VISUALS_NO_WIND,
  DECODE_VISUALS_WIND_VARIABLE,
} from '@/utils/decodeVisualsCopy';

/**
 * Type `RegionBox`.
 * @example
 * const _ = true;
 */
export type RegionBox = {
  prefix: string;
  label: string;
  x: number;
  y: number;
  w: number;
  h: number;
};

const REGION_BOXES: Record<string, RegionBox> = {
  C: { prefix: 'C', label: 'Canada', x: 18, y: 18, w: 64, h: 28 },
  K: { prefix: 'K', label: 'United States', x: 18, y: 50, w: 64, h: 36 },
  E: { prefix: 'E', label: 'Northern Europe', x: 150, y: 28, w: 58, h: 26 },
  L: { prefix: 'L', label: 'Southern Europe', x: 150, y: 58, w: 58, h: 26 },
  Y: { prefix: 'Y', label: 'Australia', x: 250, y: 120, w: 56, h: 28 },
  Z: { prefix: 'Z', label: 'East Asia', x: 230, y: 48, w: 56, h: 28 },
};

/**
 * Region box for an ICAO station prefix, or null when the prefix is not sketched.
 *
 * @param icao - Station code
 * @returns Sketch box
 * @example
 * const _ = true;
 */
export function regionForStation(icao: string): RegionBox | null {
  const prefix = icao.trim().toUpperCase().charAt(0);
  if (!prefix) {
    return null;
  }
  return REGION_BOXES[prefix] ?? null;
}

/**
 * Every sketched region, in prefix order.
 *
 * @returns Sketch boxes
 * @example
 * const _ = true;
 */
export function regionBoxes(): RegionBox[] {
  return Object.values(REGION_BOXES);
}

/**
 * Station heading. Uses the airport name when the local catalog has one.
 *
 * @param icao - Station code
 * @returns Name or the code
 * @example
 * const _ = true;
 */
export function stationDisplayName(icao: string): string {
  const code = icao.trim().toUpperCase();
  if (!code) {
    return '';
  }
  return airports.findWhere({ icao: code })?.name ?? code;
}

/**
 * First station-like token in a TAC report.
 *
 * @param text - Report text
 * @returns Four-letter code, or an empty string
 * @example
 * const _ = true;
 */
export function stationFromReport(text: string): string {
  const tokens = text.toUpperCase().match(/\b[A-Z]{4}\b/g) ?? [];
  const skipped = new Set(['METAR', 'SPECI', 'TAF']);
  const candidates = tokens.filter((token) => !skipped.has(token));
  return candidates.find((token) => airports.isValid(token)) ?? candidates[0] ?? '';
}

/**
 * Type `WindCueModel`.
 * @example
 * const _ = true;
 */
export type WindCueModel = {
  label: string;
  degrees: number | null;
};

/**
 * Wind cue from decode rows. Degrees are null when the direction is variable or absent.
 *
 * @param segments - Decode rows
 * @returns Cue, or null when no wind group is present
 * @example
 * const _ = true;
 */
export function windCueFromSegments(
  segments: { code: string; explanation: string }[],
): WindCueModel | null {
  for (const segment of segments) {
    const compact = segment.code.replace(/\s+/g, '').toUpperCase();
    if (/^VRB\d{2,3}(?:G\d{2,3})?KT$/.test(compact)) {
      return { label: DECODE_VISUALS_WIND_VARIABLE, degrees: null };
    }
    const group = /^(\d{3})\d{2,3}(?:G\d{2,3})?KT$/.exec(compact);
    if (group) {
      const degrees = Number(group[1]);
      if (degrees <= 360) {
        return { label: `Wind from ${degrees} degrees`, degrees };
      }
    }
    if (/wind/i.test(segment.explanation)) {
      const named = /^(\d{1,3})\b/.exec(segment.code.trim());
      if (named) {
        const degrees = Number(named[1]);
        if (degrees <= 360) {
          return { label: `Wind from ${degrees} degrees`, degrees };
        }
      }
    }
  }
  return null;
}

/**
 * Text used when a decode has no wind cue.
 *
 * @returns Empty-state sentence
 * @example
 * const _ = true;
 */
export function windCueEmptyLabel(): string {
  return DECODE_VISUALS_NO_WIND;
}
