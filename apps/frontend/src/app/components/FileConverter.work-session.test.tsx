/* eslint-disable @typescript-eslint/no-explicit-any */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { FileConverter } from './FileConverter';
import { convertMetarToIwxxm } from '/utils/api';
import { uploadConvertedFiles } from '/utils/databaseUpload';
import { toast } from 'sonner';

const mockScheduleAutoSave = vi.fn();
const mockPersistSession = vi.fn();
const mockConvert = vi.mocked(convertMetarToIwxxm);
const mockUpload = vi.mocked(uploadConvertedFiles);
const mockToast = vi.mocked(toast);

vi.mock('@/hooks/useWorkSessionSync', () => ({
  AUTOSAVE_DEBOUNCE_MS: 3000,
  useWorkSessionSync: (options: { sessionStatus?: string | null }) => ({
    isReadOnly: options.sessionStatus === 'finished',
    saveIndicator: 'saved' as const,
    scheduleAutoSave: mockScheduleAutoSave,
    persistSession: mockPersistSession,
  }),
}));

vi.mock('/utils/supabase/logout', () => ({
  signOutWithScope: vi.fn().mockResolvedValue(true),
}));

vi.mock('/utils/api', () => ({
  convertMetarToIwxxm: vi.fn(),
  fetchLintIssueCatalog: vi.fn().mockResolvedValue({ issues: [] }),
  lintTac: vi.fn().mockResolvedValue({
    ok: true,
    issues: [],
    fixes: [],
  }),
  decodeTac: vi
    .fn()
    .mockResolvedValue({ product: 'METAR', segments: [], residuals: [] }),
}));

vi.mock('./TacEditor', () => ({
  TacEditor: ({
    id,
    value,
    onChange,
    readOnly,
    'aria-label': ariaLabel,
  }: {
    id?: string;
    value: string;
    onChange: (v: string) => void;
    readOnly?: boolean;
    'aria-label'?: string;
  }) => (
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

vi.mock('./DecodePanel', () => ({
  DecodePanel: () => null,
}));

vi.mock('/utils/databaseUpload', () => ({
  uploadConvertedFiles: vi.fn(),
  CONVERT_AND_SEND_UPLOAD_OPTIONS: {},
}));

vi.mock('sonner', () => ({
  toast: { success: vi.fn(), error: vi.fn(), info: vi.fn() },
}));

vi.mock('jszip', () => ({
  default: class JSZip {
    file() {
      return this;
    }
    generateAsync() {
      return Promise.resolve(new Blob(['test']));
    }
  },
}));

vi.mock('./DatabaseUploadDialog', () => ({
  DatabaseUploadDialog: () => null,
}));
vi.mock('./UserPreferencesDialog', () => ({
  UserPreferencesDialog: () => null,
}));
vi.mock('./ThemeToggle', () => ({ ThemeToggle: () => null }));
vi.mock('./IcaoAutocomplete', () => ({ IcaoAutocomplete: () => null }));
vi.mock('./AirportDetailsCard', () => ({ AirportDetailsCard: () => null }));
vi.mock('./WorkHistorySidebar', () => ({ WorkHistorySidebar: () => null }));
vi.mock('./ErrorLogPanel', () => ({ ErrorLogPanel: () => null }));

describe('FileConverter F5 workflow', () => {
  // Coverage runs can exceed the suite default when typing METAR + Convert&Send.
  vi.setConfig({ testTimeout: 20_000 });

  beforeEach(() => {
    mockScheduleAutoSave.mockReset();
    mockPersistSession.mockReset();
    mockPersistSession.mockResolvedValue(null);
    mockConvert.mockReset();
    mockUpload.mockReset();
    mockConvert.mockResolvedValue({
      results: [{ iwxxm_xml: '<iwxxm/>', name: 'manual.txt', tac_input: 'METAR' }],
    } as any);
    mockUpload.mockResolvedValue({ message: 'sent' } as any);
  });

  it('shows draft saved indicator when authenticated (T4.11)', () => {
    render(<FileConverter />);
    expect(screen.getByTestId('autosave-indicator')).toHaveTextContent('Draft saved');
    expect(screen.getByTestId('new-metar-button')).toBeInTheDocument();
  });

  it('disables convert buttons for finished sessions (F5-R35)', () => {
    render(
      <FileConverter
        loadedWorkSession={
          {
            id: 'sess-1',
            status: 'finished',
            product: 'metar',
            title: 'KJFK',
            manual_tac: 'METAR KJFK',
            pending_files: [],
            converted_results: [],
            errors: [],
            issues: [],
            conversion_params: {},
            kv_upload_key: null,
            deleted_at: null,
            user_id: 'u1',
            created_at: '2026-06-24T00:00:00Z',
            updated_at: '2026-06-24T00:00:00Z',
          } as any
        }
      />,
    );

    expect(screen.getByTestId('convert-button')).toBeDisabled();
    expect(screen.getByTestId('convert-and-send-button')).toBeDisabled();
    expect(screen.getByText(/read-only/i)).toBeInTheDocument();
  });

  it('no-ops convert handlers when read-only even if buttons are force-enabled', async () => {
    mockConvert.mockClear();

    render(
      <FileConverter
        loadedWorkSession={
          {
            id: 'sess-1',
            status: 'finished',
            product: 'metar',
            title: 'KJFK',
            manual_tac: 'METAR KJFK',
            pending_files: [],
            converted_results: [],
            errors: [],
            issues: [],
            conversion_params: {},
            kv_upload_key: null,
            deleted_at: null,
            user_id: 'u1',
            created_at: '2026-06-24T00:00:00Z',
            updated_at: '2026-06-24T00:00:00Z',
          } as any
        }
      />,
    );

    const invokeReactClick = (element: HTMLElement) => {
      const reactPropsKey = Object.keys(element).find((key) =>
        key.startsWith('__reactProps'),
      );
      const onClick = reactPropsKey
        ? (element as unknown as Record<string, { onClick?: () => void }>)[
            reactPropsKey
          ]?.onClick
        : undefined;
      onClick?.();
    };

    invokeReactClick(screen.getByTestId('convert-button'));
    invokeReactClick(screen.getByTestId('convert-and-send-button'));

    expect(mockConvert).not.toHaveBeenCalled();
    expect(mockUpload).not.toHaveBeenCalled();
  });

  it('starts a new METAR draft from the toolbar', async () => {
    const user = userEvent.setup();
    const onNewMetar = vi.fn();

    render(<FileConverter onNewMetar={onNewMetar} />);

    await user.click(screen.getByTestId('new-metar-button'));
    expect(onNewMetar).toHaveBeenCalled();
    expect(mockToast.info).toHaveBeenCalledWith('Starting a new METAR draft');
  });

  it('persists failed status when convert returns partial errors', async () => {
    const user = userEvent.setup();
    mockConvert.mockResolvedValueOnce({
      results: [{ iwxxm_xml: '<iwxxm/>', name: 'manual.txt' }],
      errors: ['partial failure'],
      issues: [],
    } as any);

    const { container } = render(<FileConverter />);

    const textarea = container.querySelector('textarea') as HTMLTextAreaElement;
    await user.type(textarea, 'METAR KJFK 121251Z 18012KT 10SM');
    await user.click(screen.getByTestId('convert-button'));

    await waitFor(() => {
      expect(mockPersistSession).toHaveBeenCalledWith(
        expect.any(Object),
        expect.objectContaining({ status: 'failed' }),
      );
    });
  });

  it('skips upload when Convert&Send gets partial conversion errors', async () => {
    const user = userEvent.setup();
    mockConvert.mockResolvedValueOnce({
      results: [{ iwxxm_xml: '<iwxxm/>', name: 'manual.txt' }],
      errors: ['partial failure'],
      issues: [],
    } as any);

    const { container } = render(<FileConverter />);

    const textarea = container.querySelector('textarea') as HTMLTextAreaElement;
    await user.type(textarea, 'METAR KJFK 121251Z 18012KT 10SM');
    await user.click(screen.getByTestId('convert-and-send-button'));

    await waitFor(() => {
      expect(mockUpload).not.toHaveBeenCalled();
      expect(mockPersistSession).toHaveBeenCalledWith(
        expect.any(Object),
        expect.objectContaining({ status: 'failed' }),
      );
    });
  });

  it('persists failed status when Convert&Send conversion returns no files', async () => {
    const user = userEvent.setup();
    mockConvert.mockResolvedValueOnce({
      results: [],
      errors: ['Invalid METAR'],
      issues: [],
    } as any);

    const { container } = render(<FileConverter />);

    const textarea = container.querySelector('textarea') as HTMLTextAreaElement;
    await user.type(textarea, 'NOT VALID');
    await user.click(screen.getByTestId('convert-and-send-button'));

    await waitFor(() => {
      expect(mockPersistSession).toHaveBeenCalledWith(
        expect.any(Object),
        expect.objectContaining({ status: 'failed' }),
      );
    });
  });

  it('persists WIP after successful Convert&Send', async () => {
    const user = userEvent.setup();
    const { container } = render(<FileConverter />);

    const textarea = container.querySelector('textarea') as HTMLTextAreaElement;
    await user.type(textarea, 'METAR KJFK 121251Z 18012KT 10SM');
    await user.click(screen.getByTestId('convert-and-send-button'));

    await waitFor(() => {
      expect(mockUpload).toHaveBeenCalled();
      expect(mockPersistSession).toHaveBeenCalledWith(
        expect.any(Object),
        expect.objectContaining({ status: 'finished' }),
      );
    });
  });

  it('keeps WIP when Convert&Send upload fails', async () => {
    const user = userEvent.setup();
    mockUpload.mockRejectedValueOnce(new Error('upload failed'));

    const { container } = render(<FileConverter />);

    const textarea = container.querySelector('textarea') as HTMLTextAreaElement;
    await user.type(textarea, 'METAR KJFK 121251Z 18012KT 10SM');
    await user.click(screen.getByTestId('convert-and-send-button'));

    await waitFor(() => {
      expect(mockPersistSession).toHaveBeenCalledWith(
        expect.any(Object),
        expect.objectContaining({ status: 'wip' }),
      );
    });
  });

  it('hydrates converter from loaded work session including converted results', async () => {
    render(
      <FileConverter
        loadedWorkSession={
          {
            id: 'sess-hydrate',
            status: 'wip',
            product: 'metar',
            title: 'KJFK',
            manual_tac: 'METAR KJFK 121251Z 18012KT 10SM',
            pending_files: [{ name: 'pending.txt', content: 'METAR PENDING' }],
            converted_results: [
              {
                name: 'out.txt',
                iwxxm_xml: '<iwxxm>hydrated</iwxxm>',
                tac_input: 'METAR SOURCE',
              },
            ],
            errors: ['partial warning'],
            issues: [],
            conversion_params: {},
            kv_upload_key: null,
            deleted_at: null,
            user_id: 'u1',
            created_at: '2026-06-24T00:00:00Z',
            updated_at: '2026-06-24T00:00:00Z',
          } as any
        }
      />,
    );

    expect(
      screen.getByDisplayValue('METAR KJFK 121251Z 18012KT 10SM'),
    ).toBeInTheDocument();
    expect(screen.getByText('<iwxxm>hydrated</iwxxm>')).toBeInTheDocument();
  });

  it('hydrates multi-line manual line chips from converted_results (#655)', async () => {
    render(
      <FileConverter
        loadedWorkSession={
          {
            id: 'sess-multi-line',
            status: 'wip',
            product: 'metar',
            title: 'KJFK',
            manual_tac: '',
            pending_files: [],
            converted_results: [
              {
                name: 'manual_input_1.txt',
                iwxxm_xml: '<iwxxm>one</iwxxm>',
                tac_input: 'METAR ONE',
                manual_line_index: 1,
                manual_line_total: 2,
              },
              {
                name: 'manual_input_2.txt',
                iwxxm_xml: '<iwxxm>two</iwxxm>',
                tac_input: 'METAR TWO',
                manual_line_index: 2,
                manual_line_total: 2,
              },
            ],
            errors: [],
            issues: [],
            conversion_params: {},
            kv_upload_key: null,
            deleted_at: null,
            user_id: 'u1',
            created_at: '2026-06-24T00:00:00Z',
            updated_at: '2026-06-24T00:00:00Z',
          } as any
        }
      />,
    );

    expect(screen.getByText('Line 1 of 2')).toBeInTheDocument();
    expect(screen.getByText('Line 2 of 2')).toBeInTheDocument();
  });
});
