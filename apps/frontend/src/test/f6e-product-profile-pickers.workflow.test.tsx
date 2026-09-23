/**
 * T8.1 / TC-F6-001 (browser unit): F6.e product + Conversion library + version pickers.
 *
 * Spec: docs/feature-list.md F6.e; docs/user-journeys.md UJ-005;
 * docs/test-plan.md TC-F6-001; docs/spec.md §apps/frontend F6 delta.
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
        content: '<iwxxm:METAR>f6e</iwxxm:METAR>',
        source: 'manual_input',
        size_bytes: 32,
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

const PRODUCTS = [
  'auto',
  'AIRMET',
  'METAR',
  'SIGMET',
  'SPECI',
  'TAF',
  'VAA',
  'TCA',
  'SWXA',
  'VONA',
] as const;

const GUEST_CONVERSION_IDS = [
  defaultLibraryId('conversion', 'ICAO_2025'),
  defaultLibraryId('conversion', 'US_FAA_NWS'),
  defaultLibraryId('conversion', 'CA_ECCC'),
] as const;

describe('T8.1 / TC-F6-001: F6.e product + Conversion library + version pickers', () => {
  beforeEach(() => {
    vi.stubGlobal(
      'confirm',
      vi.fn(() => true),
    );
  });

  const defaultProps = {
    onLogout: vi.fn(),
    userEmail: 'f6e@example.com',
    accessToken: 'f6e-token',
    onSwitchToAdmin: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('renders product type next to TAC; Conversion library and version when parameters are expanded', async () => {
    const user = userEvent.setup();
    render(<FileConverter {...defaultProps} />);

    const product = screen.getByTestId('product-type-select') as HTMLSelectElement;
    expect(product).toBeInTheDocument();

    const productValues = Array.from(product.options).map((o) => o.value);
    for (const p of PRODUCTS) {
      expect(productValues).toContain(p);
    }

    const conversion = screen.getByTestId(
      'conversion-library-select',
    ) as HTMLSelectElement;
    expect(conversion).toBeVisible();
    expect(screen.getByTestId('library-pickers-bar')).toBeVisible();

    await user.click(screen.getByLabelText(/expand parameters/i));

    const version = screen.getByLabelText(/iwxxm version/i) as HTMLSelectElement;

    expect(conversion).toBeInTheDocument();
    expect(version).toBeInTheDocument();

    const conversionValues = Array.from(conversion.options).map((o) => o.value);
    for (const id of GUEST_CONVERSION_IDS) {
      expect(conversionValues).toContain(id);
    }

    expect(product.value).toBe('auto');
    expect(conversion.value).toBe(defaultLibraryId('conversion', 'ICAO_2025'));
    expect(version.value).toBe('2025-2');

    // UJ-050 / TC-EV038-007 — Latest / Previous labels from SoT JSON roles (#854)
    const versionLabels = Array.from(version.options).map((o) => o.textContent ?? '');
    expect(versionLabels.some((t) => t.includes('(Latest)'))).toBe(true);
    expect(versionLabels.some((t) => t.includes('(Previous)'))).toBe(true);
  });

  it('sends selected product, conversionLibraryId, and version on convert (ICAO METAR)', async () => {
    const user = userEvent.setup();
    const { container } = render(<FileConverter {...defaultProps} />);

    await user.click(screen.getByLabelText(/expand parameters/i));

    const product = container.querySelector('#param-product') as HTMLSelectElement;
    const conversion = screen.getByTestId(
      'conversion-library-select',
    ) as HTMLSelectElement;
    const version = container.querySelector(
      '#param-iwxxm-version',
    ) as HTMLSelectElement;

    await user.selectOptions(product, 'METAR');
    await user.selectOptions(conversion, defaultLibraryId('conversion', 'ICAO_2025'));
    await user.selectOptions(version, '2023-1');

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
        product: 'METAR',
        conversionLibraryId: defaultLibraryId('conversion', 'ICAO_2025'),
        iwxxmVersion: '2023-1',
        // EV-1051: signed-in convert always forwards Bearer (preset_id auth).
        accessToken: 'f6e-token',
      }),
    );
  });

  it('sends US_FAA_NWS conversionLibraryId when selected', async () => {
    const user = userEvent.setup();
    const { container } = render(<FileConverter {...defaultProps} />);

    await user.click(screen.getByLabelText(/expand parameters/i));

    const product = container.querySelector('#param-product') as HTMLSelectElement;
    const conversion = screen.getByTestId(
      'conversion-library-select',
    ) as HTMLSelectElement;

    await user.selectOptions(product, 'TAF');
    await user.selectOptions(conversion, defaultLibraryId('conversion', 'US_FAA_NWS'));

    const manualInput = screen.getByLabelText(/enter metar data manually/i);
    fireEvent.change(manualInput, {
      target: {
        value:
          'TAF KJFK 121730Z 1218/1324 24012KT P6SM SCT040 BKN080 FM130000 25015G25KT',
      },
    });

    await user.click(screen.getByTestId('convert-button'));

    await waitFor(() => {
      expect(mockConvertMetarToIwxxm).toHaveBeenCalledTimes(1);
    });

    expect(mockConvertMetarToIwxxm).toHaveBeenCalledWith(
      expect.objectContaining({
        product: 'TAF',
        conversionLibraryId: defaultLibraryId('conversion', 'US_FAA_NWS'),
      }),
    );
  });

  it('auto product resolves to detected keyword before API call', async () => {
    const user = userEvent.setup();
    const { container } = render(<FileConverter {...defaultProps} />);

    await user.click(screen.getByLabelText(/expand parameters/i));

    const product = container.querySelector('#param-product') as HTMLSelectElement;
    expect(product.value).toBe('auto');

    const manualInput = screen.getByLabelText(/enter metar data manually/i);
    fireEvent.change(manualInput, {
      target: {
        value: 'SPECI KJFK 122045Z 18012KT 5SM 15/07 A3005=',
      },
    });

    await user.click(screen.getByTestId('convert-button'));

    await waitFor(() => {
      expect(mockConvertMetarToIwxxm).toHaveBeenCalledTimes(1);
    });

    expect(mockConvertMetarToIwxxm).toHaveBeenCalledWith(
      expect.objectContaining({
        product: 'SPECI',
        conversionLibraryId: defaultLibraryId('conversion', 'ICAO_2025'),
      }),
    );
  });

  it('warns when explicit product differs from auto-detect but still converts', async () => {
    const user = userEvent.setup();
    const { container } = render(<FileConverter {...defaultProps} />);

    await user.click(screen.getByLabelText(/expand parameters/i));

    const product = container.querySelector('#param-product') as HTMLSelectElement;
    await user.selectOptions(product, 'TAF');

    const manualInput = screen.getByLabelText(/enter metar data manually/i);
    fireEvent.change(manualInput, {
      target: {
        value: 'METAR KJFK 121251Z 24016G28KT 10SM FEW250 14/11 A2990',
      },
    });

    await user.click(screen.getByTestId('convert-button'));

    await waitFor(() => {
      expect(mockConvertMetarToIwxxm).toHaveBeenCalledTimes(1);
    });

    expect(mockToast.warning).toHaveBeenCalled();
    expect(mockConvertMetarToIwxxm).toHaveBeenCalledWith(
      expect.objectContaining({
        product: 'TAF',
      }),
    );
  });
});
