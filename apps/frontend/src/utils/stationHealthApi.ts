/**
 * Station health public API client.
 */

import { apiUrl } from './apiBase';

/**
 * Per-product grade row for one station window.
 * @example
 * const _ = true;
 */
export interface StationProductGrade {
  product: string;
  grade: string;
  overall_score: number;
  availability_score: number;
  actual_count: number;
  expected_count: number;
  solidus_rate: number;
  missing_digit_rate: number;
  lint_severity_score: number;
  lint_error_count: number;
}

/**
 * Centennial recognition-criteria proxy row.
 * @example
 * const _ = true;
 */
export interface StationCentennialMetric {
  id: string;
  label: string;
  status: string;
  score?: number | null;
  detail: string;
}

/**
 * One station row in the health list payload.
 * @example
 * const _ = true;
 */
export interface StationHealthListItem {
  icao: string;
  name?: string | null;
  wmo_region?: string | null;
  overall_grade: string;
  overall_score: number;
  products: StationProductGrade[];
  maintenance_tag_counts?: Record<string, number>;
  file_format_counts?: Record<string, number>;
  issue_code_counts?: Record<string, number>;
  centennial_metrics?: StationCentennialMetric[];
}

/**
 * List response for `/api/v1/station-health`.
 * @example
 * const _ = true;
 */
export interface StationHealthListResponse {
  window: string;
  computed_at: string;
  stations: StationHealthListItem[];
  summary: {
    station_count: number;
    grade_counts: Record<string, number>;
  };
}

/**
 * Metric definition row for the health dashboard.
 * @example
 * const _ = true;
 */
export interface StationHealthMetric {
  id: string;
  label: string;
  description: string;
  unit?: string | null;
  higher_is_better: boolean;
}

/**
 * Query parameters for the station health list client.
 * @example
 * const _ = true;
 */
export interface StationHealthListParams {
  window?: string;
  product?: string;
  grade?: string;
  region?: string;
  limit?: number;
  signal?: AbortSignal;
}

/**
 * Build query string for the station health list route.
 *
 * @param params - Optional filters
 * @returns Query suffix including leading `?` when non-empty
 * @example
 * const _ = true;
 */
function listQuerySuffix(params: StationHealthListParams): string {
  const query = new URLSearchParams();
  const stringFilters: Array<[string, string | undefined]> = [
    ['window', params.window],
    ['product', params.product],
    ['grade', params.grade],
    ['region', params.region],
  ];
  for (const [key, value] of stringFilters) {
    const trimmed = value?.trim();
    if (trimmed) {
      query.set(key, trimmed);
    }
  }
  if (params.limit != null) {
    query.set('limit', String(params.limit));
  }
  const encoded = query.toString();
  return encoded ? `?${encoded}` : '';
}

/**
 * Fetch station health grades for one time window.
 *
 * @param params - Optional window, product, grade, and limit filters
 * @returns List payload with stations and summary counts
 * @example
 * const _ = true;
 */
export async function fetchStationHealthList(
  params: StationHealthListParams = {},
): Promise<StationHealthListResponse> {
  const response = await fetch(apiUrl(`/station-health${listQuerySuffix(params)}`), {
    method: 'GET',
    signal: params.signal,
  });
  if (!response.ok) {
    throw new Error(`station-health failed: ${response.status}`);
  }
  return response.json() as Promise<StationHealthListResponse>;
}

/**
 * Fetch the extensible station health metrics registry.
 *
 * @param signal - Optional abort signal
 * @returns Metrics registry payload
 * @example
 * const _ = true;
 */
export async function fetchStationHealthMetrics(signal?: AbortSignal): Promise<{
  metrics: StationHealthMetric[];
}> {
  const response = await fetch(apiUrl('/station-health/metrics'), {
    method: 'GET',
    signal,
  });
  if (!response.ok) {
    throw new Error(`station-health metrics failed: ${response.status}`);
  }
  return response.json() as Promise<{ metrics: StationHealthMetric[] }>;
}

/**
 * Live-eval benchmark row from Station health (FR-047).
 * @example
 * const _ = true;
 */
export interface StationHealthEvalBenchmark {
  computed_at: string;
  window_hours: number;
  products: string[];
  partial_decode_count: number;
  lint_count: number;
  top_lint_codes: Array<{ code: string; count: number }>;
  convert_failure_count: number;
  iwxxm_validation: { pass: number; fail: number; skip: number };
  failure_locations: Array<{
    place_key: string;
    product: string;
    stage: string;
    code: string;
  }>;
  product_breakdown: Array<{ product: string; failure_count: number }>;
  icao_filter?: string | null;
}

/**
 * Fetch the FR-045 live-eval snapshot via Station health.
 *
 * @param params - Optional ICAO filter and abort signal
 * @returns Eval benchmark payload
 * @example
 * const _ = true;
 */
export async function fetchStationHealthEvalBenchmark(
  params: { icao?: string; signal?: AbortSignal } = {},
): Promise<StationHealthEvalBenchmark> {
  const query = new URLSearchParams();
  const icao = params.icao?.trim();
  if (icao) {
    query.set('icao', icao);
  }
  const suffix = query.toString() ? `?${query.toString()}` : '';
  const response = await fetch(apiUrl(`/station-health/eval-benchmark${suffix}`), {
    method: 'GET',
    signal: params.signal,
  });
  if (!response.ok) {
    throw new Error(`station-health eval-benchmark failed: ${response.status}`);
  }
  return response.json() as Promise<StationHealthEvalBenchmark>;
}
