/**
 * BUG-2026-11-10 — IWXXM downloads use .xml; ZIP includes TAC .txt/.tac.
 *
 * Success: queue convert with .tac/.txt → Download label .xml; Download-all ZIP
 * has paired .xml + TAC members.
 * Failure: colliding .tac names uniquify XML stems; TAC members keep TAC ext.
 */
/* eslint-disable @typescript-eslint/no-explicit-any */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, cleanup, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { FileConverter } from '@/app/components/FileConverter';

const mockConvertMetarToIwxxm = vi.hoisted(() => vi.fn());
const mockPersistSession = vi.hoisted(() => vi.fn().mockResolvedValue(null));
const mockScheduleAutoSave = vi.hoisted(() => vi.fn());
const zipEntries = vi.hoisted(() => [] as string[]);

vi.mock('/utils/supabase/logout', () => ({
  signOutWithScope: vi.fn().mockResolvedValue(true),
}));

vi.mock('/utils/api', () => ({
  convertMetarToIwxxm: mockConvertMetarToIwxxm,
  convertTafToIwxxm: vi.fn(),
  convertBulletin: vi.fn(),
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
  fetchAirportRegion: vi.fn(),
  downloadBlob: (blob: Blob, filename: string) => {
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
  },
}));

vi.mock('@/utils/conversionProfilesApi', () => ({
  fetchProfileCatalog: vi.fn().mockResolvedValue({ profiles: [] }),
  listPresets: vi.fn().mockResolvedValue([]),
  listTemplates: vi.fn().mockResolvedValue([]),
  listOverlays: vi.fn().mockResolvedValue([]),
  listConversionTemplates: vi.fn().mockResolvedValue([]),
  previewConversionTemplate: vi.fn().mockResolvedValue({}),
  listLibraryAssets: vi.fn().mockResolvedValue([]),
}));

vi.mock('@/app/components/TacEditor', () => ({
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

vi.mock('@/app/components/DecodePanel', () => ({
  DecodePanel: () => null,
}));

vi.mock('/utils/databaseUpload', () => ({
  uploadConvertedFiles: vi.fn(),
  CONVERT_AND_SEND_UPLOAD_OPTIONS: {},
}));

vi.mock('sonner', () => ({
  toast: { success: vi.fn(), error: vi.fn(), info: vi.fn() },
}));

vi.mock('@/hooks/useWorkSessionSync', () => ({
  AUTOSAVE_DEBOUNCE_MS: 3000,
  useWorkSessionSync: () => ({
    isReadOnly: false,
    saveIndicator: 'idle' as const,
    scheduleAutoSave: mockScheduleAutoSave,
    persistSession: mockPersistSession,
    flushAutoSave: vi.fn().mockResolvedValue(null),
  }),
}));

vi.mock('@/app/components/WorkHistorySidebar', () => ({
  WorkHistorySidebar: () => null,
}));

vi.mock('jszip', () => ({
  default: class JSZip {
    /**
     *
     */
    file(name: string) {
      zipEntries.push(name);
      return this;
    }
    /**
     *
     */
    generateAsync() {
      return Promise.resolve(new Blob(['zip']));
    }
  },
}));

vi.mock('@/app/components/DatabaseUploadDialog', () => ({
  DatabaseUploadDialog: () => null,
}));
vi.mock('@/app/components/UserPreferencesDialog', () => ({
  UserPreferencesDialog: () => null,
}));
vi.mock('@/app/components/ThemeToggle', () => ({ ThemeToggle: () => null }));
vi.mock('@/app/components/IcaoAutocomplete', () => ({
  IcaoAutocomplete: () => null,
}));
vi.mock('@/app/components/AirportDetailsCard', () => ({
  AirportDetailsCard: () => null,
}));
vi.mock('@/app/components/ErrorLogPanel', () => ({ ErrorLogPanel: () => null }));

const defaultProps = {
  onLogout: vi.fn(),
  userEmail: 'user@example.com',
};

async function uploadQueueFiles(
  container: HTMLElement,
  files: Array<{ name: string; text: string }>,
) {
  const fileInput = container.querySelector(
    'input[type="file"]:not([data-testid])',
  ) as HTMLInputElement;
  const fileList: Record<string, unknown> = { length: files.length };
  files.forEach((file, index) => {
    fileList[index] = {
      name: file.name,
      text: vi.fn().mockResolvedValue(file.text),
    };
  });
  fireEvent.change(fileInput, { target: { files: fileList } });
  await screen.findByTestId('operator-work-queue');
}

describe('BUG-2026-11-10 download extensions xml vs tac', () => {
  beforeEach(() => {
    mockConvertMetarToIwxxm.mockReset();
    mockPersistSession.mockReset();
    mockPersistSession.mockResolvedValue(null);
    mockScheduleAutoSave.mockReset();
    zipEntries.length = 0;
  });

  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
  });

  it('success: Download label is .xml and ZIP includes paired .xml + TAC', async () => {
    const user = userEvent.setup({ delay: null });
    mockConvertMetarToIwxxm.mockResolvedValue({
      results: [
        {
          name: 'bulletin_report_1.tac',
          iwxxm_xml: '<?xml version="1.0"?><iwxxm:METAR/>',
          tac_input: 'METAR A=',
        },
        {
          name: 'METARYUD.txt',
          iwxxm_xml: '<?xml version="1.0"?><iwxxm:METAR id="2"/>',
          tac_input: 'METAR B=',
        },
      ],
    });

    const { container } = render(
      <FileConverter {...defaultProps} accessToken="token" />,
    );
    await uploadQueueFiles(container, [
      { name: 'bulletin_report_1.tac', text: 'METAR A=' },
      { name: 'METARYUD.txt', text: 'METAR B=' },
    ]);
    await user.click(screen.getByTestId('queue-select-0'));
    await user.click(screen.getByTestId('queue-select-1'));
    await user.click(screen.getByTestId('batch-convert-button'));

    await waitFor(() => {
      expect(screen.getByTestId('convert-results-drawer')).toHaveAttribute(
        'data-open',
        'true',
      );
    });
    await user.click(screen.getByTestId('convert-results-tab-downloads'));

    await waitFor(() => {
      expect(screen.getByText(/Download: bulletin_report_1\.xml/i)).toBeInTheDocument();
      expect(screen.getByText(/Download: METARYUD\.xml/i)).toBeInTheDocument();
      expect(
        screen.queryByText(/Download: bulletin_report_1\.tac/i),
      ).not.toBeInTheDocument();
    });

    await user.click(screen.getByTestId('convert-downloads-zip'));

    await waitFor(() => {
      expect(zipEntries).toEqual(
        expect.arrayContaining([
          'bulletin_report_1.xml',
          'bulletin_report_1.tac',
          'METARYUD.xml',
          'METARYUD.txt',
        ]),
      );
      expect(zipEntries.filter((n) => n.endsWith('.xml'))).toHaveLength(2);
      expect(zipEntries.filter((n) => /\.(tac|txt)$/i.test(n))).toHaveLength(2);
      expect(zipEntries.some((n) => /\.(tac|txt)$/i.test(n) && !n.includes('.'))).toBe(
        false,
      );
    });
  }, 30_000);

  it('failure/collision: duplicate .tac stems uniquify XML; TAC keeps .tac', async () => {
    const user = userEvent.setup({ delay: null });
    mockConvertMetarToIwxxm.mockResolvedValue({
      results: [
        {
          name: 'only.tac',
          iwxxm_xml: '<?xml version="1.0"?><iwxxm:METAR/>',
          tac_input: 'METAR A=',
        },
        {
          name: 'only.tac',
          iwxxm_xml: '<?xml version="1.0"?><iwxxm:METAR id="dup"/>',
          tac_input: 'METAR B=',
        },
      ],
    });

    const { container } = render(
      <FileConverter {...defaultProps} accessToken="token" />,
    );
    await uploadQueueFiles(container, [
      { name: 'only.tac', text: 'METAR A=' },
      { name: 'only.tac', text: 'METAR B=' },
    ]);
    await user.click(screen.getByTestId('queue-select-0'));
    await user.click(screen.getByTestId('queue-select-1'));
    await user.click(screen.getByTestId('batch-convert-button'));

    await waitFor(() => {
      expect(screen.getByTestId('convert-results-drawer')).toHaveAttribute(
        'data-open',
        'true',
      );
    });
    await user.click(screen.getByTestId('convert-downloads-zip'));

    await waitFor(() => {
      expect(zipEntries).toEqual(
        expect.arrayContaining(['only.xml', 'only.tac', 'only_2.xml', 'only_2.tac']),
      );
      // Converted IWXXM members are never bare colliding .tac without remap.
      expect(zipEntries.filter((n) => n.endsWith('.xml'))).toEqual([
        'only.xml',
        'only_2.xml',
      ]);
      expect(zipEntries.filter((n) => n.endsWith('.tac'))).toEqual([
        'only.tac',
        'only_2.tac',
      ]);
    });
  }, 30_000);

  it('success: manual convert ZIP pairs live .xml with .txt TAC source', async () => {
    const user = userEvent.setup({ delay: null });
    mockConvertMetarToIwxxm.mockResolvedValue({
      results: [
        {
          iwxxm_xml: '<?xml version="1.0"?><iwxxm:METAR/>',
          tac_input: 'METAR KJFK 071251Z 18008KT 10SM FEW250 22/14 A2992',
        },
      ],
    });

    const { container } = render(
      <FileConverter {...defaultProps} accessToken="token" />,
    );
    const filenameInput = screen.getByTestId('output-filename-input');
    fireEvent.change(filenameInput, { target: { value: 'manual_stem' } });
    const textarea = container.querySelector('textarea') as HTMLTextAreaElement;
    fireEvent.change(textarea, {
      target: { value: 'METAR KJFK 071251Z 18008KT 10SM FEW250 22/14 A2992' },
    });
    await user.click(screen.getByTestId('convert-button'));

    await waitFor(() => {
      expect(screen.getByTestId('convert-results-drawer')).toHaveAttribute(
        'data-open',
        'true',
      );
    });
    await user.click(screen.getByTestId('convert-settings-cog'));
    await user.click(
      screen.getByRole('button', {
        name: /download all 1 converted files as zip/i,
      }),
    );

    await waitFor(() => {
      expect(zipEntries).toContain('manual_stem.xml');
      expect(zipEntries).toContain('manual_stem.txt');
      expect(zipEntries).not.toContain('manual_stem.tac');
    });
  }, 30_000);
});
