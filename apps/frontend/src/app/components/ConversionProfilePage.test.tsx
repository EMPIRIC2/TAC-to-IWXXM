/**
 * Vitest for ConversionProfile editor page (TC-EV933-001/002 FE).
 */

import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { ConversionProfilePage } from './ConversionProfilePage';
import { CONVERSION_PROFILE_SHARE_BUNDLE_VERSION } from '@/utils/conversionProfileShare';

const fetchProfileCatalog = vi.fn();
const listRulePacks = vi.fn();
const createRulePack = vi.fn();
const listOverlays = vi.fn();
const createOverlay = vi.fn();

vi.mock('@/utils/conversionProfilesApi', () => ({
  fetchProfileCatalog: (...args: unknown[]) => fetchProfileCatalog(...args),
  listRulePacks: (...args: unknown[]) => listRulePacks(...args),
  createRulePack: (...args: unknown[]) => createRulePack(...args),
  listOverlays: (...args: unknown[]) => listOverlays(...args),
  createOverlay: (...args: unknown[]) => createOverlay(...args),
}));

const samplePack = {
  id: '1',
  user_id: 'u',
  slug: 'my-pack',
  profile: 'ICAO_2025',
  product: 'METAR',
  stage: 'lint',
  severity: 'warning',
  when: '',
  message: '',
  standardReference: '',
  created_at: '',
  updated_at: '',
};

const sampleOverlay = {
  id: 'ov-1',
  user_id: 'u',
  slug: 'my-overlay',
  baseProfileId: 'ICAO_2025',
  body: {},
  signature: 'sig',
  shared: false,
  created_at: '',
  updated_at: '',
};

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
    listRulePacks.mockResolvedValue({ items: [samplePack] });
    createRulePack.mockResolvedValue(samplePack);
    listOverlays.mockResolvedValue({ items: [sampleOverlay] });
    createOverlay.mockResolvedValue(sampleOverlay);
  });

  it('prompts sign-in when unauthenticated', async () => {
    const onRequestLogin = vi.fn();
    const user = userEvent.setup();
    render(<ConversionProfilePage onRequestLogin={onRequestLogin} />);
    expect(screen.getByTestId('conversion-profiles-sign-in')).toBeInTheDocument();
    await user.click(screen.getByTestId('conversion-profiles-sign-in'));
    expect(onRequestLogin).toHaveBeenCalled();
  });

  it('loads inspector and saves a rule pack when authenticated', async () => {
    const user = userEvent.setup();
    render(<ConversionProfilePage accessToken="tok" />);

    await waitFor(() => {
      expect(
        screen.getByTestId('conversion-profiles-inspector-detail'),
      ).toBeInTheDocument();
    });
    expect(fetchProfileCatalog).toHaveBeenCalledWith('tok');
    expect(listRulePacks).toHaveBeenCalledWith('tok');
    expect(listOverlays).toHaveBeenCalledWith('tok');
    expect(screen.getByTestId('conversion-profiles-pack-list')).toBeInTheDocument();
    expect(screen.getByTestId('conversion-profiles-overlay-list')).toBeInTheDocument();

    await user.clear(screen.getByTestId('conversion-profiles-pack-slug'));
    await user.type(screen.getByTestId('conversion-profiles-pack-slug'), 'pack-a');
    await user.clear(screen.getByTestId('conversion-profiles-pack-profile'));
    await user.type(
      screen.getByTestId('conversion-profiles-pack-profile'),
      'US_FAA_NWS',
    );
    await user.clear(screen.getByTestId('conversion-profiles-pack-product'));
    await user.type(screen.getByTestId('conversion-profiles-pack-product'), 'TAF');
    await user.clear(screen.getByTestId('conversion-profiles-pack-stage'));
    await user.type(screen.getByTestId('conversion-profiles-pack-stage'), 'validate');
    await user.clear(screen.getByTestId('conversion-profiles-pack-severity'));
    await user.type(screen.getByTestId('conversion-profiles-pack-severity'), 'error');
    await user.type(screen.getByTestId('conversion-profiles-pack-when'), 'x');
    await user.type(screen.getByTestId('conversion-profiles-pack-message'), 'msg');
    await user.type(screen.getByTestId('conversion-profiles-pack-ref'), 'ref');
    await user.click(screen.getByTestId('conversion-profiles-pack-save'));

    await waitFor(() => {
      expect(createRulePack).toHaveBeenCalled();
    });
    const createArgs = createRulePack.mock.calls[0]?.[1] as
      | { slug?: string; profile?: string }
      | undefined;
    expect(createArgs?.slug).toBe('pack-a');
    expect(createArgs?.profile).toBe('US_FAA_NWS');
  });

  it('shows empty catalog and load error', async () => {
    fetchProfileCatalog.mockResolvedValue({ profiles: [] });
    listRulePacks.mockRejectedValue(new Error('boom'));
    render(<ConversionProfilePage accessToken="tok" />);

    await waitFor(() => {
      expect(screen.getByTestId('conversion-profiles-error')).toBeInTheDocument();
    });
    expect(screen.getByTestId('conversion-profiles-error')).toHaveTextContent('boom');
    expect(screen.getByTestId('conversion-profiles-packs')).toHaveTextContent(
      /Rule packs unavailable/i,
    );
  });

  it('shows the empty inspector state when catalog loads without profiles', async () => {
    fetchProfileCatalog.mockResolvedValue({ profiles: [] });
    listRulePacks.mockResolvedValue({ items: [] });
    listOverlays.mockResolvedValue({ items: [] });
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

  it('shows save failure message', async () => {
    const user = userEvent.setup();
    createRulePack.mockRejectedValue(new Error('save failed'));
    render(<ConversionProfilePage accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('conversion-profiles-pack-save')).toBeInTheDocument();
    });
    await user.click(screen.getByTestId('conversion-profiles-pack-save'));
    await waitFor(() => {
      expect(screen.getByText(/save failed/)).toBeInTheDocument();
    });
  });

  it('changes selected profile and exports packs', async () => {
    const user = userEvent.setup();
    const createObjectURL = vi.fn((_blob: Blob) => 'blob:pack');
    const revokeObjectURL = vi.fn();
    vi.stubGlobal('URL', {
      ...URL,
      createObjectURL,
      revokeObjectURL,
    });
    const click = vi.fn();
    const origCreate = document.createElement.bind(document);
    vi.spyOn(document, 'createElement').mockImplementation((tag: string) => {
      const el = origCreate(tag);
      if (tag === 'a') {
        Object.defineProperty(el, 'click', { value: click });
      }
      return el;
    });

    render(<ConversionProfilePage accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('conversion-profiles-pack-list')).toBeInTheDocument();
    });

    await user.selectOptions(
      screen.getByTestId('conversion-profiles-select'),
      'US_FAA_NWS',
    );
    expect(
      screen.getByTestId('conversion-profiles-inspector-detail'),
    ).toBeInTheDocument();

    await user.click(screen.getByTestId('conversion-profiles-export'));
    expect(createObjectURL).toHaveBeenCalled();
    expect(createObjectURL.mock.calls[0]?.[0]).toBeInstanceOf(Blob);
    const blob = createObjectURL.mock.calls[0]![0] as unknown as Blob;
    const exported = JSON.parse(await blob.text()) as {
      schemaVersion: number;
      rulePacks: Array<Record<string, unknown>>;
      overlays: Array<Record<string, unknown>>;
    };
    expect(exported.schemaVersion).toBe(CONVERSION_PROFILE_SHARE_BUNDLE_VERSION);
    expect(exported.rulePacks[0]).toMatchObject({
      slug: 'my-pack',
      profile: 'ICAO_2025',
      product: 'METAR',
    });
    expect(exported.rulePacks[0]).not.toHaveProperty('user_id');
    expect(exported.overlays[0]).toMatchObject({
      slug: 'my-overlay',
      baseProfileId: 'ICAO_2025',
      body: {},
      shared: false,
    });
    expect(exported.overlays[0]).not.toHaveProperty('signature');
    expect(click).toHaveBeenCalled();
    expect(revokeObjectURL).toHaveBeenCalled();
  });

  it('imports a share bundle through the create APIs', async () => {
    const user = userEvent.setup();
    render(<ConversionProfilePage accessToken="tok" />);

    await waitFor(() => {
      expect(screen.getByTestId('conversion-profiles-import')).toBeInTheDocument();
    });

    const file = new File(
      [
        JSON.stringify({
          schemaVersion: CONVERSION_PROFILE_SHARE_BUNDLE_VERSION,
          rulePacks: [
            {
              slug: 'shared-pack',
              profile: 'US_FAA_NWS',
              product: 'METAR',
              stage: 'lint',
              severity: 'warning',
              when: 'RMK',
              message: 'Preserve RMK',
              standardReference: 'FMH-1',
            },
          ],
          overlays: [
            {
              slug: 'shared-overlay',
              baseProfileId: 'US_FAA_NWS',
              body: { note: 'shared' },
              shared: true,
            },
          ],
        }),
      ],
      'profiles-share.json',
      { type: 'application/json' },
    );

    await user.upload(screen.getByTestId('conversion-profiles-import-input'), file);

    await waitFor(() => {
      expect(createRulePack).toHaveBeenCalledWith('tok', {
        slug: 'shared-pack',
        profile: 'US_FAA_NWS',
        product: 'METAR',
        stage: 'lint',
        severity: 'warning',
        when: 'RMK',
        message: 'Preserve RMK',
        standardReference: 'FMH-1',
      });
    });
    expect(createOverlay).toHaveBeenCalledWith('tok', {
      slug: 'shared-overlay',
      baseProfileId: 'US_FAA_NWS',
      body: { note: 'shared' },
      shared: true,
    });
  });

  it('shows an import error for an invalid share bundle', async () => {
    const user = userEvent.setup();
    render(<ConversionProfilePage accessToken="tok" />);

    await waitFor(() => {
      expect(
        screen.getByTestId('conversion-profiles-import-input'),
      ).toBeInTheDocument();
    });

    const file = new File(['{not json'], 'broken-share.json', {
      type: 'application/json',
    });
    await user.upload(screen.getByTestId('conversion-profiles-import-input'), file);

    await waitFor(() => {
      expect(screen.getByTestId('conversion-profiles-error')).toHaveTextContent(
        'Share bundle must be valid JSON',
      );
    });
    expect(createRulePack).not.toHaveBeenCalled();
    expect(createOverlay).not.toHaveBeenCalled();
  });

  it('ignores import changes with no selected file', async () => {
    render(<ConversionProfilePage accessToken="tok" />);

    await waitFor(() => {
      expect(
        screen.getByTestId('conversion-profiles-import-input'),
      ).toBeInTheDocument();
    });

    fireEvent.change(screen.getByTestId('conversion-profiles-import-input'), {
      target: { files: [] },
    });

    await waitFor(() => {
      expect(createRulePack).not.toHaveBeenCalled();
      expect(createOverlay).not.toHaveBeenCalled();
    });
  });

  it('clicks the hidden import input from the import button', async () => {
    const user = userEvent.setup();
    render(<ConversionProfilePage accessToken="tok" />);

    await waitFor(() => {
      expect(screen.getByTestId('conversion-profiles-import')).toBeInTheDocument();
    });

    const input = screen.getByTestId(
      'conversion-profiles-import-input',
    ) as HTMLInputElement;
    const clickSpy = vi.spyOn(input, 'click').mockImplementation(() => {});

    await user.click(screen.getByTestId('conversion-profiles-import'));
    expect(clickSpy).toHaveBeenCalledTimes(1);
  });

  it('exports overlays even when rule packs are unavailable', async () => {
    const user = userEvent.setup();
    const createObjectURL = vi.fn((_blob: Blob) => 'blob:overlay');
    const revokeObjectURL = vi.fn();
    vi.stubGlobal('URL', {
      ...URL,
      createObjectURL,
      revokeObjectURL,
    });
    const click = vi.fn();
    const origCreate = document.createElement.bind(document);
    vi.spyOn(document, 'createElement').mockImplementation((tag: string) => {
      const el = origCreate(tag);
      if (tag === 'a') {
        Object.defineProperty(el, 'click', { value: click });
      }
      return el;
    });
    listRulePacks.mockRejectedValue(new Error('packs offline'));

    render(<ConversionProfilePage accessToken="tok" />);

    await waitFor(() => {
      expect(screen.getByTestId('conversion-profiles-export')).toBeInTheDocument();
    });

    await user.click(screen.getByTestId('conversion-profiles-export'));

    expect(createObjectURL).toHaveBeenCalled();
    const blob = createObjectURL.mock.calls[0]![0] as unknown as Blob;
    const exported = JSON.parse(await blob.text()) as {
      rulePacks: Array<Record<string, unknown>>;
      overlays: Array<Record<string, unknown>>;
    };
    expect(exported.rulePacks).toEqual([]);
    expect(exported.overlays).toHaveLength(1);
    expect(click).toHaveBeenCalled();
    expect(revokeObjectURL).toHaveBeenCalled();
  });

  it('exports rule packs even when overlays are unavailable', async () => {
    const user = userEvent.setup();
    const createObjectURL = vi.fn((_blob: Blob) => 'blob:pack-only');
    const revokeObjectURL = vi.fn();
    vi.stubGlobal('URL', {
      ...URL,
      createObjectURL,
      revokeObjectURL,
    });
    const click = vi.fn();
    const origCreate = document.createElement.bind(document);
    vi.spyOn(document, 'createElement').mockImplementation((tag: string) => {
      const el = origCreate(tag);
      if (tag === 'a') {
        Object.defineProperty(el, 'click', { value: click });
      }
      return el;
    });
    listOverlays.mockRejectedValue(new Error('overlays offline'));

    render(<ConversionProfilePage accessToken="tok" />);

    await waitFor(() => {
      expect(screen.getByTestId('conversion-profiles-export')).toBeInTheDocument();
    });

    await user.click(screen.getByTestId('conversion-profiles-export'));

    expect(createObjectURL).toHaveBeenCalled();
    const blob = createObjectURL.mock.calls[0]![0] as unknown as Blob;
    const exported = JSON.parse(await blob.text()) as {
      rulePacks: Array<Record<string, unknown>>;
      overlays: Array<Record<string, unknown>>;
    };
    expect(exported.rulePacks).toHaveLength(1);
    expect(exported.overlays).toEqual([]);
    expect(click).toHaveBeenCalled();
    expect(revokeObjectURL).toHaveBeenCalled();
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
    expect(screen.getByText(/IWXXM 2025-2 core/)).toBeInTheDocument();
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
    expect(screen.getByTestId('conversion-profiles-examples')).toHaveTextContent(
      /reused from the ICAO \/ WMO demo set/i,
    );
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
    expect(screen.getByTestId('conversion-profiles-block-jump-packs')).toHaveAttribute(
      'href',
      '#conversion-profiles-packs',
    );
    expect(
      screen.getByTestId('conversion-profiles-block-jump-overlays'),
    ).toHaveAttribute('href', '#conversion-profiles-overlays');
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

  it('seeds starter pack and overlay forms only while untouched', async () => {
    const user = userEvent.setup();
    listRulePacks.mockResolvedValue({ items: [] });
    listOverlays.mockResolvedValue({ items: [] });
    render(<ConversionProfilePage accessToken="tok" />);

    await waitFor(() => {
      expect(
        screen.getByTestId('conversion-profiles-pack-profile'),
      ).toBeInTheDocument();
    });

    await user.selectOptions(
      screen.getByTestId('conversion-profiles-select'),
      'US_FAA_NWS',
    );
    expect(screen.getByTestId('conversion-profiles-pack-profile')).toHaveValue(
      'US_FAA_NWS',
    );
    expect(screen.getByTestId('conversion-profiles-overlay-base')).toHaveValue(
      'US_FAA_NWS',
    );

    await user.clear(screen.getByTestId('conversion-profiles-pack-slug'));
    await user.type(screen.getByTestId('conversion-profiles-pack-slug'), 'custom-pack');
    await user.clear(screen.getByTestId('conversion-profiles-overlay-slug'));
    await user.type(
      screen.getByTestId('conversion-profiles-overlay-slug'),
      'custom-overlay',
    );

    await user.selectOptions(
      screen.getByTestId('conversion-profiles-select'),
      'CA_ECCC',
    );
    expect(screen.getByTestId('conversion-profiles-pack-slug')).toHaveValue(
      'custom-pack',
    );
    expect(screen.getByTestId('conversion-profiles-pack-profile')).toHaveValue(
      'US_FAA_NWS',
    );
    expect(screen.getByTestId('conversion-profiles-overlay-slug')).toHaveValue(
      'custom-overlay',
    );
    expect(screen.getByTestId('conversion-profiles-overlay-base')).toHaveValue(
      'US_FAA_NWS',
    );
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
    listRulePacks.mockResolvedValue({ items: [] });
    listOverlays.mockResolvedValue({ items: [] });

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

  it('export is disabled when packs empty', async () => {
    listRulePacks.mockResolvedValue({ items: [] });
    render(<ConversionProfilePage accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('conversion-profiles-export')).toBeDisabled();
    });
  });

  it('saves a signed overlay', async () => {
    const user = userEvent.setup();
    const { fireEvent } = await import('@testing-library/react');
    render(<ConversionProfilePage accessToken="tok" />);
    await waitFor(() => {
      expect(
        screen.getByTestId('conversion-profiles-overlay-save'),
      ).toBeInTheDocument();
    });
    await user.clear(screen.getByTestId('conversion-profiles-overlay-slug'));
    await user.type(screen.getByTestId('conversion-profiles-overlay-slug'), 'ov-a');
    await user.clear(screen.getByTestId('conversion-profiles-overlay-base'));
    await user.type(
      screen.getByTestId('conversion-profiles-overlay-base'),
      'US_FAA_NWS',
    );
    fireEvent.change(screen.getByTestId('conversion-profiles-overlay-body'), {
      target: { value: '{"lint":true}' },
    });
    await user.click(screen.getByTestId('conversion-profiles-overlay-save'));
    await waitFor(() => {
      expect(createOverlay).toHaveBeenCalled();
    });
    const args = createOverlay.mock.calls[0]?.[1] as
      | { slug?: string; baseProfileId?: string; body?: Record<string, unknown> }
      | undefined;
    expect(args?.slug).toBe('ov-a');
    expect(args?.baseProfileId).toBe('US_FAA_NWS');
    expect(args?.body).toEqual({ lint: true });
  });

  it('rejects non-object overlay JSON', async () => {
    const user = userEvent.setup();
    const { fireEvent } = await import('@testing-library/react');
    render(<ConversionProfilePage accessToken="tok" />);
    await waitFor(() => {
      expect(
        screen.getByTestId('conversion-profiles-overlay-body'),
      ).toBeInTheDocument();
    });
    fireEvent.change(screen.getByTestId('conversion-profiles-overlay-body'), {
      target: { value: '[]' },
    });
    await user.click(screen.getByTestId('conversion-profiles-overlay-save'));
    await waitFor(() => {
      expect(screen.getByText(/Overlay JSON must be an object/)).toBeInTheDocument();
    });
    expect(createOverlay).not.toHaveBeenCalled();
  });

  it('rejects invalid overlay JSON syntax', async () => {
    const user = userEvent.setup();
    const { fireEvent } = await import('@testing-library/react');
    render(<ConversionProfilePage accessToken="tok" />);
    await waitFor(() => {
      expect(
        screen.getByTestId('conversion-profiles-overlay-body'),
      ).toBeInTheDocument();
    });
    fireEvent.change(screen.getByTestId('conversion-profiles-overlay-body'), {
      target: { value: '{not-json' },
    });
    await user.click(screen.getByTestId('conversion-profiles-overlay-save'));
    await waitFor(() => {
      expect(screen.getByText(/Overlay JSON must be valid/)).toBeInTheDocument();
    });
    expect(createOverlay).not.toHaveBeenCalled();
  });

  it('treats blank overlay body as empty object', async () => {
    const user = userEvent.setup();
    const { fireEvent } = await import('@testing-library/react');
    render(<ConversionProfilePage accessToken="tok" />);
    await waitFor(() => {
      expect(
        screen.getByTestId('conversion-profiles-overlay-save'),
      ).toBeInTheDocument();
    });
    fireEvent.change(screen.getByTestId('conversion-profiles-overlay-body'), {
      target: { value: '   ' },
    });
    await user.click(screen.getByTestId('conversion-profiles-overlay-save'));
    await waitFor(() => {
      expect(createOverlay).toHaveBeenCalled();
    });
    const args = createOverlay.mock.calls.at(-1)?.[1] as
      | { body?: Record<string, unknown> }
      | undefined;
    expect(args?.body).toEqual({});
  });

  it('shows empty overlays list', async () => {
    listOverlays.mockResolvedValue({ items: [] });
    render(<ConversionProfilePage accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByText(/No overlays yet/)).toBeInTheDocument();
    });
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

  it('keeps catalog summary visible and marks overlays degraded when overlay fetch fails', async () => {
    listOverlays.mockRejectedValue(new Error('overlay fetch failed'));
    render(<ConversionProfilePage accessToken="tok" />);

    await waitFor(() => {
      expect(
        screen.getByTestId('conversion-profiles-summary-primary'),
      ).toBeInTheDocument();
    });

    expect(screen.getByTestId('conversion-profiles-summary-primary')).toHaveTextContent(
      'ICAO_2025',
    );
    expect(screen.getByTestId('conversion-profiles-overlays')).toHaveTextContent(
      /Overlays unavailable/i,
    );
    expect(screen.getByTestId('conversion-profiles-error')).toHaveTextContent(
      /overlay fetch failed/i,
    );
    expect(screen.queryByText(/No overlays yet\./i)).not.toBeInTheDocument();
  });

  it('shows a catalog degraded hint without collapsing the rest of the page', async () => {
    fetchProfileCatalog.mockRejectedValue(new Error('catalog fetch failed'));
    listRulePacks.mockResolvedValue({ items: [samplePack] });
    listOverlays.mockResolvedValue({ items: [sampleOverlay] });
    render(<ConversionProfilePage accessToken="tok" />);

    await waitFor(() => {
      expect(screen.getByTestId('conversion-profiles-summary')).toBeInTheDocument();
    });

    expect(screen.getByTestId('conversion-profiles-summary')).toHaveTextContent(
      /Catalog unavailable/i,
    );
    expect(screen.getByTestId('conversion-profiles-pack-list')).toBeInTheDocument();
    expect(screen.getByTestId('conversion-profiles-overlay-list')).toBeInTheDocument();
    expect(
      screen.queryByText(/No catalog profiles available\./i),
    ).not.toBeInTheDocument();
  });

  it('preserves the last successful catalog view when a save-triggered reload degrades', async () => {
    fetchProfileCatalog
      .mockResolvedValueOnce({
        profiles: [
          {
            id: 'ICAO_2025',
            kind: 'semantic',
            status: 'implemented',
            products: ['METAR'],
            emit_key: 'annex3',
            iwxxm_line: 'IWXXM 2025-2 core',
            rule_pack_count: 1,
            overlay_count: 1,
          },
        ],
      })
      .mockResolvedValueOnce({
        profiles: [
          {
            id: 'ICAO_2025',
            kind: 'semantic',
            status: 'implemented',
            products: ['METAR'],
            emit_key: 'annex3',
            iwxxm_line: 'IWXXM 2025-2 core',
            rule_pack_count: 1,
            overlay_count: 1,
          },
        ],
      })
      .mockRejectedValueOnce(new Error('catalog fetch failed after save'));
    listRulePacks.mockResolvedValue({ items: [] });
    listOverlays.mockResolvedValue({ items: [] });

    const user = userEvent.setup();
    render(<ConversionProfilePage accessToken="tok" />);

    await waitFor(() => {
      expect(
        screen.getByTestId('conversion-profiles-summary-primary'),
      ).toBeInTheDocument();
    });

    expect(screen.getByTestId('conversion-profiles-summary-primary')).toHaveTextContent(
      'ICAO_2025',
    );

    await user.click(screen.getByTestId('conversion-profiles-pack-save'));

    await waitFor(() => {
      expect(createRulePack).toHaveBeenCalled();
    });

    await waitFor(() => {
      expect(screen.getByTestId('conversion-profiles-error')).toHaveTextContent(
        /catalog fetch failed after save/i,
      );
    });

    expect(screen.getByTestId('conversion-profiles-summary-primary')).toHaveTextContent(
      'ICAO_2025',
    );
    expect(
      screen.getByTestId('conversion-profiles-inspector-detail'),
    ).toBeInTheDocument();
  });

  it('preserves the last successful pack and overlay lists when a later reload degrades', async () => {
    listRulePacks
      .mockResolvedValueOnce({ items: [samplePack] })
      .mockResolvedValueOnce({ items: [samplePack] })
      .mockRejectedValueOnce(new Error('pack fetch failed after save'));
    listOverlays
      .mockResolvedValueOnce({ items: [sampleOverlay] })
      .mockResolvedValueOnce({ items: [sampleOverlay] })
      .mockRejectedValueOnce(new Error('overlay fetch failed after save'));

    const user = userEvent.setup();
    render(<ConversionProfilePage accessToken="tok" />);

    await waitFor(() => {
      expect(screen.getByTestId('conversion-profiles-pack-list')).toBeInTheDocument();
    });

    expect(screen.getByTestId('conversion-profiles-pack-list')).toHaveTextContent(
      'my-pack',
    );
    expect(screen.getByTestId('conversion-profiles-overlay-list')).toHaveTextContent(
      'my-overlay',
    );

    await user.click(screen.getByTestId('conversion-profiles-pack-save'));

    await waitFor(() => {
      expect(createRulePack).toHaveBeenCalled();
    });

    await waitFor(() => {
      expect(screen.getByTestId('conversion-profiles-error')).toHaveTextContent(
        /pack fetch failed after save/i,
      );
    });

    expect(screen.getByTestId('conversion-profiles-pack-list')).toHaveTextContent(
      'my-pack',
    );
    expect(screen.getByTestId('conversion-profiles-overlay-list')).toHaveTextContent(
      'my-overlay',
    );
    expect(screen.getByTestId('conversion-profiles-packs')).toHaveTextContent(
      /Rule packs unavailable/i,
    );
    expect(screen.getByTestId('conversion-profiles-overlays')).toHaveTextContent(
      /Overlays unavailable/i,
    );
  });
});
