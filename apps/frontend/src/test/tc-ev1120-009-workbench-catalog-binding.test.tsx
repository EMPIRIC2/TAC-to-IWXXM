/**
 * TC-EV1120-009 — workbench Validation Issues Catalog follows Profile + packaging Exchange.
 *
 * AC (#1123): Changing Profile refetches catalog; Exchange filter applies when Disseminate
 * packaging UI exposes Exchange. Complements hook unit tests and Rule catalogs page filters.
 *
 * [Corpus: tests] [Corpus: product §F15] [Corpus: journeys UJ-073]
 */
/* eslint-disable @typescript-eslint/no-explicit-any */
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { FileConverter } from '../app/components/FileConverter';
import { defaultLibraryId } from '../utils/libraryIds';

const fetchLintIssueCatalog = vi.hoisted(() =>
  vi.fn().mockResolvedValue({ issues: [] }),
);

vi.mock('/utils/supabase/logout', () => ({
  signOutWithScope: vi.fn().mockResolvedValue(true),
}));

vi.mock('/utils/api', () => ({
  convertMetarToIwxxm: vi.fn().mockResolvedValue({
    results: [],
    errors: [],
    issues: [],
    total_processed: 0,
    successful: 0,
    failed: 0,
  }),
  convertBulletin: vi.fn(),
  ingestCollect: vi.fn(),
  EndpointNotImplementedError: class extends Error {},
  convertTafToIwxxm: vi.fn(),
  fetchLintIssueCatalog,
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
  lintTac: vi.fn().mockResolvedValue({ ok: true, issues: [], fixes: [] }),
  decodeTac: vi
    .fn()
    .mockResolvedValue({ product: 'METAR', segments: [], residuals: [] }),
  fetchAirportRegion: vi.fn().mockResolvedValue(null),
  validateIwxxm: vi.fn().mockResolvedValue({
    ok: true,
    layers: [],
    issues: [],
  }),
  listDisseminationTemplates: vi.fn().mockResolvedValue({ templates: [] }),
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
    promise: vi.fn(),
    info: vi.fn(),
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

describe('TC-EV1120-009 workbench catalog Profile/Exchange binding', () => {
  const defaultProps = {
    onLogout: vi.fn(),
    userEmail: 'ev1123@example.com',
    accessToken: 'token',
    onSwitchToAdmin: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    fetchLintIssueCatalog.mockResolvedValue({ issues: [] });
    vi.spyOn(window, 'confirm').mockReturnValue(true);
  });

  it('refetches lint catalog when Conversion Profile (library) changes', async () => {
    const user = userEvent.setup();
    render(<FileConverter {...defaultProps} />);

    await waitFor(() => {
      expect(fetchLintIssueCatalog).toHaveBeenCalledWith(
        expect.objectContaining({
          semantic_profile: 'ICAO_2025',
          exchange_profile: 'GLOBAL_AFS',
        }),
      );
    });

    await user.selectOptions(
      screen.getByTestId('conversion-library-select'),
      defaultLibraryId('conversion', 'US_FAA_NWS'),
    );

    await waitFor(() => {
      expect(fetchLintIssueCatalog).toHaveBeenCalledWith(
        expect.objectContaining({
          semantic_profile: 'US_FAA_NWS',
        }),
      );
    });
  });

  it('applies Disseminate Exchange control to catalog while packaging UI is open', async () => {
    const user = userEvent.setup();
    render(<FileConverter {...defaultProps} />);

    await waitFor(() => {
      expect(fetchLintIssueCatalog).toHaveBeenCalled();
    });
    fetchLintIssueCatalog.mockClear();

    await user.click(screen.getByTestId('open-dissemination-drawer'));
    expect(await screen.findByTestId('dissemination-drawer')).toBeInTheDocument();

    await user.selectOptions(
      screen.getByTestId('dissemination-exchange-profile'),
      'EUR_RODEX',
    );

    await waitFor(() => {
      expect(fetchLintIssueCatalog).toHaveBeenCalledWith(
        expect.objectContaining({
          exchange_profile: 'EUR_RODEX',
        }),
      );
    });
  });
});
