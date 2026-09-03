/**
 * Vitest for ConversionProfile editor page (TC-EV933-001/002 FE).
 */

import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { ConversionProfilePage } from './ConversionProfilePage';

const fetchProfileCatalog = vi.fn();
const listRulePacks = vi.fn();
const createRulePack = vi.fn();

vi.mock('@/utils/conversionProfilesApi', () => ({
  fetchProfileCatalog: (...args: unknown[]) => fetchProfileCatalog(...args),
  listRulePacks: (...args: unknown[]) => listRulePacks(...args),
  createRulePack: (...args: unknown[]) => createRulePack(...args),
}));

describe('ConversionProfilePage', () => {
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
      ],
    });
    listRulePacks.mockResolvedValue({ items: [] });
    createRulePack.mockResolvedValue({
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

    await user.clear(screen.getByTestId('conversion-profiles-pack-slug'));
    await user.type(screen.getByTestId('conversion-profiles-pack-slug'), 'pack-a');
    await user.click(screen.getByTestId('conversion-profiles-pack-save'));

    await waitFor(() => {
      expect(createRulePack).toHaveBeenCalled();
    });
    const createArgs = createRulePack.mock.calls[0]?.[1] as
      | { slug?: string }
      | undefined;
    expect(createArgs?.slug).toBe('pack-a');
  });
});
