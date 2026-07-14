/**
 * BUG-2026-07-12 — Conversion results Card not dismissed after Clear/Remove.
 *
 * Repro for production stuck-card: Clear leaves convertedFiles; Remove can be
 * undone when a stale loadedWorkSession update rehydrates converted_results.
 *
 * Runs in frontend CI (`npm test`), not pytest `tests/bugs/`.
 */
/* eslint-disable @typescript-eslint/no-explicit-any */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { FileConverter } from '@/app/components/FileConverter';

const mockConvertMetarToIwxxm = vi.hoisted(() => vi.fn());
const mockPersistSession = vi.hoisted(() => vi.fn().mockResolvedValue(null));
const mockScheduleAutoSave = vi.hoisted(() => vi.fn());

vi.mock('/utils/supabase/logout', () => ({
  signOutWithScope: vi.fn().mockResolvedValue(true),
}));

vi.mock('/utils/api', () => ({
  convertMetarToIwxxm: mockConvertMetarToIwxxm,
  convertTafToIwxxm: vi.fn(),
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
    file() {
      return this;
    }
    generateAsync() {
      return Promise.resolve(new Blob(['test']));
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

describe('BUG-2026-07-12 result card dismiss', () => {
  beforeEach(() => {
    mockConvertMetarToIwxxm.mockReset();
    mockPersistSession.mockReset();
    mockPersistSession.mockResolvedValue(null);
    mockScheduleAutoSave.mockReset();
    mockConvertMetarToIwxxm.mockResolvedValue({
      results: [
        {
          iwxxm_xml: '<?xml version="1.0"?><iwxxm:METAR/>',
          tac_input: 'METAR FAOR 101200Z COR 12012KT 9999 FEW020 22/14 Q1018',
        },
      ],
    });
  });

  it('Clear dismisses the conversion results Card (manual_input.txt)', async () => {
    const user = userEvent.setup();
    const { container } = render(
      <FileConverter {...defaultProps} accessToken="token" />,
    );

    const textarea = container.querySelector('textarea') as HTMLTextAreaElement;
    await user.type(textarea, 'METAR FAOR 101200Z COR 12012KT 9999 FEW020 22/14 Q1018');
    await user.click(screen.getByTestId('convert-button'));

    await waitFor(() => {
      expect(screen.getByText('METAR FAOR 101200Z')).toBeInTheDocument();
    });

    await user.click(
      screen.getByRole('button', {
        name: /clear all pending files and manual input/i,
      }),
    );

    await waitFor(() => {
      expect(screen.queryByText('METAR FAOR 101200Z')).not.toBeInTheDocument();
    });
  });

  it('Remove stays dismissed when a stale work-session update rehydrates', async () => {
    const user = userEvent.setup();
    const baseSession = {
      id: 'sess-stuck-card',
      status: 'wip' as const,
      title: 'FAOR',
      manual_tac: '',
      pending_files: [],
      converted_results: [
        {
          name: 'manual_input.txt',
          tac_input: 'METAR FAOR 101200Z COR 12012KT 9999 FEW020 22/14 Q1018',
          iwxxm_xml: '<?xml version="1.0"?><iwxxm:METAR/>',
        },
      ],
      errors: [],
      issues: [],
      conversion_params: {},
      kv_upload_key: null,
      deleted_at: null,
      user_id: 'u1',
      created_at: '2026-07-12T00:00:00Z',
      updated_at: '2026-07-12T00:00:00Z',
    };

    const { rerender } = render(
      <FileConverter
        {...defaultProps}
        accessToken="token"
        activeWorkSessionId={baseSession.id}
        loadedWorkSession={baseSession as any}
      />,
    );

    expect(screen.getByText(/manual_input\.txt/)).toBeInTheDocument();

    await user.click(
      screen.getByRole('button', {
        name: /remove manual_input\.txt from results/i,
      }),
    );

    await waitFor(() => {
      expect(screen.queryByText(/manual_input\.txt/)).not.toBeInTheDocument();
    });

    // Stale autosave / persist completion pushes the pre-remove session back
    // into loadedWorkSession (production: onSessionSaved → setLoadedWorkSession).
    rerender(
      <FileConverter
        {...defaultProps}
        accessToken="token"
        activeWorkSessionId={baseSession.id}
        loadedWorkSession={
          {
            ...baseSession,
            updated_at: '2026-07-12T00:00:03Z',
          } as any
        }
      />,
    );

    await waitFor(() => {
      expect(screen.queryByText(/manual_input\.txt/)).not.toBeInTheDocument();
    });
  });
});
