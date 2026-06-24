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
  beforeEach(() => {
    mockScheduleAutoSave.mockReset();
    mockPersistSession.mockReset();
    mockPersistSession.mockResolvedValue(null);
    mockConvert.mockResolvedValue({
      results: [{ iwxxm_xml: '<iwxxm/>', name: 'manual.txt', tac_input: 'METAR' }],
    } as any);
    mockUpload.mockResolvedValue({ message: 'sent' } as any);
  });

  it('shows draft saved indicator when authenticated (T4.11)', () => {
    render(
      <FileConverter
        onLogout={vi.fn()}
        userEmail="user@example.com"
        accessToken="token"
      />,
    );
    expect(screen.getByTestId('autosave-indicator')).toHaveTextContent('Draft saved');
    expect(screen.getByTestId('new-metar-button')).toBeInTheDocument();
  });

  it('disables convert buttons for finished sessions (F5-R35)', () => {
    render(
      <FileConverter
        onLogout={vi.fn()}
        userEmail="user@example.com"
        accessToken="token"
        loadedWorkSession={
          {
            id: 'sess-1',
            status: 'finished',
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

  it('starts a new METAR draft from the toolbar', async () => {
    const user = userEvent.setup();
    const onNewMetar = vi.fn();

    render(
      <FileConverter
        onLogout={vi.fn()}
        userEmail="user@example.com"
        accessToken="token"
        onNewMetar={onNewMetar}
      />,
    );

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

    const { container } = render(
      <FileConverter
        onLogout={vi.fn()}
        userEmail="user@example.com"
        accessToken="token"
      />,
    );

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

    const { container } = render(
      <FileConverter
        onLogout={vi.fn()}
        userEmail="user@example.com"
        accessToken="token"
      />,
    );

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

    const { container } = render(
      <FileConverter
        onLogout={vi.fn()}
        userEmail="user@example.com"
        accessToken="token"
      />,
    );

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
    const { container } = render(
      <FileConverter
        onLogout={vi.fn()}
        userEmail="user@example.com"
        accessToken="token"
      />,
    );

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

    const { container } = render(
      <FileConverter
        onLogout={vi.fn()}
        userEmail="user@example.com"
        accessToken="token"
      />,
    );

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

  it('prompts guest users to sign in from the header', async () => {
    const user = userEvent.setup();
    const onRequestLogin = vi.fn();

    render(
      <FileConverter
        onLogout={vi.fn()}
        userEmail="guest@example.com"
        isGuest
        onRequestLogin={onRequestLogin}
      />,
    );

    await user.click(screen.getByRole('button', { name: /sign in to save work/i }));
    expect(onRequestLogin).toHaveBeenCalled();
  });
});
