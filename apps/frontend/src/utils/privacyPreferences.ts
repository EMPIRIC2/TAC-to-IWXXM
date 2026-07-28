/**
 * Privacy preference store (F22 / ADR-031 / E17-7/16/17).
 *
 * Persistence target: `localStorage` (work sessions stay in IndexedDB). This stub
 * exists so TC-F22-001..003 can import the contract and fail red until T6.2
 * (notice + settings) and T6.3 (GPC honor).
 */

/** localStorage key for versioned privacy preferences (E17-17). */
export const PRIVACY_PREFS_STORAGE_KEY = 'tac_privacy_preferences' as const;

/** Bump when preference schema changes — re-shows first-visit notice (UJ-033). */
export const PRIVACY_SCHEMA_VERSION = 1 as const;

/**
 * Solution A preference schema (F22).
 *
 * `necessary` is always on. Non-essential categories default false and are only
 * shown in UI when the product actually uses them (v1: none).
 */
export interface PrivacyPreferences {
  schemaVersion: number;
  /** Always true — required client storage for app function. */
  necessary: true;
  /** Non-essential analytics; default false; unused in Solution A v1. */
  analytics: boolean;
  /** Non-essential marketing; default false; unused in Solution A v1. */
  marketing: boolean;
  /** Sale/sharing opt-out — forced when GPC is detected (E17-16). */
  saleOrSharingOptOut: boolean;
  /** Targeted-advertising opt-out — forced when GPC is detected (E17-16). */
  targetedAdvertisingOptOut: boolean;
  /** ISO timestamp when the first-visit notice was acknowledged; null if never. */
  noticeAcknowledgedAt: string | null;
  /** Schema version for which the notice was acknowledged. */
  noticeSchemaVersion: number | null;
}

/** Client storage inventory disclosed in Privacy settings (F22 / UJ-033). */
export interface StorageInventoryItem {
  kind: 'indexedDB' | 'localStorage' | 'sessionStorage' | 'cookie' | 'cdn';
  purpose: string;
  /** When true, category is required for app function (cannot be turned off). */
  necessary: boolean;
}

export const STORAGE_INVENTORY: readonly StorageInventoryItem[] = [
  {
    kind: 'indexedDB',
    purpose: 'Work history and converter sessions (F5 / F7.h)',
    necessary: true,
  },
  {
    kind: 'localStorage',
    purpose: 'Privacy preferences and converter UI preferences',
    necessary: true,
  },
] as const;

function notImplemented(op: string): never {
  throw new Error(`privacyPreferences.${op}: not implemented (T6.2/T6.3)`);
}

/** Default Solution A preferences (non-essential off; notice not acknowledged). */
export function defaultPrivacyPreferences(): PrivacyPreferences {
  return {
    schemaVersion: PRIVACY_SCHEMA_VERSION,
    necessary: true,
    analytics: false,
    marketing: false,
    saleOrSharingOptOut: false,
    targetedAdvertisingOptOut: false,
    noticeAcknowledgedAt: null,
    noticeSchemaVersion: null,
  };
}

/** Load preferences from localStorage (applies GPC overrides when implemented). */
export function loadPrivacyPreferences(): PrivacyPreferences {
  notImplemented('loadPrivacyPreferences');
}

/** Persist preferences to localStorage (client-only; no server PII). */
export function savePrivacyPreferences(
  _partial: Partial<Omit<PrivacyPreferences, 'necessary' | 'schemaVersion'>> & {
    schemaVersion?: number;
  },
): PrivacyPreferences {
  notImplemented('savePrivacyPreferences');
}

/** Acknowledge / dismiss the first-visit privacy notice for the current schema. */
export function acknowledgePrivacyNotice(): PrivacyPreferences {
  notImplemented('acknowledgePrivacyNotice');
}

/**
 * Whether the first-visit notice should show.
 *
 * True when never acknowledged, or when `schemaVersion` bumped past the
 * acknowledged version.
 */
export function shouldShowPrivacyNotice(): boolean {
  notImplemented('shouldShowPrivacyNotice');
}

/**
 * Detect Global Privacy Control from `navigator.globalPrivacyControl` and/or an
 * explicit Sec-GPC signal (E17-16).
 *
 * @param options.navigatorGpc - `navigator.globalPrivacyControl` when available
 * @param options.secGpc - request/header Sec-GPC value (`"1"` ⇒ enabled)
 */
export function detectGlobalPrivacyControl(_options?: {
  navigatorGpc?: boolean | undefined;
  secGpc?: string | null | undefined;
}): boolean {
  notImplemented('detectGlobalPrivacyControl');
}

/**
 * Force sale/sharing and targeted-advertising opt-outs when GPC is on.
 * Does not disable disclosed necessary IndexedDB work history.
 */
export function applyGpcToPreferences(
  _prefs: PrivacyPreferences,
  _gpcEnabled: boolean,
): PrivacyPreferences {
  notImplemented('applyGpcToPreferences');
}

/** Clear privacy preferences from localStorage (site-data wipe / tests). */
export function clearPrivacyPreferences(): void {
  notImplemented('clearPrivacyPreferences');
}
