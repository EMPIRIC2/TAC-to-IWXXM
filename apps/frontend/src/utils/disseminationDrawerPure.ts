/**
 * Pure DisseminationDrawer helpers (no API client imports).
 */
import type { DisseminationRowUiState } from '@/models/disseminationDrawer';

/**
 * True when a drop FileList has at least one file.
 * @example
 * const _ = true;
 */
/**
 * hasDropFiles.
 * @example
 * const _ = true;
 */
export function hasDropFiles(files: FileList | null | undefined): boolean {
  return Boolean(files && files.length > 0);
}

/**
 * Normalize FileReader result to text.
 * @example
 * const _ = true;
 */
/**
 * dropReaderText.
 * @example
 * const _ = true;
 */
export function dropReaderText(result: string | ArrayBuffer | null): string {
  return String(result ?? '');
}

/**
 * Progress row state with pending fallback.
 * @example
 * const _ = true;
 */
/**
 * progressRowState.
 * @example
 * const _ = true;
 */
export function progressRowState(
  state: Record<string, DisseminationRowUiState>,
  id: string,
): DisseminationRowUiState {
  return state[id] ?? { status: 'pending' };
}
