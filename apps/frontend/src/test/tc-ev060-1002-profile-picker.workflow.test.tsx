/**
 * T3.1 / TC-EV060-1002 (browser unit): Conversion library labeled at converter top.
 *
 * Spec: docs/test-plan.md TC-EV060-1002-001..003; UJ-061;
 * [Corpus: product §F7] [Corpus: tests].
 */
/* eslint-disable @typescript-eslint/no-explicit-any */
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { FileConverter } from '../app/components/FileConverter';
import { defaultLibraryId } from '../utils/libraryIds';

const mockSignOutWithScope = vi.hoisted(() => vi.fn().mockResolvedValue(true));
const mockConvertMetarToIwxxm = vi.hoisted(() =>
  vi.fn().mockResolvedValue({
    results: [
      {
        name: 'manual_input.txt',
        content: '<iwxxm:METAR>profile</iwxxm:METAR>',
        source: 'manual_input',
        size_bytes: 36,
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
  vi.fn().mockResolvedValue({
    is_valid: true,
    version: '2025-2',
    layers_passed: ['XML_WELLFORMED'],
    layers_failed: [],
    package_ok: true,
    package_issues: [],
  }),
);
const mockToast = vi.hoisted(() => ({
  success: vi.fn(),
  error: vi.fn(),
  warning: vi.fn(),
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
  fetchSelectionOptions: vi
    .fn()
    .mockImplementation(async ({ kind }: { kind: string }) => ({
      kind,
      options: [],
    })),
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

const TAC_SAMPLE = 'METAR KJFK 121251Z 24016G28KT 3SM -RA BR BKN020 OVC040 14/11 A2990';
const XML_SAMPLE =
  '<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2"><ok/></iwxxm:METAR>';

describe('T3.1 / TC-EV060-1002: Conversion library at converter top', () => {
  const defaultProps = {
    onLogout: vi.fn(),
    userEmail: 'profile@example.com',
    accessToken: 'profile-token',
    onSwitchToAdmin: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    vi.stubGlobal(
      'confirm',
      vi.fn(() => true),
    );
  });

  it('shows Product + Conversion library at the converter top without expanding parameters (TC-EV060-1002-001)', () => {
    render(<FileConverter {...defaultProps} />);

    const product = screen.getByTestId('product-type-select');
    const conversion = screen.getByTestId(
      'conversion-library-select',
    ) as HTMLSelectElement;

    expect(product).toBeVisible();
    expect(screen.getByTestId('library-pickers-bar')).toBeVisible();
    expect(conversion).toBeVisible();
    expect(conversion).toHaveAccessibleName(/^conversion$/i);
    expect(screen.getByLabelText(/^conversion$/i)).toBe(conversion);

    const values = Array.from(conversion.options).map((o) => o.value);
    expect(values).toEqual(
      expect.arrayContaining([
        defaultLibraryId('conversion', 'ICAO_2025'),
        defaultLibraryId('conversion', 'US_FAA_NWS'),
        defaultLibraryId('conversion', 'CA_ECCC'),
      ]),
    );
    expect(values).not.toContain(defaultLibraryId('conversion', 'AU_BOM'));
    expect(conversion.value).toBe(defaultLibraryId('conversion', 'ICAO_2025'));
    expect(screen.queryByTestId('profile-type-select')).not.toBeInTheDocument();
  });

  it('exposes a keyboard-accessible Conversion name, not icon-only (TC-EV060-1002-002)', () => {
    render(<FileConverter {...defaultProps} />);

    const product = screen.getByTestId('product-type-select');
    const conversion = screen.getByTestId('conversion-library-select');
    expect(conversion).toHaveAccessibleName(/^conversion$/i);
    expect(conversion.tagName).toBe('SELECT');
    expect(product.parentElement).toContainElement(conversion);
  });

  it('sends selected conversionLibraryId on convert without opening Conversion Parameters (TC-EV060-1002-001)', async () => {
    const user = userEvent.setup();
    render(<FileConverter {...defaultProps} />);

    const conversion = screen.getByTestId('conversion-library-select');
    await user.selectOptions(conversion, defaultLibraryId('conversion', 'US_FAA_NWS'));

    fireEvent.change(screen.getByLabelText(/enter metar data manually/i), {
      target: { value: TAC_SAMPLE },
    });
    await user.click(screen.getByTestId('convert-button'));

    await waitFor(() => {
      expect(mockConvertMetarToIwxxm).toHaveBeenCalledTimes(1);
    });
    expect(mockConvertMetarToIwxxm).toHaveBeenCalledWith(
      expect.objectContaining({
        conversionLibraryId: defaultLibraryId('conversion', 'US_FAA_NWS'),
      }),
    );
  });

  it('sends selected profile on Validate IWXXM after Conversion library change (TC-EV060-1002-001)', async () => {
    const user = userEvent.setup();
    render(<FileConverter {...defaultProps} />);

    await user.selectOptions(
      screen.getByTestId('conversion-library-select'),
      defaultLibraryId('conversion', 'US_FAA_NWS'),
    );
    await user.click(screen.getByTestId('input-mode-validate_iwxxm'));
    fireEvent.change(screen.getByTestId('tac-editor'), {
      target: { value: XML_SAMPLE },
    });
    await user.click(screen.getByRole('button', { name: /validate iwxxm xml/i }));

    await waitFor(() => {
      expect(mockValidateIwxxm).toHaveBeenCalledTimes(1);
    });
    expect(mockValidateIwxxm).toHaveBeenCalledWith(
      expect.objectContaining({
        profile: 'US_FAA_NWS',
        xmlContent: XML_SAMPLE,
      }),
    );
  });

  it('hydrates FileConverter product from a stored session (TC-EV060-1002-003)', () => {
    render(
      <FileConverter
        {...defaultProps}
        loadedWorkSession={
          {
            id: 'sess-profile',
            status: 'wip',
            conversion_params: { product: 'TAF', profile: 'iwxxm_us' },
          } as any
        }
      />,
    );

    expect(screen.getByTestId('product-type-select')).toHaveValue('TAF');
    expect(screen.getByTestId('conversion-library-select')).toBeVisible();
    expect(screen.getByTestId('workbench-profile-summary')).toHaveTextContent(
      'US_FAA_NWS',
    );
  });
});
