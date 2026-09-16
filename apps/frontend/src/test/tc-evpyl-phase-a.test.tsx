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
  WMO_LIBRARY_DEFAULTS_SYNC_KEY,
  defaultWmoLibraryDefaultsSync,
  readWmoLibraryDefaultsSync,
  resetWmoLibraryDefaultsSync,
  writeWmoLibraryDefaultsSync,
} from '@/utils/wmoLibraryDefaultsSync';

const fetchProfileCatalog = vi.fn();
const listLibraryAssets = vi.fn();
const listConversionTemplates = vi.fn();
const previewConversionTemplate = vi.fn();
const createConversionTemplate = vi.fn();
const createLibraryAsset = vi.fn();
const updateLibraryAsset = vi.fn();

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
    createLibraryAsset: (...args: unknown[]) => createLibraryAsset(...args),
    updateLibraryAsset: (...args: unknown[]) => updateLibraryAsset(...args),
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
    createLibraryAsset.mockResolvedValue({
      id: 'asset-draft-1',
      kind: 'decoding',
      name: 'Draft',
      access: 'custom',
      engineProfileId: 'ICAO_2025',
      attachedNationalLine: 'ICAO_2025',
      status: 'draft',
    });
    updateLibraryAsset.mockResolvedValue({
      id: 'asset-draft-1',
      kind: 'decoding',
      name: 'Draft',
      access: 'custom',
      engineProfileId: 'ICAO_2025',
      attachedNationalLine: 'ICAO_2025',
      status: 'activated',
    });
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

  it('keeps draft YAML when switching library tabs after Save draft', async () => {
    const user = userEvent.setup();
    render(<ConversionProfilePage accessToken="tok" />);

    await waitFor(() => {
      expect(screen.getByTestId('library-draft-shell-conversion')).toBeInTheDocument();
    });

    await user.click(screen.getByTestId('library-draft-new-template-conversion'));
    const editor = screen.getByTestId(
      'library-draft-yaml-conversion',
    ) as HTMLTextAreaElement;
    expect(editor.value).toContain('kind: conversion');
    await user.click(screen.getByTestId('library-draft-save-conversion'));

    await user.click(screen.getByTestId('profile-library-tab-decoding'));
    await user.click(screen.getByTestId('profile-library-tab-conversion'));

    expect(
      (screen.getByTestId('library-draft-yaml-conversion') as HTMLTextAreaElement)
        .value,
    ).toContain('kind: conversion');
  });

  it('exposes WMO reset help on Profile builder', async () => {
    render(<ConversionProfilePage accessToken="tok" />);
    await waitFor(() => {
      expect(
        screen.getByTestId('profile-builder-reset-wmo-defaults-help'),
      ).toBeInTheDocument();
    });
  });

  it('resets shared WMO library defaults from Profile builder', async () => {
    const user = userEvent.setup();
    writeWmoLibraryDefaultsSync({
      profile: 'US_FAA_NWS',
      libraryIds: {
        conversionLibraryId: 'LIB.CONVERSION.US_FAA_NWS',
        tacValidationLibraryId: 'LIB.TAC_VALIDATION.US_FAA_NWS',
        iwxxmValidationLibraryId: 'LIB.IWXXM_VALIDATION.US_FAA_NWS',
        disseminationLibraryId: 'LIB.DISSEMINATION.US_FAA_NWS',
        decodingLibraryId: 'LIB.DECODING.US_FAA_NWS',
      },
    });
    render(<ConversionProfilePage accessToken="tok" />);
    await waitFor(() => {
      expect(
        screen.getByTestId('profile-builder-reset-wmo-defaults'),
      ).toBeInTheDocument();
    });
    await user.click(screen.getByTestId('profile-builder-reset-wmo-defaults'));
    expect(readWmoLibraryDefaultsSync()).toEqual(defaultWmoLibraryDefaultsSync());
    expect(localStorage.getItem(WMO_LIBRARY_DEFAULTS_SYNC_KEY)).toBeTruthy();
  });

  it('loads conversion schema blocks from library assets into the draft shell', async () => {
    listLibraryAssets.mockResolvedValue({
      items: [
        {
          id: 'LIB.CONVERSION.ICAO_2025',
          kind: 'conversion',
          name: 'ICAO conversion',
          access: 'first_party',
          engineProfileId: 'ICAO_2025',
          attachedNationalLine: 'ICAO_2025',
          body: {
            schema_blocks: [
              null,
              { label: 'missing-id', cards: [{ id: 'c1', label: 'Card' }] },
              { id: 'label-fallback' },
              {
                id: 'obs',
                label: 'Observation',
                cards: [
                  null,
                  { label: 'no-id' },
                  { id: 'wind', label: 'Wind' },
                  { id: 'vis' },
                ],
              },
              { id: 'empty-cards', label: 'Empty', cards: 'nope' },
            ],
          },
        },
      ],
    });

    render(<ConversionProfilePage accessToken="tok" />);
    await waitFor(() => {
      expect(
        screen.getByTestId('library-draft-block-obs-conversion'),
      ).toBeInTheDocument();
    });
    expect(
      screen.getByTestId('library-draft-block-label-fallback-conversion'),
    ).toBeInTheDocument();
    expect(screen.getByText('Wind')).toBeInTheDocument();
    expect(screen.getByText('vis')).toBeInTheDocument();
    expect(
      screen.getByTestId('library-draft-block-empty-cards-conversion'),
    ).toBeInTheDocument();
  });

  it('clears schema blocks when library asset fetch fails or unmounts early', async () => {
    let resolveAssets: (value: { items: unknown[] }) => void = () => undefined;
    let rejectAssets: (reason?: unknown) => void = () => undefined;
    listLibraryAssets.mockImplementation(
      () =>
        new Promise((resolve, reject) => {
          resolveAssets = resolve;
          rejectAssets = reject;
        }),
    );

    const first = render(<ConversionProfilePage accessToken="tok" />);
    await waitFor(() => {
      expect(listLibraryAssets).toHaveBeenCalled();
    });
    first.unmount();
    resolveAssets({ items: [] });

    listLibraryAssets.mockImplementation(
      () =>
        new Promise((_resolve, reject) => {
          rejectAssets = reject;
        }),
    );
    const second = render(<ConversionProfilePage accessToken="tok" />);
    await waitFor(() => {
      expect(listLibraryAssets).toHaveBeenCalled();
    });
    second.unmount();
    rejectAssets(new Error('cancelled-network'));

    listLibraryAssets.mockRejectedValue(new Error('network'));
    render(<ConversionProfilePage accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('library-draft-shell-conversion')).toBeInTheDocument();
    });
    await waitFor(() => {
      expect(
        screen.getByTestId('library-draft-block-observation-conversion'),
      ).toBeInTheDocument();
    });

    listLibraryAssets.mockResolvedValue({
      items: [
        {
          id: 'LIB.CONVERSION.ICAO_2025',
          kind: 'conversion',
          name: 'ICAO conversion',
          access: 'first_party',
          engineProfileId: 'ICAO_2025',
          attachedNationalLine: 'ICAO_2025',
          body: {
            schema_blocks: [{ label: 'no-id-only', cards: [] }, null],
          },
        },
      ],
    });
    cleanup();
    render(<ConversionProfilePage accessToken="tok" />);
    await waitFor(() => {
      expect(
        screen.getByTestId('library-draft-block-observation-conversion'),
      ).toBeInTheDocument();
    });
  });

  it('resolves schema blocks by library id and shows national inspector fields', async () => {
    const user = userEvent.setup();
    const usProfile = {
      id: 'US_FAA_NWS',
      kind: 'semantic',
      status: 'implemented',
      products: [] as string[],
      emit_key: 'iwxxm_us',
      deltas_vs_icao: [],
      iwxxm_line: '',
      rule_pack_count: 1,
      overlay_count: 0,
    };
    fetchProfileCatalog.mockResolvedValue({
      profiles: [
        catalogProfile,
        usProfile,
        {
          id: 'CUSTOM',
          kind: 'semantic',
          status: 'implemented',
          products: ['TAF'],
          emit_key: null,
          deltas_vs_icao: [],
          iwxxm_line: 'IWXXM 2023-1',
          rule_pack_count: 0,
          overlay_count: 0,
        },
      ],
    });
    listLibraryAssets.mockResolvedValue({
      items: [
        {
          id: 'LIB.CONVERSION.US_FAA_NWS',
          kind: 'conversion',
          name: 'US conversion',
          access: 'first_party',
          engineProfileId: 'US_FAA_NWS',
          attachedNationalLine: 'OTHER_LINE',
          body: {
            schema_blocks: [{ id: 'rmk', label: 'Remarks', cards: [] }],
          },
        },
      ],
    });

    render(<ConversionProfilePage accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('profile-builder-libraries')).toBeInTheDocument();
    });

    const profileSelect = screen.getByTestId('conversion-profiles-select');
    await user.selectOptions(profileSelect, 'US_FAA_NWS');
    await waitFor(() => {
      expect(
        screen.getByTestId('library-draft-block-rmk-conversion'),
      ).toBeInTheDocument();
    });
    expect(
      screen.getByTestId('conversion-profiles-inspector-detail'),
    ).toHaveTextContent(/National|US - FAA NWS|Coverage unavailable/i);

    await user.selectOptions(profileSelect, 'CUSTOM');
    await waitFor(() => {
      expect(
        screen.getByTestId('conversion-profiles-inspector-detail'),
      ).toHaveTextContent('CUSTOM');
    });
  });

  it('marks non-conversion inspector status as Draft after save', async () => {
    const user = userEvent.setup();
    render(<ConversionProfilePage accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('library-draft-shell-conversion')).toBeInTheDocument();
    });
    await user.click(screen.getByTestId('profile-library-tab-decoding'));
    await user.click(screen.getByTestId('library-draft-new-template-decoding'));
    await user.click(screen.getByTestId('library-draft-save-decoding'));
    await waitFor(() => {
      expect(createLibraryAsset).toHaveBeenCalled();
    });
    await waitFor(() => {
      expect(
        screen.getByTestId('conversion-profiles-inspector-detail'),
      ).toHaveTextContent(/Draft/i);
    });
  });

  it('clears mined schema blocks when every raw entry is invalid', async () => {
    listLibraryAssets.mockResolvedValue({
      items: [
        {
          id: 'LIB.CONVERSION.ICAO_2025',
          kind: 'conversion',
          name: 'ICAO conversion',
          access: 'first_party',
          engineProfileId: 'ICAO_2025',
          attachedNationalLine: 'ICAO_2025',
          body: {
            schema_blocks: [null, { label: 'no-id' }, 'skip', { id: 1 }],
          },
        },
      ],
    });
    render(<ConversionProfilePage accessToken="tok" />);
    await waitFor(() => {
      expect(
        screen.getByTestId('library-draft-block-observation-conversion'),
      ).toBeInTheDocument();
    });
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
