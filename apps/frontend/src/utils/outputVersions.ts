/**
 * Versions stored on a work session after each successful convert.
 * Live preview does not append a version.
 */

/**
 * Type `OutputVersion`.
 * @example
 * const _ = true;
 */
export interface OutputVersion {
  at: number;
  tac: string;
  xml: string;
  conversionProfile: string;
  decodingProfile: string;
}

const MAX_VERSIONS = 20;

/**
 * Read versions persisted on a session's conversion params.
 *
 * @param params - Session conversion_params object
 * @returns Versions in chronological order
 * @example
 * const _ = true;
 */
export function readOutputVersions(
  params: Record<string, unknown> | undefined,
): OutputVersion[] {
  const raw = params?.output_versions;
  if (!Array.isArray(raw)) {
    return [];
  }
  const versions: OutputVersion[] = [];
  for (const item of raw) {
    if (!item || typeof item !== 'object') {
      continue;
    }
    const row = item as Record<string, unknown>;
    if (typeof row.xml !== 'string' || typeof row.tac !== 'string') {
      continue;
    }
    versions.push({
      at: typeof row.at === 'number' ? row.at : 0,
      tac: row.tac,
      xml: row.xml,
      conversionProfile:
        typeof row.conversionProfile === 'string' ? row.conversionProfile : '',
      decodingProfile:
        typeof row.decodingProfile === 'string' ? row.decodingProfile : '',
    });
  }
  return versions;
}

/**
 * Append a successful convert. Skips a repeat of the latest XML.
 *
 * @param existing - Versions already stored
 * @param next - Convert that just succeeded
 * @returns Next version list, capped
 * @example
 * const _ = true;
 */
export function appendOutputVersion(
  existing: OutputVersion[],
  next: OutputVersion,
): OutputVersion[] {
  const last = existing[existing.length - 1];
  if (last && last.xml === next.xml && last.tac === next.tac) {
    return existing;
  }
  const combined = [...existing, next];
  if (combined.length <= MAX_VERSIONS) {
    return combined;
  }
  return combined.slice(combined.length - MAX_VERSIONS);
}
