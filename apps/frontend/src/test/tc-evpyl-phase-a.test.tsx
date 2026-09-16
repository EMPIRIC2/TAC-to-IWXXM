/**
 * EV profile-builder YAML libraries — Phase A acceptance (TC-EVPYL-001..005).
 */

import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { ConversionProfilePage } from '@/app/components/ConversionProfilePage';
import type { LibraryAssetKind } from '@/utils/conversionProfilesApi';
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
    vi.restoreAllMocks();
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

  it('TC-EVPYL-001: assembly, glossary, workflows, and examples are absent', async () => {
    render(<ConversionProfilePage accessToken="tok" />);

    await waitFor(() => {
      expect(screen.getByTestId('profile-builder-libraries')).toBeInTheDocument();
    });

    expect(screen.queryByTestId('profile-builder-assembly')).not.toBeInTheDocument();
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

  it('TC-EVPYL-002: inspector lives under libraries and Kind follows the active tab', async () => {
    const user = userEvent.setup();
    render(<ConversionProfilePage accessToken="tok" />);

    await waitFor(() => {
      expect(screen.getByTestId('conversion-profiles-inspector')).toBeInTheDocument();
    });

    const libraries = screen.getByTestId('profile-builder-libraries');
    expect(libraries).toContainElement(
      screen.getByTestId('conversion-profiles-inspector'),
    );

    expect(
      screen.getByTestId('conversion-profiles-inspector-detail'),
    ).toHaveTextContent('Conversion');

    await user.click(screen.getByTestId('profile-library-tab-decoding'));
    expect(
      screen.getByTestId('conversion-profiles-inspector-detail'),
    ).toHaveTextContent('Decoding');
  });

  it('TC-EVPYL-003: WMO reset helpers return ICAO_2025 library ids', () => {
    const defaults = defaultWmoLibraryDefaultsSync();
    expect(defaults.profile).toBe('ICAO_2025');
    expect(defaults.libraryIds.conversionLibraryId).toBe('LIB.CONVERSION.ICAO_2025');

    const reset = resetWmoLibraryDefaultsSync();
    expect(reset).toEqual(defaults);
  });

  it('TC-EVPYL-004: LibraryDraftShell renders for all five library kinds', async () => {
    const user = userEvent.setup();
    render(<ConversionProfilePage accessToken="tok" />);

    await waitFor(() => {
      expect(screen.getByTestId('library-draft-shell-conversion')).toBeInTheDocument();
    });

    const tabs: Array<{ testId: string; kind: LibraryAssetKind }> = [
      { testId: 'profile-library-tab-conversion', kind: 'conversion' },
      { testId: 'profile-library-tab-tac-validation', kind: 'tac_validation' },
      { testId: 'profile-library-tab-iwxxm-validation', kind: 'iwxxm_validation' },
      { testId: 'profile-library-tab-dissemination', kind: 'dissemination' },
      { testId: 'profile-library-tab-decoding', kind: 'decoding' },
    ];

    for (const tab of tabs) {
      await user.click(screen.getByTestId(tab.testId));
      expect(screen.getByTestId(`library-draft-shell-${tab.kind}`)).toBeInTheDocument();
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
