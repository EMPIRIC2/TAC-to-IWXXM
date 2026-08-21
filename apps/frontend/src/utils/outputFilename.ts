/**
 * Helpers for the optional manual-input output filename (#664 / EV-005).
 *
 * The custom name applies to manual-input conversion results only. A blank or
 * unsafe value falls back to the historical `manual_input` default so existing
 * behavior is preserved.
 *
 * EV-057 / #903: empty custom archive name uses a short stem from the first
 * accumulated TAC + ``yyyyMMddHHmmss`` when provided.
 */

/** Default base name when no custom output filename is provided. */
export const DEFAULT_OUTPUT_BASENAME = 'manual_input';

/** Soft cap for accumulated convert results (F7.r / #903). */
export const ACCUMULATE_RESULT_CAP = 200;

/** Max length of the content-derived ZIP stem when custom name is empty. */
export const ARCHIVE_TAC_STEM_LEN = 8;

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
 * Derive a filesystem-safe ZIP stem from the first accumulated TAC text.
 *
 * Collapses whitespace, strips illegal characters, then takes the first
 * {@link ARCHIVE_TAC_STEM_LEN} characters.
 *
 * @param tac - Raw TAC from the first successful conversion in the batch.
 * @returns A non-empty stem (falls back to ``converted`` when empty after sanitize).
 */
export function stemFromFirstTac(tac: string): string {
  const collapsed = tac.replace(/\s+/g, '');
  const cleaned = collapsed.replace(ILLEGAL_CHARS_RE, '');
  const stem = cleaned.slice(0, ARCHIVE_TAC_STEM_LEN);
  return stem || 'converted';
}

/**
 * Format a local timestamp as ``yyyyMMddHHmmss`` for default ZIP names.
 *
 * @param date - Instant to format (defaults to now).
 * @returns Compact timestamp string.
 */
export function formatArchiveTimestamp(date: Date = new Date()): string {
  const pad = (n: number): string => String(n).padStart(2, '0');
  return (
    `${date.getFullYear()}${pad(date.getMonth() + 1)}${pad(date.getDate())}` +
    `${pad(date.getHours())}${pad(date.getMinutes())}${pad(date.getSeconds())}`
  );
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

export type OutputArchiveNameOptions = {
  /** TAC text from the first successful conversion in the accumulate batch. */
  firstTac?: string;
  /** Clock override for tests. */
  now?: Date;
};

/**
 * Build the "Download All" ZIP archive name.
 *
 * Uses `<base>.zip` when the user set a custom name. When empty: if
 * ``firstTac`` is provided, ``{stem8}_{yyyyMMddHHmmss}.zip`` (#903); otherwise
 * the historical ``converted_files_<ms>.zip`` fallback.
 *
 * @param base - The raw custom output filename (empty ⇒ content-derived or legacy).
 * @param options - Optional first-TAC stem and clock.
 * @returns The ZIP archive filename.
 */
export function outputArchiveName(
  base: string,
  options?: OutputArchiveNameOptions,
): string {
  if (base.trim().length > 0) {
    return `${sanitizeOutputFilename(base)}.zip`;
  }
  const now = options?.now ?? new Date();
  if (options?.firstTac !== undefined && options.firstTac.length > 0) {
    return `${stemFromFirstTac(options.firstTac)}_${formatArchiveTimestamp(now)}.zip`;
  }
  return `converted_files_${now.getTime()}.zip`;
}
