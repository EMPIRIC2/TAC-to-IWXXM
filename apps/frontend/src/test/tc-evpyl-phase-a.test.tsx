/**
 * EV profile-builder YAML libraries — Phase A acceptance (TC-EVPYL-001..005).
 *
 * Authoring UI assertions retired under ADR-044 / TC-EVPVD-001 — Profile Builder
 * five-library shells are unmounted; keep WMO sync + export metadata helpers.
 * [Corpus: tests] [Corpus: adr/ADR-044] [Corpus: product §F7.w]
 */

import { cleanup, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { ConversionProfilePage } from '@/app/components/ConversionProfilePage';
import {
  buildConversionExportMetadata,
  defaultConversionMetadataChecklist,
  isConversionMetadataExportEnabled,
  metaSidecarFileName,
  sanitizeMetadataForExport,
} from '@/utils/conversionExportMetadata';
import {
  defaultWmoLibraryDefaultsSync,
  resetWmoLibraryDefaultsSync,
} from '@/utils/wmoLibraryDefaultsSync';

const fetchProfileCatalog = vi.fn();
const listLibraryAssets = vi.fn();
const listConversionTemplates = vi.fn();
const previewConversionTemplate = vi.fn();
const createConversionTemplate = vi.fn();

vi.mock('@/utils/conversionProfilesApi', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/utils/conversionProfilesApi')>();
  return {
    ...actual,
    fetchProfileCatalog: (...args: unknown[]) => fetchProfileCatalog(...args),
    listLibraryAssets: (...args: unknown[]) => listLibraryAssets(...args),
    listConversionTemplates: (...args: unknown[]) => listConversionTemplates(...args),
    previewConversionTemplate: (...args: unknown[]) =>
      previewConversionTemplate(...args),
    createConversionTemplate: (...args: unknown[]) => createConversionTemplate(...args),
  };
});

const catalogProfile = {
  id: 'ICAO_2025',
  kind: 'semantic',
  status: 'implemented',
  products: ['METAR'],
  emit_key: 'annex3',
  deltas_vs_icao: [],
  iwxxm_line: 'IWXXM 2025-2 core',
  rule_pack_count: 1,
  overlay_count: 0,
};

describe('TC-EVPYL Phase A', () => {
  afterEach(() => {
    cleanup();
    localStorage.clear();
  });

  beforeEach(() => {
    vi.clearAllMocks();
    fetchProfileCatalog.mockResolvedValue({ profiles: [catalogProfile] });
    listConversionTemplates.mockResolvedValue({ items: [] });
    previewConversionTemplate.mockResolvedValue({
      templateId: 'CV.WIND',
      focusGroup: '',
      matched: false,
      captures: [],
      xmlBlock: '',
      compiledPattern: '',
    });
    createConversionTemplate.mockResolvedValue({
      id: 'ct-1',
      slug: 'fork',
      name: 'Fork',
      access: 'custom',
      iwxxmBlock: 'iwxxm:WindObservation',
      slots: [],
    });
    listLibraryAssets.mockResolvedValue({ items: [] });
  });

  it('TC-EVPYL-001 / TC-EVPVD-001: Profile Builder authoring chrome is absent', async () => {
    render(<ConversionProfilePage accessToken="tok" />);

    await waitFor(() => {
      expect(screen.getByTestId('conversion-profiles-summary')).toBeInTheDocument();
    });

    expect(
      screen.getByTestId('conversion-profiles-authoring-retired'),
    ).toBeInTheDocument();
    expect(screen.queryByTestId('profile-builder-libraries')).not.toBeInTheDocument();
    expect(screen.queryByTestId('profile-builder-assembly')).not.toBeInTheDocument();
    expect(
      screen.queryByTestId('library-draft-shell-conversion'),
    ).not.toBeInTheDocument();
    expect(
      screen.queryByTestId('conversion-profiles-glossary'),
    ).not.toBeInTheDocument();
    expect(
      screen.queryByTestId('conversion-profiles-workflows'),
    ).not.toBeInTheDocument();
    expect(
      screen.queryByTestId('conversion-profiles-examples'),
    ).not.toBeInTheDocument();
  });

  it('TC-EVPYL-002: catalog inspector summary remains without library tabs', async () => {
    render(<ConversionProfilePage accessToken="tok" />);

    await waitFor(() => {
      expect(screen.getByTestId('conversion-profiles-select')).toBeInTheDocument();
    });

    expect(screen.getByTestId('conversion-profiles-blocks')).toBeInTheDocument();
    expect(
      screen.queryByTestId('profile-library-tab-conversion'),
    ).not.toBeInTheDocument();
    expect(
      screen.queryByTestId('conversion-profiles-inspector'),
    ).not.toBeInTheDocument();
  });

  it('TC-EVPYL-003: WMO reset helpers return ICAO_2025 library ids', () => {
    const defaults = defaultWmoLibraryDefaultsSync();
    expect(defaults.profile).toBe('ICAO_2025');
    expect(defaults.libraryIds.conversionLibraryId).toBe('LIB.CONVERSION.ICAO_2025');

    const reset = resetWmoLibraryDefaultsSync();
    expect(reset).toEqual(defaults);
  });

  it('TC-EVPYL-004: five-library draft shells are not mounted on Conversion profiles', async () => {
    render(<ConversionProfilePage accessToken="tok" />);

    await waitFor(() => {
      expect(screen.getByTestId('conversion-profiles-summary')).toBeInTheDocument();
    });

    for (const kind of [
      'conversion',
      'tac_validation',
      'iwxxm_validation',
      'dissemination',
      'decoding',
    ] as const) {
      expect(
        screen.queryByTestId(`library-draft-shell-${kind}`),
      ).not.toBeInTheDocument();
    }
  });

  it('TC-EVPYL-005: export metadata helpers sanitize secrets and omit guest operator', () => {
    expect(metaSidecarFileName('report.xml')).toBe('report.meta.json');
    expect(
      sanitizeMetadataForExport({
        nested: { accessToken: 'secret', apiKey: 'secret' },
      }),
    ).toEqual({ nested: {} });

    const guestMetadata = buildConversionExportMetadata({
      tacContent: 'METAR KJFK 121251Z',
      convertedAt: Date.now(),
      product: 'METAR',
      iwxxmVersion: '2025-2',
      libraries: defaultWmoLibraryDefaultsSync().libraryIds,
      checklist: defaultConversionMetadataChecklist(),
      isGuest: true,
      userEmail: 'operator@example.com',
      accessToken: 'token',
    });
    expect(guestMetadata.operator).toBeUndefined();
    expect(
      isConversionMetadataExportEnabled({
        enabled: false,
        checklist: defaultConversionMetadataChecklist(),
      }),
    ).toBe(false);
  });
});
