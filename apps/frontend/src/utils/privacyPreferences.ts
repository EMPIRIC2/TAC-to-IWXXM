/**
 * Privacy preference store (F22 / ADR-031 / E17-7/16/17; deepened F31 / TC-F31-005).
 *
 * Preferences live in `localStorage`. Guest work-history IndexedDB is **gateable**.
 * GPC detect/apply (E17-16) is completed in T6.3.
 */

/** localStorage key for versioned privacy preferences (E17-17). */
export const PRIVACY_PREFS_STORAGE_KEY = 'tac_privacy_preferences' as const;

/** Bump when preference schema changes — re-shows first-visit notice (UJ-033 / F31). */
export const PRIVACY_SCHEMA_VERSION = 2 as const;

/**
 * Solution A preference schema (F22) + F31 guest work-history gate.
 *
 * `necessary` is always on. Non-essential categories default false.
 */
export interface PrivacyPreferences {
  schemaVersion: number;
  /** Always true — required client storage for app function. */
  necessary: true;
  /** Non-essential analytics; default false; unused in Solution A v1. */
  analytics: boolean;
  /** Non-essential marketing; default false; unused in Solution A v1. */
  marketing: boolean;
  /**
   * Guest work-history IndexedDB persistence (F31 / TC-F31-005).
   * When false, callers must not write work-session rows to IndexedDB.
   */
  workHistoryLocal: boolean;
  /** Sale/sharing opt-out — forced when GPC is detected (E17-16). */
  saleOrSharingOptOut: boolean;
  /** Targeted-advertising opt-out — forced when GPC is detected (E17-16). */
  targetedAdvertisingOptOut: boolean;
  /** ISO timestamp when the first-visit notice was acknowledged; null if never. */
  noticeAcknowledgedAt: string | null;
  /** Schema version for which the notice was acknowledged. */
  noticeSchemaVersion: number | null;
}

/** Client storage inventory disclosed in Privacy settings (F22 / UJ-033 / UJ-047). */
export interface StorageInventoryItem {
  kind: 'indexedDB' | 'localStorage' | 'sessionStorage' | 'cookie' | 'cdn';
  purpose: string;
  /** When true, category is required for app function (cannot be turned off). */
  necessary: boolean;
}

export const STORAGE_INVENTORY: readonly StorageInventoryItem[] = [
  {
    kind: 'indexedDB',
    purpose: 'Guest work history and converter sessions (F5 / F7.h / F31)',
    necessary: false,
  },
  {
    kind: 'localStorage',
    purpose: 'Privacy preferences and converter UI preferences',
    necessary: true,
  },
  {
    kind: 'cookie',
    purpose: 'Supabase Auth session cookies when signed in (F31 / UJ-047)',
    necessary: false,
  },
] as const;

export type PrivacyPreferencesPatch = Partial<
  Omit<PrivacyPreferences, 'necessary' | 'schemaVersion'>
> & {
  schemaVersion?: number;
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

/** Default Solution A preferences (non-essential off; work history on for guests). */
export function defaultPrivacyPreferences(): PrivacyPreferences {
  return {
    schemaVersion: PRIVACY_SCHEMA_VERSION,
    necessary: true,
    analytics: false,
    marketing: false,
    workHistoryLocal: true,
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
    workHistoryLocal:
      typeof input.workHistoryLocal === 'boolean'
        ? input.workHistoryLocal
        : base.workHistoryLocal,
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

/** Load preferences from localStorage; apply GPC opt-out overrides (E17-16). */
export function loadPrivacyPreferences(): PrivacyPreferences {
  const prefs = readStoredPreferences();
  const gpcEnabled = detectGlobalPrivacyControl({
    navigatorGpc: readNavigatorGlobalPrivacyControl(),
  });
  return applyGpcToPreferences(prefs, gpcEnabled);
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
  const gpcEnabled = detectGlobalPrivacyControl({
    navigatorGpc: readNavigatorGlobalPrivacyControl(),
  });
  return applyGpcToPreferences(next, gpcEnabled);
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
 * explicit Sec-GPC signal (E17-16).
 *
 * @param options.navigatorGpc - `navigator.globalPrivacyControl` when available
 * @param options.secGpc - request/header Sec-GPC value (`"1"` ⇒ enabled)
 */
export function detectGlobalPrivacyControl(options?: {
  navigatorGpc?: boolean | undefined;
  secGpc?: string | null | undefined;
}): boolean {
  if (options?.navigatorGpc === true) {
    return true;
  }
  if (options?.secGpc === '1') {
    return true;
  }
  if (options !== undefined) {
    return false;
  }
  return readNavigatorGlobalPrivacyControl() === true;
}

function readNavigatorGlobalPrivacyControl(): boolean | undefined {
  if (typeof navigator === 'undefined') {
    return undefined;
  }
  const gpc = (navigator as Navigator & { globalPrivacyControl?: boolean })
    .globalPrivacyControl;
  return typeof gpc === 'boolean' ? gpc : undefined;
}

/**
 * Force sale/sharing and targeted-advertising opt-outs when GPC is on.
 * Does not force-enable guest work-history IndexedDB (TC-F31-005).
 */
export function applyGpcToPreferences(
  prefs: PrivacyPreferences,
  gpcEnabled: boolean,
): PrivacyPreferences {
  if (!gpcEnabled) {
    return {
      ...prefs,
      necessary: true,
    };
  }
  return {
    ...prefs,
    necessary: true,
    analytics: false,
    marketing: false,
    saleOrSharingOptOut: true,
    targetedAdvertisingOptOut: true,
  };
}

/**
 * Whether guest work-history may be written to IndexedDB (TC-F31-005 / UJ-047).
 *
 * Parameters
 * ----------
 * prefs :
 *     Loaded privacy preferences (optional — loads from storage when omitted).
 *
 * Returns
 * -------
 * boolean
 *     ``false`` when the user declined local work-history persistence.
 */
export function canPersistWorkHistoryLocal(prefs?: PrivacyPreferences): boolean {
  const resolved = prefs ?? loadPrivacyPreferences();
  return resolved.workHistoryLocal === true;
}

/** Clear privacy preferences from localStorage (site-data wipe / tests). */
export function clearPrivacyPreferences(): void {
  if (typeof localStorage === 'undefined') {
    return;
  }
  localStorage.removeItem(PRIVACY_PREFS_STORAGE_KEY);
}
