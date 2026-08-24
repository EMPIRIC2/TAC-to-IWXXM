/**
 * TC-EV064-005 (browser unit): CA_ECCC profile picker sends ca_eccc on convert.
 *
 * Spec: docs/test-plan.md §TC-EV064-005; #1024 slice.
 */
/* eslint-disable @typescript-eslint/no-explicit-any */
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { FileConverter } from '../app/components/FileConverter';

const mockConvertMetarToIwxxm = vi.hoisted(() =>
  vi.fn().mockResolvedValue({
    results: [
      {
        name: 'manual_input.txt',
        content: '<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/3.0"/>',
        source: 'manual_input',
        size_bytes: 48,
      },
    ],
    errors: [],
    issues: [],
    total_processed: 1,
    successful: 1,
    failed: 0,
  }),
);

vi.mock('/utils/supabase/logout', () => ({
  signOutWithScope: vi.fn().mockResolvedValue(true),
}));

vi.mock('/utils/api', () => ({
  convertMetarToIwxxm: mockConvertMetarToIwxxm,
  convertBulletin: vi.fn(),
  ingestCollect: vi.fn(),
  EndpointNotImplementedError: class extends Error {},
  convertTafToIwxxm: vi.fn(),
  fetchLintIssueCatalog: vi.fn().mockResolvedValue({ issues: [] }),
  fetchSchemaStatus: vi.fn().mockResolvedValue({
    profile_pins: {
      ca_eccc: { extension_bundle_available: true, iwxxm_version: '3.0.0' },
    },
  }),
  lintTac: vi.fn().mockResolvedValue({ ok: true, issues: [], fixes: [] }),
  decodeTac: vi
    .fn()
    .mockResolvedValue({ product: 'METAR', segments: [], residuals: [] }),
  fetchAirportRegion: vi
    .fn()
    .mockResolvedValue({ airport_code: 'CYUL', icao_region: 'NAM' }),
  validateIwxxm: vi.fn(),
}));

vi.mock('../app/components/TacEditor', () => ({
  TacEditor: ({ id, value, onChange, readOnly, 'aria-label': ariaLabel }: any) => (
    <textarea
      id={id}
      value={value}
      readOnly={readOnly}
      aria-label={ariaLabel}
      data-testid="tac-editor"
      onChange={(e) => onChange(e.target.value)}
    />
  ),
}));

vi.mock('../app/components/DecodePanel', () => ({
  DecodePanel: () => null,
}));

vi.mock('sonner', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn(),
    loading: vi.fn(),
    dismiss: vi.fn(),
  },
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

const CA_TAC = 'METAR CYUL 231800Z 24010KT 9999 FEW240 22/12 A3012=';

describe('TC-EV064-005: CA_ECCC profile picker', () => {
  const defaultProps = {
    onLogout: vi.fn(),
    userEmail: 'ca@example.com',
    accessToken: 'token',
    onSwitchToAdmin: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('lists Canada (ECCC) in the profile dropdown', () => {
    render(<FileConverter {...defaultProps} />);
    const profile = screen.getByTestId('profile-type-select') as HTMLSelectElement;
    const values = Array.from(profile.options).map((o) => o.value);
    expect(values).toEqual(expect.arrayContaining(['ca_eccc']));
  });

  it('sends ca_eccc profile and 3.0.0 version on convert', async () => {
    const user = userEvent.setup();
    render(<FileConverter {...defaultProps} />);

    await user.selectOptions(screen.getByTestId('profile-type-select'), 'ca_eccc');
    fireEvent.change(screen.getByLabelText(/enter metar data manually/i), {
      target: { value: CA_TAC },
    });
    await user.click(screen.getByTestId('convert-button'));

    await waitFor(() => {
      expect(mockConvertMetarToIwxxm).toHaveBeenCalledTimes(1);
    });
    expect(mockConvertMetarToIwxxm).toHaveBeenCalledWith(
      expect.objectContaining({
        profile: 'ca_eccc',
        iwxxmVersion: '3.0.0',
      }),
    );
  });

  it('resets IWXXM version to SoT default when leaving ca_eccc profile', async () => {
    const user = userEvent.setup();
    const { container } = render(<FileConverter {...defaultProps} />);
    await user.click(screen.getByLabelText(/expand parameters/i));

    const profile = screen.getByTestId('profile-type-select') as HTMLSelectElement;
    const version = container.querySelector(
      '#param-iwxxm-version',
    ) as HTMLSelectElement;

    await user.selectOptions(profile, 'ca_eccc');
    expect(version.value).toBe('3.0.0');

    await user.selectOptions(profile, 'annex3');
    expect(version.value).not.toBe('3.0.0');
  });

  it('hydrates ca_eccc profile with pinned 3.0.0 from saved preferences', async () => {
    localStorage.setItem(
      'metar_converter_preferences',
      JSON.stringify({
        profile: 'ca_eccc',
        iwxxmVersion: '2025-2',
        bulletinIdExample: 'CYUL01',
        issuingCenter: 'CYUL',
      }),
    );

    const user = userEvent.setup();
    const { container } = render(<FileConverter {...defaultProps} />);
    await user.click(screen.getByLabelText(/expand parameters/i));

    expect((screen.getByTestId('profile-type-select') as HTMLSelectElement).value).toBe(
      'ca_eccc',
    );
    expect(
      (container.querySelector('#param-iwxxm-version') as HTMLSelectElement).value,
    ).toBe('3.0.0');
  });
});
