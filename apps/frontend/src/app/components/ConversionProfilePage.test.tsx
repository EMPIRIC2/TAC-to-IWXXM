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
          products: ['METAR'],
          emit_key: 'annex3',
        },
        {
          id: 'US_FAA_NWS',
          kind: 'semantic',
          products: [],
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
