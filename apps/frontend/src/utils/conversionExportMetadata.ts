/**
 * Convert export metadata sidecar helpers (Phase A / F7.w).
 *
 * Builds optional `*.meta.json` siblings for IWXXM downloads. Never embeds
 * credentials, destination URIs, or auth tokens.
 */

/** Minimal lint log shape for export metadata summaries. */
export interface ConversionMetadataLintLog {
  errors?: string[];
  issues?: Array<{
    severity?: string;
    code?: string | null;
    message?: string | null;
  }>;
}

/** localStorage key for export-metadata toggle + checklist. */
export const CONVERSION_METADATA_PREFS_KEY = 'tac_conversion_metadata_prefs';

export const CONVERSION_METADATA_TOGGLE_LABEL = 'Include conversion metadata';
export const CONVERSION_METADATA_CHECKLIST_HEADING = 'Choose what to include';
export const CONVERSION_METADATA_CHECKLIST_LIBRARIES = 'Library selections';
export const CONVERSION_METADATA_CHECKLIST_YAML_HASHES =
  'Library YAML snapshots (hashes)';
export const CONVERSION_METADATA_CHECKLIST_CONVERT_CONTEXT =
  'Product, IWXXM version, and conversion time';
export const CONVERSION_METADATA_CHECKLIST_OPERATOR = 'Operator identity';
export const CONVERSION_METADATA_CHECKLIST_LINT = 'Lint and validation summary';
export const CONVERSION_METADATA_CHECKLIST_TAC_FINGERPRINT = 'TAC fingerprint';
export const CONVERSION_METADATA_CHECKLIST_MAPPING_BRIDGE = 'Mapping bridge summary';

export const CONVERSION_METADATA_PLACEHOLDER_YAML =
  'Library YAML hash snapshots will be included in a later release.';
export const CONVERSION_METADATA_PLACEHOLDER_LINT =
  'Per-result lint and validation summaries will be included in a later release.';
export const CONVERSION_METADATA_PLACEHOLDER_MAPPING =
  'Mapping bridge match summaries will be included in a later release.';

export const CONVERSION_METADATA_SCHEMA_VERSION = 1 as const;

export type ConversionMetadataChecklistKey =
  | 'libraries'
  | 'libraryYamlHashes'
  | 'convertContext'
  | 'operator'
  | 'lintSummary'
  | 'tacFingerprint'
  | 'mappingBridgeSummary';

export type ConversionMetadataChecklist = Record<
  ConversionMetadataChecklistKey,
  boolean
>;

export interface ConversionMetadataPrefs {
  enabled: boolean;
  checklist: ConversionMetadataChecklist;
}

export interface ConversionMetadataLibraryIds {
  conversionLibraryId: string;
  tacValidationLibraryId: string;
  iwxxmValidationLibraryId: string;
  disseminationLibraryId: string;
  decodingLibraryId: string;
}

export interface BuildConversionMetadataInput {
  tacContent: string;
  convertedAt: number;
  product: string;
  iwxxmVersion: string;
  reportVariant?: string;
  libraries: ConversionMetadataLibraryIds;
  checklist: ConversionMetadataChecklist;
  isGuest: boolean;
  userEmail?: string;
  accessToken?: string;
  conversionLog?: ConversionMetadataLintLog | null;
  generatedAt?: Date;
}

const FORBIDDEN_METADATA_KEYS = new Set([
  'password',
  'token',
  'access_token',
  'accessToken',
  'authorization',
  'credential',
  'credentials',
  'destination_uri',
  'destinationUri',
  'uri',
  'url',
  'dsn',
  'secret',
  'api_key',
  'apiKey',
]);

const FORBIDDEN_VALUE_RE =
  /(?:^|\s)(?:Bearer\s+[A-Za-z0-9._~+/=-]+|postgresql:\/\/|mongodb:\/\/|mysql:\/\/|smtp:\/\/|https?:\/\/[^\s]*(?:password|token|secret)=)/i;

/** Default checklist — all groups on when export metadata is enabled. */
export function defaultConversionMetadataChecklist(): ConversionMetadataChecklist {
  return {
    libraries: true,
    libraryYamlHashes: true,
    convertContext: true,
    operator: true,
    lintSummary: true,
    tacFingerprint: true,
    mappingBridgeSummary: true,
  };
}

/** Default prefs — opt-in off until the operator enables the toggle. */
export function defaultConversionMetadataPrefs(): ConversionMetadataPrefs {
  return {
    enabled: false,
    checklist: defaultConversionMetadataChecklist(),
  };
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function parseChecklist(raw: unknown): ConversionMetadataChecklist {
  const defaults = defaultConversionMetadataChecklist();
  if (!isRecord(raw)) {
    return defaults;
  }
  const next = { ...defaults };
  for (const key of Object.keys(defaults) as ConversionMetadataChecklistKey[]) {
    if (typeof raw[key] === 'boolean') {
      next[key] = raw[key];
    }
  }
  return next;
}

/**
 * Read remembered export-metadata prefs from localStorage.
 */
export function readConversionMetadataPrefs(): ConversionMetadataPrefs {
  try {
    const raw = localStorage.getItem(CONVERSION_METADATA_PREFS_KEY);
    if (!raw) {
      return defaultConversionMetadataPrefs();
    }
    const parsed = JSON.parse(raw) as unknown;
    if (!isRecord(parsed)) {
      return defaultConversionMetadataPrefs();
    }
    return {
      enabled: parsed.enabled === true,
      checklist: parseChecklist(parsed.checklist),
    };
  } catch {
    return defaultConversionMetadataPrefs();
  }
}

/**
 * Persist export-metadata prefs to localStorage.
 *
 * @param prefs - Toggle + checklist selections to remember.
 */
export function writeConversionMetadataPrefs(prefs: ConversionMetadataPrefs): void {
  try {
    localStorage.setItem(CONVERSION_METADATA_PREFS_KEY, JSON.stringify(prefs));
  } catch {
    // localStorage may be unavailable in private mode
  }
}

/**
 * Derive sibling sidecar name for an XML download member.
 *
 * @param xmlFileName - Intended `.xml` filename (e.g. `report.xml`).
 */
export function metaSidecarFileName(xmlFileName: string): string {
  const trimmed = xmlFileName.trim() || 'download.xml';
  const dot = trimmed.lastIndexOf('.');
  if (dot > 0) {
    return `${trimmed.slice(0, dot)}.meta.json`;
  }
  return `${trimmed}.meta.json`;
}

/**
 * Extract JWT `sub` for operator identity without persisting the token.
 *
 * @param accessToken - Bearer JWT from auth storage.
 */
export function jwtSubject(accessToken: string | undefined): string | undefined {
  const token = accessToken?.trim();
  if (!token) {
    return undefined;
  }
  const parts = token.split('.');
  if (parts.length < 2) {
    return undefined;
  }
  try {
    const payload = JSON.parse(
      atob(parts[1]!.replace(/-/g, '+').replace(/_/g, '/')),
    ) as unknown;
    if (!isRecord(payload)) {
      return undefined;
    }
    const sub = payload.sub;
    return typeof sub === 'string' && sub.trim().length > 0 ? sub.trim() : undefined;
  } catch {
    return undefined;
  }
}

/**
 * Normalize TAC for fingerprinting (trim, collapse whitespace, uppercase).
 *
 * @param tac - Raw TAC text.
 */
export function normalizeTacForFingerprint(tac: string): string {
  return tac.trim().replace(/\s+/g, ' ').toUpperCase();
}

/**
 * Deterministic TAC fingerprint (Phase A — client-side; not a security hash).
 *
 * @param tac - Raw TAC text.
 */
export function computeTacFingerprint(tac: string): string {
  const normalized = normalizeTacForFingerprint(tac);
  let hash = 2166136261;
  for (let i = 0; i < normalized.length; i += 1) {
    hash ^= normalized.charCodeAt(i);
    hash = Math.imul(hash, 16777619);
  }
  return `fnv1a32:${(hash >>> 0).toString(16).padStart(8, '0')}`;
}

function placeholderBlock(note: string): Record<string, unknown> {
  return { status: 'placeholder', note };
}

function lintSummaryFromLog(
  log: ConversionMetadataLintLog | null | undefined,
): Record<string, unknown> {
  if (!log) {
    return placeholderBlock(CONVERSION_METADATA_PLACEHOLDER_LINT);
  }
  const issues = log.issues ?? [];
  const errors = log.errors ?? [];
  const warningCount = issues.filter((i) => i.severity === 'warning').length;
  const infoCount = issues.filter((i) => i.severity === 'info').length;
  const errorCount =
    errors.length + issues.filter((i) => i.severity === 'error').length;
  return {
    status: 'available',
    errorCount,
    warningCount,
    infoCount,
    issueCount: issues.length,
  };
}

/**
 * Build export metadata JSON for one converted result.
 *
 * @param input - Conversion context and checklist selections.
 */
export function buildConversionExportMetadata(
  input: BuildConversionMetadataInput,
): Record<string, unknown> {
  const generatedAt = (input.generatedAt ?? new Date()).toISOString();
  const metadata: Record<string, unknown> = {
    schemaVersion: CONVERSION_METADATA_SCHEMA_VERSION,
    generatedAt,
  };

  if (input.checklist.convertContext) {
    metadata.convert = {
      product: input.product,
      iwxxmVersion: input.iwxxmVersion,
      ...(input.reportVariant?.trim()
        ? { reportVariant: input.reportVariant.trim() }
        : {}),
      convertedAt: new Date(input.convertedAt).toISOString(),
    };
  }

  if (input.checklist.libraries) {
    metadata.libraries = { ...input.libraries };
  }

  if (input.checklist.libraryYamlHashes) {
    metadata.libraryYamlHashes = placeholderBlock(CONVERSION_METADATA_PLACEHOLDER_YAML);
  }

  if (input.checklist.operator && !input.isGuest) {
    const email =
      input.userEmail && input.userEmail.trim() !== 'Guest'
        ? input.userEmail.trim()
        : undefined;
    const id = jwtSubject(input.accessToken);
    if (email || id) {
      metadata.operator = {
        ...(id ? { id } : {}),
        ...(email ? { email } : {}),
      };
    }
  }

  if (input.checklist.lintSummary) {
    metadata.lintSummary = lintSummaryFromLog(input.conversionLog);
  }

  if (input.checklist.tacFingerprint) {
    metadata.tacFingerprint = {
      algorithm: 'fnv1a32-normalized-tac',
      value: computeTacFingerprint(input.tacContent),
    };
  }

  if (input.checklist.mappingBridgeSummary) {
    metadata.mappingBridgeSummary = placeholderBlock(
      CONVERSION_METADATA_PLACEHOLDER_MAPPING,
    );
  }

  return sanitizeMetadataForExport(metadata);
}

/**
 * Serialize metadata for download (pretty JSON).
 *
 * @param metadata - Sanitized metadata object.
 */
export function serializeConversionMetadata(metadata: Record<string, unknown>): string {
  return `${JSON.stringify(metadata, null, 2)}\n`;
}

/**
 * Fail-closed scrub for secret-like keys/values before writing sidecars.
 *
 * @param value - Metadata object tree.
 */
export function sanitizeMetadataForExport(
  value: Record<string, unknown>,
): Record<string, unknown> {
  const out: Record<string, unknown> = {};
  for (const [key, child] of Object.entries(value)) {
    const lowered = key.toLowerCase();
    if (FORBIDDEN_METADATA_KEYS.has(lowered)) {
      continue;
    }
    out[key] = sanitizeMetadataNode(child);
  }
  return out;
}

function sanitizeMetadataNode(value: unknown): unknown {
  if (typeof value === 'string') {
    return FORBIDDEN_VALUE_RE.test(value) ? '[redacted]' : value;
  }
  if (Array.isArray(value)) {
    return value.map((item) => sanitizeMetadataNode(item));
  }
  if (isRecord(value)) {
    return sanitizeMetadataForExport(value);
  }
  return value;
}

/**
 * Whether metadata export is active for downloads.
 *
 * @param prefs - Stored toggle + checklist.
 */
export function isConversionMetadataExportEnabled(
  prefs: ConversionMetadataPrefs,
): boolean {
  return prefs.enabled;
}
