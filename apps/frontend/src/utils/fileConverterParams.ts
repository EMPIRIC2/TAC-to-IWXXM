/* eslint-disable complexity */
/** ConversionParams helpers for FileConverter. */
import type {
  ConversionParams,
  StoredConverterPreferences,
} from '@/models/fileConverter';
import type { ConversionExportContext } from '@/utils/conversionExportMetadata';
import type {
  MetarFamilyVariant,
  ProfileCatalogEntry,
} from '@/utils/conversionProfilesApi';
import type {
  ConvertLogLevel,
  ConvertOnError,
  ConvertParamsBar,
} from '@/utils/convertParams';
import {
  DEFAULT_EXCHANGE_PROFILE,
  coerceExchangeProfile,
} from '@/utils/exchangeProfile';
import {
  DEFAULT_IWXXM_VERSION,
  coerceIwxxmVersionForProfile,
} from '@/utils/iwxxmVersions';
import { libraryIdsForNationalLine } from '@/utils/libraryIds';
import type { TacProductSelection } from '@/utils/tacProduct';
import {
  DEFAULT_SEMANTIC_PROFILE,
  coerceIwxxmProfile,
  hydrateSemanticProfile,
} from '@/utils/tacProduct';
import { readWmoLibraryDefaultsSync } from '@/utils/wmoLibraryDefaultsSync';

/**
 * Function `snapshotExportContext`.
 */
/**
 * paramsBarFromState.
 */
export function paramsBarFromState(
  params: ConversionParams,
  reportVariant: string,
): ConvertParamsBar {
  return {
    bulletinId: params.bulletinId,
    issuingCenter: params.issuingCenter,
    reportVariant,
    profile: params.profile,
    exchangeProfile: params.exchangeProfile,
    presetId: params.presetId,
    conversionLibraryId: params.conversionLibraryId,
    tacValidationLibraryId: params.tacValidationLibraryId,
    iwxxmValidationLibraryId: params.iwxxmValidationLibraryId,
    disseminationLibraryId: params.disseminationLibraryId,
    decodingLibraryId: params.decodingLibraryId,
    iwxxmVersion: params.iwxxmVersion,
    strictValidation: params.strictValidation,
    strictLint: params.strictLint,
    strictConvert: params.strictConvert,
    strictValidate: params.strictValidate,
    includeNilReasons: params.includeNilReasons,
    onError: params.onError as ConvertOnError,
    logLevel: params.logLevel as ConvertLogLevel,
  };
}

/**
 * Function `snapshotExportContext`.
 */
/**
 * Function `snapshotExportContext`.
 */
/**
 * snapshotExportContext.
 */
export function snapshotExportContext(
  params: ConversionParams,
  product: string,
  reportVariant?: string,
): ConversionExportContext {
  const variant = (reportVariant ?? params.reportVariant).trim();
  return {
    product,
    iwxxmVersion: params.iwxxmVersion,
    ...(variant ? { reportVariant: variant } : {}),
    conversionLibraryId: params.conversionLibraryId,
    tacValidationLibraryId: params.tacValidationLibraryId,
    iwxxmValidationLibraryId: params.iwxxmValidationLibraryId,
    disseminationLibraryId: params.disseminationLibraryId,
    decodingLibraryId: params.decodingLibraryId,
  };
}

/**
 * Function `initialConversionParams`.
 */
/**
 * Function `initialConversionParams`.
 */
/**
 * initialConversionParams.
 */
export function initialConversionParams(): ConversionParams {
  const base: ConversionParams = {
    bulletinId: '',
    issuingCenter: '',
    product: 'auto',
    profile: DEFAULT_SEMANTIC_PROFILE,
    reportVariant: '',
    exchangeProfile: DEFAULT_EXCHANGE_PROFILE,
    presetId: '',
    disseminationTemplateId: '',
    overlayId: '',
    ...libraryIdsForNationalLine(DEFAULT_SEMANTIC_PROFILE),
    iwxxmVersion: DEFAULT_IWXXM_VERSION,
    strictValidation: false,
    strictLint: true,
    strictConvert: true,
    strictValidate: true,
    includeNilReasons: true,
    onError: 'warn',
    logLevel: 'INFO',
  };
  const sync = readWmoLibraryDefaultsSync();
  if (!sync) {
    return base;
  }
  const profile = coerceIwxxmProfile(sync.profile);
  return {
    ...base,
    ...sync.libraryIds,
    profile,
    reportVariant: '',
    iwxxmVersion: coerceIwxxmVersionForProfile(profile, base.iwxxmVersion),
  };
}

/**
 * Apply saved converter preferences, preferring shared WMO library sync when present.
 */
/**
 * Apply saved converter preferences, preferring shared WMO library sync when present.
 */
/**
 * conversionParamsFromStoredPreferences.
 */
export function conversionParamsFromStoredPreferences(
  prefs: StoredConverterPreferences,
): ConversionParams {
  const sync = readWmoLibraryDefaultsSync();
  const profile = sync
    ? coerceIwxxmProfile(sync.profile)
    : hydrateSemanticProfile(prefs.profile);
  const iwxxmVersion = coerceIwxxmVersionForProfile(profile, prefs.iwxxmVersion);
  return {
    bulletinId:
      (typeof prefs.bulletinIdExample === 'string' && prefs.bulletinIdExample) ||
      'SAAA00',
    issuingCenter: typeof prefs.issuingCenter === 'string' ? prefs.issuingCenter : '',
    product: ((typeof prefs.product === 'string' && prefs.product) ||
      'auto') as TacProductSelection,
    profile,
    reportVariant: '',
    exchangeProfile: coerceExchangeProfile(prefs.exchangeProfile),
    presetId: '',
    disseminationTemplateId: '',
    overlayId: '',
    ...(sync ? sync.libraryIds : libraryIdsForNationalLine(profile)),
    iwxxmVersion,
    strictValidation: prefs.strictValidation === true,
    strictLint: prefs.strictLint !== false,
    strictConvert: prefs.strictConvert !== false,
    strictValidate: prefs.strictValidate !== false,
    includeNilReasons: prefs.includeNilReasons !== false,
    onError: ((typeof prefs.onError === 'string' && prefs.onError) ||
      'warn') as ConversionParams['onError'],
    logLevel: ((typeof prefs.logLevel === 'string' && prefs.logLevel) ||
      'INFO') as ConversionParams['logLevel'],
  };
}

/**
 * Function `activeMetarFamilyVariants`.
 */
/**
 * Function `activeMetarFamilyVariants`.
 */
/**
 * activeMetarFamilyVariants.
 */
export function activeMetarFamilyVariants(
  entry: ProfileCatalogEntry,
  product: string,
): MetarFamilyVariant[] {
  const productU = product.trim().toUpperCase();
  const variants = entry.metar_family_variants;
  if (!variants || variants.length === 0) {
    return [];
  }
  return variants.filter(
    (variant) => variant.api_product.trim().toUpperCase() === productU,
  );
}

/**
 * Operator workbench: TAC queue, convert, validate, and dissemination entry points.
 *
 * @param props.accessToken - Bearer token for authenticated API calls (empty for guest)
 * @param props.userEmail - Display email in the header
 * @param props.isGuest - When true, guest-mode limits apply
 * @param props.onLogout - Sign-out handler
 * @param props.onRequestLogin - Opens sign-in when a gated action needs auth
 * @param props.onOpenHistory - Opens F5 work-session history
 * @param props.onLoadWorkSession - Loads a saved work session into the workbench
 * @param props.onNewMetar - Clears toward a new METAR/SPECI draft
 * @param props.onSessionUpdated - Notifies parent after autosave / session mutate
 * @param props.onActiveSessionIdChange - Reports the active F5 session id
 * @param props.activeWorkSessionId - Current F5 session id when known
 * @param props.loadedWorkSession - Hydration payload for the active session
 * @param props.pendingMapTac - TAC from the Map shell page (Send to converter)
 * @param props.onPendingMapTacConsumed - Clears pending Map TAC after apply
 * @param props.onOpenCatalog - Opens Rule catalogs from Convert trust links
 * @example
 * const _ = true;
 */
