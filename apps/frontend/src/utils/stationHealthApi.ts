/**
 * Station health public API client.
 */

import { apiUrl } from './apiBase';

/**
 * Per-product grade row for one station window.
 * @example
 * const row: StationProductGrade = {
 *   product: 'metar',
 *   grade: 'A',
 *   overall_score: 95,
 *   availability_score: 100,
 *   actual_count: 6,
 *   expected_count: 6,
 *   solidus_rate: 0,
 *   missing_digit_rate: 0,
 *   lint_severity_score: 100,
 *   lint_error_count: 0,
 * };
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
 * One station row in the health list payload.
 * @example
 * const item: StationHealthListItem = {
 *   icao: 'KJFK',
 *   overall_grade: 'B',
 *   overall_score: 84,
 *   products: [],
 * };
 */
export interface StationHealthListItem {
  icao: string;
  name?: string | null;
  overall_grade: string;
  overall_score: number;
  products: StationProductGrade[];
}

/**
 * List response for `/api/v1/station-health`.
 * @example
 * const body: StationHealthListResponse = {
 *   window: '6h',
 *   computed_at: '2026-11-13T12:00:00Z',
 *   stations: [],
 *   summary: { station_count: 0, grade_counts: {} },
 * };
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
 * const metric: StationHealthMetric = {
 *   id: 'availability',
 *   label: 'Availability',
 *   description: 'Share of expected TAC reports',
 *   higher_is_better: true,
 * };
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
 * const params: StationHealthListParams = { window: '6h', limit: 50 };
 */
export interface StationHealthListParams {
  window?: string;
  product?: string;
  grade?: string;
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
  if (params.window?.trim()) {
    query.set('window', params.window.trim());
  }
  if (params.product?.trim()) {
    query.set('product', params.product.trim());
  }
  if (params.grade?.trim()) {
    query.set('grade', params.grade.trim());
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
