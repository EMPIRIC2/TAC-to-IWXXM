/**
 * Vitest for ConversionProfile editor page (TC-EV933-001/002 FE).
 */

import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { ConversionProfilePage } from './ConversionProfilePage';

const fetchProfileCatalog = vi.fn();
const listLibraryAssets = vi.fn();
const listConversionTemplates = vi.fn();
const previewConversionTemplate = vi.fn();
const createConversionTemplate = vi.fn();

vi.mock('@/utils/conversionProfilesApi', () => ({
  fetchProfileCatalog: (...args: unknown[]) => fetchProfileCatalog(...args),
  listLibraryAssets: (...args: unknown[]) => listLibraryAssets(...args),
  listConversionTemplates: (...args: unknown[]) => listConversionTemplates(...args),
  previewConversionTemplate: (...args: unknown[]) => previewConversionTemplate(...args),
  createConversionTemplate: (...args: unknown[]) => createConversionTemplate(...args),
}));

describe('ConversionProfilePage', () => {
  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
  });

  beforeEach(() => {
    vi.clearAllMocks();
    fetchProfileCatalog.mockResolvedValue({
      profiles: [
        {
          id: 'ICAO_2025',
          kind: 'semantic',
          status: 'implemented',
          products: ['METAR', 'TAF'],
          emit_key: 'annex3',
          deltas_vs_icao: ['Baseline ICAO/WMO line used for cross-profile comparison.'],
          iwxxm_line: 'IWXXM 2025-2 core',
          rule_pack_count: 1,
          overlay_count: 1,
          vendor_pins: { iwxxm: 'WMO IWXXM 2025-2' },
          implementation: {
            input: 'tac2iwxxm/profiles/annex3',
            conversion: 'annex3 emit plugin',
            exchange: 'GLOBAL_AFS default',
          },
        },
        {
          id: 'US_FAA_NWS',
          kind: 'semantic',
          status: 'implemented',
          products: ['METAR'],
          emit_key: 'iwxxm_us',
          deltas_vs_icao: [
            'Retains selected RMK content in output.',
            'Adds FAA/NWS national extension coverage.',
          ],
          iwxxm_line: 'IWXXM-US 3.0.0',
          rule_pack_count: 2,
          overlay_count: 0,
          vendor_pins: { iwxxm: 'iwxxm-us 3.0.0' },
          implementation: {
            input: 'tac2iwxxm/profiles/iwxxm_us',
            conversion: 'iwxxm_us emit plugin',
          },
        },
        {
          id: 'CA_ECCC',
          kind: 'semantic',
          status: 'pilot',
          products: ['METAR', 'SPECI', 'TAF', 'AIRMET'],
          emit_key: 'ca_eccc',
          deltas_vs_icao: ['Pins the MSC operational IWXXM line.'],
          iwxxm_line: 'IWXXM 3.0.0 (MSC operational)',
          rule_pack_count: 0,
          overlay_count: 0,
          vendor_pins: { iwxxm: 'MSC 3.0.0' },
          implementation: {
            input: 'tac2iwxxm/profiles/ca_eccc',
            conversion: 'ca_eccc emit plugin',
          },
        },
      ],
    });
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
    listLibraryAssets.mockResolvedValue({
      items: [
        {
          id: 'LIB.TAC_VALIDATION.ICAO_2025',
          kind: 'tac_validation',
          name: 'ICAO TAC validation',
          access: 'first_party',
          engineProfileId: 'ICAO_2025',
          attachedNationalLine: 'ICAO_2025',
          body: {},
        },
      ],
    });
  });

  it('prompts sign-in when unauthenticated', async () => {
    const onRequestLogin = vi.fn();
    const user = userEvent.setup();
    render(<ConversionProfilePage onRequestLogin={onRequestLogin} />);
    expect(screen.getByTestId('conversion-profiles-sign-in')).toBeInTheDocument();
    await user.click(screen.getByTestId('conversion-profiles-sign-in'));
    expect(onRequestLogin).toHaveBeenCalled();
  });

  it('loads inspector and five library tabs when authenticated', async () => {
    const user = userEvent.setup();
    render(<ConversionProfilePage accessToken="tok" />);

    await waitFor(() => {
      expect(
        screen.getByTestId('conversion-profiles-inspector-detail'),
      ).toBeInTheDocument();
    });
    expect(screen.getByTestId('profile-builder-assembly')).toBeInTheDocument();
    expect(screen.getByTestId('profile-builder-step-convert')).toBeInTheDocument();
    expect(fetchProfileCatalog).toHaveBeenCalledWith('tok');
    expect(screen.getByTestId('profile-builder-libraries')).toBeInTheDocument();
    expect(
      screen
        .getByTestId('profile-builder-libraries')
        .querySelector('[data-testid="beta-badge"]'),
    ).toBeTruthy();
    expect(screen.getByTestId('profile-library-tab-conversion')).toBeInTheDocument();
    expect(screen.queryByTestId('conversion-profiles-presets')).not.toBeInTheDocument();
    expect(screen.queryByTestId('conversion-profiles-packs')).not.toBeInTheDocument();
    expect(
      screen.queryByTestId('conversion-profiles-templates'),
    ).not.toBeInTheDocument();
    expect(
      screen.queryByTestId('conversion-profiles-overlays'),
    ).not.toBeInTheDocument();

    await user.click(screen.getByTestId('profile-library-tab-tac-validation'));
    await waitFor(() => {
      expect(listLibraryAssets).toHaveBeenCalledWith('tok', 'tac_validation');
    });
    expect(
      screen.getByTestId('library-assets-panel-tac_validation'),
    ).toBeInTheDocument();

    await user.click(screen.getByTestId('profile-library-tab-iwxxm-validation'));
    await waitFor(() => {
      expect(listLibraryAssets).toHaveBeenCalledWith('tok', 'iwxxm_validation');
    });
    await user.click(screen.getByTestId('profile-library-tab-dissemination'));
    await waitFor(() => {
      expect(
        screen.getByTestId('library-assets-panel-dissemination'),
      ).toBeInTheDocument();
    });
    await user.click(screen.getByTestId('profile-library-tab-decoding'));
    await waitFor(() => {
      expect(screen.getByTestId('library-assets-panel-decoding')).toBeInTheDocument();
    });
  });

  it('shows empty catalog and load error', async () => {
    fetchProfileCatalog.mockRejectedValue(new Error('catalog boom'));
    render(<ConversionProfilePage accessToken="tok" />);

    await waitFor(() => {
      expect(screen.getByTestId('conversion-profiles-error')).toBeInTheDocument();
    });
    expect(screen.getByTestId('conversion-profiles-error')).toHaveTextContent(
      'catalog boom',
    );
    expect(screen.queryByTestId('conversion-profiles-packs')).not.toBeInTheDocument();
    expect(screen.getByTestId('profile-builder-libraries')).toBeInTheDocument();
  });

  it('shows the empty inspector state when catalog loads without profiles', async () => {
    fetchProfileCatalog.mockResolvedValue({ profiles: [] });
    render(<ConversionProfilePage accessToken="tok" />);

    await waitFor(() => {
      expect(
        screen.getAllByText(/No catalog profiles available\./).length,
      ).toBeGreaterThan(0);
    });

    expect(
      screen.queryByTestId('conversion-profiles-summary-primary'),
    ).not.toBeInTheDocument();
  });

  it('shows Unknown error for non-Error load rejection', async () => {
    fetchProfileCatalog.mockRejectedValue('weird');
    render(<ConversionProfilePage accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('conversion-profiles-error')).toHaveTextContent(
        /Unknown error/,
      );
    });
  });

  it('renders a summary-first compare view', async () => {
    const user = userEvent.setup();
    const onOpenConverterExamples = vi.fn();
    render(
      <ConversionProfilePage
        accessToken="tok"
        onOpenConverterExamples={onOpenConverterExamples}
      />,
    );

    await waitFor(() => {
      expect(screen.getByTestId('conversion-profiles-summary')).toBeInTheDocument();
    });

    expect(screen.getByTestId('conversion-profiles-summary-primary')).toHaveTextContent(
      'ICAO_2025',
    );
    expect(screen.getAllByText(/IWXXM 2025-2 core/).length).toBeGreaterThan(0);
    expect(
      screen.getByTestId('conversion-profiles-inspector-detail'),
    ).toHaveTextContent('ICAO / WMO baseline');
    expect(
      screen.getByTestId('conversion-profiles-inspector-detail'),
    ).toHaveTextContent('ICAO / WMO');
    expect(screen.getByTestId('conversion-profiles-glossary')).toHaveTextContent(
      /Libraries hold conversion, validation, dissemination, and decoding assets/i,
    );
    expect(screen.getByTestId('conversion-profiles-summary-primary')).toHaveTextContent(
      'Rule packs',
    );

    await user.selectOptions(
      screen.getByTestId('conversion-profiles-compare-select'),
      'US_FAA_NWS',
    );

    expect(screen.getByTestId('conversion-profiles-summary-compare')).toHaveTextContent(
      'US_FAA_NWS',
    );
    expect(screen.getAllByText(/Different from/).length).toBeGreaterThan(0);
    expect(
      screen.getByText(/Retains selected RMK content in output\./),
    ).toBeInTheDocument();
    expect(
      screen.getByText(/Difference notes compared with ICAO_2025/),
    ).toBeInTheDocument();
    expect(screen.getByTestId('conversion-profiles-workflows')).toHaveTextContent(
      /Workflow references/i,
    );
    expect(screen.getByTestId('conversion-profiles-workflows')).toHaveTextContent(
      /read-only in this screen/i,
    );
    expect(screen.getByTestId('conversion-profiles-examples')).toHaveTextContent(
      /Examples available on Convert/i,
    );
    expect(screen.getByTestId('conversion-profiles-examples')).toHaveTextContent(
      /METAR, TAF/i,
    );
    expect(
      screen.getByTestId('conversion-profiles-workflow-definitions'),
    ).toHaveAttribute('href', expect.stringContaining('/workflows'));
    expect(screen.getByTestId('conversion-profiles-workflow-runtime')).toHaveAttribute(
      'href',
      expect.stringContaining('/packages/workflows'),
    );
    await user.click(screen.getByTestId('conversion-profiles-open-examples'));
    expect(onOpenConverterExamples).toHaveBeenCalledTimes(1);
    await user.selectOptions(
      screen.getByTestId('conversion-profiles-select'),
      'US_FAA_NWS',
    );
    expect(
      screen.getByTestId('conversion-profiles-inspector-detail'),
    ).toHaveTextContent('US - FAA NWS');
    expect(screen.getByTestId('conversion-profiles-examples')).toHaveTextContent(
      /reused from the ICAO \/ WMO demo set/i,
    );
  });

  it('falls back to raw authority code when profile id has no suffix', async () => {
    fetchProfileCatalog.mockReset();
    fetchProfileCatalog.mockResolvedValue({
      profiles: [
        {
          id: 'ECCC',
          kind: 'semantic',
          status: 'pilot',
          products: [],
          emit_key: 'eccc',
          deltas_vs_icao: [],
          iwxxm_line: null,
          rule_pack_count: 0,
          overlay_count: 0,
          vendor_pins: {},
          implementation: {
            input: 'profiles/eccc',
            conversion: 'eccc emit plugin',
          },
        },
      ],
    });

    render(<ConversionProfilePage accessToken="tok" />);

    await waitFor(() => {
      expect(
        screen.getByTestId('conversion-profiles-inspector-detail'),
      ).toBeInTheDocument();
    });

    expect(
      screen.getByTestId('conversion-profiles-inspector-detail'),
    ).toHaveTextContent('ECCC');
    expect(
      screen.getByTestId('conversion-profiles-inspector-detail'),
    ).toHaveTextContent('Coverage details unavailable');
  });

  it('opens ADR-038 block detail and jump links', async () => {
    const user = userEvent.setup();
    render(<ConversionProfilePage accessToken="tok" />);

    await waitFor(() => {
      expect(screen.getByTestId('conversion-profiles-block-input')).toBeInTheDocument();
    });

    await user.click(screen.getByTestId('conversion-profiles-block-output-validation'));

    expect(screen.getByTestId('conversion-profiles-block-detail')).toHaveTextContent(
      'IWXXM validate',
    );
    expect(screen.getByTestId('conversion-profiles-block-detail')).toHaveTextContent(
      'WMO IWXXM 2025-2',
    );
    expect(
      screen.getByTestId('conversion-profiles-block-jump-libraries'),
    ).toHaveAttribute('href', '#profile-builder-libraries');
  });

  it('does not flag delta notes when compared profiles share the same note list', async () => {
    const user = userEvent.setup();
    fetchProfileCatalog.mockResolvedValue({
      profiles: [
        {
          id: 'ICAO_2025',
          kind: 'semantic',
          status: 'implemented',
          products: ['METAR', 'TAF'],
          deltas_vs_icao: ['Baseline ICAO/WMO line used for cross-profile comparison.'],
          iwxxm_line: 'IWXXM 2025-2 core',
          rule_pack_count: 1,
          overlay_count: 1,
        },
        {
          id: 'MATCHED_PROFILE',
          kind: 'semantic',
          status: 'implemented',
          products: ['METAR'],
          deltas_vs_icao: ['Baseline ICAO/WMO line used for cross-profile comparison.'],
          iwxxm_line: 'IWXXM-US 3.0.0',
          rule_pack_count: 2,
          overlay_count: 0,
        },
      ],
    });
    render(<ConversionProfilePage accessToken="tok" />);

    await waitFor(() => {
      expect(
        screen.getByTestId('conversion-profiles-summary-primary'),
      ).toBeInTheDocument();
    });

    await user.selectOptions(
      screen.getByTestId('conversion-profiles-compare-select'),
      'MATCHED_PROFILE',
    );

    expect(
      screen.queryByText(/Difference notes compared with MATCHED_PROFILE/),
    ).not.toBeInTheDocument();
    expect(
      screen.queryByText(/Difference notes compared with ICAO_2025/),
    ).not.toBeInTheDocument();
  });

  it('flags delta notes when the compared profile has no note list', async () => {
    const user = userEvent.setup();
    fetchProfileCatalog.mockResolvedValue({
      profiles: [
        {
          id: 'ICAO_2025',
          kind: 'semantic',
          status: 'implemented',
          products: ['METAR', 'TAF'],
          deltas_vs_icao: ['Baseline ICAO/WMO line used for cross-profile comparison.'],
          iwxxm_line: 'IWXXM 2025-2 core',
          rule_pack_count: 1,
          overlay_count: 1,
        },
        {
          id: 'NO_DELTAS',
          kind: 'semantic',
          status: 'implemented',
          products: ['METAR'],
          deltas_vs_icao: [],
          iwxxm_line: 'IWXXM-US 3.0.0',
          rule_pack_count: 2,
          overlay_count: 0,
        },
      ],
    });
    render(<ConversionProfilePage accessToken="tok" />);

    await waitFor(() => {
      expect(
        screen.getByTestId('conversion-profiles-summary-primary'),
      ).toBeInTheDocument();
    });

    await user.selectOptions(
      screen.getByTestId('conversion-profiles-compare-select'),
      'NO_DELTAS',
    );

    expect(
      screen.getByText(/Difference notes compared with NO_DELTAS/),
    ).toBeInTheDocument();
    expect(
      screen.getByText(/No profile-specific differences listed\./),
    ).toBeInTheDocument();
  });

  it('flags delta notes when compared profiles have different note text with equal lengths', async () => {
    const user = userEvent.setup();
    fetchProfileCatalog.mockResolvedValue({
      profiles: [
        {
          id: 'ICAO_2025',
          kind: 'semantic',
          status: 'implemented',
          products: ['METAR', 'TAF'],
          deltas_vs_icao: ['Baseline ICAO/WMO line used for cross-profile comparison.'],
          iwxxm_line: 'IWXXM 2025-2 core',
          rule_pack_count: 1,
          overlay_count: 1,
        },
        {
          id: 'DIFFERENT_NOTE',
          kind: 'semantic',
          status: 'implemented',
          products: ['METAR'],
          deltas_vs_icao: ['Uses a different national note for compare coverage.'],
          iwxxm_line: 'IWXXM-US 3.0.0',
          rule_pack_count: 2,
          overlay_count: 0,
        },
      ],
    });
    render(<ConversionProfilePage accessToken="tok" />);

    await waitFor(() => {
      expect(
        screen.getByTestId('conversion-profiles-summary-primary'),
      ).toBeInTheDocument();
    });

    await user.selectOptions(
      screen.getByTestId('conversion-profiles-compare-select'),
      'DIFFERENT_NOTE',
    );

    expect(
      screen.getByText(/Difference notes compared with DIFFERENT_NOTE/),
    ).toBeInTheDocument();
  });

  it('clears compare when selecting the same profile and shows fallback detail copy', async () => {
    const user = userEvent.setup();
    fetchProfileCatalog.mockResolvedValue({
      profiles: [
        {
          id: 'ZZ_TEST_PROFILE',
          kind: 'semantic',
          products: [],
        },
        {
          id: 'ICAO_2025',
          kind: 'semantic',
          status: 'implemented',
          products: ['METAR', 'TAF'],
          emit_key: 'annex3',
          rule_pack_count: 1,
          overlay_count: 1,
          vendor_pins: { iwxxm: 'WMO IWXXM 2025-2' },
          implementation: {
            input: 'tac2iwxxm/profiles/annex3',
            exchange: 'GLOBAL_AFS default',
          },
        },
      ],
    });

    render(<ConversionProfilePage accessToken="tok" />);

    await waitFor(() => {
      expect(screen.getByTestId('conversion-profiles-summary')).toBeInTheDocument();
    });

    await user.selectOptions(
      screen.getByTestId('conversion-profiles-compare-select'),
      'ICAO_2025',
    );
    expect(
      screen.getByTestId('conversion-profiles-summary-compare'),
    ).toBeInTheDocument();

    await user.selectOptions(
      screen.getByTestId('conversion-profiles-select'),
      'ICAO_2025',
    );
    expect(
      screen.queryByTestId('conversion-profiles-summary-compare'),
    ).not.toBeInTheDocument();

    await user.click(screen.getByTestId('conversion-profiles-block-validation-tac'));
    expect(screen.getByTestId('conversion-profiles-block-detail')).toHaveTextContent(
      'TAC lint applies the annex3 registry path.',
    );
    await user.click(screen.getByTestId('conversion-profiles-block-conversion'));
    expect(screen.getByTestId('conversion-profiles-block-detail')).toHaveTextContent(
      'Convert emits with the annex3 profile mapper.',
    );

    await user.selectOptions(
      screen.getByTestId('conversion-profiles-select'),
      'ZZ_TEST_PROFILE',
    );
    expect(screen.getByTestId('conversion-profiles-summary-primary')).toHaveTextContent(
      'Products',
    );
    expect(screen.getAllByText('—').length).toBeGreaterThan(0);
    await user.click(screen.getByTestId('conversion-profiles-block-validation-tac'));
    expect(screen.getByTestId('conversion-profiles-block-detail')).toHaveTextContent(
      'TAC lint registry details are not listed for this profile.',
    );
    await user.click(screen.getByTestId('conversion-profiles-block-conversion'));
    expect(screen.getByTestId('conversion-profiles-block-detail')).toHaveTextContent(
      'Convert mapping details are not listed for this profile.',
    );

    await user.click(screen.getByTestId('conversion-profiles-block-output-validation'));
    expect(screen.getByTestId('conversion-profiles-block-detail')).toHaveTextContent(
      'IWXXM validation line is not listed for this profile.',
    );

    await user.click(screen.getByTestId('conversion-profiles-block-exchange'));
    expect(screen.getByTestId('conversion-profiles-block-detail')).toHaveTextContent(
      'No exchange default is listed for this profile.',
    );
    expect(screen.getByText('Status')).toBeInTheDocument();
  });

  it('distinguishes loaded zero counts from unavailable counts', async () => {
    fetchProfileCatalog.mockResolvedValue({
      profiles: [
        {
          id: 'ICAO_2025',
          kind: 'semantic',
          products: ['METAR'],
          rule_pack_count: 0,
          overlay_count: 0,
        },
        {
          id: 'ZZ_UNAVAILABLE',
          kind: 'semantic',
          products: ['TAF'],
          rule_pack_count: undefined,
          overlay_count: null,
        },
      ],
    });

    const user = userEvent.setup();
    render(<ConversionProfilePage accessToken="tok" />);

    await waitFor(() => {
      expect(
        screen.getByTestId('conversion-profiles-summary-primary'),
      ).toBeInTheDocument();
    });

    expect(screen.getByTestId('conversion-profiles-summary-primary')).toHaveTextContent(
      'Rule packs',
    );
    expect(screen.getByTestId('conversion-profiles-summary-primary')).toHaveTextContent(
      '0',
    );

    await user.selectOptions(
      screen.getByTestId('conversion-profiles-select'),
      'ZZ_UNAVAILABLE',
    );

    expect(screen.getByTestId('conversion-profiles-summary-primary')).toHaveTextContent(
      'Unavailable',
    );
  });

  it('shows a catalog degraded hint without collapsing the rest of the page', async () => {
    fetchProfileCatalog.mockRejectedValue(new Error('catalog fetch failed'));
    render(<ConversionProfilePage accessToken="tok" />);

    await waitFor(() => {
      expect(screen.getByTestId('conversion-profiles-summary')).toBeInTheDocument();
    });

    expect(screen.getByTestId('conversion-profiles-summary')).toHaveTextContent(
      /Catalog unavailable/i,
    );
    expect(screen.getByTestId('profile-builder-libraries')).toBeInTheDocument();
    expect(
      screen.queryByText(/No catalog profiles available\./i),
    ).not.toBeInTheDocument();
  });

  it('keeps catalog summary and shows degraded hints when a later reload fails', async () => {
    const user = userEvent.setup();
    render(<ConversionProfilePage accessToken="tok" />);
    await waitFor(() => {
      expect(
        screen.getByTestId('conversion-profiles-inspector-detail'),
      ).toBeInTheDocument();
    });

    fetchProfileCatalog.mockRejectedValueOnce(new Error('reload failed'));
    await user.selectOptions(
      screen.getByTestId('conversion-profiles-select'),
      'US_FAA_NWS',
    );

    await waitFor(() => {
      expect(screen.getByTestId('conversion-profiles-summary')).toHaveTextContent(
        /reload failed/i,
      );
    });
    expect(
      screen.getByTestId('conversion-profiles-summary-primary'),
    ).toBeInTheDocument();
    expect(screen.getByTestId('conversion-profiles-inspector')).toHaveTextContent(
      /reload failed/i,
    );
    expect(screen.getByTestId('conversion-profiles-blocks')).toHaveTextContent(
      /reload failed/i,
    );
  });
});
