/**
 * Share-bundle helpers for ConversionProfile assets.
 *
 * Bundles intentionally include only non-secret, importable fields so operators can
 * exchange rule packs and overlays without exposing ownership metadata or signatures.
 */

import type {
  OverlayCreateBody,
  OverlayOut,
  RulePackCreateBody,
  RulePackOut,
} from './conversionProfilesApi';

export const CONVERSION_PROFILE_SHARE_BUNDLE_VERSION = 1;

/** Keys that must never appear in a shareable overlay body (or nested objects). */
const FORBIDDEN_SECRET_KEYS = new Set([
  'password',
  'passwd',
  'secret',
  'api_key',
  'apikey',
  'access_token',
  'refresh_token',
  'authorization',
  'bearer',
  'private_key',
  'service_role',
  'supabase_service_role_key',
  'connection_string',
  'dsn',
]);

export interface ConversionProfileShareBundle {
  schemaVersion: number;
  rulePacks: RulePackCreateBody[];
  overlays: OverlayCreateBody[];
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

/**
 * Reject payloads that embed credential-like keys.
 *
 * @param value - Arbitrary JSON fragment
 * @param path - Dot path for error messages
 */
export function assertNoShareSecrets(value: unknown, path = 'root'): void {
  if (Array.isArray(value)) {
    value.forEach((item, index) => {
      assertNoShareSecrets(item, `${path}[${index}]`);
    });
    return;
  }
  if (!isRecord(value)) {
    return;
  }
  for (const [key, child] of Object.entries(value)) {
    const normalized = key.toLowerCase().replace(/-/g, '_');
    if (FORBIDDEN_SECRET_KEYS.has(normalized)) {
      throw new Error(`Share bundle must not include secret field: ${path}.${key}`);
    }
    assertNoShareSecrets(child, `${path}.${key}`);
  }
}

function asString(value: unknown, field: string): string {
  if (typeof value !== 'string' || !value.trim()) {
    throw new Error(`Share bundle field must be a non-empty string: ${field}`);
  }
  return value;
}

function asOptionalString(value: unknown, field: string): string | undefined {
  if (value === undefined) {
    return undefined;
  }
  if (typeof value !== 'string') {
    throw new Error(`Share bundle field must be a string when present: ${field}`);
  }
  return value;
}

function toRulePackCreateBody(value: unknown): RulePackCreateBody {
  if (!isRecord(value)) {
    throw new Error('Share bundle rule packs must be objects');
  }
  return {
    slug: asString(value.slug, 'rulePacks[].slug'),
    profile: asString(value.profile, 'rulePacks[].profile'),
    product: asString(value.product, 'rulePacks[].product'),
    stage: asString(value.stage, 'rulePacks[].stage'),
    severity: asString(value.severity, 'rulePacks[].severity'),
    when: asOptionalString(value.when, 'rulePacks[].when'),
    message: asOptionalString(value.message, 'rulePacks[].message'),
    standardReference: asOptionalString(
      value.standardReference,
      'rulePacks[].standardReference',
    ),
  };
}

function toOverlayCreateBody(value: unknown): OverlayCreateBody {
  if (!isRecord(value)) {
    throw new Error('Share bundle overlays must be objects');
  }
  const body = value.body;
  if (body !== undefined && !isRecord(body)) {
    throw new Error('Share bundle overlay body must be an object');
  }
  if (body !== undefined) {
    assertNoShareSecrets(body, 'overlays[].body');
  }
  const shared = value.shared;
  if (shared !== undefined && typeof shared !== 'boolean') {
    throw new Error('Share bundle overlay shared flag must be boolean when present');
  }
  return {
    slug: asString(value.slug, 'overlays[].slug'),
    baseProfileId: asString(value.baseProfileId, 'overlays[].baseProfileId'),
    body: (body as Record<string, unknown> | undefined) ?? {},
    shared: shared as boolean | undefined,
  };
}

/**
 * Build a shareable bundle from persisted ConversionProfile assets.
 *
 * @param input.rulePacks - Saved rule packs to export in import-ready form.
 * @param input.overlays - Saved overlays to export in import-ready form.
 * @returns A non-secret bundle payload suitable for download or copy/share flows.
 */
export function createConversionProfileShareBundle(input: {
  rulePacks: readonly RulePackOut[];
  overlays: readonly OverlayOut[];
}): ConversionProfileShareBundle {
  const bundle: ConversionProfileShareBundle = {
    schemaVersion: CONVERSION_PROFILE_SHARE_BUNDLE_VERSION,
    rulePacks: input.rulePacks.map((pack) => ({
      slug: pack.slug,
      profile: pack.profile,
      product: pack.product,
      stage: pack.stage,
      severity: pack.severity,
      when: pack.when,
      message: pack.message,
      standardReference: pack.standardReference,
    })),
    overlays: input.overlays.map((overlay) => {
      assertNoShareSecrets(overlay.body, 'overlays[].body');
      return {
        slug: overlay.slug,
        baseProfileId: overlay.baseProfileId,
        body: overlay.body,
        shared: overlay.shared,
      };
    }),
  };
  return bundle;
}

/**
 * Parse a downloaded or pasted ConversionProfile share bundle.
 *
 * @param rawText - Raw JSON bundle text provided by the operator.
 * @returns A validated bundle payload ready for import flows.
 * @throws Error If the payload is not valid JSON or does not match the supported bundle schema.
 */
export function parseConversionProfileShareBundle(
  rawText: string,
): ConversionProfileShareBundle {
  let parsed: unknown;
  try {
    parsed = JSON.parse(rawText);
  } catch {
    throw new Error('Share bundle must be valid JSON');
  }
  if (!isRecord(parsed)) {
    throw new Error('Share bundle root must be an object');
  }
  if (parsed.schemaVersion !== CONVERSION_PROFILE_SHARE_BUNDLE_VERSION) {
    throw new Error(
      `Unsupported share bundle schemaVersion: ${String(parsed.schemaVersion ?? '') || 'missing'}`,
    );
  }
  if (!Array.isArray(parsed.rulePacks)) {
    throw new Error('Share bundle rulePacks must be an array');
  }
  if (!Array.isArray(parsed.overlays)) {
    throw new Error('Share bundle overlays must be an array');
  }
  return {
    schemaVersion: CONVERSION_PROFILE_SHARE_BUNDLE_VERSION,
    rulePacks: parsed.rulePacks.map(toRulePackCreateBody),
    overlays: parsed.overlays.map(toOverlayCreateBody),
  };
}
