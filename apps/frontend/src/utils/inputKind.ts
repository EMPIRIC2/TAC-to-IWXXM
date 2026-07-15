/**
 * Classify operator inputs: single TAC, WMO AHL bulletin, IWXXM COLLECT, gzip wrappers.
 */

export type OperatorInputKind =
  | 'tac'
  | 'ahl_bulletin'
  | 'collect_iwxxm'
  | 'gzip'
  | 'unknown';

export type OperatorInputMode = 'tac' | 'ahl_bulletin' | 'collect_iwxxm';

const AHL_LINE = /^[A-Z]{4}\d{2}\s+[A-Z]{4}\s+\d{6}(?:\s+[A-Z]{3})?\s*$/m;

/**
 * Detect AHL bulletin header (TTAAii CCCC YYGGgg [BBB]).
 *
 * @param text - Raw text
 */
export function looksLikeAhlBulletin(text: string): boolean {
  const trimmed = text.trim();
  if (!trimmed) {
    return false;
  }
  const first = trimmed.split(/\r?\n/).find((line) => line.trim()) ?? '';
  return AHL_LINE.test(first.trim().toUpperCase());
}

/**
 * Detect IWXXM COLLECT / collection wrapper XML.
 *
 * @param text - Raw text or XML
 */
export function looksLikeCollectIwxxm(text: string): boolean {
  const head = text.slice(0, 4000).toLowerCase();
  return (
    head.includes('collect') &&
    (head.includes('iwxxm') ||
      head.includes('meteorologicalbulletin') ||
      head.includes('<collect'))
  );
}

/**
 * Guess kind from filename extension and optional content.
 *
 * @param fileName - File name
 * @param content - Optional decoded text
 */
export function detectInputKind(fileName: string, content?: string): OperatorInputKind {
  const lower = fileName.toLowerCase();
  if (lower.endsWith('.gz') || lower.endsWith('.gzip')) {
    return 'gzip';
  }
  if (content) {
    if (looksLikeCollectIwxxm(content)) {
      return 'collect_iwxxm';
    }
    if (looksLikeAhlBulletin(content)) {
      return 'ahl_bulletin';
    }
    if (looksLikeCollectIwxxm(content) === false && content.trim().startsWith('<')) {
      if (content.toLowerCase().includes('iwxxm')) {
        return 'collect_iwxxm';
      }
    }
  }
  if (lower.endsWith('.xml')) {
    return content && looksLikeCollectIwxxm(content) ? 'collect_iwxxm' : 'unknown';
  }
  return 'tac';
}

/**
 * Map detected kind onto operator mode (gzip stays tac until inflated).
 *
 * @param kind - Detected kind
 */
export function kindToMode(kind: OperatorInputKind): OperatorInputMode {
  if (kind === 'ahl_bulletin') {
    return 'ahl_bulletin';
  }
  if (kind === 'collect_iwxxm') {
    return 'collect_iwxxm';
  }
  return 'tac';
}
