/**
 * Library YAML assets and conversion template clients.
 */
import { apiUrl } from './apiBase';
import type {
  ConversionTemplateListResponse,
  ConversionTemplateOut,
  ConversionTemplatePreviewResponse,
  ConversionTemplateSlot,
  LibraryAssetKind,
  LibraryAssetListResponse,
  LibraryAssetOut,
  LibraryYamlValidateResponse,
} from '@/models/conversionLibraries';

/**
 * Function `authHeaders`.
 */
function authHeaders(accessToken: string): HeadersInit {
  return {
    Authorization: `Bearer ${accessToken}`,
    'Content-Type': 'application/json',
  };
}

/**
 * Function `parseJson`.
 */
async function parseJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    const detail =
      typeof error.detail === 'string' ? error.detail : response.statusText;
    throw new Error(detail || `HTTP ${response.status}`);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}

/**
 * Catalog variant row for profile-scoped METAR-family roots.
 * @example
 * const _ = true;
 */

/**
 * List first-party and owner custom library assets.
 *
 * @param accessToken - Bearer JWT
 * @param kind - Optional kind filter
 * @example
 * const _ = true;
 */
export async function listLibraryAssets(
  accessToken: string,
  kind?: LibraryAssetKind,
): Promise<LibraryAssetListResponse> {
  const query = kind ? `?kind=${encodeURIComponent(kind)}` : '';
  const response = await fetch(apiUrl(`/api/v1/profiles/library-assets${query}`), {
    headers: authHeaders(accessToken),
  });
  return parseJson(response);
}

/**
 * Validate library YAML + regex without persisting.
 *
 * @param accessToken - Bearer JWT
 * @param body - YAML + expected kind
 * @example
 * const _ = true;
 */
export async function validateLibraryYaml(
  accessToken: string,
  body: {
    yamlBody: string;
    kind: LibraryAssetKind;
    lifecycle?: 'draft' | 'activated';
  },
): Promise<LibraryYamlValidateResponse> {
  const response = await fetch(
    apiUrl('/api/v1/profiles/library-assets/validate-yaml'),
    {
      method: 'POST',
      headers: authHeaders(accessToken),
      body: JSON.stringify(body),
    },
  );
  return parseJson(response);
}

/**
 * Create a custom library asset (draft or activated).
 *
 * @param accessToken - Bearer JWT
 * @param body - Create payload
 * @example
 * const _ = true;
 */
export async function createLibraryAsset(
  accessToken: string,
  body: {
    slug: string;
    name: string;
    kind: LibraryAssetKind;
    engineProfileId: string;
    attachedNationalLine: string;
    body?: Record<string, unknown>;
    forkOf?: string;
    shared?: boolean;
    yamlBody?: string;
    status?: 'draft' | 'activated';
    schemaVersion?: number;
  },
): Promise<LibraryAssetOut> {
  const response = await fetch(apiUrl('/api/v1/profiles/library-assets'), {
    method: 'POST',
    headers: authHeaders(accessToken),
    body: JSON.stringify(body),
  });
  return parseJson(response);
}

/**
 * Patch an owned custom library asset.
 *
 * @param accessToken - Bearer JWT
 * @param assetId - Custom asset UUID
 * @param body - Partial update
 * @example
 * const _ = true;
 */
export async function updateLibraryAsset(
  accessToken: string,
  assetId: string,
  body: {
    name?: string;
    yamlBody?: string;
    status?: 'draft' | 'activated';
    body?: Record<string, unknown>;
  },
): Promise<LibraryAssetOut> {
  const response = await fetch(
    apiUrl(`/api/v1/profiles/library-assets/${encodeURIComponent(assetId)}`),
    {
      method: 'PATCH',
      headers: authHeaders(accessToken),
      body: JSON.stringify(body),
    },
  );
  return parseJson(response);
}

/**
 * List first-party and custom conversion templates.
 *
 * @param accessToken - Bearer JWT
 * @example
 * const _ = true;
 */
export async function listConversionTemplates(
  accessToken: string,
): Promise<ConversionTemplateListResponse> {
  const response = await fetch(apiUrl('/api/v1/profiles/conversion-templates'), {
    headers: authHeaders(accessToken),
  });
  return parseJson(response);
}

/**
 * Preview TAC group mapping for a conversion template.
 *
 * @param accessToken - Bearer JWT
 * @param body - Preview request
 * @example
 * const _ = true;
 */
export async function previewConversionTemplate(
  accessToken: string,
  body: {
    templateId: string;
    focusGroup: string;
    fullTac?: string;
    slots?: ConversionTemplateSlot[];
    iwxxmBlock?: string;
  },
): Promise<ConversionTemplatePreviewResponse> {
  const response = await fetch(
    apiUrl('/api/v1/profiles/conversion-templates/preview'),
    {
      method: 'POST',
      headers: authHeaders(accessToken),
      body: JSON.stringify(body),
    },
  );
  return parseJson(response);
}

/**
 * Create a custom conversion template (often a fork).
 *
 * @param accessToken - Bearer JWT
 * @param body - Create payload
 * @example
 * const _ = true;
 */
export async function createConversionTemplate(
  accessToken: string,
  body: {
    slug: string;
    name: string;
    iwxxmBlock: string;
    slots: ConversionTemplateSlot[];
    sample?: string;
    comments?: string;
    forkOf?: string;
    shared?: boolean;
  },
): Promise<ConversionTemplateOut> {
  const response = await fetch(apiUrl('/api/v1/profiles/conversion-templates'), {
    method: 'POST',
    headers: authHeaders(accessToken),
    body: JSON.stringify(body),
  });
  return parseJson(response);
}

/**
 * Update an owned custom conversion template (fails closed for first-party ids).
 *
 * @param accessToken - Bearer JWT
 * @param templateId - Custom template id
 * @param body - Partial update (camelCase aliases)
 * @example
 * const _ = true;
 */
export async function updateConversionTemplate(
  accessToken: string,
  templateId: string,
  body: {
    slug?: string;
    name?: string;
    iwxxmBlock?: string;
    slots?: ConversionTemplateSlot[];
    sample?: string;
    comments?: string | null;
    shared?: boolean;
  },
): Promise<ConversionTemplateOut> {
  const response = await fetch(
    apiUrl(`/api/v1/profiles/conversion-templates/${encodeURIComponent(templateId)}`),
    {
      method: 'PATCH',
      headers: authHeaders(accessToken),
      body: JSON.stringify(body),
    },
  );
  return parseJson(response);
}
