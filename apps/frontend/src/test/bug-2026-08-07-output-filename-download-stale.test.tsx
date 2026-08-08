/**
 * BUG-2026-08-07 / #904 — Output filename change after convert ignored on Download.
 *
 * Steps: convert with first_name → change field to second_name → Download / ZIP
 * members must use second_name.xml (preview already updates).
 *
 * Runs in frontend CI (`npm test`), not pytest `tests/bugs/`.
 */
/* eslint-disable @typescript-eslint/no-explicit-any */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, cleanup, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { FileConverter } from '@/app/components/FileConverter';

/** Avoid per-keystroke delays — full `make ci` suite otherwise times out at 20s. */
async function setInputValue(el: HTMLElement, value: string) {
  fireEvent.change(el, { target: { value } });
}

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
  fetchLintIssueCatalog: vi.fn().mockResolvedValue({ issues: [] }),
  lintTac: vi.fn().mockResolvedValue({
    ok: true,
    issues: [],
    fixes: [],
  }),
  decodeTac: vi
    .fn()
    .mockResolvedValue({ product: 'METAR', segments: [], residuals: [] }),
  fetchAirportRegion: vi.fn(),
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
    file(name: string) {
      zipEntries.push(name);
      return this;
    }
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

const SAMPLE_TAC = 'METAR KJFK 071251Z 18008KT 10SM FEW250 22/14 A2992';

describe('BUG-2026-08-07 output filename download stale (#904)', () => {
  beforeEach(() => {
    mockConvertMetarToIwxxm.mockReset();
    mockPersistSession.mockReset();
    mockPersistSession.mockResolvedValue(null);
    mockScheduleAutoSave.mockReset();
    zipEntries.length = 0;
    mockConvertMetarToIwxxm.mockResolvedValue({
      results: [
        {
          iwxxm_xml: '<?xml version="1.0"?><iwxxm:METAR/>',
          tac_input: SAMPLE_TAC,
        },
      ],
    });
  });

  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
  });

  it('Download uses the current Output filename after rename (not convert-time)', async () => {
    const user = userEvent.setup({ delay: null });
    let downloadedName = '';
    const createUrlSpy = vi
      .spyOn(URL, 'createObjectURL')
      .mockReturnValue('blob:rename-download');
    const revokeUrlSpy = vi
      .spyOn(URL, 'revokeObjectURL')
      .mockImplementation(() => undefined);
    const clickSpy = vi
      .spyOn(HTMLAnchorElement.prototype, 'click')
      .mockImplementation(function (this: HTMLAnchorElement) {
        downloadedName = this.download;
      });

    const { container } = render(
      <FileConverter {...defaultProps} accessToken="token" />,
    );

    const filenameInput = screen.getByTestId('output-filename-input');
    await setInputValue(filenameInput, 'first_name');

    const textarea = container.querySelector('textarea') as HTMLTextAreaElement;
    await setInputValue(textarea, SAMPLE_TAC);
    await user.click(screen.getByTestId('convert-button'));

    await waitFor(() => {
      expect(
        screen.getByRole('button', {
          name: /download first_name\.txt as xml/i,
        }),
      ).toBeInTheDocument();
    });

    await setInputValue(filenameInput, 'second_name');
    expect(screen.getByTestId('output-filename-preview')).toHaveTextContent(
      'second_name.xml',
    );

    // Card label may still show convert-time originalName; download attribute uses live field.
    await user.click(
      screen.getByRole('button', {
        name: /download first_name\.txt as xml/i,
      }),
    );

    await waitFor(() => {
      expect(downloadedName).toBe('second_name.xml');
    });

    createUrlSpy.mockRestore();
    revokeUrlSpy.mockRestore();
    clickSpy.mockRestore();
  }, 30_000);

  it('Download All ZIP members use the current Output filename after rename', async () => {
    const user = userEvent.setup({ delay: null });
    const createUrlSpy = vi
      .spyOn(URL, 'createObjectURL')
      .mockReturnValue('blob:rename-zip');
    const revokeUrlSpy = vi
      .spyOn(URL, 'revokeObjectURL')
      .mockImplementation(() => undefined);
    const clickSpy = vi
      .spyOn(HTMLAnchorElement.prototype, 'click')
      .mockImplementation(() => undefined);

    const { container } = render(
      <FileConverter {...defaultProps} accessToken="token" />,
    );

    const filenameInput = screen.getByTestId('output-filename-input');
    await setInputValue(filenameInput, 'first_name');

    const textarea = container.querySelector('textarea') as HTMLTextAreaElement;
    await setInputValue(textarea, SAMPLE_TAC);
    await user.click(screen.getByTestId('convert-button'));

    await waitFor(() => {
      expect(screen.getByText(/first_name\.txt/)).toBeInTheDocument();
    });

    await setInputValue(filenameInput, 'second_name');
    expect(screen.getByTestId('output-filename-preview')).toHaveTextContent(
      'second_name.xml',
    );

    await user.click(
      screen.getByRole('button', {
        name: /download all 1 converted files as zip/i,
      }),
    );

    await waitFor(() => {
      expect(zipEntries).toContain('second_name.xml');
      expect(zipEntries).not.toContain('first_name.xml');
    });

    createUrlSpy.mockRestore();
    revokeUrlSpy.mockRestore();
    clickSpy.mockRestore();
  }, 30_000);
});
