/**
 * Helpers for the optional manual-input output filename (#664 / EV-005).
 *
 * The custom name applies to manual-input conversion results only. A blank or
 * unsafe value falls back to the historical `manual_input` default so existing
 * behavior is preserved.
 */

/** Default base name when no custom output filename is provided. */
export const DEFAULT_OUTPUT_BASENAME = 'manual_input';

// Characters disallowed in filenames across common platforms, plus control chars.
// eslint-disable-next-line no-control-regex
const ILLEGAL_CHARS_RE = /[<>:"/\\|?*\u0000-\u001f]/g;

/**
 * Sanitize a user-supplied output filename into a safe base name.
 *
 * Keeps only the last path segment, drops any trailing extension, removes
 * illegal/control characters, and trims whitespace.
 *
 * @param raw - The raw user input (may be empty, null, or undefined).
 * @returns A safe base name, or {@link DEFAULT_OUTPUT_BASENAME} when empty.
 */
export function sanitizeOutputFilename(raw: string | null | undefined): string {
  if (!raw) {
    return DEFAULT_OUTPUT_BASENAME;
  }
  let name = raw.trim();
  // Strip directories — keep the final path segment.
  name = name.split(/[\\/]/).pop() ?? '';
  // Drop a single trailing extension (e.g. ".xml", ".txt").
  name = name.replace(/\.[^.]+$/, '');
  // Remove illegal/control characters and re-trim.
  name = name.replace(ILLEGAL_CHARS_RE, '').trim();
  return name || DEFAULT_OUTPUT_BASENAME;
}

/**
 * Build the download name for a manual-input result.
 *
 * Returns `<base>.txt` so the converter's existing `.txt`→`.xml` swap yields
 * `<base>.xml`. Multi-line manual input suffixes `_1`, `_2`, … (1-based).
 *
 * @param base - The raw custom output filename (sanitized internally).
 * @param index - Zero-based index of the manual result.
 * @param total - Total number of manual results in the batch.
 * @returns The `.txt` base name for the result.
 */
export function manualOutputName(base: string, index: number, total: number): string {
  const safe = sanitizeOutputFilename(base);
  const suffix = total > 1 ? `_${index + 1}` : '';
  return `${safe}${suffix}.txt`;
}

/**
 * Build the download XML filename from the *current* Output filename field.
 *
 * Used after convert when the operator renames the field (#904) — must not
 * rely on the convert-time {@link manualOutputName} baked into result state.
 *
 * @param base - Current raw Output filename field value.
 * @param index - Zero-based index of the manual result.
 * @param total - Total number of manual results in the batch.
 * @returns The `.xml` download name (sanitized + multi-line suffix).
 */
export function manualDownloadXmlName(
  base: string,
  index: number,
  total: number,
): string {
  return manualOutputName(base, index, total).replace(/\.(txt|metar)$/i, '.xml');
}

/**
 * Build the "Download All" ZIP archive name.
 *
 * Uses `<base>.zip` when the user set a custom name; otherwise the historical
 * timestamped `converted_files_<ts>.zip`.
 *
 * @param base - The raw custom output filename (empty ⇒ timestamped default).
 * @returns The ZIP archive filename.
 */
export function outputArchiveName(base: string): string {
  if (base.trim().length === 0) {
    return `converted_files_${Date.now()}.zip`;
  }
  return `${sanitizeOutputFilename(base)}.zip`;
}
