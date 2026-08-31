/**
 * TC-EV073-006..008 — CA_ECCC profile wire: extensions, metadata, vendor pin.
 *
 * Spec: docs/test-plan.md §TC-EV073-006..008; #1042.
 */
/* eslint-disable @typescript-eslint/no-explicit-any */
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { FileConverter } from '../app/components/FileConverter';
import { CA_ECCC_NATIONAL_EXTENSION } from '@/utils/profileWire';

const mockConvertMetarToIwxxm = vi.hoisted(() =>
  vi.fn().mockResolvedValue({
    results: [
      {
        name: 'manual_input.txt',
        content: '<collect:MeteorologicalBulletin/>',
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

const mockValidateIwxxm = vi.hoisted(() =>
  vi.fn().mockResolvedValue({ is_valid: true, issues: [], package_stages: [] }),
);

const mockFetchSchemaStatus = vi.hoisted(() =>
  vi.fn().mockResolvedValue({
    profile_pins: {
      ca_eccc: {
        iwxxm_version: '3.0.0',
        extension_bundle_available: true,
      },
    },
  }),
);

vi.mock('/utils/supabase/logout', () => ({
  signOutWithScope: vi.fn().mockResolvedValue(true),
}));

vi.mock('/utils/api', () => ({
  convertMetarToIwxxm: mockConvertMetarToIwxxm,
  convertBulletin: vi.fn(),
  ingestCollect: vi.fn(),
  fetchSchemaStatus: mockFetchSchemaStatus,
  EndpointNotImplementedError: class extends Error {},
  fetchLintIssueCatalog: vi.fn().mockResolvedValue({ issues: [] }),
  lintTac: vi.fn().mockResolvedValue({ ok: true, issues: [], fixes: [] }),
  decodeTac: vi
    .fn()
    .mockResolvedValue({ product: 'METAR', segments: [], residuals: [] }),
  fetchAirportRegion: vi
    .fn()
    .mockResolvedValue({ airport_code: 'CYUL', icao_region: 'NAM' }),
  validateIwxxm: mockValidateIwxxm,
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

describe('TC-EV073-006..008: CA_ECCC profile wiring', () => {
  const defaultProps = {
    onLogout: vi.fn(),
    userEmail: 'ca@example.com',
    accessToken: 'token',
    onSwitchToAdmin: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    mockFetchSchemaStatus.mockResolvedValue({
      profile_pins: {
        ca_eccc: {
          iwxxm_version: '3.0.0',
          extension_bundle_available: true,
        },
      },
    });
  });

  it('TC-EV073-006 sends IWXXM_CA extension and exchange output on convert', async () => {
    const user = userEvent.setup();
    render(<FileConverter {...defaultProps} />);

    await user.selectOptions(screen.getByTestId('profile-type-select'), 'CA_ECCC');
    fireEvent.change(screen.getByLabelText(/enter metar data manually/i), {
      target: { value: CA_TAC },
    });
    await user.click(screen.getByTestId('convert-button'));

    await waitFor(() => {
      expect(mockConvertMetarToIwxxm).toHaveBeenCalledTimes(1);
    });
    expect(mockConvertMetarToIwxxm).toHaveBeenCalledWith(
      expect.objectContaining({
        profile: 'CA_ECCC',
        extensions: [CA_ECCC_NATIONAL_EXTENSION],
        exchangeOutput: true,
      }),
    );
  });

  it('TC-EV073-006 sends IWXXM_CA on validate-only path', async () => {
    const user = userEvent.setup();
    render(<FileConverter {...defaultProps} />);

    await user.selectOptions(screen.getByTestId('profile-type-select'), 'CA_ECCC');
    await user.click(screen.getByTestId('input-mode-validate_iwxxm'));
    fireEvent.change(screen.getByTestId('tac-editor'), {
      target: { value: '<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/3.0"/>' },
    });
    await user.click(screen.getByRole('button', { name: /validate iwxxm xml/i }));

    await waitFor(() => {
      expect(mockValidateIwxxm).toHaveBeenCalled();
    });
    expect(mockValidateIwxxm).toHaveBeenCalledWith(
      expect.objectContaining({
        profile: 'CA_ECCC',
        extensions: [CA_ECCC_NATIONAL_EXTENSION],
      }),
    );
  });

  it('TC-EV073-007 surfaces operator profile metadata when CA_ECCC selected', async () => {
    const user = userEvent.setup();
    render(<FileConverter {...defaultProps} />);

    await user.selectOptions(screen.getByTestId('profile-type-select'), 'CA_ECCC');

    const panel = screen.getByTestId('ca-eccc-profile-metadata');
    expect(panel).toHaveTextContent('3.0.0');
    expect(panel).toHaveTextContent('Canadian national IWXXM extensions');
    expect(panel).toHaveTextContent('METAR');
    expect(panel).toHaveTextContent('AIRMET');
    expect(panel.textContent).not.toMatch(/EV-|TC-|ADR-/);
  });

  it('TC-EV073-008 blocks convert when extension bundle unavailable', async () => {
    mockFetchSchemaStatus.mockResolvedValue({
      profile_pins: {
        ca_eccc: {
          iwxxm_version: '3.0.0',
          extension_bundle_available: false,
        },
      },
    });

    const user = userEvent.setup();
    render(<FileConverter {...defaultProps} />);

    await waitFor(() => {
      expect(mockFetchSchemaStatus).toHaveBeenCalled();
    });

    await user.selectOptions(screen.getByTestId('profile-type-select'), 'CA_ECCC');
    fireEvent.change(screen.getByLabelText(/enter metar data manually/i), {
      target: { value: CA_TAC },
    });

    const convertButton = screen.getByTestId('convert-button');
    expect(convertButton).toBeDisabled();
    expect(screen.getByTestId('ca-eccc-profile-metadata')).toHaveTextContent(
      'Conversion is blocked',
    );
  });

  it('TC-EV073-008 allows convert when schema-status fetch fails (fail-open)', async () => {
    mockFetchSchemaStatus.mockRejectedValue(new Error('network'));

    const user = userEvent.setup();
    render(<FileConverter {...defaultProps} />);

    await waitFor(() => {
      expect(mockFetchSchemaStatus).toHaveBeenCalled();
    });

    await user.selectOptions(screen.getByTestId('profile-type-select'), 'CA_ECCC');
    fireEvent.change(screen.getByLabelText(/enter metar data manually/i), {
      target: { value: CA_TAC },
    });

    expect(screen.getByTestId('convert-button')).not.toBeDisabled();
  });

  it('ignores late schema-status response after unmount', async () => {
    let resolveStatus: (value: unknown) => void = () => undefined;
    mockFetchSchemaStatus.mockImplementation(
      () =>
        new Promise((resolve) => {
          resolveStatus = resolve;
        }),
    );

    const { unmount } = render(<FileConverter {...defaultProps} />);
    unmount();

    resolveStatus({
      profile_pins: {
        ca_eccc: { extension_bundle_available: false, iwxxm_version: '3.0.0' },
      },
    });

    await Promise.resolve();
  });
});
