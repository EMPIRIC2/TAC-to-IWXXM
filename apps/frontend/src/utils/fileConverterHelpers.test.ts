/**
 * Tests for fallbackProfileSummary.
 *
 * FR-019..022 / M1: FALLBACK_PROFILE_SUMMARIES is ICAO-only and no reachable profile is
 * an MSC operational line, so both fallback branches need mocked inputs.
 */

import { beforeEach, describe, expect, it, vi } from 'vitest';

const state = vi.hoisted(() => ({
  fallbacks: {} as Record<string, unknown>,
  msc: false,
}));

vi.mock('./fileConverterProfileFallbacks', () => ({
  FALLBACK_PROFILE_SUMMARIES: state.fallbacks,
}));

vi.mock('@/utils/iwxxmVersions', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/utils/iwxxmVersions')>();
  return { ...actual, isMscOperationalLine: () => state.msc };
});

import { fallbackProfileSummary } from './fileConverterHelpers';
import { CA_ECCC_IWXXM_VERSION } from '@/utils/iwxxmVersions';

const icaoEntry = {
  id: 'ICAO_2025',
  kind: 'semantic',
  products: ['METAR'],
  deltas_vs_icao: ['baseline'],
};

describe('fallbackProfileSummary', () => {
  beforeEach(() => {
    for (const key of Object.keys(state.fallbacks)) {
      delete state.fallbacks[key];
    }
    state.msc = false;
  });

  it('returns a minimal semantic summary when no fallback entry exists', () => {
    expect(fallbackProfileSummary('ICAO_2025', '2025-2')).toEqual({
      id: 'ICAO_2025',
      kind: 'semantic',
      products: [],
      deltas_vs_icao: [],
      iwxxm_line: 'IWXXM 2025-2',
    });
  });

  it('uses the requested IWXXM version for a known fallback entry', () => {
    state.fallbacks.ICAO_2025 = icaoEntry;
    expect(fallbackProfileSummary('ICAO_2025', '2025-2')).toEqual({
      ...icaoEntry,
      iwxxm_line: 'IWXXM 2025-2',
    });
  });

  it('labels MSC operational lines with the CA IWXXM version', () => {
    state.fallbacks.ICAO_2025 = icaoEntry;
    state.msc = true;
    expect(fallbackProfileSummary('ICAO_2025', '2025-2').iwxxm_line).toBe(
      `IWXXM ${CA_ECCC_IWXXM_VERSION} (MSC operational)`,
    );
  });
});
