/* eslint-disable @typescript-eslint/no-explicit-any */
/**
 * FileConverter hook branches left uncovered after M1 (destinations off, ICAO-only):
 * dissemination close, session hydration, schema-status failure, CA blocked convert.
 * FR-019..022, FR-052..056 / DI-008.
 */
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { FileConverter } from './FileConverter';

const mockFetchSchemaStatus = vi.hoisted(() => vi.fn());
const caProfileFlag = vi.hoisted(() => ({ value: false }));

vi.mock('/utils/supabase/logout', () => ({
  signOutWithScope: vi.fn().mockResolvedValue(true),
}));

vi.mock('/utils/api', () => ({
  convertMetarToIwxxm: vi.fn(),
  massIngestFiles: vi.fn(),
  fetchLintIssueCatalog: vi.fn().mockResolvedValue({ issues: [] }),
  fetchSelectionOptions: vi
    .fn()
    .mockImplementation(async ({ kind }: { kind: string }) => ({ kind, options: [] })),
  fetchSchemaStatus: (...args: unknown[]) => mockFetchSchemaStatus(...args),
  lintTac: vi.fn().mockResolvedValue({ ok: true, issues: [], fixes: [] }),
  decodeTac: vi
    .fn()
    .mockResolvedValue({ product: 'METAR', segments: [], residuals: [] }),
}));

vi.mock('@/utils/conversionProfilesApi', () => ({
  fetchProfileCatalog: vi.fn().mockResolvedValue({
    profiles: [
      {
        id: 'ICAO_2025',
        kind: 'semantic',
        products: ['METAR', 'SPECI'],
        deltas_vs_icao: [],
        iwxxm_line: 'IWXXM 2025-2 core',
        metar_family_variants: [
          { tac_lead: 'METAR', api_product: 'METAR', iwxxm_root: 'iwxxm:METAR' },
          { tac_lead: 'LWIS', api_product: 'METAR', iwxxm_root: 'iwxxm-ca:LWIS' },
        ],
      },
    ],
  }),
  listPresets: vi.fn().mockResolvedValue({ items: [] }),
  listTemplates: vi.fn().mockResolvedValue({ items: [] }),
  listOverlays: vi.fn().mockResolvedValue({ items: [] }),
  listConversionTemplates: vi.fn().mockResolvedValue({ items: [] }),
  previewConversionTemplate: vi.fn(),
  listLibraryAssets: vi.fn().mockResolvedValue({ items: [] }),
}));

// Real helpers, except isCaEcccProfile (CA_ECCC is no longer a reachable profile).
vi.mock('@/utils/tacProduct', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/utils/tacProduct')>();
  return {
    ...actual,
    isCaEcccProfile: (profile: string) =>
      caProfileFlag.value || actual.isCaEcccProfile(profile),
  };
});

vi.mock('@/hooks/useWorkSessionSync', () => ({
  AUTOSAVE_DEBOUNCE_MS: 3000,
  useWorkSessionSync: () => ({
    isReadOnly: false,
    saveIndicator: 'saved' as const,
    scheduleAutoSave: vi.fn(),
    persistSession: vi.fn().mockResolvedValue(null),
  }),
}));

vi.mock('/utils/guestConverterState', () => ({
  readGuestConverterState: vi.fn(() => null),
  saveGuestConverterState: vi.fn(),
  clearGuestConverterState: vi.fn(),
}));

vi.mock('/utils/databaseUpload', () => ({
  uploadConvertedFiles: vi.fn(),
  CONVERT_AND_SEND_UPLOAD_OPTIONS: {},
}));

vi.mock('sonner', () => ({
  toast: { success: vi.fn(), error: vi.fn(), info: vi.fn(), warning: vi.fn() },
}));

vi.mock('./TacEditor', () => ({
  TacEditor: ({ id, value, onChange }: any) => (
    <textarea
      id={id}
      value={value}
      data-testid="tac-editor"
      onChange={(e) => onChange(e.target.value)}
    />
  ),
}));
vi.mock('./DecodePanel', () => ({ DecodePanel: () => null }));
vi.mock('./DatabaseUploadDialog', () => ({ DatabaseUploadDialog: () => null }));
vi.mock('./UserPreferencesDialog', () => ({ UserPreferencesDialog: () => null }));
vi.mock('./ThemeToggle', () => ({ ThemeToggle: () => null }));
vi.mock('./IcaoAutocomplete', () => ({ IcaoAutocomplete: () => null }));
vi.mock('./WorkHistorySidebar', () => ({ WorkHistorySidebar: () => null }));
/**
 *
 */
function session(conversionParams: Record<string, unknown>) {
  return {
    id: 'sess-m1',
    status: 'draft',
    product: 'metar',
    title: 'KJFK',
    manual_tac: '',
    pending_files: [],
    converted_results: [],
    errors: [],
    issues: [],
    conversion_params: conversionParams,
    kv_upload_key: null,
    deleted_at: null,
    user_id: 'u1',
    created_at: '2026-06-24T00:00:00Z',
    updated_at: '2026-06-24T00:00:00Z',
  } as any;
}

describe('FileConverter M1 coverage fills', () => {
  it('does not expose Disseminate controls (DI-008)', () => {
    render(<FileConverter />);
    expect(screen.queryByTestId('open-dissemination-drawer')).not.toBeInTheDocument();
    expect(screen.queryByTestId('dissemination-drawer')).not.toBeInTheDocument();
  });

  beforeEach(() => {
    caProfileFlag.value = false;
    mockFetchSchemaStatus.mockReset();
    mockFetchSchemaStatus.mockResolvedValue({
      profile_pins: { ca_eccc: { extension_bundle_available: true } },
    });
  });

  afterEach(() => {
    caProfileFlag.value = false;
    cleanup();
  });

  it('falls back to Auto-detect when the stored report variant is not offered', async () => {
    render(
      <FileConverter
        accessToken="tok"
        loadedWorkSession={session({ product: 'METAR', reportVariant: 'NOPE' })}
      />,
    );
    await waitFor(() =>
      expect(screen.getByTestId('report-variant-select')).toBeInTheDocument(),
    );
    expect(screen.getByTestId('report-variant-select')).toHaveValue('');
  });

  it('keeps an allowed stored report variant selected', async () => {
    render(
      <FileConverter
        accessToken="tok"
        loadedWorkSession={session({ product: 'METAR', reportVariant: 'LWIS' })}
      />,
    );
    await waitFor(() =>
      expect(screen.getByTestId('report-variant-select')).toHaveValue('LWIS'),
    );
  });

  it('hydrates camelCase disseminationTemplateId without mounting destinations UI', () => {
    render(
      <FileConverter
        accessToken="tok"
        loadedWorkSession={session({ disseminationTemplateId: 'tpl-camel' })}
      />,
    );
    expect(screen.queryByTestId('open-dissemination-drawer')).not.toBeInTheDocument();
    expect(
      screen.queryByTestId('dissemination-template-select'),
    ).not.toBeInTheDocument();
  });

  it('treats a schema-status failure as unknown CA bundle availability', async () => {
    mockFetchSchemaStatus.mockRejectedValue(new Error('schema status down'));
    render(<FileConverter />);
    await waitFor(() => expect(mockFetchSchemaStatus).toHaveBeenCalled());
    // Failure leaves the bundle state unknown (null), so Convert is not CA-blocked.
    await waitFor(() =>
      expect(screen.queryByTestId('ca-eccc-profile-metadata')).not.toBeInTheDocument(),
    );
  });

  it('disables Convert when a CA profile has no extension bundle', async () => {
    caProfileFlag.value = true;
    mockFetchSchemaStatus.mockResolvedValue({
      profile_pins: { ca_eccc: { extension_bundle_available: false } },
    });
    render(<FileConverter />);
    fireEvent.change(screen.getByTestId('tac-editor'), {
      target: { value: 'METAR KJFK 121251Z 18004KT 10SM FEW020 18/12 A3012=' },
    });
    await waitFor(() => expect(screen.getByTestId('convert-button')).toBeDisabled());
  });
});
