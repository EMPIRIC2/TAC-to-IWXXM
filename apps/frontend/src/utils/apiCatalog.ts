/* eslint-disable complexity */
/**
 * Ingest, rule catalog, code-name dictionary, and selection-option clients.
 */
import { apiUrl } from './apiBase';
import type {
  CodeNameDictionaryFacets,
  CodeNameDictionaryItem,
  MassIngestResponse,
  SelectionOptionKind,
} from '@/models/api';
import { DEFAULT_IWXXM_VERSION } from './iwxxmVersions';
import { wireSemanticProfile } from './semanticProfile';
import { EndpointNotImplementedError, apiErrorMessage, withTimeout } from './apiErrors';

export { EndpointNotImplementedError } from './apiErrors';

/**
 * Ingest / validate IWXXM COLLECT (or gzipped COLLECT).
 *
 * **Endpoint**: POST /api/v1/ingest-collect (placeholder until implemented).
 * @example
 * const _ = true;
 */
/**
 * ingestCollect.
 */
export async function ingestCollect(params: {
  manualText?: string;
  files?: File[];
  profile?: string;
  iwxxmVersion?: string;
  accessToken?: string;
  signal?: AbortSignal;
}): Promise<{ message: string; status: string }> {
  const formData = new FormData();
  if (params.manualText?.trim()) {
    formData.append('manual_text', params.manualText.trim());
  }
  if (params.files?.length) {
    params.files.forEach((file) => formData.append('files', file));
  }
  formData.append('semantic_profile', wireSemanticProfile(params.profile));
  formData.append('iwxxm_version', params.iwxxmVersion || DEFAULT_IWXXM_VERSION);

  const response = await withTimeout(
    fetch(apiUrl('/ingest-collect'), {
      method: 'POST',
      body: formData,
      signal: params.signal,
    }),
    30000,
  );

  if (response.status === 501) {
    const body = await response.json().catch(() => ({}));
    throw new EndpointNotImplementedError(
      body?.detail?.message ||
        body?.message ||
        'COLLECT / FTBP ingest is not implemented yet (placeholder).',
      501,
      body?.detail?.code || 'not_implemented',
    );
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({
      message: `COLLECT ingest failed: ${response.statusText}`,
    }));
    throw new Error(
      error.detail?.message || error.message || `HTTP ${response.status}`,
    );
  }

  return (await response.json()) as { message: string; status: string };
}

/**
 * Lint TAC via tac-validate (parse gate + shared rules — not Schematron).
 *
 * **Endpoint**: POST /api/v1/lint-tac
 *
 * @param params.manualText - TAC text
 * @param params.product - Optional product hint
 * @param params.signal - AbortSignal for live workbench cancellation
 * @returns Lint report with optional start/end spans
 * @example
 * const _ = true;
 */

/**
 * Auth-gated mass file/folder ingest with server-side caps and sniff guards.
 *
 * **Endpoint**: POST /api/v1/ingest/mass
 *
 * Client expands folder picks to files before upload; zip archives may be sent
 * as-is for server unpack ([Corpus: product §F33], [Corpus: api]).
 *
 * @param params.files - Multipart files and/or ``.zip`` archives
 * @param params.accessToken - Required Bearer JWT
 * @param params.signal - Optional abort signal
 * @returns Per-file accept/reject list and summary counts
 * @example
 * const _ = true;
 */
/**
 * massIngestFiles.
 */
export async function massIngestFiles(params: {
  files: File[];
  accessToken: string;
  signal?: AbortSignal;
}): Promise<MassIngestResponse> {
  if (!params.accessToken.trim()) {
    throw new Error('Sign in required for mass ingest');
  }
  if (!params.files.length) {
    throw new Error('At least one file is required');
  }

  const formData = new FormData();
  for (const file of params.files) {
    formData.append('files', file, file.name);
  }

  const response = await withTimeout(
    fetch(apiUrl('/ingest/mass'), {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${params.accessToken}`,
      },
      body: formData,
      signal: params.signal,
    }),
    120000,
  );

  if (!response.ok) {
    const error = await response.json().catch(() => ({
      message: `Mass ingest failed: ${response.statusText}`,
    }));
    throw new Error(apiErrorMessage(error, `HTTP ${response.status}`));
  }

  return (await response.json()) as MassIngestResponse;
}

/**
 * Fetch a package-owned trust catalog by family (ADR-044).
 *
 * **Endpoint**: GET /api/v1/rule-catalogs
 * @example
 * const _ = true;
 */

/**
 * Fetch a package-owned trust catalog by family (ADR-044).
 *
 * **Endpoint**: GET /api/v1/rule-catalogs
 * @example
 * const _ = true;
 */
/**
 * fetchRuleCatalog.
 */
export async function fetchRuleCatalog(params: {
  family: 'tac' | 'iwxxm' | 'conversion' | 'dissemination' | 'decoding';
  product?: string;
  signal?: AbortSignal;
}): Promise<{
  family: string;
  items: Array<{
    id: string;
    title: string;
    summary: string;
    severity?: string | null;
    tags?: string[];
    issue_type?: string | null;
    source_url?: string | null;
    source_attribution?: string | null;
    source_access?: string | null;
    source_locator?: string | null;
    conform_note?: string | null;
  }>;
}> {
  const query = new URLSearchParams();
  query.set('family', params.family);
  if (params.product?.trim()) {
    query.set('product', params.product.trim().toLowerCase());
  }
  const response = await fetch(apiUrl(`/rule-catalogs?${query.toString()}`), {
    method: 'GET',
    signal: params.signal,
  });
  if (!response.ok) {
    throw new Error(`rule-catalogs failed: ${response.status}`);
  }
  return response.json() as Promise<{
    family: string;
    items: Array<{
      id: string;
      title: string;
      summary: string;
      severity?: string | null;
      tags?: string[];
      issue_type?: string | null;
      source_url?: string | null;
      source_attribution?: string | null;
      source_access?: string | null;
      source_locator?: string | null;
      conform_note?: string | null;
    }>;
  }>;
}

/**
 * One code-name dictionary row from GET /code-name-dictionary.
 * @example
 * const _ = true;
 */

/**
 * Fetch the tagged Decoding code-name dictionary.
 *
 * **Endpoint**: GET /api/v1/code-name-dictionary
 * @example
 * const _ = true;
 */
/**
 * fetchCodeNameDictionary.
 */
export async function fetchCodeNameDictionary(
  params: {
    q?: string;
    product?: string;
    country?: string;
    wmo_amendment?: string;
    signal?: AbortSignal;
  } = {},
): Promise<{
  items: CodeNameDictionaryItem[];
  facets: CodeNameDictionaryFacets;
}> {
  const query = new URLSearchParams();
  if (params.q?.trim()) {
    query.set('q', params.q.trim());
  }
  if (params.product?.trim()) {
    query.set('product', params.product.trim());
  }
  if (params.country?.trim()) {
    query.set('country', params.country.trim());
  }
  if (params.wmo_amendment?.trim()) {
    query.set('wmo_amendment', params.wmo_amendment.trim());
  }
  const suffix = query.toString() ? `?${query.toString()}` : '';
  const response = await fetch(apiUrl(`/code-name-dictionary${suffix}`), {
    method: 'GET',
    signal: params.signal,
  });
  if (!response.ok) {
    throw new Error(`code-name-dictionary failed: ${response.status}`);
  }
  return response.json() as Promise<{
    items: CodeNameDictionaryItem[];
    facets: CodeNameDictionaryFacets;
  }>;
}

/**
 * Selection-option kinds for Convert (four) + Send drawer (dissemination).
 * @example
 * const _ = true;
 */

/**
 * Fetch deployed selection options for dropdowns (ADR-044 / TP-YCL-01).
 *
 * **Endpoint**: GET /api/v1/selection-options
 * @example
 * const _ = true;
 */
/**
 * fetchSelectionOptions.
 */
export async function fetchSelectionOptions(params: {
  kind: SelectionOptionKind;
  signal?: AbortSignal;
}): Promise<{ kind: string; options: Array<{ id: string; label: string }> }> {
  const query = new URLSearchParams({ kind: params.kind });
  const response = await fetch(apiUrl(`/selection-options?${query.toString()}`), {
    method: 'GET',
    signal: params.signal,
  });
  if (!response.ok) {
    throw new Error(`selection-options failed: ${response.status}`);
  }
  return response.json() as Promise<{
    kind: string;
    options: Array<{ id: string; label: string }>;
  }>;
}
