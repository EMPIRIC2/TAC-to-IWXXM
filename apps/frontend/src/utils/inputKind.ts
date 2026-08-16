/**
 * Classify operator inputs: single TAC, WMO AHL bulletin, IWXXM COLLECT, gzip wrappers.
 */

export type OperatorInputKind =
  | 'tac'
  | 'ahl_bulletin'
  | 'collect_iwxxm'
  | 'iwxxm_document'
  | 'gzip'
  | 'unknown';

export type OperatorInputMode =
  | 'tac'
  | 'ahl_bulletin'
  | 'collect_iwxxm'
  | 'validate_iwxxm';

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
 * Detect a standalone IWXXM document (not a COLLECT wrapper) for validate-only mode.
 *
 * @param text - Raw XML text
 */
export function looksLikeIwxxmDocument(text: string): boolean {
  const trimmed = text.trim();
  if (!trimmed.startsWith('<')) {
    return false;
  }
  if (looksLikeCollectIwxxm(trimmed)) {
    return false;
  }
  const head = trimmed.slice(0, 4000).toLowerCase();
  return head.includes('iwxxm');
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
    if (looksLikeIwxxmDocument(content)) {
      return 'iwxxm_document';
    }
    if (looksLikeAhlBulletin(content)) {
      return 'ahl_bulletin';
    }
  }
  if (lower.endsWith('.xml')) {
    if (content && looksLikeCollectIwxxm(content)) {
      return 'collect_iwxxm';
    }
    if (content && looksLikeIwxxmDocument(content)) {
      return 'iwxxm_document';
    }
    return 'unknown';
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
  if (kind === 'iwxxm_document') {
    return 'validate_iwxxm';
  }
  return 'tac';
}
