/* eslint-disable @typescript-eslint/no-explicit-any */
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { FileConverter } from '../app/components/FileConverter';

const mockSignOutWithScope = vi.hoisted(() => vi.fn().mockResolvedValue(true));
const mockConvertMetarToIwxxm = vi.hoisted(() =>
  vi.fn().mockResolvedValue({
    results: [
      {
        name: 'manual_input.txt',
        content: '<iwxxm:METAR>mapped</iwxxm:METAR>',
        source: 'manual_input',
        size_bytes: 29,
      },
    ],
    errors: [],
    issues: [],
    total_processed: 1,
    successful: 1,
    failed: 0,
  }),
);
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
  convertBulletin: vi.fn(),
  ingestCollect: vi.fn(),
  EndpointNotImplementedError: class extends Error {},
  convertTafToIwxxm: vi.fn().mockResolvedValue({ success: true, data: '<iwxxm />' }),
  fetchLintIssueCatalog: vi.fn().mockResolvedValue({ issues: [] }),
  fetchSchemaStatus: vi.fn().mockResolvedValue({
    profile_pins: {
      ca_eccc: { extension_bundle_available: true, iwxxm_version: '3.0.0' },
    },
  }),
  lintTac: vi.fn().mockResolvedValue({
    ok: true,
    issues: [],
    fixes: [],
  }),
  decodeTac: vi
    .fn()
    .mockResolvedValue({ product: 'METAR', segments: [], residuals: [] }),
  fetchAirportRegion: vi
    .fn()
    .mockResolvedValue({ airport_code: 'KJFK', icao_region: 'NAM' }),
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

describe('UI Workflow: Conversion Parameter Mapping', () => {
  const defaultProps = {
    onLogout: vi.fn(),
    userEmail: 'mapping@example.com',
    accessToken: 'mapping-token',
    onSwitchToAdmin: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('sends selected IWXXM version in conversion API payload', async () => {
    const user = userEvent.setup();
    const { container } = render(<FileConverter {...defaultProps} />);

    await user.click(screen.getByLabelText(/expand parameters/i));

    const iwxxmVersion = container.querySelector(
      '#param-iwxxm-version',
    ) as HTMLSelectElement;
    await user.selectOptions(iwxxmVersion, '2023-1');

    const manualInput = screen.getByLabelText(/enter metar data manually/i);
    fireEvent.change(manualInput, {
      target: {
        value: 'METAR KJFK 121251Z 24016G28KT 3SM -RA BR BKN020 OVC040 14/11 A2990',
      },
    });

    await user.click(screen.getByTestId('convert-button'));

    await waitFor(() => {
      expect(mockConvertMetarToIwxxm).toHaveBeenCalledTimes(1);
    });

    expect(mockConvertMetarToIwxxm).toHaveBeenCalledWith(
      expect.objectContaining({
        manualText:
          'METAR KJFK 121251Z 24016G28KT 3SM -RA BR BKN020 OVC040 14/11 A2990',
        iwxxmVersion: '2023-1',
        validateOutput: true,
        validationLevel: 'comprehensive',
        stopOnError: false,
      }),
    );
    expect(mockConvertMetarToIwxxm.mock.calls[0]?.[0]).not.toHaveProperty(
      'accessToken',
    );
  });

  it('maps bulletin, issuing centre, onError fail, and soft-preview validation off', async () => {
    const user = userEvent.setup();
    const { container } = render(<FileConverter {...defaultProps} />);

    await user.click(screen.getByLabelText(/expand parameters/i));

    const bulletinId = container.querySelector(
      '#param-bulletin-id',
    ) as HTMLInputElement;
    await user.clear(bulletinId);
    await user.type(bulletinId, 'saaa00');

    const onError = container.querySelector('#param-on-error') as HTMLSelectElement;
    await user.selectOptions(onError, 'fail');

    fireEvent.click(screen.getByTestId('soft-preview-toggle'));

    fireEvent.change(screen.getByLabelText(/enter metar data manually/i), {
      target: {
        value: 'METAR KJFK 121251Z 24016G28KT 10SM FEW250 14/11 A2990',
      },
    });

    await user.click(screen.getByTestId('convert-button'));

    await waitFor(() => {
      expect(mockConvertMetarToIwxxm).toHaveBeenCalledTimes(1);
    });

    expect(mockConvertMetarToIwxxm).toHaveBeenCalledWith(
      expect.objectContaining({
        bulletinId: 'SAAA00',
        stopOnError: true,
        preview: true,
        validateOutput: false,
        validationLevel: 'basic',
      }),
    );
  });

  it('maps default parameters from saved preferences before conversion', async () => {
    localStorage.setItem(
      'metar_converter_preferences',
      JSON.stringify({
        bulletinIdExample: 'ABCD12',
        issuingCenter: 'KLAX',
        iwxxmVersion: '2023-1',
        strictValidation: false,
        includeNilReasons: false,
        onError: 'skip',
        logLevel: 'DEBUG',
      }),
    );

    const user = userEvent.setup();
    const { container } = render(<FileConverter {...defaultProps} />);

    await user.click(screen.getByLabelText(/expand parameters/i));

    const bulletinId = container.querySelector(
      '#param-bulletin-id',
    ) as HTMLInputElement;
    const issuingCenter = container.querySelector(
      '#param-issuing-center',
    ) as HTMLInputElement;
    const iwxxmVersion = container.querySelector(
      '#param-iwxxm-version',
    ) as HTMLSelectElement;
    const onError = container.querySelector('#param-on-error') as HTMLSelectElement;
    const logLevel = container.querySelector('#param-log-level') as HTMLSelectElement;

    expect(bulletinId.value).toBe('ABCD12');
    expect(issuingCenter.value).toBe('KLAX');
    expect(iwxxmVersion.value).toBe('2023-1');
    expect(onError.value).toBe('skip');
    expect(logLevel.value).toBe('DEBUG');
  });

  it('updates mapped payload when user changes version after preferences load', async () => {
    localStorage.setItem(
      'metar_converter_preferences',
      JSON.stringify({
        bulletinIdExample: 'WXYZ34',
        issuingCenter: 'KSEA',
        iwxxmVersion: '2023-1',
        strictValidation: true,
        includeNilReasons: true,
        onError: 'warn',
        logLevel: 'INFO',
      }),
    );

    const user = userEvent.setup();
    const { container } = render(<FileConverter {...defaultProps} />);

    await user.click(screen.getByLabelText(/expand parameters/i));
    const iwxxmVersion = container.querySelector(
      '#param-iwxxm-version',
    ) as HTMLSelectElement;
    await user.selectOptions(iwxxmVersion, '2025-2');

    fireEvent.change(screen.getByLabelText(/enter metar data manually/i), {
      target: { value: 'METAR KDEN 121653Z 02006KT 10SM SCT050 21/08 A3010' },
    });

    await user.click(screen.getByTestId('convert-button'));

    await waitFor(() => {
      expect(mockConvertMetarToIwxxm).toHaveBeenCalledTimes(1);
    });

    expect(mockConvertMetarToIwxxm).toHaveBeenCalledWith(
      expect.objectContaining({
        iwxxmVersion: '2025-2',
      }),
    );
  });
});
