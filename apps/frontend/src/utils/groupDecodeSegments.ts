/**
 * Group adjacent Live decode segments into natural-language phrase rows.
 *
 * Display composition only — does not change the decode_tac wire contract.
 * [Corpus: product §F9] [Corpus: ui-style] UX-2026-10-29-live-decode-phrases
 */

/**
 * Minimal segment shape shared with DecodePanel.
 * @example
 * const _ = true;
 */
export interface DecodeSegmentLike {
  start: number;
  end: number;
  code: string;
  explanation: string;
}

const RE_TC_NAME = /^Tropical cyclone \((.+)\)$/;
const RE_FIR_NAME = /^FIR name \((.+)\)$/;
const RE_TIME = /^Time (.+)$/;
const RE_LAT = /^Latitude (.+)$/;
const RE_LON = /^Longitude (.+)$/;
const RE_FL = /^Flight level (\d+)$/;
const RE_MOV_DIR = /^Movement direction \((.+)\)$/;
const RE_SPEED = /^Speed (.+)$/;

/**
 * Join member codes with a single space (preserve TAC token spelling).
 *
 * @param members - Contiguous decode segments
 * @returns Joined Code column text
 */
function joinCodes(members: DecodeSegmentLike[]): string {
  return members.map((m) => m.code).join(' ');
}

/**
 * Compact a latitude explanation into a short coordinate token.
 *
 * @param explanation - e.g. ``Latitude 15°40' N``
 * @returns e.g. ``15°40'N``
 */
function compactLat(explanation: string): string | null {
  const m = RE_LAT.exec(explanation);
  const raw = m?.[1];
  if (!raw) {
    return null;
  }
  return raw.replace(/\s+/g, '');
}

/**
 * Compact a longitude explanation into a short coordinate token.
 *
 * @param explanation - e.g. ``Longitude 156°20' E``
 * @returns e.g. ``156°20'E``
 */
function compactLon(explanation: string): string | null {
  const m = RE_LON.exec(explanation);
  const raw = m?.[1];
  if (!raw) {
    return null;
  }
  return raw.replace(/\s+/g, '');
}

/**
 * Try TC + named cyclone.
 *
 * @param segments - Full list
 * @param i - Cursor
 * @returns Phrase and next index, or null
 */
function tryTc(
  segments: DecodeSegmentLike[],
  i: number,
): { phrase: DecodeSegmentLike; next: number } | null {
  const a = segments[i];
  const b = segments[i + 1];
  if (!a || !b) {
    return null;
  }
  if (a.code.toUpperCase() !== 'TC' || !/^Tropical cyclone$/i.test(a.explanation)) {
    return null;
  }
  const nameMatch = RE_TC_NAME.exec(b.explanation);
  const name = nameMatch?.[1];
  if (!name) {
    return null;
  }
  return {
    phrase: {
      start: a.start,
      end: b.end,
      code: joinCodes([a, b]),
      explanation: `Tropical cyclone ${name}`,
    },
    next: i + 2,
  };
}

/**
 * Try FIR name + FIR marker.
 *
 * @param segments - Full list
 * @param i - Cursor
 * @returns Phrase and next index, or null
 */
function tryFirName(
  segments: DecodeSegmentLike[],
  i: number,
): { phrase: DecodeSegmentLike; next: number } | null {
  const a = segments[i];
  const b = segments[i + 1];
  if (!a || !b) {
    return null;
  }
  const name = RE_FIR_NAME.exec(a.explanation)?.[1];
  if (!name) {
    return null;
  }
  if (!/^Flight information region$/i.test(b.explanation)) {
    return null;
  }
  return {
    phrase: {
      start: a.start,
      end: b.end,
      code: joinCodes([a, b]),
      explanation: `${name} flight information region`,
    },
    next: i + 2,
  };
}

/**
 * Try OBS/FCST (+ AT) + time (+ lat) (+ lon).
 *
 * @param segments - Full list
 * @param i - Cursor
 * @returns Phrase and next index, or null
 */
function tryObsFcst(
  segments: DecodeSegmentLike[],
  i: number,
): { phrase: DecodeSegmentLike; next: number } | null {
  const head = segments[i];
  if (!head) {
    return null;
  }
  const kind =
    head.explanation === 'Observed'
      ? 'Observed'
      : head.explanation === 'Forecast'
        ? 'Forecast'
        : null;
  if (!kind) {
    return null;
  }

  const members: DecodeSegmentLike[] = [head];
  let j = i + 1;

  const at = segments[j];
  if (at && /^At \(observation \/ forecast time\)$/i.test(at.explanation)) {
    members.push(at);
    j += 1;
  }

  const timeSeg = segments[j];
  if (!timeSeg) {
    return null;
  }
  const timeText = RE_TIME.exec(timeSeg.explanation)?.[1];
  if (!timeText) {
    return null;
  }
  members.push(timeSeg);
  j += 1;

  let near = '';
  const latSeg = segments[j];
  const lat = latSeg ? compactLat(latSeg.explanation) : null;
  if (latSeg && lat) {
    members.push(latSeg);
    j += 1;
    const lonSeg = segments[j];
    const lon = lonSeg ? compactLon(lonSeg.explanation) : null;
    if (lonSeg && lon) {
      members.push(lonSeg);
      j += 1;
      near = ` near ${lat} ${lon}`;
    } else {
      near = ` near ${lat}`;
    }
  }

  // members always starts with head; last is therefore defined.
  const last = members[members.length - 1]!;

  return {
    phrase: {
      start: head.start,
      end: last.end,
      code: joinCodes(members),
      explanation: `${kind} at ${timeText}${near}`,
    },
    next: j,
  };
}

/**
 * Try CB + TOP + flight level.
 *
 * @param segments - Full list
 * @param i - Cursor
 * @returns Phrase and next index, or null
 */
function tryCbTop(
  segments: DecodeSegmentLike[],
  i: number,
): { phrase: DecodeSegmentLike; next: number } | null {
  const a = segments[i];
  const b = segments[i + 1];
  const c = segments[i + 2];
  if (!a || !b || !c) {
    return null;
  }
  if (!/^Cumulonimbus/i.test(a.explanation)) {
    return null;
  }
  if (!/^Top$/i.test(b.explanation)) {
    return null;
  }
  const fl = RE_FL.exec(c.explanation)?.[1];
  if (!fl) {
    return null;
  }
  return {
    phrase: {
      start: a.start,
      end: c.end,
      code: joinCodes([a, b, c]),
      explanation: `Cumulonimbus top at flight level ${fl}`,
    },
    next: i + 3,
  };
}

/**
 * Try MOV + direction + speed.
 *
 * @param segments - Full list
 * @param i - Cursor
 * @returns Phrase and next index, or null
 */
function tryMov(
  segments: DecodeSegmentLike[],
  i: number,
): { phrase: DecodeSegmentLike; next: number } | null {
  const a = segments[i];
  const b = segments[i + 1];
  const c = segments[i + 2];
  if (!a || !b || !c) {
    return null;
  }
  if (!/^Moving$/i.test(a.explanation)) {
    return null;
  }
  const dirRaw = RE_MOV_DIR.exec(b.explanation)?.[1];
  const speedRaw = RE_SPEED.exec(c.explanation)?.[1];
  if (!dirRaw || !speedRaw) {
    return null;
  }
  const direction = dirRaw.toLowerCase();
  return {
    phrase: {
      start: a.start,
      end: c.end,
      code: joinCodes([a, b, c]),
      explanation: `Moving ${direction} at ${speedRaw}`,
    },
    next: i + 3,
  };
}

/**
 * Collapse adjacent decode segments into natural-language phrase rows.
 *
 * Unmatched segments pass through unchanged. Order is preserved.
 *
 * @param segments - Atomic Code | Explanation rows from decode-tac
 * @returns Display phrases for Live decode
 * @example
 * const _ = true;
 */
export function groupDecodeSegments(
  segments: DecodeSegmentLike[],
): DecodeSegmentLike[] {
  const out: DecodeSegmentLike[] = [];
  let i = 0;
  while (i < segments.length) {
    const hit =
      tryFirName(segments, i) ??
      tryTc(segments, i) ??
      tryObsFcst(segments, i) ??
      tryCbTop(segments, i) ??
      tryMov(segments, i);
    if (hit) {
      out.push(hit.phrase);
      i = hit.next;
      continue;
    }
    const one = segments[i];
    if (one) {
      out.push(one);
    }
    i += 1;
  }
  return out;
}
