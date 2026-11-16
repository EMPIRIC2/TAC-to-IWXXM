/** Small FileConverter helpers. */
import { FALLBACK_PROFILE_SUMMARIES } from './fileConverterProfileFallbacks';
import type { ConversionLog, IWXXMVersion } from '@/models/fileConverter';
import type { ProfileCatalogEntry } from '@/utils/conversionProfilesApi';
import { CA_ECCC_IWXXM_VERSION, isMscOperationalLine } from '@/utils/iwxxmVersions';
import type { IwxxmProfile } from '@/utils/tacProduct';
import { hydrateSemanticProfile } from '@/utils/tacProduct';

/**
 * Function `isStructuredConvertError`.
 */
/**
 * isStructuredConvertError.
 * @example
 * const _ = true;
 */
export function isStructuredConvertError(
  error: unknown,
): error is Error & { errors: string[]; issues: ConversionLog['issues'] } {
  if (!(error instanceof Error)) {
    return false;
  }
  const candidate = error as Partial<{
    errors: unknown;
    issues: unknown;
  }>;
  return Array.isArray(candidate.errors) && Array.isArray(candidate.issues);
}

/**
 * Function `mergeVisibleConvertErrors`.
 */
/**
 * mergeVisibleConvertErrors.
 * @example
 * const _ = true;
 */
export function mergeVisibleConvertErrors(
  primaryMessage: string,
  errors: string[],
): string[] {
  const merged = new Set<string>();
  const normalizedPrimary = primaryMessage.trim();
  if (normalizedPrimary) {
    merged.add(normalizedPrimary);
  }
  for (const error of errors) {
    const normalized = error.trim();
    if (normalized) {
      merged.add(normalized);
    }
  }
  return Array.from(merged);
}

/**
 * Function `fallbackProfileSummary`.
 */
/**
 * fallbackProfileSummary.
 * @example
 * const _ = true;
 */
export function fallbackProfileSummary(
  profile: IwxxmProfile,
  iwxxmVersion: IWXXMVersion,
): ProfileCatalogEntry {
  const canonicalId = hydrateSemanticProfile(profile);
  const fallback = FALLBACK_PROFILE_SUMMARIES[canonicalId];
  if (fallback) {
    return {
      ...fallback,
      iwxxm_line: isMscOperationalLine(canonicalId)
        ? `IWXXM ${CA_ECCC_IWXXM_VERSION} (MSC operational)`
        : `IWXXM ${iwxxmVersion}`,
    };
  }
  return {
    id: canonicalId,
    kind: 'semantic',
    products: [],
    deltas_vs_icao: [],
    iwxxm_line: `IWXXM ${iwxxmVersion}`,
  };
}

/**
 * Re-export conversion helpers and models for FileConverter consumers.
 */
export {
  paramsBarFromState,
  snapshotExportContext,
  initialConversionParams,
  conversionParamsFromStoredPreferences,
  activeMetarFamilyVariants,
} from './fileConverterParams';
export type {
  ConversionParams,
  ConvertedFile,
  ConvertedFileResultCard,
  FileConverterProps,
  IWXXMVersion,
  LogLevel,
  OnErrorBehavior,
  PendingFile,
  StoredConverterPreferences,
} from '@/models/fileConverter';
