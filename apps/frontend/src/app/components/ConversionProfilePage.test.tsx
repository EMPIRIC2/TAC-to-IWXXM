/**
 * Vitest for ConversionProfile editor page (TC-EV933-001/002 FE).
 */

import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { ConversionProfilePage } from './ConversionProfilePage';

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
    expect(screen.getByText(/boom/)).toBeInTheDocument();
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
      expect(screen.getByText(/Unknown error/)).toBeInTheDocument();
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
    const createObjectURL = vi.fn(() => 'blob:pack');
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
    expect(click).toHaveBeenCalled();
    expect(revokeObjectURL).toHaveBeenCalled();
  });

  it('renders a summary-first compare view', async () => {
    const user = userEvent.setup();
    render(<ConversionProfilePage accessToken="tok" />);

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
});
