/**
 * TC-EV073-006..008 — CA_ECCC wire paths after M1 ICAO-only drop.
 *
 * Selecting a CA LIB id no longer auto-wires IWXXM_CA, exchange output, CA metadata,
 * or extension-bundle convert blocks. Profile coerces to ICAO_2025.
 *
 * Spec: docs/test-plan.md §TC-EV073-006..008; FR-019 / M1. [Corpus: fr]
 */
/* eslint-disable @typescript-eslint/no-explicit-any */
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { FileConverter } from '../app/components/FileConverter';
import { defaultLibraryId } from '../utils/libraryIds';

const mockConvertMetarToIwxxm = vi.hoisted(() =>
  vi.fn().mockResolvedValue({
    results: [
      {
        name: 'manual_input.txt',
        content: '<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2"/>',
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
        extension_bundle_available: false,
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
  fetchSelectionOptions: vi
    .fn()
    .mockImplementation(async ({ kind }: { kind: string }) => ({
      kind,
      options: [],
    })),
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
const CA_CONVERSION = defaultLibraryId('conversion', 'CA_ECCC');

beforeEach(() => {
  vi.stubGlobal(
    'confirm',
    vi.fn(() => true),
  );
});

describe('TC-EV073-006..008: CA_ECCC Conversion library wiring (M1 ICAO-only)', () => {
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
          extension_bundle_available: false,
        },
      },
    });
  });

  it('TC-EV073-006 does not send IWXXM_CA or exchange output on convert', async () => {
    const user = userEvent.setup();
    render(<FileConverter {...defaultProps} />);
    fireEvent.click(screen.getByTestId('live-iwxxm-toggle'));

    await user.selectOptions(
      screen.getByTestId('conversion-library-select'),
      CA_CONVERSION,
    );
    fireEvent.change(screen.getByLabelText(/enter metar data manually/i), {
      target: { value: CA_TAC },
    });
    await user.click(screen.getByTestId('convert-button'));

    await waitFor(() => {
      expect(mockConvertMetarToIwxxm).toHaveBeenCalledTimes(1);
    });
    expect(mockConvertMetarToIwxxm).toHaveBeenCalledWith(
      expect.objectContaining({
        conversionLibraryId: CA_CONVERSION,
        profile: 'ICAO_2025',
        extensions: [],
        exchangeOutput: false,
      }),
    );
  });

  it('TC-EV073-006 validate-only path uses ICAO_2025 without IWXXM_CA', async () => {
    const user = userEvent.setup();
    render(<FileConverter {...defaultProps} />);

    await user.selectOptions(
      screen.getByTestId('conversion-library-select'),
      CA_CONVERSION,
    );
    await user.click(screen.getByTestId('input-mode-validate_iwxxm'));
    fireEvent.change(screen.getByTestId('tac-editor'), {
      target: { value: '<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2"/>' },
    });
    await user.click(screen.getByRole('button', { name: /validate iwxxm xml/i }));

    await waitFor(() => {
      expect(mockValidateIwxxm).toHaveBeenCalled();
    });
    expect(mockValidateIwxxm).toHaveBeenCalledWith(
      expect.objectContaining({
        profile: 'ICAO_2025',
        extensions: [],
      }),
    );
  });

  it('TC-EV073-007 does not surface CA_ECCC operator profile metadata', async () => {
    const user = userEvent.setup();
    render(<FileConverter {...defaultProps} />);

    await user.selectOptions(
      screen.getByTestId('conversion-library-select'),
      CA_CONVERSION,
    );

    expect(screen.queryByTestId('ca-eccc-profile-metadata')).not.toBeInTheDocument();
  });

  it('TC-EV073-008 does not block convert when CA extension bundle unavailable', async () => {
    const user = userEvent.setup();
    render(<FileConverter {...defaultProps} />);

    await waitFor(() => {
      expect(mockFetchSchemaStatus).toHaveBeenCalled();
    });

    await user.selectOptions(
      screen.getByTestId('conversion-library-select'),
      CA_CONVERSION,
    );
    fireEvent.change(screen.getByLabelText(/enter metar data manually/i), {
      target: { value: CA_TAC },
    });

    expect(screen.getByTestId('convert-button')).not.toBeDisabled();
    expect(screen.queryByTestId('ca-eccc-profile-metadata')).not.toBeInTheDocument();
  });
});
