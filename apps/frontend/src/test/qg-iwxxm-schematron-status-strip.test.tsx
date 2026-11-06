/**
 * QA-gap QG-iwxxm-schematron-not-run: Results Console schema/Schematron pills.
 *
 * Soft-preview / live IWXXM keep validate_output off (expected). Hard Convert with
 * Strict Validation should surface schema/Schematron on the status strip once wired;
 * FileConverter currently hardcodes both to "not run".
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
        content:
          '<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2">ok</iwxxm:METAR>',
        iwxxm_xml:
          '<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2">ok</iwxxm:METAR>',
        source: 'manual_input',
        size_bytes: 64,
      },
    ],
    errors: [],
    issues: [],
    ok: true,
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
  ConvertApiError: class extends Error {},
  ingestCollect: vi.fn(),
  EndpointNotImplementedError: class extends Error {},
  convertTafToIwxxm: vi.fn().mockResolvedValue({ success: true, data: '<iwxxm />' }),
  fetchLintIssueCatalog: vi.fn().mockResolvedValue({ issues: [] }),
  fetchSchemaStatus: vi.fn().mockResolvedValue({
    profile_pins: {
      ca_eccc: { extension_bundle_available: true, iwxxm_version: '3.0.0' },
    },
  }),
  lintTac: vi.fn().mockResolvedValue({ ok: true, issues: [], fixes: [] }),
  decodeTac: vi.fn().mockResolvedValue({
    product: 'METAR',
    segments: [{ start: 0, end: 5, code: 'METAR', explanation: 'type' }],
    residuals: [],
    summary: '',
  }),
  validateIwxxm: vi.fn(),
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
  toast: {
    success: vi.fn(),
    error: vi.fn(),
    loading: vi.fn(),
    dismiss: vi.fn(),
    promise: vi.fn(),
    info: vi.fn(),
    warning: vi.fn(),
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

const TAC = 'METAR KJFK 121251Z 18004KT 10SM FEW020 18/12 A3012=';

const defaultProps = {
  onLogout: vi.fn(),
  userEmail: 'qg-schematron@example.com',
  accessToken: 'qg-token',
  onSwitchToAdmin: vi.fn(),
};

async function openExpandedParameters(
  user: ReturnType<typeof userEvent.setup>,
): Promise<void> {
  await user.click(screen.getByTestId('convert-settings-cog'));
  await user.click(screen.getByLabelText(/expand parameters/i));
}

describe('QG-iwxxm-schematron-not-run: Console schema/Schematron pills', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    sessionStorage.clear();
    sessionStorage.setItem(
      'metar_guest_converter_state',
      JSON.stringify({
        manualInput: TAC,
        pendingFiles: [],
        convertedFiles: [],
        conversionLog: null,
        conversionParams: {},
      }),
    );
  });

  it('soft-preview Convert leaves schema/Schematron idle (validate_output off)', async () => {
    const user = userEvent.setup({ delay: null });
    render(<FileConverter {...defaultProps} />);

    // Avoid live debounce convert; exercise soft-preview hard-button path.
    if ((screen.getByTestId('live-iwxxm-toggle') as HTMLInputElement).checked) {
      await user.click(screen.getByTestId('live-iwxxm-toggle'));
    }
    await user.click(screen.getByTestId('soft-preview-toggle'));
    expect(screen.getByTestId('soft-preview-toggle')).toBeChecked();

    fireEvent.change(screen.getByTestId('tac-editor'), {
      target: { value: TAC },
    });
    await user.click(screen.getByTestId('convert-button'));

    await waitFor(() => {
      expect(mockConvertMetarToIwxxm).toHaveBeenCalled();
    });
    const lastCall = mockConvertMetarToIwxxm.mock.calls.at(-1)?.[0] as {
      validateOutput?: boolean;
      preview?: boolean;
    };
    expect(lastCall.validateOutput).toBe(false);
    expect(lastCall.preview).toBe(true);

    await user.click(screen.getByTestId('convert-results-tab-console'));
    const strip = screen.getByTestId('convert-status-strip');
    expect(strip).toHaveTextContent('XML schema: not run yet');
    expect(strip).toHaveTextContent('Schematron: not run yet');
    expect(screen.getByText('XML schema: not run yet')).toHaveAttribute(
      'title',
      'It runs when you validate.',
    );
  });

  it('hard Convert with Strict Validation flips Console schema/Schematron off idle', async () => {
    const user = userEvent.setup({ delay: null });
    render(<FileConverter {...defaultProps} />);

    if ((screen.getByTestId('live-iwxxm-toggle') as HTMLInputElement).checked) {
      await user.click(screen.getByTestId('live-iwxxm-toggle'));
    }
    expect(screen.getByTestId('soft-preview-toggle')).not.toBeChecked();

    await openExpandedParameters(user);
    const strict = screen.getByTestId('strict-validation-checkbox');
    if (!(strict as HTMLInputElement).checked) {
      await user.click(strict);
    }

    mockConvertMetarToIwxxm.mockResolvedValueOnce({
      results: [
        {
          name: 'manual_input.txt',
          content:
            '<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2">ok</iwxxm:METAR>',
          iwxxm_xml:
            '<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2">ok</iwxxm:METAR>',
          source: 'manual_input',
          size_bytes: 64,
        },
      ],
      errors: [],
      issues: [],
      ok: true,
      total_processed: 1,
      successful: 1,
      failed: 0,
    });

    await user.click(screen.getByTestId('convert-button'));
    await waitFor(() => {
      expect(mockConvertMetarToIwxxm).toHaveBeenCalled();
    });
    const hardCall = mockConvertMetarToIwxxm.mock.calls.at(-1)?.[0] as {
      validateOutput?: boolean;
      preview?: boolean;
      validationLevel?: string;
    };
    expect(hardCall.preview).toBe(false);
    expect(hardCall.validateOutput).toBe(true);
    expect(hardCall.validationLevel).toBe('comprehensive');

    await user.click(screen.getByTestId('convert-results-tab-console'));
    const strip = screen.getByTestId('convert-status-strip');
    expect(strip).not.toHaveTextContent('XML schema: not run yet');
    expect(strip).not.toHaveTextContent('Schematron: not run yet');
    expect(strip).toHaveTextContent('XML schema: passed');
    expect(strip).toHaveTextContent('Schematron: passed');
  });
});
