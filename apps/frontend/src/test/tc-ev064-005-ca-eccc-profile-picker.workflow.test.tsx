/**
 * TC-EV064-005 (browser unit): CA_ECCC Conversion library — M1 ICAO-only product.
 *
 * National CA pins / 3.0.0 IWXXM / profile coercion are dropped. Guest LIB.* ids may
 * still appear in the Conversion select; convert stays on ICAO_2025 + 2025-2.
 *
 * Spec: docs/test-plan.md §TC-EV064-005; FR-019 / M1. [Corpus: product] [Corpus: fr]
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
  fetchSelectionOptions: vi
    .fn()
    .mockImplementation(async ({ kind }: { kind: string }) => ({
      kind,
      options: [],
    })),
  fetchSchemaStatus: vi.fn().mockResolvedValue({
    profile_pins: {},
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
const CA_CONVERSION = defaultLibraryId('conversion', 'CA_ECCC');
const ICAO_CONVERSION = defaultLibraryId('conversion', 'ICAO_2025');

describe('TC-EV064-005: CA_ECCC Conversion library picker (M1 ICAO-only)', () => {
  const defaultProps = {
    onLogout: vi.fn(),
    userEmail: 'ca@example.com',
    accessToken: 'token',
    onSwitchToAdmin: vi.fn(),
  };

  beforeEach(() => {
    vi.stubGlobal(
      'confirm',
      vi.fn(() => true),
    );
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('lists Canada (ECCC) LIB id in guest Conversion fallbacks', () => {
    render(<FileConverter {...defaultProps} />);
    const conversion = screen.getByTestId(
      'conversion-library-select',
    ) as HTMLSelectElement;
    const values = Array.from(conversion.options).map((o) => o.value);
    expect(values).toEqual(expect.arrayContaining([CA_CONVERSION, ICAO_CONVERSION]));
  });

  it('keeps ICAO profile + 2025-2 when CA LIB id is selected on convert', async () => {
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
        iwxxmVersion: '2025-2',
      }),
    );
  });

  it('does not pin IWXXM version to 3.0.0 for CA LIB id', async () => {
    const user = userEvent.setup();
    const { container } = render(<FileConverter {...defaultProps} />);
    await user.click(screen.getByLabelText(/expand parameters/i));

    const conversion = screen.getByTestId(
      'conversion-library-select',
    ) as HTMLSelectElement;
    const version = container.querySelector(
      '#param-iwxxm-version',
    ) as HTMLSelectElement;

    await user.selectOptions(conversion, CA_CONVERSION);
    expect(version.value).toBe('2025-2');
    expect(Array.from(version.options).map((o) => o.value)).toEqual(
      expect.arrayContaining(['2025-2', '2023-1']),
    );
    expect(Array.from(version.options).map((o) => o.value)).not.toContain('3.0.0');
  });

  it('hydrates dropped ca_eccc prefs to ICAO Conversion library', async () => {
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

    expect(
      (screen.getByTestId('conversion-library-select') as HTMLSelectElement).value,
    ).toBe(ICAO_CONVERSION);
    expect(
      (container.querySelector('#param-iwxxm-version') as HTMLSelectElement).value,
    ).toBe('2025-2');
  });
});
