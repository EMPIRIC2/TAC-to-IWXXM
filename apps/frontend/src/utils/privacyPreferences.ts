/**
 * Privacy preference store (F22 / ADR-031 / E17-7/16/17).
 *
 * Preferences live in `localStorage`. Work sessions stay in IndexedDB.
 * GPC detect/apply (E17-16) is completed in T6.3.
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

export type PrivacyPreferencesPatch = Partial<
  Omit<PrivacyPreferences, 'necessary' | 'schemaVersion'>
> & {
  schemaVersion?: number;
};

function notImplemented(op: string): never {
  throw new Error(`privacyPreferences.${op}: not implemented (T6.3)`);
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
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

function normalizePrivacyPreferences(input: unknown): PrivacyPreferences {
  const base = defaultPrivacyPreferences();
  if (!isRecord(input)) {
    return base;
  }
  return {
    schemaVersion:
      typeof input.schemaVersion === 'number'
        ? input.schemaVersion
        : base.schemaVersion,
    necessary: true,
    analytics: Boolean(input.analytics),
    marketing: Boolean(input.marketing),
    saleOrSharingOptOut: Boolean(input.saleOrSharingOptOut),
    targetedAdvertisingOptOut: Boolean(input.targetedAdvertisingOptOut),
    noticeAcknowledgedAt:
      typeof input.noticeAcknowledgedAt === 'string'
        ? input.noticeAcknowledgedAt
        : null,
    noticeSchemaVersion:
      typeof input.noticeSchemaVersion === 'number' ? input.noticeSchemaVersion : null,
  };
}

function readStoredPreferences(): PrivacyPreferences {
  if (typeof localStorage === 'undefined') {
    return defaultPrivacyPreferences();
  }
  try {
    const raw = localStorage.getItem(PRIVACY_PREFS_STORAGE_KEY);
    if (!raw) {
      return defaultPrivacyPreferences();
    }
    return normalizePrivacyPreferences(JSON.parse(raw) as unknown);
  } catch {
    return defaultPrivacyPreferences();
  }
}

function writeStoredPreferences(prefs: PrivacyPreferences): void {
  if (typeof localStorage === 'undefined') {
    return;
  }
  localStorage.setItem(PRIVACY_PREFS_STORAGE_KEY, JSON.stringify(prefs));
}

/** Load preferences from localStorage (GPC overrides applied in T6.3). */
export function loadPrivacyPreferences(): PrivacyPreferences {
  return readStoredPreferences();
}

/** Persist preferences to localStorage (client-only; no server PII). */
export function savePrivacyPreferences(
  partial: PrivacyPreferencesPatch,
): PrivacyPreferences {
  const current = readStoredPreferences();
  const next = normalizePrivacyPreferences({
    ...current,
    ...partial,
    necessary: true,
  });
  writeStoredPreferences(next);
  return next;
}

/** Acknowledge / dismiss the first-visit privacy notice for the current schema. */
export function acknowledgePrivacyNotice(): PrivacyPreferences {
  const current = readStoredPreferences();
  return savePrivacyPreferences({
    noticeAcknowledgedAt: new Date().toISOString(),
    noticeSchemaVersion: current.schemaVersion,
  });
}

/**
 * Whether the first-visit notice should show.
 *
 * True when never acknowledged, or when `schemaVersion` bumped past the
 * acknowledged version.
 */
export function shouldShowPrivacyNotice(): boolean {
  const prefs = readStoredPreferences();
  if (prefs.noticeAcknowledgedAt == null || prefs.noticeSchemaVersion == null) {
    return true;
  }
  return prefs.noticeSchemaVersion < prefs.schemaVersion;
}

/**
 * Detect Global Privacy Control from `navigator.globalPrivacyControl` and/or an
 * explicit Sec-GPC signal (E17-16). Implemented in T6.3.
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
 * Implemented in T6.3.
 */
export function applyGpcToPreferences(
  _prefs: PrivacyPreferences,
  _gpcEnabled: boolean,
): PrivacyPreferences {
  notImplemented('applyGpcToPreferences');
}

/** Clear privacy preferences from localStorage (site-data wipe / tests). */
export function clearPrivacyPreferences(): void {
  if (typeof localStorage === 'undefined') {
    return;
  }
  localStorage.removeItem(PRIVACY_PREFS_STORAGE_KEY);
}
