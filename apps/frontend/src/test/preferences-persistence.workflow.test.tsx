/* eslint-disable @typescript-eslint/no-explicit-any */
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { FileConverter } from '../app/components/FileConverter';

const mockSignOutWithScope = vi.hoisted(() => vi.fn().mockResolvedValue(true));
const mockConvertMetarToIwxxm = vi.hoisted(() => vi.fn().mockResolvedValue({ results: [] }));
const mockToast = vi.hoisted(() => ({
  success: vi.fn(),
  error: vi.fn(),
  loading: vi.fn(),
  dismiss: vi.fn(),
  promise: vi.fn(),
  info: vi.fn(),
}));

vi.mock('/utils/supabase/logout', () => ({
  signOutWithScope: mockSignOutWithScope,
}));

vi.mock('/utils/api', () => ({
  convertMetarToIwxxm: mockConvertMetarToIwxxm,
  convertTafToIwxxm: vi.fn().mockResolvedValue({ success: true, data: '<iwxxm />' }),
}));

vi.mock('sonner', () => ({
  toast: mockToast,
}));

vi.mock('../app/components/IcaoAutocomplete', () => ({
  IcaoAutocomplete: ({ value, onChange, id }: any) => (
    <input
      id={id}
      data-testid="icao-autocomplete"
      value={value}
      onChange={(e) => onChange(e.target.value)}
    />
  ),
}));

describe('UI Workflow: Preferences Persistence', () => {
  const defaultProps = {
    onLogout: vi.fn(),
    userEmail: 'workflow@example.com',
    accessToken: 'workflow-token',
    onSwitchToAdmin: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('loads persisted preferences into converter controls on initial mount', async () => {
    localStorage.setItem(
      'metar_converter_preferences',
      JSON.stringify({
        bulletinIdExample: 'BBBB01',
        issuingCenter: 'KDEN',
        iwxxmVersion: '2023-1',
        strictValidation: false,
        includeNilReasons: false,
        onError: 'fail',
        logLevel: 'ERROR',
      })
    );

    const user = userEvent.setup();
    const { container } = render(<FileConverter {...defaultProps} />);

    await user.click(screen.getByLabelText(/expand parameters/i));

    const iwxxmVersion = container.querySelector('#param-iwxxm-version') as HTMLSelectElement;
    const onError = container.querySelector('#param-on-error') as HTMLSelectElement;
    const bulletinId = container.querySelector('#param-bulletin-id') as HTMLInputElement;
    const issuingCenter = container.querySelector('#param-issuing-center') as HTMLInputElement;

    expect(iwxxmVersion.value).toBe('2023-1');
    expect(onError.value).toBe('fail');
    expect(bulletinId.value).toBe('BBBB01');
    expect(issuingCenter.value).toBe('KDEN');
  });

  it('applies saved preferences from dialog callback and updates converter parameters', async () => {
    const user = userEvent.setup();
    const { container } = render(<FileConverter {...defaultProps} />);

    await user.click(screen.getByLabelText(/expand parameters/i));

    const iwxxmVersion = container.querySelector('#param-iwxxm-version') as HTMLSelectElement;
    expect(iwxxmVersion.value).toBe('2025-2');

    localStorage.setItem(
      'metar_converter_preferences',
      JSON.stringify({
        bulletinIdExample: 'CCCC02',
        issuingCenter: 'KJFK',
        iwxxmVersion: '2023-1',
        strictValidation: true,
        includeNilReasons: true,
        onError: 'skip',
        logLevel: 'DEBUG',
      })
    );

    await user.click(screen.getByRole('button', { name: /open user preferences/i }));
    await user.click(screen.getByRole('button', { name: /save preferences/i }));

    await waitFor(() => {
      expect(iwxxmVersion.value).toBe('2023-1');
      expect(mockToast.info).toHaveBeenCalledWith('Conversion parameters updated from preferences');
    });
  });

  it('migrates unsupported iwxxmVersion values to 2025-2 during preference reload', async () => {
    const user = userEvent.setup();
    const { container } = render(<FileConverter {...defaultProps} />);

    await user.click(screen.getByLabelText(/expand parameters/i));

    localStorage.setItem(
      'metar_converter_preferences',
      JSON.stringify({
        bulletinIdExample: 'DDDD03',
        issuingCenter: 'EGLL',
        iwxxmVersion: '2.1',
        strictValidation: true,
        includeNilReasons: true,
        onError: 'warn',
        logLevel: 'INFO',
      })
    );

    await user.click(screen.getByRole('button', { name: /open user preferences/i }));
    await user.click(screen.getByRole('button', { name: /save preferences/i }));

    const iwxxmVersion = container.querySelector('#param-iwxxm-version') as HTMLSelectElement;
    await waitFor(() => {
      expect(iwxxmVersion.value).toBe('2025-2');
    });
  });
});
