/**
 * Plain-language reason for a Convert library selection.
 */

const WMO_BASELINE = 'WMO baseline. Choose another line when the report is national.';
const CUSTOM_LIBRARY = 'Custom library for this conversion.';
const NATIONAL_LINE =
  'National line for this conversion. Reset to WMO defaults to use the baseline.';

/**
 * National line suffix of a first-party library id.
 *
 * @param libraryId - Library id such as LIB.DECODING.ICAO_2025
 * @returns Line id, or null when the id is not a first-party library
 * @example
 * const _ = true;
 */
export function libraryLine(libraryId: string): string | null {
  const parts = libraryId.trim().split('.');
  if (parts[0] !== 'LIB' || parts.length < 3) return null;
  const line = parts.slice(2).join('.').trim();
  return line.length > 0 ? line : null;
}

/**
 * Why this library is the current choice.
 *
 * @param libraryId - Selected library id, or blank when the default is shown
 * @returns Operator-facing reason
 * @example
 * const _ = true;
 */
export function libraryChoiceReason(libraryId: string): string {
  const trimmed = libraryId.trim();
  if (!trimmed) return WMO_BASELINE;
  const line = libraryLine(trimmed);
  if (line?.toUpperCase() === 'ICAO_2025') return WMO_BASELINE;
  if (!line) return CUSTOM_LIBRARY;
  return NATIONAL_LINE;
}
