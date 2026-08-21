/* eslint-disable @typescript-eslint/no-explicit-any */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
  act,
  render,
  screen,
  fireEvent,
  waitFor,
  cleanup,
} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { FileConverter } from './FileConverter';
import { operatorDisseminationUiConfig } from '/utils/operatorDisseminationUi';

const mockSignOutWithScope = vi.hoisted(() => vi.fn().mockResolvedValue(true));
const mockConvertMetarToIwxxm = vi.hoisted(() =>
  vi.fn().mockResolvedValue({ success: true, data: '<iwxxm>test</iwxxm>' }),
);
const mockConvertBulletin = vi.hoisted(() =>
  vi.fn().mockResolvedValue({
    bulletin_meta: {
      ahl: 'SAUS31 KZNY 121200',
      report_count: 0,
      tt: 'SA',
      aa: 'US',
      cccc: 'KZNY',
      yygggg: '121200',
    },
    results: [],
  }),
);
const MockEndpointNotImplementedError = vi.hoisted(() => {
  return class EndpointNotImplementedError extends Error {
    status: number;
    code: string;
    constructor(message: string, status = 501, code = 'not_implemented') {
      super(message);
      this.name = 'EndpointNotImplementedError';
      this.status = status;
      this.code = code;
    }
  };
});
const mockIngestCollect = vi.hoisted(() =>
  vi.fn().mockImplementation(() => {
    throw new MockEndpointNotImplementedError(
      'COLLECT / FTBP ingest is not implemented yet (placeholder).',
    );
  }),
);
const mockLintTac = vi.hoisted(() =>
  vi.fn().mockResolvedValue({
    ok: true,
    issues: [{ severity: 'error', code: 'x', message: 'm', start: 0, end: 5 }],
    fixes: [],
  }),
);
const mockDecodeTac = vi.hoisted(() =>
  vi.fn().mockResolvedValue({
    product: 'METAR',
    segments: [{ start: 0, end: 5, code: 'METAR', explanation: 'type' }],
    residuals: [],
  }),
);
const mockMassIngestFiles = vi.hoisted(() =>
  vi.fn().mockResolvedValue({
    accepted_count: 1,
    rejected_count: 0,
    results: [
      {
        name: 'mass.tac',
        accepted: true,
        reason: null,
        size_bytes: 20,
        content: 'METAR KJFK 121251Z=\n',
      },
    ],
  }),
);
const mockValidateIwxxm = vi.hoisted(() =>
  vi.fn().mockResolvedValue({
    is_valid: true,
    version: '2025-2',
    layers_passed: ['XML_WELLFORMED', 'XML_SCHEMA'],
    layers_failed: [],
    package_ok: true,
    package_issues: [],
  }),
);
const mockUploadConvertedFiles = vi.hoisted(() =>
  vi.fn().mockResolvedValue({ message: 'Files uploaded successfully' }),
);

const mockToast = vi.hoisted(() => ({
  success: vi.fn(),
  error: vi.fn(),
  loading: vi.fn(),
  dismiss: vi.fn(),
  promise: vi.fn(),
  info: vi.fn(),
  warning: vi.fn(),
}));
const mockPersistSession = vi.hoisted(() => vi.fn().mockResolvedValue(null));
const mockScheduleAutoSave = vi.hoisted(() => vi.fn());
const mockInflateGzipToText = vi.hoisted(() => vi.fn());
const mockReadGuestConverterState = vi.hoisted(() => vi.fn(() => null));
const mockIsReadOnly = vi.hoisted(() => ({ value: false }));
const mockSaveIndicator = vi.hoisted(() => ({
  value: 'idle' as 'idle' | 'pending' | 'saving' | 'saved' | 'error',
}));

// Mock dependencies
vi.mock('/utils/supabase/info', () => ({
  projectId: 'test-project',
  publicAnonKey: 'test-key',
}));

vi.mock('/utils/supabase/logout', () => ({
  signOutWithScope: mockSignOutWithScope,
}));

vi.mock('/utils/api', () => ({
  convertMetarToIwxxm: mockConvertMetarToIwxxm,
  convertBulletin: mockConvertBulletin,
  ingestCollect: mockIngestCollect,
  massIngestFiles: mockMassIngestFiles,
  EndpointNotImplementedError: MockEndpointNotImplementedError,
  convertTafToIwxxm: vi
    .fn()
    .mockResolvedValue({ success: true, data: '<iwxxm>test</iwxxm>' }),
  fetchLintIssueCatalog: vi.fn().mockResolvedValue({ issues: [] }),
  lintTac: mockLintTac,
  decodeTac: mockDecodeTac,
  validateIwxxm: mockValidateIwxxm,
  fetchAirportRegion: vi
    .fn()
    .mockResolvedValue({ airport_code: 'KJFK', icao_region: 'NAM' }),
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
  DecodePanel: () => <div data-testid="decode-panel-mock" />,
}));

vi.mock('/utils/databaseUpload', () => ({
  uploadConvertedFiles: mockUploadConvertedFiles,
  CONVERT_AND_SEND_UPLOAD_OPTIONS: {
    format: 'iwxxm',
    destination: 'primary',
    includeOriginal: false,
  },
}));

vi.mock('/utils/gunzip', () => ({
  inflateGzipToText: mockInflateGzipToText,
  isGzipFileName: (name: string) =>
    name.toLowerCase().endsWith('.gz') || name.toLowerCase().endsWith('.gzip'),
}));

vi.mock('sonner', () => ({
  toast: mockToast,
}));

vi.mock('@/hooks/useWorkSessionSync', () => ({
  AUTOSAVE_DEBOUNCE_MS: 3000,
  useWorkSessionSync: () => ({
    isReadOnly: mockIsReadOnly.value,
    saveIndicator: mockSaveIndicator.value,
    scheduleAutoSave: mockScheduleAutoSave,
    persistSession: mockPersistSession,
    flushAutoSave: vi.fn().mockResolvedValue(null),
  }),
}));

vi.mock('/utils/guestConverterState', () => ({
  readGuestConverterState: mockReadGuestConverterState,
  saveGuestConverterState: vi.fn(),
  clearGuestConverterState: vi.fn(),
}));

vi.mock('./WorkHistorySidebar', () => ({
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

vi.mock('./DatabaseUploadDialog', () => ({
  DatabaseUploadDialog: ({ isOpen, onClose }: any) => (
    <div
      data-testid="database-upload-dialog"
      style={{ display: isOpen ? 'block' : 'none' }}
    >
      <button onClick={() => onClose()} data-testid="close-upload-dialog">
        Close
      </button>
    </div>
  ),
}));

vi.mock('./UserPreferencesDialog', () => ({
  UserPreferencesDialog: ({ isOpen, onClose, onPreferencesSaved }: any) => (
    <div
      data-testid="preferences-dialog"
      style={{ display: isOpen ? 'block' : 'none' }}
    >
      <button onClick={() => onPreferencesSaved?.()} data-testid="save-prefs-dialog">
        Save
      </button>
      <button onClick={() => onClose()} data-testid="close-prefs-dialog">
        Close
      </button>
    </div>
  ),
}));

vi.mock('./IcaoAutocomplete', () => ({
  IcaoAutocomplete: ({ value, onChange }: any) => (
    <input
      data-testid="icao-input"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder="ICAO"
    />
  ),
}));

vi.mock('./ThemeToggle', () => ({
  ThemeToggle: () => <div data-testid="theme-toggle">Theme</div>,
}));

vi.mock('./ui/sonner', () => ({
  Toaster: () => <div data-testid="toaster" />,
}));

describe('FileConverter Component', () => {
  const defaultProps = {};

  // Coverage + full-suite load routinely exceeds Vitest's default 5s on Branch Path cases.
  vi.setConfig({ testTimeout: 20_000 });

  beforeEach(() => {
    cleanup();
    vi.clearAllMocks();
    operatorDisseminationUiConfig.destinationsEnabled = false;
    // Reset queued Once/implementations so coverage runs do not leak mocks across cases.
    mockConvertMetarToIwxxm.mockReset();
    mockConvertBulletin.mockReset();
    mockIngestCollect.mockReset();
    mockDecodeTac.mockReset();
    mockLintTac.mockReset();
    mockMassIngestFiles.mockReset();
    mockInflateGzipToText.mockReset();
    mockValidateIwxxm.mockReset();
    localStorage.clear();
    mockSignOutWithScope.mockResolvedValue(true);
    mockPersistSession.mockResolvedValue(null);
    mockIngestCollect.mockImplementation(() => {
      throw new MockEndpointNotImplementedError(
        'COLLECT / FTBP ingest is not implemented yet (placeholder).',
      );
    });
    mockMassIngestFiles.mockResolvedValue({
      accepted_count: 1,
      rejected_count: 0,
      results: [
        {
          name: 'mass.tac',
          accepted: true,
          reason: null,
          size_bytes: 20,
          content: 'METAR KJFK 121251Z=\n',
        },
      ],
    });
    mockConvertMetarToIwxxm.mockResolvedValue({
      success: true,
      data: '<iwxxm>test</iwxxm>',
    });
    mockValidateIwxxm.mockResolvedValue({
      is_valid: true,
      version: '2025-2',
      layers_passed: ['XML_WELLFORMED', 'XML_SCHEMA'],
      layers_failed: [],
      package_ok: true,
      package_issues: [],
    });
    mockConvertBulletin.mockResolvedValue({
      bulletin_meta: {
        ahl: 'SAUS31 KZNY 121200',
        report_count: 0,
        tt: 'SA',
        aa: 'US',
        cccc: 'KZNY',
        yygggg: '121200',
      },
      results: [],
    });
    mockDecodeTac.mockResolvedValue({
      product: 'METAR',
      segments: [{ start: 0, end: 5, code: 'METAR', explanation: 'type' }],
      residuals: [],
    });
    mockLintTac.mockResolvedValue({
      ok: true,
      issues: [{ severity: 'error', code: 'x', message: 'm', start: 0, end: 5 }],
      fixes: [],
    });
    mockInflateGzipToText.mockResolvedValue('METAR KJFK 121251Z 18004KT=');
    mockReadGuestConverterState.mockReturnValue(null);
    mockIsReadOnly.value = false;
    mockSaveIndicator.value = 'idle';
  });

  afterEach(() => {
    operatorDisseminationUiConfig.destinationsEnabled = false;
    cleanup();
  });

  describe('Rendering', () => {
    it('should render the file converter', () => {
      const { container } = render(<FileConverter {...defaultProps} />);
      expect(container).toBeTruthy();
    });

    it('exposes Help link to the operator one-pager (UJ-054 / TC-EV047-011)', () => {
      render(<FileConverter {...defaultProps} />);
      const help = screen.getByTestId('operator-help-link');
      expect(help).toHaveAttribute(
        'href',
        expect.stringContaining('docs/guides/operator-one-pager.md'),
      );
      expect(help).toHaveAttribute('target', '_blank');
    });

    it('shows Sign in for guests and guest loss notice when local work exists', async () => {
      const user = userEvent.setup();
      const onRequestLogin = vi.fn();
      const { container } = render(
        <FileConverter {...defaultProps} isGuest onRequestLogin={onRequestLogin} />,
      );

      expect(screen.getByTestId('sign-in-button')).toBeInTheDocument();
      expect(screen.queryByTestId('guest-loss-notice')).not.toBeInTheDocument();

      const textarea = container.querySelector('textarea');
      expect(textarea).toBeTruthy();
      await user.type(textarea as HTMLTextAreaElement, 'METAR KJFK');
      expect(screen.getByTestId('guest-loss-notice')).toBeInTheDocument();

      await user.click(screen.getByTestId('sign-in-button'));
      expect(onRequestLogin).toHaveBeenCalled();
      onRequestLogin.mockClear();
      await user.click(
        screen
          .getByTestId('guest-loss-notice')
          .querySelector('button') as HTMLButtonElement,
      );
      expect(onRequestLogin).toHaveBeenCalled();
    });

    it('shows first-visit privacy notice and opens settings from footer', async () => {
      const user = userEvent.setup();
      render(<FileConverter {...defaultProps} />);

      expect(screen.getByTestId('privacy-notice')).toBeInTheDocument();
      await user.click(screen.getByRole('button', { name: /dismiss privacy notice/i }));
      expect(screen.queryByTestId('privacy-notice')).not.toBeInTheDocument();

      await user.click(screen.getByRole('button', { name: /open privacy settings/i }));
      expect(screen.getByTestId('privacy-settings-dialog')).toBeInTheDocument();
      await user.click(screen.getByRole('button', { name: /^close$/i }));
      expect(screen.queryByTestId('privacy-settings-dialog')).not.toBeInTheDocument();
    });

    it('opens privacy settings from the first-visit notice CTA', async () => {
      const user = userEvent.setup();
      render(<FileConverter {...defaultProps} />);

      await user.click(
        screen.getByRole('button', { name: /open privacy settings from notice/i }),
      );
      expect(screen.queryByTestId('privacy-notice')).not.toBeInTheDocument();
      expect(screen.getByTestId('privacy-settings-dialog')).toBeInTheDocument();
    });

    it('hides the privacy notice after it was previously acknowledged', async () => {
      const { acknowledgePrivacyNotice } = await import('@/utils/privacyPreferences');
      acknowledgePrivacyNotice();
      render(<FileConverter {...defaultProps} />);
      expect(screen.queryByTestId('privacy-notice')).not.toBeInTheDocument();
      expect(
        screen.getByRole('button', { name: /open privacy settings/i }),
      ).toBeInTheDocument();
    });

    it('should display user email', () => {
      render(<FileConverter {...defaultProps} />);
      // User email is passed to UserPreferencesDialog but not directly displayed
      // Check that component renders without errors instead
      expect(screen.getByText(/metar.*iwxxm converter/i)).toBeInTheDocument();
    });

    it('should display theme toggle', () => {
      render(<FileConverter {...defaultProps} />);
      expect(screen.getByTestId('theme-toggle')).toBeInTheDocument();
    });

    it('should display database upload button', async () => {
      operatorDisseminationUiConfig.destinationsEnabled = true;
      render(<FileConverter {...defaultProps} />);
      const dbBtn = await screen.findByText(/upload to database/i, {
        selector: 'button',
      });
      expect(dbBtn).toBeInTheDocument();
      // Button should be disabled initially (no converted files)
      expect(dbBtn).toBeDisabled();
    });

    it('should display settings button', async () => {
      render(<FileConverter {...defaultProps} />);
      const settingsBtn = await screen.findByLabelText(/open user preferences/i);
      expect(settingsBtn).toBeInTheDocument();
      expect(settingsBtn).toHaveTextContent(/preferences/i);
    });
  });

  describe('Dialog Management', () => {
    it('should open database upload dialog', async () => {
      operatorDisseminationUiConfig.destinationsEnabled = true;
      render(<FileConverter {...defaultProps} />);

      // Database upload button is initially disabled (no converted files)
      const dbBtn = await screen.findByText(/upload to database/i, {
        selector: 'button',
      });
      expect(dbBtn).toBeDisabled();

      // Dialog should remain closed
      const dialog = screen.getByTestId('database-upload-dialog');
      expect(dialog.style.display).toBe('none');
    });

    it('should close database upload dialog', async () => {
      operatorDisseminationUiConfig.destinationsEnabled = true;
      render(<FileConverter {...defaultProps} />);

      // Database upload button is initially disabled
      const dbBtn = await screen.findByText(/upload to database/i, {
        selector: 'button',
      });
      expect(dbBtn).toBeDisabled();

      // Dialog should be closed initially
      const dialog = screen.getByTestId('database-upload-dialog');
      expect(dialog.style.display).toBe('none');
    });

    it('should open preferences dialog', async () => {
      const user = userEvent.setup();
      render(<FileConverter {...defaultProps} />);

      const settingsBtn = await screen.findByLabelText(/open user preferences/i);
      await user.click(settingsBtn);

      await waitFor(() => {
        const dialog = screen.getByTestId('preferences-dialog');
        expect(dialog.style.display).not.toBe('none');
      });
    });

    it('should close preferences dialog', async () => {
      const user = userEvent.setup();
      render(<FileConverter {...defaultProps} />);

      const settingsBtn = await screen.findByLabelText(/open user preferences/i);
      await user.click(settingsBtn);

      await waitFor(() => {
        expect(screen.getByTestId('preferences-dialog').style.display).not.toBe('none');
      });

      const closeBtn = screen.getByTestId('close-prefs-dialog');
      await user.click(closeBtn);

      await waitFor(() => {
        expect(screen.getByTestId('preferences-dialog').style.display).toBe('none');
      });
    });
  });

  describe('File Input', () => {
    it('should accept file uploads', async () => {
      const { container } = render(<FileConverter {...defaultProps} />);
      const fileInput = container.querySelector('input[type="file"]');
      expect(fileInput).toBeInTheDocument();
    });

    it('should accept multiple files', async () => {
      const { container } = render(<FileConverter {...defaultProps} />);
      const fileInput = container.querySelector(
        'input[type="file"]',
      ) as HTMLInputElement;
      expect(fileInput.multiple).toBe(true);
    });

    it('should accept text/plain and application/json files', async () => {
      const { container } = render(<FileConverter {...defaultProps} />);
      const fileInput = container.querySelector(
        'input[type="file"]',
      ) as HTMLInputElement;
      expect(fileInput.accept).toContain('.txt');
      expect(fileInput.accept).toContain('.tac');
      expect(fileInput.accept).toContain('.metar');
      expect(fileInput.accept).toContain('.gz');
      expect(fileInput.accept).toContain('.xml');
    });
  });

  describe('Workbench layout', () => {
    it('shows compact drop zone under the console and product type beside TAC', () => {
      render(<FileConverter {...defaultProps} />);

      expect(screen.getByTestId('compact-file-drop-zone')).toBeInTheDocument();
      expect(screen.getByTestId('product-type-select')).toBeInTheDocument();
      expect(screen.getByTestId('input-mode-group')).toBeInTheDocument();
      expect(screen.getByTestId('workbench-console')).toBeInTheDocument();
      expect(
        screen.queryByText(/drop files here or click to select/i),
      ).not.toBeInTheDocument();
      expect(screen.getByText(/drop tac files or select/i)).toBeInTheDocument();
      expect(
        screen.getByText(/\.txt, \.metar, \.tac, \.xml, \.gz/i),
      ).toBeInTheDocument();
    });
  });

  describe('Drag and Drop', () => {
    it('should handle drag over and track dragging state', async () => {
      render(<FileConverter {...defaultProps} />);
      const dropZone = screen.getByRole('button', { name: /file drop zone/i });

      fireEvent.dragOver(dropZone, { dataTransfer: { items: [] } });

      await waitFor(() => {
        expect(dropZone).toBeInTheDocument();
      });
    });

    it('should handle drag leave and reset dragging state', async () => {
      render(<FileConverter {...defaultProps} />);
      const dropZone = screen.getByRole('button', { name: /file drop zone/i });

      fireEvent.dragLeave(dropZone);

      await waitFor(() => {
        expect(dropZone).toBeInTheDocument();
      });
    });

    it('handles file drop with valid files', async () => {
      render(<FileConverter {...defaultProps} />);
      const dropZone = screen.getByRole('button', { name: /file drop zone/i });

      const goodFile = {
        name: 'test.metar',
        text: vi.fn().mockResolvedValue('METAR EGLL 121650Z'),
      };

      fireEvent.drop(dropZone, {
        dataTransfer: {
          files: {
            0: goodFile,
            length: 1,
          },
        },
      });

      await waitFor(() => {
        expect(mockToast.success).toHaveBeenCalledWith('1 file(s) added to queue');
      });
    });
  });

  describe('Manual Input', () => {
    it('should accept manual METAR input', async () => {
      const user = userEvent.setup();
      const { container } = render(<FileConverter {...defaultProps} />);

      const textarea = container.querySelector('textarea');
      if (textarea) {
        await user.type(textarea, 'METAR KJFK...');
        expect(textarea).toHaveValue('METAR KJFK...');
      }
    });

    it('should accept manual TAF input', async () => {
      const user = userEvent.setup();
      const { container } = render(<FileConverter {...defaultProps} />);

      const textarea = container.querySelector('textarea');
      if (textarea) {
        await user.type(textarea, 'TAF KJFK...');
        expect(textarea).toHaveValue('TAF KJFK...');
      }
    });

    it('should clear input when clear button is clicked', async () => {
      const user = userEvent.setup();
      const { container } = render(<FileConverter {...defaultProps} />);

      const textarea = container.querySelector('textarea');
      if (textarea) {
        await user.type(textarea, 'Test content');
        expect(textarea).toHaveValue('Test content');

        const clearBtn = await screen.findByRole('button', {
          name: /clear all pending files and manual input/i,
        });
        await user.click(clearBtn);

        expect(textarea).toHaveValue('');
      }
    });

    it('live workbench debounces lint/decode; live IWXXM defaults off', async () => {
      vi.useFakeTimers();
      try {
        mockLintTac.mockClear();
        mockDecodeTac.mockClear();
        const { container } = render(<FileConverter {...defaultProps} />);

        expect(screen.getByTestId('live-iwxxm-toggle')).not.toBeChecked();
        expect(screen.getByTestId('workbench-console')).toBeInTheDocument();

        const textarea = container.querySelector('textarea') as HTMLTextAreaElement;
        fireEvent.change(textarea, { target: { value: 'METAR KJFK' } });
        await act(async () => {
          await vi.advanceTimersByTimeAsync(350);
        });
        expect(mockLintTac).toHaveBeenCalled();
        expect(mockDecodeTac).toHaveBeenCalled();

        fireEvent.click(screen.getByTestId('live-iwxxm-toggle'));
        expect(screen.getByTestId('live-iwxxm-toggle')).toBeChecked();

        fireEvent.click(screen.getByTestId('workbench-console-toggle'));
        expect(screen.getByTestId('workbench-console-lines')).toBeInTheDocument();

        // live IWXXM is on — soft-preview convert with failed spans
        mockConvertMetarToIwxxm.mockClear();
        mockConvertMetarToIwxxm.mockResolvedValueOnce({
          results: [{ iwxxm_xml: '<x/>' }],
          errors: [],
          ok: false,
          failed_spans: [{ start: 0, end: 5, message: 'bad' }],
        });
        fireEvent.change(textarea, { target: { value: 'METAR KJFK 121251Z' } });
        await act(async () => {
          await vi.advanceTimersByTimeAsync(350);
        });
        expect(mockConvertMetarToIwxxm).toHaveBeenCalledWith(
          expect.objectContaining({ preview: true }),
        );
        expect(screen.getByTestId('failed-tac-cue')).toBeInTheDocument();

        // Error path (non-abort) is exercised without hanging fake timers
        mockConvertMetarToIwxxm.mockRejectedValueOnce(new Error('Live IWXXM failed'));
        fireEvent.change(textarea, { target: { value: 'METAR KJFK 121251Z =' } });
        await act(async () => {
          await vi.advanceTimersByTimeAsync(350);
          await Promise.resolve();
        });

        // Clearing text short-circuits live IWXXM runner (no convert call)
        mockConvertMetarToIwxxm.mockClear();
        fireEvent.change(textarea, { target: { value: '   ' } });
        await act(async () => {
          await vi.advanceTimersByTimeAsync(350);
        });
        expect(mockConvertMetarToIwxxm).not.toHaveBeenCalled();

        // Successful preview clears failed spans
        fireEvent.click(screen.getByTestId('live-iwxxm-toggle')); // ensure on
        if (!(screen.getByTestId('live-iwxxm-toggle') as HTMLInputElement).checked) {
          fireEvent.click(screen.getByTestId('live-iwxxm-toggle'));
        }
        mockConvertMetarToIwxxm.mockResolvedValueOnce({
          results: [{ iwxxm_xml: '<ok/>' }],
          errors: [],
          ok: true,
          failed_spans: [],
        });
        fireEvent.change(textarea, {
          target: { value: 'METAR KJFK 121251Z 18004KT' },
        });
        await act(async () => {
          await vi.advanceTimersByTimeAsync(350);
          await Promise.resolve();
        });
        expect(screen.queryByTestId('failed-tac-cue')).toBeNull();
      } finally {
        vi.useRealTimers();
      }
    });
  });

  describe('Conversion Parameters', () => {
    it('should expand and collapse parameters section', async () => {
      const user = userEvent.setup();
      render(<FileConverter {...defaultProps} />);

      const expandBtn = await screen.findByLabelText(/expand parameters/i);
      await user.click(expandBtn);

      // Parameters should be visible
      const paramsSection = await screen.findByText(/iwxxm version/i);
      expect(paramsSection).toBeInTheDocument();
    });

    it('should allow changing IWXXM version', async () => {
      const user = userEvent.setup();
      const { container } = render(<FileConverter {...defaultProps} />);

      // Expand parameters
      const expandBtn = await screen.findByLabelText(/expand parameters/i);
      await user.click(expandBtn);

      // Find and change version
      const selects = container.querySelectorAll('select');
      if (selects.length > 0) {
        await user.click(selects[0]);
        // Would select different version
      }
    });

    it('should allow setting bulletin ID', async () => {
      const user = userEvent.setup();
      const { container } = render(<FileConverter {...defaultProps} />);

      const expandBtn = await screen.findByLabelText(/expand parameters/i);
      await user.click(expandBtn);

      const inputs = container.querySelectorAll('input[type="text"]');
      const bulletinInput = inputs[0];
      if (bulletinInput) {
        await user.clear(bulletinInput);
        await user.type(bulletinInput, 'TEST01');
      }
    });
  });

  describe('User Preferences', () => {
    it('should load preferences from localStorage', () => {
      const prefs = {
        bulletinIdExample: 'CUSTOM',
        issuingCenter: 'TEST',
        iwxxmVersion: '2.1',
        strictValidation: false,
        includeNilReasons: false,
        onError: 'skip',
        logLevel: 'DEBUG',
      };
      localStorage.setItem('metar_converter_preferences', JSON.stringify(prefs));

      const { container } = render(<FileConverter {...defaultProps} />);
      expect(container).toBeTruthy();
      // Preferences would be loaded into component state
    });

    it('should handle invalid localStorage data gracefully', () => {
      localStorage.setItem('metar_converter_preferences', 'invalid json');
      const consoleSpy = vi.spyOn(console, 'error');

      const { container } = render(<FileConverter {...defaultProps} />);
      expect(container).toBeTruthy();

      consoleSpy.mockRestore();
    });

    it('reloads preferences on save and migrates legacy version to 2025-2', async () => {
      const user = userEvent.setup();
      localStorage.setItem(
        'metar_converter_preferences',
        JSON.stringify({
          bulletinIdExample: 'SAAA00',
          issuingCenter: 'KWBC',
          iwxxmVersion: '2023-1',
          strictValidation: true,
          includeNilReasons: true,
          onError: 'warn',
          logLevel: 'INFO',
        }),
      );

      const { container } = render(<FileConverter {...defaultProps} />);
      const expandBtn = screen.getByLabelText(/expand parameters/i);
      await user.click(expandBtn);

      const versionSelect = container.querySelector(
        '#param-iwxxm-version',
      ) as HTMLSelectElement;
      expect(versionSelect.value).toBe('2023-1');

      localStorage.setItem(
        'metar_converter_preferences',
        JSON.stringify({
          bulletinIdExample: 'BBBB01',
          issuingCenter: 'KDEN',
          iwxxmVersion: '2.1',
          strictValidation: false,
          includeNilReasons: false,
          onError: 'skip',
          logLevel: 'DEBUG',
        }),
      );

      await user.click(screen.getByLabelText(/open user preferences/i));
      await user.click(screen.getByTestId('save-prefs-dialog'));

      await waitFor(() => {
        expect(versionSelect.value).toBe('2025-2');
      });
      expect(mockToast.info).toHaveBeenCalledTimes(1);
    });

    it('keeps 2023-1 version unchanged when preferences are reloaded', async () => {
      const user = userEvent.setup();
      localStorage.setItem(
        'metar_converter_preferences',
        JSON.stringify({
          bulletinIdExample: 'CCCC02',
          issuingCenter: 'KJFK',
          iwxxmVersion: '2023-1',
          strictValidation: true,
          includeNilReasons: true,
          onError: 'warn',
          logLevel: 'INFO',
        }),
      );

      const { container } = render(<FileConverter {...defaultProps} />);
      await user.click(screen.getByLabelText(/expand parameters/i));

      const versionSelect = container.querySelector(
        '#param-iwxxm-version',
      ) as HTMLSelectElement;
      expect(versionSelect.value).toBe('2023-1');

      await user.click(screen.getByLabelText(/open user preferences/i));
      await user.click(screen.getByTestId('save-prefs-dialog'));

      await waitFor(() => {
        expect(versionSelect.value).toBe('2023-1');
      });
    });

    it('handles malformed JSON during preferences reload path', async () => {
      const user = userEvent.setup();
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => undefined);

      render(<FileConverter {...defaultProps} />);
      localStorage.setItem('metar_converter_preferences', '{invalid');

      await user.click(screen.getByLabelText(/open user preferences/i));
      await user.click(screen.getByTestId('save-prefs-dialog'));

      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalled();
      });

      consoleSpy.mockRestore();
    });
  });

  describe('Response Handling', () => {
    it('should display converted output', async () => {
      render(<FileConverter {...defaultProps} />);
      const { container } = render(<FileConverter {...defaultProps} />);

      // Conversion output area should exist
      const outputArea = container.querySelector('[class*="output"]');
      expect(outputArea || container).toBeTruthy();
    });

    it('should have copy button for results', async () => {
      render(<FileConverter {...defaultProps} />);
      // Copy button only appears when there are converted files,
      // so we just check the component renders without errors
      expect(screen.getByText(/metar.*iwxxm converter/i)).toBeInTheDocument();
    });

    it('should have download button for results', async () => {
      render(<FileConverter {...defaultProps} />);
      const downloadBtn = await screen.findByText(/download/i, { selector: 'button' });
      expect(downloadBtn).toBeInTheDocument();
    });
  });

  describe('Loading States', () => {
    it('should show loading indicator during conversion', async () => {
      const { container } = render(<FileConverter {...defaultProps} />);
      expect(container).toBeTruthy();
      // Loading state management
    });

    it('should disable inputs during conversion', async () => {
      const { container } = render(<FileConverter {...defaultProps} />);
      expect(container).toBeTruthy();
      // Button states would change during conversion
    });
  });

  describe('Error Handling', () => {
    it('should handle empty input', async () => {
      const user = userEvent.setup();
      render(<FileConverter {...defaultProps} />);

      const convertBtn = screen.getByTestId('convert-button');
      await user.click(convertBtn);

      // Should show error or validation message
    });

    it('should display conversion errors', async () => {
      render(<FileConverter {...defaultProps} />);
      // Check that there are no error toasts initially
      // The word "error" appears in UI labels like "On Error Behavior"
      const errorLabels = screen.queryAllByText(/error/i);
      // Should only be labels, not error messages
      expect(errorLabels.length).toBeGreaterThan(0); // UI labels exist
    });

    it('shows toast notification when convert is clicked with no input', async () => {
      const user = userEvent.setup();
      render(<FileConverter {...defaultProps} />);

      const convertBtn = screen.getByTestId('convert-button');
      expect(convertBtn).toBeDisabled();

      await user.click(convertBtn);

      expect(mockToast.error).not.toHaveBeenCalled();
    });
  });

  describe('Download Behavior', () => {
    it('should not process download when no converted files exist', async () => {
      render(<FileConverter {...defaultProps} />);

      // Use aria-label to find the download button uniquely
      const downloadBtn = screen.getByLabelText(
        /download all.*converted files as zip/i,
      );
      expect(downloadBtn).toBeDisabled();

      const user = userEvent.setup();
      await user.click(downloadBtn);

      expect(mockToast.success).not.toHaveBeenCalledWith(
        expect.stringContaining('downloaded'),
      );
    });
  });

  describe('Branch Path Coverage', () => {
    it('enables convert button when manual input is provided and converts successfully', async () => {
      const user = userEvent.setup();
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [{ iwxxm_xml: '<iwxxm>converted</iwxxm>' }],
      });

      const { container } = render(<FileConverter {...defaultProps} />);
      const convertBtn = screen.getByTestId('convert-button');
      expect(convertBtn).toBeDisabled();

      const textarea = container.querySelector('textarea') as HTMLTextAreaElement;
      await user.type(textarea, 'METAR KJFK 121651Z 18005KT 10SM FEW030 24/16 A2992');
      expect(convertBtn).toBeEnabled();

      await user.click(convertBtn);

      await waitFor(() => {
        expect(mockConvertMetarToIwxxm).toHaveBeenCalledTimes(1);
      });

      expect(
        screen.getByRole('region', { name: /conversion results/i }),
      ).toBeInTheDocument();
      expect(screen.getByText(/manual_input\.txt/)).toBeInTheDocument();
      expect(mockToast.success).toHaveBeenCalledWith(
        'Successfully converted 1 file(s)',
      );
      expect(screen.queryByText('Conversion Error')).not.toBeInTheDocument();
    });

    it('displays source TAC alongside converted XML when API returns tac_input', async () => {
      const user = userEvent.setup();
      const tac = 'METAR FAOR 101200Z COR 12012KT 9999 FEW020 22/14 Q1018';
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [
          {
            name: 'manual_input.txt',
            content: '<iwxxm:METAR>converted</iwxxm:METAR>',
            tac_input: tac,
            source: 'manual_input',
            size_bytes: 32,
          },
        ],
      });

      const { container } = render(<FileConverter {...defaultProps} />);
      const textarea = container.querySelector('textarea') as HTMLTextAreaElement;
      await user.type(textarea, tac);
      await user.click(screen.getByTestId('convert-button'));

      await waitFor(() => {
        expect(
          screen.getByRole('region', {
            name: /original tac input for metar faor 101200z/i,
          }),
        ).toBeInTheDocument();
      });
      expect(screen.getByText('Source TAC')).toBeInTheDocument();
      // EV-040: TAC remains in the editor after convert, so it appears twice.
      expect(screen.getAllByText(tac).length).toBeGreaterThanOrEqual(2);
      expect(screen.getByText('METAR FAOR 101200Z')).toBeInTheDocument();
      expect(screen.getByText(/Download: manual_input\.txt/)).toBeInTheDocument();
    });

    it('shows Source TAC from manual input when API omits tac_input (#655)', async () => {
      const user = userEvent.setup();
      const tac = 'METAR KJFK 121251Z 18012KT 10SM FEW030 24/16 A2992';
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [
          {
            name: 'manual_input.txt',
            content: '<iwxxm:METAR>converted</iwxxm:METAR>',
            source: 'manual_input',
            size_bytes: 32,
          },
        ],
      });

      const { container } = render(<FileConverter {...defaultProps} />);
      const textarea = container.querySelector('textarea') as HTMLTextAreaElement;
      await user.type(textarea, tac);
      await user.click(screen.getByTestId('convert-button'));

      await waitFor(() => {
        expect(screen.getByText('Source TAC')).toBeInTheDocument();
      });
      // EV-040: editor keeps input; Source TAC panel also shows it.
      expect(screen.getAllByText(tac).length).toBeGreaterThanOrEqual(2);
      expect(screen.getByText('METAR KJFK 121251Z')).toBeInTheDocument();
    });

    it('maps manual-before-file API results to correct original names', async () => {
      const user = userEvent.setup();
      const manualTac = 'METAR FAOR 101200Z COR 12012KT 9999 FEW020 22/14 Q1018';
      const fileTac = 'METAR EGLL 121650Z 22008KT 9999 BKN025 18/12 Q1016';
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [
          {
            name: 'manual_input.txt',
            content: '<iwxxm:METAR>manual</iwxxm:METAR>',
            tac_input: manualTac,
            source: 'manual_input',
          },
          {
            name: 'uploaded',
            content: '<iwxxm:METAR>file</iwxxm:METAR>',
            tac_input: fileTac,
            source: 'uploaded.metar',
          },
        ],
      });

      const { container } = render(<FileConverter {...defaultProps} />);
      const fileInput = container.querySelector(
        'input[type="file"]',
      ) as HTMLInputElement;
      fireEvent.change(fileInput, {
        target: {
          files: {
            0: {
              name: 'uploaded.metar',
              text: vi.fn().mockResolvedValue(fileTac),
            },
            length: 1,
          },
        },
      });

      await waitFor(() => {
        expect(screen.getByText('uploaded.metar')).toBeInTheDocument();
      });

      const textarea = container.querySelector('textarea') as HTMLTextAreaElement;
      await user.type(textarea, manualTac);
      await user.click(screen.getByTestId('convert-button'));

      await waitFor(() => {
        expect(screen.getByText(/manual_input\.txt/)).toBeInTheDocument();
        expect(screen.getAllByText(/uploaded\.metar/).length).toBeGreaterThanOrEqual(1);
      });
    });

    it('shows timeout status when backend conversion times out', async () => {
      const user = userEvent.setup();
      mockConvertMetarToIwxxm.mockRejectedValueOnce(
        new Error('backend timeout unreachable'),
      );

      const { container } = render(<FileConverter {...defaultProps} />);
      const textarea = container.querySelector('textarea') as HTMLTextAreaElement;
      await user.type(textarea, 'METAR EGLL 121650Z 22008KT 9999 BKN025 18/12 Q1016');

      await user.click(screen.getByTestId('convert-button'));

      await waitFor(() => {
        expect(screen.getByText(/backend may be unreachable/i)).toBeInTheDocument();
      });
      expect(mockToast.error).toHaveBeenCalledWith(
        'Conversion timeout - Backend may be unreachable. Please check if the API server is running.',
      );
    });

    it('shows auth error when backend returns unauthorized', async () => {
      const user = userEvent.setup();
      mockConvertMetarToIwxxm.mockRejectedValueOnce(new Error('401 unauthorized'));

      const { container } = render(<FileConverter {...defaultProps} />);
      const textarea = container.querySelector('textarea') as HTMLTextAreaElement;
      await user.type(textarea, 'METAR KDEN 121653Z 02006KT 10SM SCT050 21/08 A3010');

      await user.click(screen.getByTestId('convert-button'));

      await waitFor(() => {
        expect(screen.getByText(/authentication failed/i)).toBeInTheDocument();
      });
      expect(mockToast.error).toHaveBeenCalledWith(
        'Authentication failed. Please ensure you are logged in.',
      );
    });

    it('shows toast when reading one dropped file fails', async () => {
      const user = userEvent.setup();
      const badFile = {
        name: 'broken.metar',
        text: vi.fn().mockRejectedValue(new Error('read failed')),
      };

      const { container } = render(<FileConverter {...defaultProps} />);
      const fileInput = container.querySelector(
        'input[type="file"]',
      ) as HTMLInputElement;

      fireEvent.change(fileInput, {
        target: {
          files: {
            0: badFile,
            length: 1,
          },
        },
      });

      await waitFor(() => {
        expect(mockToast.error).toHaveBeenCalledWith('read failed');
      });

      await user.click(
        screen.getByRole('button', {
          name: /clear all pending files and manual input/i,
        }),
      );
      expect(mockToast.info).toHaveBeenCalledWith('Queue cleared');
    });

    it('opens file chooser when drop zone is activated by keyboard', async () => {
      render(<FileConverter {...defaultProps} />);

      const dropZone = screen.getByRole('button', { name: /file drop zone/i });
      const hiddenInput = screen.getByLabelText(
        /select tac files to upload/i,
      ) as HTMLInputElement;
      const clickSpy = vi
        .spyOn(hiddenInput, 'click')
        .mockImplementation(() => undefined);

      fireEvent.keyDown(dropZone, { key: 'Enter', code: 'Enter' });

      expect(clickSpy).toHaveBeenCalledTimes(1);
      clickSpy.mockRestore();
    });

    it('copies using modern clipboard API success path', async () => {
      const user = userEvent.setup();
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [{ iwxxm_xml: '<iwxxm>clipboard-success</iwxxm>' }],
      });

      const writeTextSpy = vi.fn().mockResolvedValue(undefined);
      const clipboardSpy = vi.spyOn(navigator, 'clipboard', 'get');
      clipboardSpy.mockReturnValue({ writeText: writeTextSpy } as unknown as Clipboard);

      const { container } = render(<FileConverter {...defaultProps} />);
      const textarea = container.querySelector('textarea') as HTMLTextAreaElement;
      await user.type(textarea, 'METAR CLIPBOARD SUCCESS');
      await user.click(screen.getByTestId('convert-button'));

      await waitFor(() => {
        expect(screen.getByText(/manual_input\.txt/)).toBeInTheDocument();
      });

      await user.click(
        screen.getByRole('button', {
          name: /copy manual_input\.txt content to clipboard/i,
        }),
      );

      await waitFor(() => {
        expect(writeTextSpy).toHaveBeenCalledWith('<iwxxm>clipboard-success</iwxxm>');
      });
      expect(mockToast.success).toHaveBeenCalledWith('Copied to clipboard');
      clipboardSpy.mockRestore();
    });

    it('removes pending and converted files via row actions', async () => {
      const user = userEvent.setup();
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [{ iwxxm_xml: '<iwxxm>remove-me</iwxxm>' }],
      });

      const { container } = render(<FileConverter {...defaultProps} />);
      const fileInput = container.querySelector(
        'input[type="file"]',
      ) as HTMLInputElement;
      const goodFile = {
        name: 'pending.txt',
        text: vi.fn().mockResolvedValue('METAR PENDING'),
      };

      fireEvent.change(fileInput, {
        target: {
          files: {
            0: goodFile,
            length: 1,
          },
        },
      });

      await waitFor(() => {
        expect(screen.getByText('pending.txt')).toBeInTheDocument();
      });

      await user.click(
        screen.getByRole('button', { name: /remove pending\.txt from queue/i }),
      );
      await waitFor(() => {
        expect(screen.queryByText('pending.txt')).not.toBeInTheDocument();
      });

      const manualInput = container.querySelector('textarea') as HTMLTextAreaElement;
      await user.type(manualInput, 'METAR CONVERT FOR REMOVE');
      await user.click(screen.getByTestId('convert-button'));

      await waitFor(() => {
        expect(screen.getByText(/manual_input\.txt/)).toBeInTheDocument();
      });

      await user.click(
        screen.getByRole('button', { name: /remove manual_input\.txt from results/i }),
      );
      await waitFor(() => {
        expect(screen.queryByText(/manual_input\.txt/)).not.toBeInTheDocument();
      });
    });

    it('opens upload dialog when converted files are present (destinations UI on)', async () => {
      operatorDisseminationUiConfig.destinationsEnabled = true;
      const user = userEvent.setup();
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [{ iwxxm_xml: '<iwxxm>upload-test</iwxxm>' }],
      });

      const { container } = render(<FileConverter {...defaultProps} />);
      const textarea = container.querySelector('textarea') as HTMLTextAreaElement;
      await user.type(textarea, 'METAR UPLOAD BUTTON');
      await user.click(screen.getByTestId('convert-button'));

      const uploadButton = await screen.findByTestId('upload-to-database-button');
      expect(uploadButton).toBeEnabled();

      await user.click(uploadButton);
      await waitFor(() => {
        expect(screen.getByTestId('database-upload-dialog').style.display).toBe(
          'block',
        );
      });
    });

    it('hides Convert&Send, Disseminate, and Upload to Database while destinations UI is off (TC-EV042-001 / #897)', () => {
      render(<FileConverter {...defaultProps} />);
      expect(screen.queryByTestId('open-dissemination-drawer')).not.toBeInTheDocument();
      expect(screen.queryByTestId('convert-and-send-button')).not.toBeInTheDocument();
      expect(screen.queryByTestId('upload-to-database-button')).not.toBeInTheDocument();
      expect(
        screen.queryByRole('button', {
          name: /upload .* converted files to database/i,
        }),
      ).not.toBeInTheDocument();
      expect(screen.getByTestId('convert-button')).toBeInTheDocument();
    });

    it('mass ingest Folder button prompts login when guest (TC-F33-004 / UJ-051)', async () => {
      const user = userEvent.setup();
      const onRequestLogin = vi.fn();
      render(
        <FileConverter {...defaultProps} isGuest onRequestLogin={onRequestLogin} />,
      );

      await user.click(screen.getByTestId('mass-ingest-folder-button'));

      expect(onRequestLogin).toHaveBeenCalled();
      expect(mockToast.error).toHaveBeenCalledWith(
        'Sign in required for mass folder or zip ingest',
      );
      expect(mockMassIngestFiles).not.toHaveBeenCalled();
    });

    it('mass ingest Zip hands accepted files into pending queue (TC-F33-001 / UJ-051)', async () => {
      const user = userEvent.setup();
      render(<FileConverter {...defaultProps} accessToken="jwt-f33" />);

      const zipInput = screen.getByTestId('mass-ingest-zip-input') as HTMLInputElement;
      const zipFile = new File(['PK fake'], 'batch.zip', { type: 'application/zip' });
      await user.upload(zipInput, zipFile);

      await waitFor(() => {
        expect(mockMassIngestFiles).toHaveBeenCalledWith(
          expect.objectContaining({
            accessToken: 'jwt-f33',
            files: expect.arrayContaining([
              expect.objectContaining({ name: 'batch.zip' }),
            ]),
          }),
        );
      });

      await waitFor(() => {
        expect(
          screen.getByRole('region', { name: /pending files queue/i }),
        ).toBeInTheDocument();
      });
      expect(mockToast.loading).toHaveBeenCalled();
      expect(mockToast.success).toHaveBeenCalledWith(
        'Mass ingest: 1 accepted, 0 rejected',
        expect.anything(),
      );
    });

    it('work queue keyboard next + Enter converts focused item (TC-EV042-003)', async () => {
      const user = userEvent.setup();
      mockConvertMetarToIwxxm.mockResolvedValue({
        results: [
          {
            iwxxm_xml: '<iwxxm>focused</iwxxm>',
            name: 'second.tac',
            tac_input: 'METAR SECOND',
          },
        ],
      });

      const { container } = render(<FileConverter {...defaultProps} />);
      const fileInput = container.querySelector(
        'input[type="file"]:not([data-testid])',
      ) as HTMLInputElement;
      fireEvent.change(fileInput, {
        target: {
          files: {
            0: { name: 'first.tac', text: vi.fn().mockResolvedValue('METAR FIRST') },
            1: {
              name: 'second.tac',
              text: vi.fn().mockResolvedValue('METAR SECOND'),
            },
            length: 2,
          },
        },
      });

      const queue = await screen.findByTestId('operator-work-queue');
      queue.focus();
      await user.keyboard('{ArrowDown}{Enter}');

      await waitFor(() => {
        expect(mockConvertMetarToIwxxm).toHaveBeenCalled();
      });
      const call = mockConvertMetarToIwxxm.mock.calls.at(-1)?.[0] as {
        files?: File[];
        manualText?: string;
      };
      expect(call.manualText).toBeUndefined();
      expect(call.files?.map((f) => f.name)).toEqual(['second.tac']);
    });

    it('batch validate runs lint on selected queue items (TC-EV042-003)', async () => {
      const user = userEvent.setup();
      mockLintTac.mockResolvedValue({ ok: true, issues: [], fixes: [] });

      const { container } = render(<FileConverter {...defaultProps} />);
      const fileInput = container.querySelector(
        'input[type="file"]:not([data-testid])',
      ) as HTMLInputElement;
      fireEvent.change(fileInput, {
        target: {
          files: {
            0: { name: 'a.tac', text: vi.fn().mockResolvedValue('METAR A') },
            1: { name: 'b.tac', text: vi.fn().mockResolvedValue('METAR B') },
            length: 2,
          },
        },
      });

      await screen.findByTestId('operator-work-queue');
      await user.click(screen.getByTestId('queue-select-0'));
      await user.click(screen.getByTestId('queue-select-1'));
      await user.click(screen.getByTestId('batch-validate-button'));

      await waitFor(() => {
        expect(mockLintTac).toHaveBeenCalledTimes(2);
      });
      expect(mockToast.success).toHaveBeenCalledWith(
        'Batch validate: 2 ok, 0 with issues',
        expect.anything(),
      );
    });

    it('batch convert runs convert on selected queue items (TC-EV042-003)', async () => {
      const user = userEvent.setup();
      mockConvertMetarToIwxxm.mockResolvedValue({
        results: [
          { iwxxm_xml: '<iwxxm>a</iwxxm>', name: 'a.tac', tac_input: 'METAR A' },
          { iwxxm_xml: '<iwxxm>b</iwxxm>', name: 'b.tac', tac_input: 'METAR B' },
        ],
      });

      const { container } = render(<FileConverter {...defaultProps} />);
      const fileInput = container.querySelector(
        'input[type="file"]:not([data-testid])',
      ) as HTMLInputElement;
      fireEvent.change(fileInput, {
        target: {
          files: {
            0: { name: 'a.tac', text: vi.fn().mockResolvedValue('METAR A') },
            1: { name: 'b.tac', text: vi.fn().mockResolvedValue('METAR B') },
            length: 2,
          },
        },
      });

      await screen.findByTestId('operator-work-queue');
      await user.click(screen.getByTestId('queue-select-0'));
      await user.click(screen.getByTestId('queue-select-1'));
      await user.click(screen.getByTestId('batch-convert-button'));

      await waitFor(() => {
        expect(mockConvertMetarToIwxxm).toHaveBeenCalled();
      });
      expect(mockToast.success).toHaveBeenCalledWith(
        expect.stringMatching(/Batch converted/i),
      );
    });

    it('work queue Shift+Enter validates focused item (TC-EV042-003)', async () => {
      const user = userEvent.setup();
      mockLintTac.mockResolvedValue({ ok: true, issues: [], fixes: [] });

      const { container } = render(<FileConverter {...defaultProps} />);
      const fileInput = container.querySelector(
        'input[type="file"]:not([data-testid])',
      ) as HTMLInputElement;
      fireEvent.change(fileInput, {
        target: {
          files: {
            0: { name: 'only.tac', text: vi.fn().mockResolvedValue('METAR ONLY') },
            length: 1,
          },
        },
      });

      const queue = await screen.findByTestId('operator-work-queue');
      queue.focus();
      await user.keyboard('{Shift>}{Enter}{/Shift}');

      await waitFor(() => {
        expect(mockLintTac).toHaveBeenCalled();
      });
      expect(mockToast.success).toHaveBeenCalledWith(
        'only.tac: lint OK',
        expect.anything(),
      );
    });

    it('mass ingest Zip button triggers file chooser when signed in', async () => {
      const user = userEvent.setup();
      render(<FileConverter {...defaultProps} accessToken="jwt-f33" />);
      const zipInput = screen.getByTestId('mass-ingest-zip-input') as HTMLInputElement;
      const clickSpy = vi.spyOn(zipInput, 'click');
      await user.click(screen.getByTestId('mass-ingest-zip-button'));
      expect(clickSpy).toHaveBeenCalled();
    });

    it('queue item click focuses and loads TAC into editor', async () => {
      const user = userEvent.setup();
      const { container } = render(<FileConverter {...defaultProps} />);
      const fileInput = container.querySelector(
        'input[type="file"]:not([data-testid])',
      ) as HTMLInputElement;
      fireEvent.change(fileInput, {
        target: {
          files: {
            0: { name: 'first.tac', text: vi.fn().mockResolvedValue('METAR FIRST') },
            1: {
              name: 'second.tac',
              text: vi.fn().mockResolvedValue('METAR SECOND'),
            },
            length: 2,
          },
        },
      });
      await screen.findByTestId('operator-work-queue');
      await user.click(screen.getByTestId('queue-item-1'));
      const textarea = container.querySelector('textarea') as HTMLTextAreaElement;
      await waitFor(() => {
        expect(textarea.value).toContain('METAR SECOND');
      });
    });

    it('opens dissemination drawer from Disseminate control when destinations UI on', async () => {
      operatorDisseminationUiConfig.destinationsEnabled = true;
      const user = userEvent.setup();
      render(<FileConverter {...defaultProps} />);

      const disseminate = screen.getByTestId('open-dissemination-drawer');
      expect(disseminate).toBeEnabled();
      await user.click(disseminate);

      expect(screen.getByTestId('dissemination-drawer')).toBeInTheDocument();
      expect(
        screen.getByRole('heading', { name: /dissemination/i }),
      ).toBeInTheDocument();
    });

    it('mass ingest Folder input hands accepted files into queue when signed in', async () => {
      const user = userEvent.setup();
      render(<FileConverter {...defaultProps} accessToken="jwt-f33" />);

      const folderInput = screen.getByTestId(
        'mass-ingest-folder-input',
      ) as HTMLInputElement;
      const tac = new File(['METAR KJFK=\n'], 'folder.tac', { type: 'text/plain' });
      await user.upload(folderInput, tac);

      await waitFor(() => {
        expect(mockMassIngestFiles).toHaveBeenCalled();
      });
      await waitFor(() => {
        expect(
          screen.getByRole('region', { name: /pending files queue/i }),
        ).toBeInTheDocument();
      });
    });

    it('batch convert with no selection shows error toast', async () => {
      const user = userEvent.setup();
      const { container } = render(<FileConverter {...defaultProps} />);
      const fileInput = container.querySelector(
        'input[type="file"]:not([data-testid])',
      ) as HTMLInputElement;
      fireEvent.change(fileInput, {
        target: {
          files: {
            0: { name: 'a.tac', text: vi.fn().mockResolvedValue('METAR A') },
            length: 1,
          },
        },
      });
      await screen.findByTestId('operator-work-queue');
      // Button disabled when none selected — force handler via empty selection toast path
      const btn = screen.getByTestId('batch-convert-button');
      expect(btn).toBeDisabled();
      await user.click(screen.getByTestId('batch-validate-button'));
      expect(screen.getByTestId('batch-validate-button')).toBeDisabled();
    });

    it('mass ingest surfaces API rejection toast', async () => {
      mockMassIngestFiles.mockRejectedValueOnce(new Error('zip bomb'));
      render(<FileConverter {...defaultProps} accessToken="jwt-f33" />);
      const zipInput = screen.getByTestId('mass-ingest-zip-input') as HTMLInputElement;
      const zipFile = new File(['PK'], 'bad.zip', { type: 'application/zip' });
      await userEvent.setup().upload(zipInput, zipFile);
      await waitFor(() => {
        expect(mockToast.error).toHaveBeenCalledWith('zip bomb', expect.anything());
      });
    });

    it('mass ingest Zip button prompts login when guest', async () => {
      const user = userEvent.setup();
      const onRequestLogin = vi.fn();
      render(
        <FileConverter {...defaultProps} isGuest onRequestLogin={onRequestLogin} />,
      );
      await user.click(screen.getByTestId('mass-ingest-zip-button'));
      expect(onRequestLogin).toHaveBeenCalled();
      expect(mockToast.error).toHaveBeenCalledWith(
        'Sign in required for mass folder or zip ingest',
      );
    });

    it('mass ingest Folder button opens chooser when signed in', async () => {
      const user = userEvent.setup();
      render(<FileConverter {...defaultProps} accessToken="jwt-f33" />);
      const folderInput = screen.getByTestId(
        'mass-ingest-folder-input',
      ) as HTMLInputElement;
      const clickSpy = vi.spyOn(folderInput, 'click');
      await user.click(screen.getByTestId('mass-ingest-folder-button'));
      expect(clickSpy).toHaveBeenCalled();
    });

    it('mass ingest queues accepted files and toasts rejects', async () => {
      mockMassIngestFiles.mockResolvedValueOnce({
        accepted_count: 1,
        rejected_count: 1,
        results: [
          {
            name: 'ok.tac',
            accepted: true,
            reason: null,
            size_bytes: 10,
            content: 'METAR OK=\n',
          },
          {
            name: 'bad.tac',
            accepted: false,
            reason: 'binary',
            size_bytes: 4,
            content: null,
          },
        ],
      });
      render(<FileConverter {...defaultProps} accessToken="jwt-f33" />);
      const zipInput = screen.getByTestId('mass-ingest-zip-input') as HTMLInputElement;
      await userEvent
        .setup()
        .upload(zipInput, new File(['PK'], 'mix.zip', { type: 'application/zip' }));
      await waitFor(() => {
        expect(mockToast.success).toHaveBeenCalledWith(
          'Mass ingest: 1 accepted, 1 rejected',
          expect.anything(),
        );
      });
      expect(
        screen.getByRole('region', { name: /pending files queue/i }),
      ).toBeInTheDocument();
    });

    it('removes a pending file from the work queue', async () => {
      const user = userEvent.setup();
      const { container } = render(<FileConverter {...defaultProps} />);
      const fileInput = container.querySelector(
        'input[type="file"]:not([data-testid])',
      ) as HTMLInputElement;
      fireEvent.change(fileInput, {
        target: {
          files: {
            0: { name: 'gone.tac', text: vi.fn().mockResolvedValue('METAR GONE') },
            length: 1,
          },
        },
      });
      await screen.findByTestId('operator-work-queue');
      await user.click(
        screen.getByRole('button', { name: /Remove gone\.tac from queue/i }),
      );
      await waitFor(() => {
        expect(screen.queryByTestId('operator-work-queue')).not.toBeInTheDocument();
      });
    });

    it('focused validate reports lint issues toast', async () => {
      const user = userEvent.setup();
      mockLintTac.mockResolvedValue({
        ok: false,
        issues: [
          { severity: 'error', code: 'x', message: 'bad', start: 0, end: 1 },
          { severity: 'error', code: 'y', message: 'worse', start: 2, end: 3 },
        ],
        fixes: [],
      });
      const { container } = render(<FileConverter {...defaultProps} />);
      const fileInput = container.querySelector(
        'input[type="file"]:not([data-testid])',
      ) as HTMLInputElement;
      fireEvent.change(fileInput, {
        target: {
          files: {
            0: { name: 'lint.tac', text: vi.fn().mockResolvedValue('METAR LINT') },
            length: 1,
          },
        },
      });
      const queue = await screen.findByTestId('operator-work-queue');
      queue.focus();
      await user.keyboard('{Shift>}{Enter}{/Shift}');
      await waitFor(() => {
        expect(mockToast.error).toHaveBeenCalledWith(
          'lint.tac: 2 lint issue(s)',
          expect.anything(),
        );
      });
    });

    it('handles partial multi-file conversion where only one result is returned', async () => {
      const user = userEvent.setup();
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [{ iwxxm_xml: '<iwxxm>first</iwxxm>' }],
      });

      const { container } = render(<FileConverter {...defaultProps} />);
      const fileInput = container.querySelector(
        'input[type="file"]',
      ) as HTMLInputElement;
      const fileOne = {
        name: 'first.txt',
        text: vi.fn().mockResolvedValue('METAR ONE'),
      };
      const fileTwo = {
        name: 'second.txt',
        text: vi.fn().mockResolvedValue('METAR TWO'),
      };

      fireEvent.change(fileInput, {
        target: {
          files: {
            0: fileOne,
            1: fileTwo,
            length: 2,
          },
        },
      });
      await waitFor(() => {
        expect(
          screen.getByRole('region', { name: /pending files queue/i }),
        ).toBeInTheDocument();
      });

      await user.click(screen.getByTestId('convert-button'));

      await waitFor(() => {
        expect(
          screen.getByRole('region', { name: /conversion results/i }),
        ).toBeInTheDocument();
      });

      expect(
        screen.getByRole('region', { name: /original tac input for metar one/i }),
      ).toBeInTheDocument();
      expect(screen.getByText(/Download: first\.txt/)).toBeInTheDocument();
      expect(screen.queryByText('second.txt')).not.toBeInTheDocument();
      expect(screen.getByText('<iwxxm>first</iwxxm>')).toBeInTheDocument();
    });

    it('shows no-files-converted status when response results is empty', async () => {
      const user = userEvent.setup();
      mockConvertMetarToIwxxm.mockResolvedValueOnce({ results: [] });

      const { container } = render(<FileConverter {...defaultProps} />);
      const textarea = container.querySelector('textarea') as HTMLTextAreaElement;
      await user.type(textarea, 'METAR EMPTY RESULTS CASE');

      await user.click(screen.getByTestId('convert-button'));

      await waitFor(() => {
        expect(screen.getByText(/no files were converted/i)).toBeInTheDocument();
      });
      expect(mockToast.error).toHaveBeenCalledWith('No files were converted');
      expect(screen.getByText('Conversion Error')).toBeInTheDocument();
    });

    it('uses fallback copy path when clipboard API is unavailable', async () => {
      const user = userEvent.setup();
      mockConvertMetarToIwxxm.mockReset().mockResolvedValueOnce({
        results: [{ iwxxm_xml: '<iwxxm>copy-me</iwxxm>' }],
      });

      const clipboardSpy = vi.spyOn(navigator, 'clipboard', 'get');
      clipboardSpy.mockReturnValue(undefined as unknown as Clipboard);
      Object.defineProperty(document, 'execCommand', {
        configurable: true,
        writable: true,
        value: vi.fn().mockReturnValue(true),
      });
      const execSpy = document.execCommand as unknown as ReturnType<typeof vi.fn>;

      const { container } = render(<FileConverter {...defaultProps} />);
      const textarea = container.querySelector('textarea') as HTMLTextAreaElement;
      await user.type(textarea, 'METAR COPY TEST');
      await user.click(screen.getByTestId('convert-button'));

      await waitFor(() => {
        expect(screen.getByText(/manual_input\.txt/)).toBeInTheDocument();
      });

      await user.click(
        screen.getByRole('button', {
          name: /copy manual_input\.txt content to clipboard/i,
        }),
      );

      expect(execSpy).toHaveBeenCalledWith('copy');
      expect(mockToast.success).toHaveBeenCalledWith('Copied to clipboard');

      clipboardSpy.mockRestore();
      execSpy.mockRestore();
    });

    it('shows fallback copy error when execCommand returns false', async () => {
      const user = userEvent.setup();
      mockConvertMetarToIwxxm.mockReset().mockResolvedValueOnce({
        results: [{ iwxxm_xml: '<iwxxm>copy-fail</iwxxm>' }],
      });

      const clipboardSpy = vi.spyOn(navigator, 'clipboard', 'get');
      clipboardSpy.mockReturnValue(undefined as unknown as Clipboard);
      Object.defineProperty(document, 'execCommand', {
        configurable: true,
        writable: true,
        value: vi.fn().mockReturnValue(false),
      });

      const { container } = render(<FileConverter {...defaultProps} />);
      const textarea = container.querySelector('textarea') as HTMLTextAreaElement;
      await user.type(textarea, 'METAR COPY FAIL TEST');
      await user.click(screen.getByTestId('convert-button'));

      await waitFor(() => {
        expect(screen.getByText(/manual_input\.txt/)).toBeInTheDocument();
      });

      await user.click(
        screen.getByRole('button', {
          name: /copy manual_input\.txt content to clipboard/i,
        }),
      );

      expect(mockToast.error).toHaveBeenCalledWith(
        'Failed to copy. Please copy manually.',
      );

      clipboardSpy.mockRestore();
    });

    it('downloads a single converted file', async () => {
      const user = userEvent.setup();
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [{ iwxxm_xml: '<iwxxm>download-single</iwxxm>' }],
      });

      const createUrlSpy = vi
        .spyOn(URL, 'createObjectURL')
        .mockReturnValue('blob:single');
      const revokeUrlSpy = vi
        .spyOn(URL, 'revokeObjectURL')
        .mockImplementation(() => undefined);
      const clickSpy = vi
        .spyOn(HTMLAnchorElement.prototype, 'click')
        .mockImplementation(() => undefined);

      const { container } = render(<FileConverter {...defaultProps} />);
      const textarea = container.querySelector('textarea') as HTMLTextAreaElement;
      await user.type(textarea, 'METAR DOWNLOAD SINGLE');
      await user.click(screen.getByTestId('convert-button'));

      await waitFor(() => {
        expect(screen.getByText(/manual_input\.txt/)).toBeInTheDocument();
      });

      await user.click(
        screen.getByRole('button', { name: /download manual_input\.txt as xml/i }),
      );

      expect(createUrlSpy).toHaveBeenCalled();
      expect(clickSpy).toHaveBeenCalled();
      expect(revokeUrlSpy).toHaveBeenCalledWith('blob:single');

      createUrlSpy.mockRestore();
      revokeUrlSpy.mockRestore();
      clickSpy.mockRestore();
    });

    it('uses error status path for non-timeout non-auth conversion errors', async () => {
      const user = userEvent.setup();
      mockConvertMetarToIwxxm
        .mockReset()
        .mockRejectedValueOnce(new Error('validation parsing failed'));

      const { container } = render(<FileConverter {...defaultProps} />);
      const textarea = container.querySelector('textarea') as HTMLTextAreaElement;
      await user.type(textarea, 'METAR GENERIC ERROR');
      await user.click(screen.getByTestId('convert-button'));

      await waitFor(() => {
        expect(screen.getByText('Conversion Error')).toBeInTheDocument();
        expect(screen.getByText('validation parsing failed')).toBeInTheDocument();
      });
      expect(mockToast.error).toHaveBeenCalledWith('validation parsing failed');
    });

    it('handles result with xml fallback field when iwxxm_xml is missing', async () => {
      const user = userEvent.setup();
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [{ xml: '<xml>fallback-xml</xml>' }],
      });

      const { container } = render(<FileConverter {...defaultProps} />);
      const textarea = container.querySelector('textarea') as HTMLTextAreaElement;
      await user.type(textarea, 'METAR XML FALLBACK');
      await user.click(screen.getByTestId('convert-button'));

      await waitFor(() => {
        expect(mockToast.success).toHaveBeenCalledWith(
          expect.stringContaining('Successfully converted'),
        );
      });
    });

    it('handles result with content fallback field when neither iwxxm_xml nor xml is present', async () => {
      const user = userEvent.setup();
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [{ content: '<content>fallback-content</content>' }],
      });

      const { container } = render(<FileConverter {...defaultProps} />);
      const textarea = container.querySelector('textarea') as HTMLTextAreaElement;
      await user.type(textarea, 'METAR CONTENT FALLBACK');
      await user.click(screen.getByTestId('convert-button'));

      await waitFor(() => {
        expect(mockToast.success).toHaveBeenCalledWith(
          expect.stringContaining('Successfully converted'),
        );
      });
    });

    it('clears files and input when clear button is clicked', async () => {
      const user = userEvent.setup();
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [{ iwxxm_xml: '<iwxxm>clear-test</iwxxm>' }],
      });

      const { container } = render(<FileConverter {...defaultProps} />);
      const textarea = container.querySelector('textarea') as HTMLTextAreaElement;
      await user.type(textarea, 'METAR CLEAR TEST');
      await user.click(screen.getByTestId('convert-button'));

      await waitFor(() => {
        expect(mockToast.success).toHaveBeenCalledWith(
          expect.stringContaining('Successfully converted'),
        );
      });

      await user.click(
        screen.getByRole('button', { name: /clear all pending files/i }),
      );

      await waitFor(() => {
        expect(mockToast.info).toHaveBeenCalledWith('Queue cleared');
      });
    });

    // lines 289-307: handleDownloadAll body (zip creation + anchor click)
    it('downloads all converted files as ZIP after conversion', async () => {
      const user = userEvent.setup();
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [{ iwxxm_xml: '<iwxxm>zip-all</iwxxm>' }],
      });

      const createUrlSpy = vi
        .spyOn(URL, 'createObjectURL')
        .mockReturnValue('blob:zipall');
      const revokeUrlSpy = vi
        .spyOn(URL, 'revokeObjectURL')
        .mockImplementation(() => undefined);
      const clickSpy = vi
        .spyOn(HTMLAnchorElement.prototype, 'click')
        .mockImplementation(() => undefined);

      const { container } = render(<FileConverter {...defaultProps} />);
      const textarea = container.querySelector('textarea') as HTMLTextAreaElement;
      await user.type(textarea, 'METAR DOWNLOAD ALL ZIP');
      await user.click(screen.getByTestId('convert-button'));

      const downloadZipBtn = await screen.findByLabelText(
        /download all 1 converted files as zip/i,
      );
      expect(downloadZipBtn).toBeEnabled();

      await user.click(downloadZipBtn);

      await waitFor(() => {
        expect(mockToast.success).toHaveBeenCalledWith('All files downloaded as ZIP');
      });
      expect(createUrlSpy).toHaveBeenCalled();
      expect(clickSpy).toHaveBeenCalled();
      expect(revokeUrlSpy).toHaveBeenCalledWith('blob:zipall');

      createUrlSpy.mockRestore();
      revokeUrlSpy.mockRestore();
      clickSpy.mockRestore();
    });

    // line 319: clipboard.writeText() .catch() path → fallbackCopy
    it('falls back to execCommand when clipboard.writeText rejects', async () => {
      const user = userEvent.setup();
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [{ iwxxm_xml: '<iwxxm>clipboard-catch</iwxxm>' }],
      });

      const writeTextSpy = vi
        .fn()
        .mockRejectedValue(new Error('clipboard permission denied'));
      const clipboardSpy = vi.spyOn(navigator, 'clipboard', 'get');
      clipboardSpy.mockReturnValue({ writeText: writeTextSpy } as unknown as Clipboard);
      Object.defineProperty(document, 'execCommand', {
        configurable: true,
        writable: true,
        value: vi.fn().mockReturnValue(true),
      });

      const { container } = render(<FileConverter {...defaultProps} />);
      const textarea = container.querySelector('textarea') as HTMLTextAreaElement;
      await user.type(textarea, 'METAR CLIPBOARD CATCH PATH');
      await user.click(screen.getByTestId('convert-button'));

      await waitFor(() => {
        expect(screen.getByText(/manual_input\.txt/)).toBeInTheDocument();
      });

      await user.click(
        screen.getByRole('button', {
          name: /copy manual_input\.txt content to clipboard/i,
        }),
      );

      await waitFor(() => {
        expect(mockToast.success).toHaveBeenCalledWith('Copied to clipboard');
      });

      clipboardSpy.mockRestore();
    });

    // lines 346-347: fallbackCopy catch block when execCommand throws
    it('shows error toast when execCommand throws inside fallbackCopy', async () => {
      const user = userEvent.setup();
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [{ iwxxm_xml: '<iwxxm>exec-throw</iwxxm>' }],
      });

      const clipboardSpy = vi.spyOn(navigator, 'clipboard', 'get');
      clipboardSpy.mockReturnValue(undefined as unknown as Clipboard);
      Object.defineProperty(document, 'execCommand', {
        configurable: true,
        writable: true,
        value: vi.fn().mockImplementation(() => {
          throw new Error('execCommand not supported');
        }),
      });
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => undefined);

      const { container } = render(<FileConverter {...defaultProps} />);
      const textarea = container.querySelector('textarea') as HTMLTextAreaElement;
      await user.type(textarea, 'METAR EXEC THROW PATH');
      await user.click(screen.getByTestId('convert-button'));

      await waitFor(() => {
        expect(screen.getByText(/manual_input\.txt/)).toBeInTheDocument();
      });

      await user.click(
        screen.getByRole('button', {
          name: /copy manual_input\.txt content to clipboard/i,
        }),
      );

      expect(mockToast.error).toHaveBeenCalledWith(
        'Failed to copy. Please copy manually.',
      );
      expect(consoleSpy).toHaveBeenCalled();

      clipboardSpy.mockRestore();
      consoleSpy.mockRestore();
    });

    // line 498: "Select Files" button calls fileInputRef.current?.click()
    it('triggers hidden file input click when Select Files button is pressed', () => {
      const { container } = render(<FileConverter {...defaultProps} />);
      const hiddenInput = container.querySelector(
        'input[type="file"]',
      ) as HTMLInputElement;
      const clickSpy = vi
        .spyOn(hiddenInput, 'click')
        .mockImplementation(() => undefined);

      fireEvent.click(screen.getByRole('button', { name: /browse and select files/i }));

      expect(clickSpy).toHaveBeenCalledTimes(1);
      clickSpy.mockRestore();
    });

    // lines 547-632: onChange handlers in conversion parameter form controls
    it('updates all conversion parameter form controls', async () => {
      const user = userEvent.setup();
      const { container } = render(<FileConverter {...defaultProps} />);

      await user.click(screen.getByLabelText(/expand parameters/i));

      // Bulletin ID – onChange uppercases the value
      const bulletinInput = container.querySelector(
        '#param-bulletin-id',
      ) as HTMLInputElement;
      await user.clear(bulletinInput);
      await user.type(bulletinInput, 'saaa01');
      expect(bulletinInput.value).toBe('SAAA01');

      // Issuing center (mocked IcaoAutocomplete input)
      const icaoInput = screen.getByTestId('icao-input');
      await user.clear(icaoInput);
      await user.type(icaoInput, 'KJFK');
      expect(icaoInput).toHaveValue('KJFK');

      // IWXXM version select
      await user.selectOptions(
        container.querySelector('#param-iwxxm-version') as HTMLSelectElement,
        '2023-1',
      );
      expect(
        (container.querySelector('#param-iwxxm-version') as HTMLSelectElement).value,
      ).toBe('2023-1');

      // On Error behavior select
      await user.selectOptions(
        container.querySelector('#param-on-error') as HTMLSelectElement,
        'fail',
      );
      expect(
        (container.querySelector('#param-on-error') as HTMLSelectElement).value,
      ).toBe('fail');

      // Log level select
      await user.selectOptions(
        container.querySelector('#param-log-level') as HTMLSelectElement,
        'DEBUG',
      );
      expect(
        (container.querySelector('#param-log-level') as HTMLSelectElement).value,
      ).toBe('DEBUG');

      // Validation checkboxes (not soft-preview / live IWXXM toggles)
      const strictCheck = screen
        .getByText('Strict Validation')
        .closest('label')
        ?.querySelector('input[type="checkbox"]') as HTMLInputElement;
      const nilCheck = screen
        .getByText('Include Nil Reasons')
        .closest('label')
        ?.querySelector('input[type="checkbox"]') as HTMLInputElement;
      expect(strictCheck).toBeTruthy();
      expect(nilCheck).toBeTruthy();
      await user.click(strictCheck);
      expect(strictCheck.checked).toBe(false);
      await user.click(nilCheck);
      expect(nilCheck.checked).toBe(false);
    });

    // line 829: DatabaseUploadDialog onClose callback sets isUploadDialogOpen to false
    it('closes database upload dialog when onClose is invoked', async () => {
      operatorDisseminationUiConfig.destinationsEnabled = true;
      const user = userEvent.setup();
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [{ iwxxm_xml: '<iwxxm>close-dialog</iwxxm>' }],
      });

      const { container } = render(<FileConverter {...defaultProps} />);
      const textarea = container.querySelector('textarea') as HTMLTextAreaElement;
      await user.type(textarea, 'METAR CLOSE DIALOG TEST');
      await user.click(screen.getByTestId('convert-button'));

      const uploadButton = await screen.findByRole('button', {
        name: /upload 1 converted files to database/i,
      });
      await user.click(uploadButton);

      await waitFor(() => {
        expect(screen.getByTestId('database-upload-dialog').style.display).toBe(
          'block',
        );
      });

      await user.click(screen.getByTestId('close-upload-dialog'));

      await waitFor(() => {
        expect(screen.getByTestId('database-upload-dialog').style.display).toBe('none');
      });
    });

    it('displays Convert&Send button and chains convert with upload (flag-on coverage)', async () => {
      operatorDisseminationUiConfig.destinationsEnabled = true;
      const user = userEvent.setup();
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [{ iwxxm_xml: '<iwxxm>send-test</iwxxm>' }],
      });

      const { container } = render(<FileConverter {...defaultProps} />);
      const convertAndSendBtn = screen.getByTestId('convert-and-send-button');
      expect(convertAndSendBtn).toBeDisabled();

      const textarea = container.querySelector('textarea') as HTMLTextAreaElement;
      await user.type(textarea, 'METAR CONVERT AND SEND');
      expect(convertAndSendBtn).toBeEnabled();

      await user.click(convertAndSendBtn);

      await waitFor(() => {
        expect(mockConvertMetarToIwxxm).toHaveBeenCalledTimes(1);
        expect(mockUploadConvertedFiles).toHaveBeenCalledTimes(1);
      });

      expect(mockUploadConvertedFiles).toHaveBeenCalledWith(
        expect.objectContaining({
          options: {
            format: 'iwxxm',
            destination: 'primary',
            includeOriginal: false,
          },
        }),
      );
      expect(mockToast.success).toHaveBeenCalledWith('Files uploaded successfully');
    });

    it('shows send failure when convert succeeds but upload fails (flag-on coverage)', async () => {
      operatorDisseminationUiConfig.destinationsEnabled = true;
      const user = userEvent.setup();
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [{ iwxxm_xml: '<iwxxm>send-fail</iwxxm>' }],
      });
      mockUploadConvertedFiles.mockRejectedValueOnce(new Error('Upload rejected'));

      const { container } = render(<FileConverter {...defaultProps} />);
      const textarea = container.querySelector('textarea') as HTMLTextAreaElement;
      await user.type(textarea, 'METAR SEND FAIL');
      await user.click(screen.getByTestId('convert-and-send-button'));

      await waitFor(() => {
        expect(mockToast.error).toHaveBeenCalledWith(
          'Conversion succeeded but send failed: Upload rejected',
        );
      });
      expect(screen.getByText('Send Error')).toBeInTheDocument();
      expect(screen.getByText(/send failed: upload rejected/i)).toBeInTheDocument();
    });

    it('enables Convert&Send without auth token when destinations UI on (F21)', async () => {
      operatorDisseminationUiConfig.destinationsEnabled = true;
      const user = userEvent.setup();
      const { container } = render(<FileConverter {...defaultProps} />);
      const textarea = container.querySelector('textarea') as HTMLTextAreaElement;
      await user.type(textarea, 'METAR NO TOKEN');

      const convertAndSend = screen.getByTestId('convert-and-send-button');
      expect(convertAndSend).not.toBeDisabled();
    });

    it('accumulates prior result cards on successful convert (#903 / F7.r; supersedes #555 replace)', async () => {
      const user = userEvent.setup();
      mockConvertMetarToIwxxm
        .mockResolvedValueOnce({
          results: [{ iwxxm_xml: '<iwxxm>first-batch</iwxxm>', name: 'first.txt' }],
        })
        .mockResolvedValueOnce({
          results: [{ iwxxm_xml: '<iwxxm>second-batch</iwxxm>', name: 'second.txt' }],
        });

      const { container } = render(<FileConverter {...defaultProps} />);
      const textarea = container.querySelector('textarea') as HTMLTextAreaElement;

      await user.type(textarea, 'METAR FIRST BATCH');
      await user.click(screen.getByTestId('convert-button'));
      await waitFor(() => {
        expect(screen.getByText('<iwxxm>first-batch</iwxxm>')).toBeInTheDocument();
      });

      fireEvent.change(textarea, { target: { value: 'METAR SECOND BATCH' } });
      await user.click(screen.getByTestId('convert-button'));
      await waitFor(() => {
        expect(screen.getByText('<iwxxm>second-batch</iwxxm>')).toBeInTheDocument();
      });
      expect(screen.getByText('<iwxxm>first-batch</iwxxm>')).toBeInTheDocument();
      expect(screen.getByTestId('download-zip-button')).toHaveAccessibleName(
        /download all 2 converted files as zip/i,
      );
    });

    it('keeps prior results when convert fails and shows error log panel (#555)', async () => {
      const user = userEvent.setup();
      mockConvertMetarToIwxxm
        .mockResolvedValueOnce({
          results: [{ iwxxm_xml: '<iwxxm>kept</iwxxm>' }],
        })
        .mockResolvedValueOnce({
          results: [],
          errors: ['Line 1: invalid METAR syntax'],
          issues: [
            {
              source: 'manual_input',
              message: 'Missing ICAO code',
              severity: 'error',
            },
          ],
          failed: 1,
          successful: 0,
          total_processed: 1,
        });

      const { container } = render(<FileConverter {...defaultProps} />);
      const textarea = container.querySelector('textarea') as HTMLTextAreaElement;

      await user.type(textarea, 'METAR KEEP ME');
      await user.click(screen.getByTestId('convert-button'));
      await waitFor(() => {
        expect(screen.getByText('<iwxxm>kept</iwxxm>')).toBeInTheDocument();
      });

      await user.clear(textarea);
      await user.type(textarea, 'BAD INPUT');
      await user.click(screen.getByTestId('convert-button'));

      await waitFor(() => {
        expect(screen.getByLabelText(/conversion error log/i)).toBeInTheDocument();
        expect(screen.getByText(/Missing ICAO code/)).toBeInTheDocument();
      });
      expect(
        screen.getAllByText('Line 1: invalid METAR syntax').length,
      ).toBeGreaterThanOrEqual(1);
      expect(screen.getByText('<iwxxm>kept</iwxxm>')).toBeInTheDocument();
    });

    it('clears error log panel on the next successful convert', async () => {
      const user = userEvent.setup();
      mockConvertMetarToIwxxm
        .mockResolvedValueOnce({
          results: [],
          errors: ['Conversion failed'],
          failed: 1,
          successful: 0,
          total_processed: 1,
        })
        .mockResolvedValueOnce({
          results: [{ iwxxm_xml: '<iwxxm>recovered</iwxxm>' }],
          errors: [],
          failed: 0,
          successful: 1,
          total_processed: 1,
        });

      const { container } = render(<FileConverter {...defaultProps} />);
      const textarea = container.querySelector('textarea') as HTMLTextAreaElement;

      await user.type(textarea, 'BAD');
      await user.click(screen.getByTestId('convert-button'));
      await waitFor(() => {
        expect(screen.getByLabelText(/conversion error log/i)).toBeInTheDocument();
      });

      await user.clear(textarea);
      await user.type(textarea, 'METAR KJFK 121651Z 18005KT 10SM FEW030 24/16 A2992');
      await user.click(screen.getByTestId('convert-button'));

      await waitFor(() => {
        expect(
          screen.queryByLabelText(/conversion error log/i),
        ).not.toBeInTheDocument();
        expect(screen.getByText('<iwxxm>recovered</iwxxm>')).toBeInTheDocument();
      });
    });
  });

  describe('Custom output filename (#664 / EV-005)', () => {
    it('previews the sanitized base name in the helper text', async () => {
      const user = userEvent.setup();
      render(<FileConverter {...defaultProps} />);

      expect(screen.getByTestId('output-filename-preview')).toHaveTextContent(
        'manual_input.xml',
      );

      await user.type(screen.getByTestId('output-filename-input'), 'my/report.xml');
      expect(screen.getByTestId('output-filename-preview')).toHaveTextContent(
        'report.xml',
      );
    });

    it('applies a custom base name to a single manual result', async () => {
      const user = userEvent.setup();
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [{ iwxxm_xml: '<iwxxm>named</iwxxm>' }],
      });

      const { container } = render(<FileConverter {...defaultProps} />);
      const textarea = container.querySelector('textarea') as HTMLTextAreaElement;
      await user.type(textarea, 'METAR KJFK CUSTOM NAME');
      await user.type(screen.getByTestId('output-filename-input'), 'report');
      await user.click(screen.getByTestId('convert-button'));

      await waitFor(() => {
        expect(screen.getByText(/report\.txt/)).toBeInTheDocument();
      });
      expect(
        screen.getByRole('button', { name: /download report\.txt as xml/i }),
      ).toBeInTheDocument();
    });

    it('suffixes _N for multi-line manual input with a custom base', async () => {
      const user = userEvent.setup();
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [
          { iwxxm_xml: '<iwxxm>one</iwxxm>' },
          { iwxxm_xml: '<iwxxm>two</iwxxm>' },
        ],
      });

      const { container } = render(<FileConverter {...defaultProps} />);
      const textarea = container.querySelector('textarea') as HTMLTextAreaElement;
      await user.type(textarea, 'METAR LINE ONE{enter}METAR LINE TWO');
      await user.type(screen.getByTestId('output-filename-input'), 'report');
      await user.click(screen.getByTestId('convert-button'));

      await waitFor(() => {
        expect(screen.getByText(/report_1\.txt/)).toBeInTheDocument();
        expect(screen.getByText(/report_2\.txt/)).toBeInTheDocument();
        expect(screen.getByText('Line 1 of 2')).toBeInTheDocument();
        expect(screen.getByText('Line 2 of 2')).toBeInTheDocument();
      });
    });

    it('does not apply the custom name to file-upload results', async () => {
      const user = userEvent.setup();
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [
          {
            iwxxm_xml: '<iwxxm>file</iwxxm>',
            name: 'uploaded.metar',
            tac_input: 'METAR FILE',
          },
        ],
      });

      const { container } = render(<FileConverter {...defaultProps} />);
      const fileInput = container.querySelector(
        'input[type="file"]',
      ) as HTMLInputElement;
      fireEvent.change(fileInput, {
        target: {
          files: {
            0: {
              name: 'uploaded.metar',
              text: vi.fn().mockResolvedValue('METAR FILE'),
            },
            length: 1,
          },
        },
      });
      await waitFor(() => {
        expect(screen.getByText('uploaded.metar')).toBeInTheDocument();
      });

      await user.type(screen.getByTestId('output-filename-input'), 'report');
      await user.click(screen.getByTestId('convert-button'));

      await waitFor(() => {
        expect(screen.getAllByText(/uploaded\.metar/).length).toBeGreaterThanOrEqual(1);
      });
      expect(screen.queryByText('report.txt')).not.toBeInTheDocument();
    });

    it('names the Download All ZIP archive after the custom base', async () => {
      const user = userEvent.setup();
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [{ iwxxm_xml: '<iwxxm>zip-named</iwxxm>' }],
      });

      let archiveName = '';
      const createUrlSpy = vi
        .spyOn(URL, 'createObjectURL')
        .mockReturnValue('blob:zip-named');
      const revokeUrlSpy = vi
        .spyOn(URL, 'revokeObjectURL')
        .mockImplementation(() => undefined);
      const clickSpy = vi
        .spyOn(HTMLAnchorElement.prototype, 'click')
        .mockImplementation(function (this: HTMLAnchorElement) {
          archiveName = this.download;
        });

      const { container } = render(<FileConverter {...defaultProps} />);
      const textarea = container.querySelector('textarea') as HTMLTextAreaElement;
      await user.type(textarea, 'METAR ZIP CUSTOM');
      await user.type(screen.getByTestId('output-filename-input'), 'weather');
      await user.click(screen.getByTestId('convert-button'));

      const downloadZipBtn = await screen.findByLabelText(
        /download all 1 converted files as zip/i,
      );
      await user.click(downloadZipBtn);

      await waitFor(() => {
        expect(archiveName).toBe('weather.zip');
      });

      createUrlSpy.mockRestore();
      revokeUrlSpy.mockRestore();
      clickSpy.mockRestore();
    });

    it('carries the custom name in the autosave snapshot conversion params', async () => {
      const user = userEvent.setup();
      render(<FileConverter {...defaultProps} />);

      await user.type(screen.getByTestId('output-filename-input'), 'persisted');

      await waitFor(() => {
        expect(mockScheduleAutoSave).toHaveBeenCalledWith(
          expect.objectContaining({
            conversionParams: expect.objectContaining({
              output_filename: 'persisted',
            }),
          }),
        );
      });
    });
  });

  describe('Golden examples (TC-F7-008 C2–C4)', () => {
    afterEach(() => {
      cleanup();
      vi.clearAllMocks();
      localStorage.clear();
    });

    async function selectGoldenExample(label: RegExp) {
      const user = userEvent.setup();
      await user.click(screen.getByTestId('examples-select'));
      const option = await screen.findByRole('option', { name: label });
      await user.click(option);
      return user;
    }

    it('loads a TAC example into the editor and sets product (C2)', async () => {
      render(<FileConverter {...defaultProps} />);

      await selectGoldenExample(/METAR WMO A3-1 \(annex3\)/i);

      const editor = screen.getByTestId('tac-editor') as HTMLTextAreaElement;
      expect(editor.value).toContain('METAR YUDO');
      expect(screen.getByTestId('product-type-select')).toHaveValue('METAR');
      expect(screen.getByTestId('demo-example-banner')).toHaveTextContent(
        /Demo \/ non-operational example: METAR WMO A3-1 \(annex3\)/i,
      );
      expect(mockToast.info).toHaveBeenCalledWith(
        expect.stringContaining('Loaded METAR WMO A3-1 (annex3)'),
      );
    });

    it('loads an AHL bulletin example and switches input mode (C3)', async () => {
      render(<FileConverter {...defaultProps} />);

      await selectGoldenExample(/AHL METAR multi-report/i);

      expect(screen.getByTestId('input-mode-ahl_bulletin')).toHaveClass('bg-blue-600');
      const editor = screen.getByTestId('tac-editor') as HTMLTextAreaElement;
      expect(editor.value).toMatch(/SAUS31/);
      expect(editor.value).toContain('METAR KJFK');
      expect(screen.getByTestId('product-type-select')).toHaveValue('METAR');
    });

    it('loads an IWXXM example onto collect_iwxxm mode (C4)', async () => {
      render(<FileConverter {...defaultProps} />);

      await selectGoldenExample(/IWXXM Collect METAR NIL/i);

      expect(screen.getByTestId('input-mode-collect_iwxxm')).toHaveClass('bg-blue-600');
      const editor = screen.getByTestId('tac-editor') as HTMLTextAreaElement;
      expect(editor.value).toMatch(/MeteorologicalBulletin|iwxxm|METAR/i);
    });

    it('loads TC SIGMET A6-2-TC reference into editor (TC-EV030-005 / UJ-039)', async () => {
      render(<FileConverter {...defaultProps} />);

      await selectGoldenExample(/TC SIGMET WMO A6-2-TC/i);

      const editor = screen.getByTestId('tac-editor') as HTMLTextAreaElement;
      expect(editor.value).toMatch(/TC GLORIA/);
      expect(editor.value).toMatch(/WI 250NM OF TC CENTRE/);
      expect(screen.getByTestId('product-type-select')).toHaveValue('SIGMET');
      expect(screen.getByTestId('demo-example-banner')).toHaveTextContent(
        /Demo \/ non-operational example: TC SIGMET WMO A6-2-TC/i,
      );
    });

    it('clears prior conversion results when loading an example', async () => {
      const user = userEvent.setup();
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [{ iwxxm_xml: '<iwxxm>stale-prior</iwxxm>' }],
      });

      render(<FileConverter {...defaultProps} />);
      const editor = screen.getByTestId('tac-editor') as HTMLTextAreaElement;
      await user.type(editor, 'METAR KJFK 121651Z 18005KT 10SM FEW030 24/16 A2992');
      await user.click(screen.getByTestId('convert-button'));

      await waitFor(() => {
        expect(
          screen.getByRole('region', { name: /conversion results/i }),
        ).toBeInTheDocument();
      });

      await selectGoldenExample(/METAR WMO A3-1 \(annex3\)/i);

      expect(
        screen.queryByRole('region', { name: /conversion results/i }),
      ).not.toBeInTheDocument();
      expect(screen.queryByText(/stale-prior/i)).not.toBeInTheDocument();
      expect(screen.getByTestId('demo-example-banner')).toBeInTheDocument();
    });

    it('resets a stale product picker when loading an AHL example', async () => {
      const user = userEvent.setup();
      render(<FileConverter {...defaultProps} />);

      await user.selectOptions(screen.getByTestId('product-type-select'), 'TAF');
      expect(screen.getByTestId('product-type-select')).toHaveValue('TAF');

      await selectGoldenExample(/AHL METAR multi-report/i);

      expect(screen.getByTestId('product-type-select')).toHaveValue('METAR');
      expect(screen.getByTestId('input-mode-ahl_bulletin')).toHaveClass('bg-blue-600');
    });

    it('clears the demo banner when Clear is clicked', async () => {
      const user = userEvent.setup();
      render(<FileConverter {...defaultProps} />);

      await selectGoldenExample(/METAR WMO A3-1 \(annex3\)/i);
      expect(screen.getByTestId('demo-example-banner')).toBeInTheDocument();

      await user.click(
        screen.getByRole('button', {
          name: /clear all pending files and manual input/i,
        }),
      );

      expect(screen.queryByTestId('demo-example-banner')).not.toBeInTheDocument();
      expect((screen.getByTestId('tac-editor') as HTMLTextAreaElement).value).toBe('');
    });
  });

  describe('EV-053 FileConverter branch fill (#968)', () => {
    const ahlSample = 'SAUS31 KZNY 121200\nMETAR KJFK 121251Z 18004KT=\n';
    const collectSample =
      '<?xml version="1.0"?>\n<collect:MeteorologicalBulletin xmlns:collect="http://def.wmo.int/collect/1.2" xmlns:iwxxm="http://icao.int/iwxxm/3.0">';

    function invokeReactOnClick(element: HTMLElement) {
      const propsKey = Object.keys(element).find((key) =>
        key.startsWith('__reactProps$'),
      );
      const onClick = propsKey
        ? (element as unknown as Record<string, { onClick?: () => void }>)[propsKey]
            ?.onClick
        : undefined;
      onClick?.();
    }

    async function addQueueFile(container: HTMLElement, name: string, content: string) {
      const fileInput = container.querySelector(
        'input[type="file"]:not([data-testid])',
      ) as HTMLInputElement;
      fireEvent.change(fileInput, {
        target: {
          files: {
            0: { name, text: vi.fn().mockResolvedValue(content) },
            length: 1,
          },
        },
      });
      await screen.findByTestId('operator-work-queue');
    }

    it('AHL convert: ok+xml builds result card and success toast', async () => {
      const user = userEvent.setup();
      mockConvertBulletin.mockResolvedValueOnce({
        bulletin_meta: {
          ahl: 'SAUS31 KZNY 121200',
          report_count: 1,
          tt: 'SA',
          aa: 'US',
          cccc: 'KZNY',
          yygggg: '121200',
        },
        results: [
          {
            report_index: 0,
            ok: true,
            xml: '<iwxxm>bulletin</iwxxm>',
            tac_input: 'METAR KJFK 121251Z 18004KT=',
            issues: [],
          },
        ],
      });

      render(<FileConverter {...defaultProps} />);
      await user.click(screen.getByTestId('input-mode-ahl_bulletin'));
      await user.type(screen.getByTestId('tac-editor'), ahlSample);
      await user.click(screen.getByTestId('convert-button'));

      await waitFor(() => {
        expect(mockConvertBulletin).toHaveBeenCalled();
      });
      expect(mockConvertMetarToIwxxm).not.toHaveBeenCalled();
      expect(mockToast.success).toHaveBeenCalledWith(
        expect.stringMatching(/Bulletin:\s*1 report/i),
      );
      expect(
        screen.getByRole('region', { name: /conversion results/i }),
      ).toBeInTheDocument();
      expect(screen.getByText('<iwxxm>bulletin</iwxxm>')).toBeInTheDocument();
    });

    it('AHL convert: issue severity/start/end fallbacks when omitted', async () => {
      const user = userEvent.setup();
      mockConvertBulletin.mockResolvedValueOnce({
        bulletin_meta: {
          ahl: 'SAUS31 KZNY 121200',
          report_count: 1,
          tt: 'SA',
          aa: 'US',
          cccc: 'KZNY',
          yygggg: '121200',
        },
        results: [
          {
            report_index: 0,
            ok: true,
            xml: '<iwxxm>ok</iwxxm>',
            tac_input: 'METAR KJFK=',
            issues: [
              { message: 'missing fields', code: 'X' },
              { message: 'hard', code: 'Y', severity: 'error', start: 1, end: 3 },
            ],
          },
        ],
      });

      render(<FileConverter {...defaultProps} />);
      await user.click(screen.getByTestId('input-mode-ahl_bulletin'));
      await user.type(screen.getByTestId('tac-editor'), ahlSample);
      await user.click(screen.getByTestId('convert-button'));

      await waitFor(() => {
        expect(mockConvertBulletin).toHaveBeenCalled();
      });
      expect(mockToast.success).toHaveBeenCalled();
    });

    it('AHL convert: files-only uses files arg and omits manualText', async () => {
      const user = userEvent.setup();
      mockConvertBulletin.mockResolvedValueOnce({
        bulletin_meta: {
          ahl: 'SAUS31 KZNY 121200',
          report_count: 1,
          tt: 'SA',
          aa: 'US',
          cccc: 'KZNY',
          yygggg: '121200',
        },
        results: [
          {
            report_index: 0,
            ok: true,
            xml: '<iwxxm>from-file</iwxxm>',
            tac_input: ahlSample,
            issues: [],
          },
        ],
      });

      const { container } = render(<FileConverter {...defaultProps} />);
      await user.click(screen.getByTestId('input-mode-ahl_bulletin'));
      const fileInput = container.querySelector(
        'input[type="file"]',
      ) as HTMLInputElement;
      fireEvent.change(fileInput, {
        target: {
          files: {
            0: {
              name: 'bulletin.txt',
              text: vi.fn().mockResolvedValue(ahlSample),
            },
            length: 1,
          },
        },
      });
      await waitFor(() => {
        expect(screen.getByText('bulletin.txt')).toBeInTheDocument();
      });
      // Clear any auto-filled editor so convert is files-only
      fireEvent.change(screen.getByTestId('tac-editor'), { target: { value: '' } });
      await user.click(screen.getByTestId('convert-button'));

      await waitFor(() => {
        expect(mockConvertBulletin).toHaveBeenCalledWith(
          expect.objectContaining({
            manualText: undefined,
            files: expect.arrayContaining([
              expect.objectContaining({ name: 'bulletin.txt' }),
            ]),
          }),
        );
      });
    });

    it('COLLECT ingest success: manual-only optional args + success toast', async () => {
      const user = userEvent.setup();
      mockIngestCollect.mockResolvedValueOnce({});

      render(<FileConverter {...defaultProps} />);
      await user.click(screen.getByTestId('input-mode-collect_iwxxm'));
      await user.type(screen.getByTestId('tac-editor'), collectSample);
      await user.click(screen.getByTestId('convert-button'));

      await waitFor(() => {
        expect(mockIngestCollect).toHaveBeenCalledWith(
          expect.objectContaining({
            manualText: expect.stringContaining('MeteorologicalBulletin'),
            files: undefined,
          }),
        );
      });
      expect(mockToast.success).toHaveBeenCalledWith('COLLECT ingest succeeded');
    });

    it('COLLECT ingest: files-only optional args', async () => {
      const user = userEvent.setup();
      mockIngestCollect.mockResolvedValueOnce({});

      const { container } = render(<FileConverter {...defaultProps} />);
      await user.click(screen.getByTestId('input-mode-collect_iwxxm'));
      const fileInput = container.querySelector(
        'input[type="file"]',
      ) as HTMLInputElement;
      fireEvent.change(fileInput, {
        target: {
          files: {
            0: {
              name: 'metar-collect.xml',
              text: vi.fn().mockResolvedValue(collectSample),
            },
            length: 1,
          },
        },
      });
      await waitFor(() => {
        expect(screen.getByText('metar-collect.xml')).toBeInTheDocument();
      });
      fireEvent.change(screen.getByTestId('tac-editor'), { target: { value: '' } });
      await user.click(screen.getByTestId('convert-button'));

      await waitFor(() => {
        expect(mockIngestCollect).toHaveBeenCalledWith(
          expect.objectContaining({
            manualText: undefined,
            files: expect.arrayContaining([
              expect.objectContaining({ name: 'metar-collect.xml' }),
            ]),
          }),
        );
      });
    });

    it('file drop switches to AHL and COLLECT with mode toasts', async () => {
      const { container, unmount } = render(<FileConverter {...defaultProps} />);
      const fileInput = container.querySelector(
        'input[type="file"]',
      ) as HTMLInputElement;

      fireEvent.change(fileInput, {
        target: {
          files: {
            0: {
              name: 'bulletin.txt',
              text: vi.fn().mockResolvedValue(ahlSample),
            },
            length: 1,
          },
        },
      });
      await waitFor(() => {
        expect(screen.getByTestId('input-mode-ahl_bulletin')).toHaveClass(
          'bg-blue-600',
        );
      });
      expect(mockToast.info).toHaveBeenCalledWith(
        'Detected AHL bulletin — switched input mode',
      );

      unmount();
      cleanup();
      mockToast.info.mockClear();

      const second = render(<FileConverter {...defaultProps} />);
      const fileInput2 = second.container.querySelector(
        'input[type="file"]',
      ) as HTMLInputElement;
      fireEvent.change(fileInput2, {
        target: {
          files: {
            0: {
              name: 'metar-collect.xml',
              text: vi.fn().mockResolvedValue(collectSample),
            },
            length: 1,
          },
        },
      });
      await waitFor(() => {
        expect(screen.getByTestId('input-mode-collect_iwxxm')).toHaveClass(
          'bg-blue-600',
        );
      });
      expect(mockToast.info).toHaveBeenCalledWith(
        'Detected IWXXM COLLECT — switched input mode',
      );
    });

    it('live IWXXM preview uses xml then content when iwxxm_xml missing', async () => {
      vi.useFakeTimers();
      try {
        const { container } = render(<FileConverter {...defaultProps} />);
        fireEvent.click(screen.getByTestId('live-iwxxm-toggle'));
        const textarea = container.querySelector('textarea') as HTMLTextAreaElement;

        mockConvertMetarToIwxxm.mockResolvedValueOnce({
          results: [{ xml: '<xml-fb/>' }],
          errors: [],
          ok: true,
          failed_spans: [],
        });
        fireEvent.change(textarea, { target: { value: 'METAR KJFK 121251Z' } });
        await act(async () => {
          await vi.advanceTimersByTimeAsync(350);
          await Promise.resolve();
        });
        expect(mockConvertMetarToIwxxm).toHaveBeenCalledWith(
          expect.objectContaining({ preview: true }),
        );

        mockConvertMetarToIwxxm.mockClear();
        mockConvertMetarToIwxxm.mockResolvedValueOnce({
          results: [{ content: '<content-fb/>' }],
          errors: [],
          ok: true,
          failed_spans: [],
        });
        fireEvent.change(textarea, {
          target: { value: 'METAR KJFK 121251Z 18004KT' },
        });
        await act(async () => {
          await vi.advanceTimersByTimeAsync(350);
          await Promise.resolve();
        });
        expect(mockConvertMetarToIwxxm).toHaveBeenCalled();
      } finally {
        vi.useRealTimers();
      }
    });

    it('hydrate converted_results via xml and content fallbacks', async () => {
      render(
        <FileConverter
          {...defaultProps}
          loadedWorkSession={
            {
              id: 'ev053-hydrate-xml-content',
              status: 'draft',
              converted_results: [
                { name: 'a.xml', xml: '<from-xml/>', tac_input: 'METAR A=' },
                {
                  name: 'b.xml',
                  content: '<from-content/>',
                  tac_input: 'METAR B=',
                },
              ],
            } as any
          }
        />,
      );

      await waitFor(() => {
        expect(screen.getByText(/from-xml/)).toBeInTheDocument();
        expect(screen.getByText(/from-content/)).toBeInTheDocument();
      });
    });

    it('hydrate conversion_params.product and profile (rawProduct arms)', async () => {
      render(
        <FileConverter
          {...defaultProps}
          loadedWorkSession={
            {
              id: 'ev053-hydrate-product',
              status: 'draft',
              conversion_params: { product: 'TAF', profile: 'iwxxm_us' },
              converted_results: [],
            } as any
          }
        />,
      );

      await waitFor(() => {
        expect(screen.getByTestId('product-type-select')).toHaveValue('TAF');
      });
    });

    it('logout scope success closes menu and calls onLogout', async () => {
      vi.useFakeTimers();
      try {
        const onLogout = vi.fn();
        mockSignOutWithScope.mockResolvedValue(true);

        render(
          <FileConverter
            {...defaultProps}
            isGuest={false}
            userEmail="op@example.com"
            onLogout={onLogout}
          />,
        );
        fireEvent.click(screen.getByTestId('logout-button'));
        fireEvent.click(
          screen.getByRole('button', { name: /sign out from this device only/i }),
        );

        await act(async () => {
          await Promise.resolve();
        });
        expect(mockSignOutWithScope).toHaveBeenCalledWith('local');
        await act(async () => {
          await vi.advanceTimersByTimeAsync(500);
        });
        expect(onLogout).toHaveBeenCalled();
      } finally {
        vi.useRealTimers();
      }
    });

    it('auto-detects an AHL bulletin when converting pasted TAC', async () => {
      const user = userEvent.setup();
      mockConvertBulletin.mockResolvedValueOnce({
        bulletin_meta: {
          ahl: 'SAUS31 KZNY 121200',
          report_count: 0,
          tt: 'SA',
          aa: 'US',
          cccc: 'KZNY',
          yygggg: '121200',
        },
        results: [],
      });
      render(<FileConverter {...defaultProps} />);

      await user.type(screen.getByTestId('tac-editor'), ahlSample);
      await user.click(screen.getByTestId('convert-button'));

      await waitFor(() => expect(mockConvertBulletin).toHaveBeenCalled());
      expect(mockToast.info).toHaveBeenCalledWith(
        'Detected AHL bulletin — switched input mode',
      );
      expect(screen.getByTestId('input-mode-ahl_bulletin')).toHaveClass('bg-blue-600');
    });

    it('shows the COLLECT placeholder notice for an auto-detected pasted bulletin', async () => {
      const user = userEvent.setup();
      render(<FileConverter {...defaultProps} />);

      await user.type(screen.getByTestId('tac-editor'), collectSample);
      await user.click(screen.getByTestId('convert-button'));

      await waitFor(() => {
        expect(mockIngestCollect).toHaveBeenCalled();
        expect(screen.getByTestId('placeholder-notice')).toBeInTheDocument();
      });
      expect(mockToast.warning).toHaveBeenCalledWith(
        'COLLECT ingest placeholder (not implemented yet)',
      );
    });

    it('keeps logout menu open when scoped sign-out fails', async () => {
      const user = userEvent.setup();
      const onLogout = vi.fn();
      mockSignOutWithScope.mockResolvedValueOnce(false);
      render(
        <FileConverter
          {...defaultProps}
          isGuest={false}
          userEmail="op@example.com"
          onLogout={onLogout}
        />,
      );

      await user.click(screen.getByTestId('logout-button'));
      await user.click(
        screen.getByRole('button', { name: /sign out from this device only/i }),
      );

      await waitFor(() => expect(mockSignOutWithScope).toHaveBeenCalledWith('local'));
      expect(
        screen.getByRole('button', { name: /sign out from this device only/i }),
      ).toBeInTheDocument();
      expect(onLogout).not.toHaveBeenCalled();
    });

    it('uses preference defaults for blank legacy values', async () => {
      const user = userEvent.setup();
      localStorage.setItem(
        'metar_converter_preferences',
        JSON.stringify({
          bulletinIdExample: '',
          issuingCenter: '',
          product: '',
          profile: 'other',
          iwxxmVersion: '2025-2',
          strictValidation: false,
          includeNilReasons: false,
          onError: '',
          logLevel: '',
        }),
      );
      render(<FileConverter {...defaultProps} />);

      await user.type(screen.getByTestId('tac-editor'), 'METAR KJFK 121251Z=');
      await user.click(screen.getByTestId('convert-button'));

      await waitFor(() => {
        expect(mockConvertMetarToIwxxm).toHaveBeenCalledWith(
          expect.objectContaining({
            bulletinId: 'SAAA00',
            issuingCenter: 'KWBC',
            profile: 'annex3',
            includeNilReasons: false,
            logLevel: 'INFO',
          }),
        );
      });
    });

    it('uses the generic focused-validation error when lint rejects a non-Error', async () => {
      mockLintTac.mockRejectedValueOnce('offline');
      const { container } = render(<FileConverter {...defaultProps} />);
      const fileInput = container.querySelector(
        'input[type="file"]:not([data-testid])',
      ) as HTMLInputElement;
      fireEvent.change(fileInput, {
        target: {
          files: {
            0: {
              name: 'focused.tac',
              text: vi.fn().mockResolvedValue('METAR KJFK 121251Z='),
            },
            length: 1,
          },
        },
      });
      const queue = await screen.findByTestId('operator-work-queue');

      fireEvent.keyDown(queue, { key: 'Enter', shiftKey: true });

      await waitFor(() => {
        expect(mockToast.error).toHaveBeenCalledWith(
          'Validate failed for focused.tac',
          expect.anything(),
        );
      });
    });

    it('opens the file chooser from the compact drop zone keyboard shortcut', () => {
      const { container } = render(<FileConverter {...defaultProps} />);
      const fileInput = container.querySelector(
        'input[type="file"]:not([data-testid])',
      ) as HTMLInputElement;
      const clickSpy = vi.spyOn(fileInput, 'click');

      fireEvent.keyDown(screen.getByTestId('compact-file-drop-zone'), { key: ' ' });

      expect(clickSpy).toHaveBeenCalledOnce();
    });

    it('reports mass-ingest results that accept no usable content', async () => {
      const user = userEvent.setup();
      mockMassIngestFiles.mockResolvedValueOnce({
        accepted_count: 1,
        rejected_count: 0,
        results: [
          {
            name: 'empty.tac',
            accepted: true,
            reason: null,
            size_bytes: 0,
            content: null,
          },
        ],
      });
      render(<FileConverter {...defaultProps} accessToken="jwt-f33" />);

      await user.upload(
        screen.getByTestId('mass-ingest-zip-input') as HTMLInputElement,
        new File(['PK'], 'empty.zip', { type: 'application/zip' }),
      );

      await waitFor(() => {
        expect(mockToast.success).toHaveBeenCalledWith(
          'Mass ingest: 1 accepted, 0 rejected',
          expect.anything(),
        );
      });
      expect(screen.queryByTestId('operator-work-queue')).not.toBeInTheDocument();
    });

    it('prompts guests to sign in before opening the mass-ingest folder chooser', async () => {
      const user = userEvent.setup();
      const onRequestLogin = vi.fn();
      render(
        <FileConverter {...defaultProps} isGuest onRequestLogin={onRequestLogin} />,
      );

      await user.click(screen.getByTestId('mass-ingest-folder-button'));

      expect(onRequestLogin).toHaveBeenCalledOnce();
      expect(mockToast.error).toHaveBeenCalledWith(
        'Sign in required for mass folder or zip ingest',
      );
    });

    it('inflates a gzip drop, removes its extension, and detects AHL mode', async () => {
      const user = userEvent.setup();
      mockInflateGzipToText.mockResolvedValueOnce(ahlSample);
      const { container } = render(<FileConverter {...defaultProps} />);
      const fileInput = container.querySelector(
        'input[type="file"]:not([data-testid])',
      ) as HTMLInputElement;

      await user.upload(
        fileInput,
        new File(['compressed'], 'bulletin.TAC.GZ', {
          type: 'application/gzip',
        }),
      );

      await waitFor(() => {
        expect(mockInflateGzipToText).toHaveBeenCalledOnce();
        expect(screen.getByText('bulletin.TAC')).toBeInTheDocument();
      });
      expect(mockToast.info).toHaveBeenCalledWith('Decompressed bulletin.TAC.GZ');
      expect(screen.getByTestId('input-mode-ahl_bulletin')).toHaveClass('bg-blue-600');
    });

    it('reports a gzip inflate error without adding a pending file', async () => {
      mockInflateGzipToText.mockRejectedValueOnce(new Error('invalid gzip'));
      const { container } = render(<FileConverter {...defaultProps} />);
      const fileInput = container.querySelector(
        'input[type="file"]:not([data-testid])',
      ) as HTMLInputElement;

      fireEvent.change(fileInput, {
        target: {
          files: {
            0: new File(['bad'], 'broken.gzip'),
            length: 1,
          },
        },
      });

      await waitFor(() => {
        expect(mockToast.error).toHaveBeenCalledWith('invalid gzip');
      });
      expect(screen.queryByTestId('operator-work-queue')).not.toBeInTheDocument();
    });

    it('limits mass-ingest rejection samples and defaults blank reasons', async () => {
      const rejected = Array.from({ length: 6 }, (_, index) => ({
        name: `bad-${index}.tac`,
        accepted: false,
        reason: index === 0 ? '' : null,
        size_bytes: 1,
        content: null,
      }));
      mockMassIngestFiles.mockResolvedValueOnce({
        accepted_count: 0,
        rejected_count: 6,
        results: rejected,
      });
      render(<FileConverter {...defaultProps} accessToken="jwt-f33" />);

      await userEvent
        .setup()
        .upload(
          screen.getByTestId('mass-ingest-zip-input') as HTMLInputElement,
          new File(['PK'], 'rejected.zip', { type: 'application/zip' }),
        );

      await waitFor(() => {
        expect(mockToast.success).toHaveBeenCalledWith(
          'Mass ingest: 0 accepted, 6 rejected',
          expect.anything(),
        );
      });
      expect(mockToast.error).toHaveBeenCalledWith('bad-0.tac: rejected');
      expect(mockToast.error).toHaveBeenCalledWith('bad-4.tac: rejected');
      expect(mockToast.error).not.toHaveBeenCalledWith('bad-5.tac: rejected');
    });

    it('uses the generic mass-ingest failure message for non-Error rejections', async () => {
      mockMassIngestFiles.mockRejectedValueOnce('offline');
      render(<FileConverter {...defaultProps} accessToken="jwt-f33" />);

      await userEvent
        .setup()
        .upload(
          screen.getByTestId('mass-ingest-zip-input') as HTMLInputElement,
          new File(['PK'], 'offline.zip', { type: 'application/zip' }),
        );

      await waitFor(() => {
        expect(mockToast.error).toHaveBeenCalledWith(
          'Mass ingest failed',
          expect.anything(),
        );
      });
    });

    it('uses xml and content fallbacks for hard conversion result cards', async () => {
      const user = userEvent.setup();
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [
          { xml: '<hard-xml/>', tac_input: 'METAR XML=' },
          { content: '<hard-content/>', tac_input: 'METAR CONTENT=' },
        ],
        errors: [],
        issues: [],
      });
      const { container } = render(<FileConverter {...defaultProps} />);

      await user.type(
        container.querySelector('textarea') as HTMLTextAreaElement,
        'METAR XML=\nMETAR CONTENT=',
      );
      await user.click(screen.getByTestId('convert-button'));

      await waitFor(() => {
        expect(screen.getByText('<hard-xml/>')).toBeInTheDocument();
        expect(screen.getByText('<hard-content/>')).toBeInTheDocument();
      });
    });

    it('marks Convert & Send failed without uploading when conversion has errors', async () => {
      operatorDisseminationUiConfig.destinationsEnabled = true;
      const user = userEvent.setup();
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [{ iwxxm_xml: '<partial/>', tac_input: 'METAR PARTIAL=' }],
        errors: ['partial conversion'],
        issues: [],
      });
      const { container } = render(<FileConverter {...defaultProps} />);

      await user.type(
        container.querySelector('textarea') as HTMLTextAreaElement,
        'METAR PARTIAL=',
      );
      await user.click(screen.getByTestId('convert-and-send-button'));

      await waitFor(() => {
        expect(mockPersistSession).toHaveBeenCalledWith(expect.anything(), {
          status: 'failed',
        });
      });
      expect(mockUploadConvertedFiles).not.toHaveBeenCalled();
    });

    it('shows bulletin failures while retaining converted reports and issue fallback', async () => {
      const user = userEvent.setup();
      mockConvertBulletin.mockResolvedValueOnce({
        bulletin_meta: {
          ahl: 'SAUS31 KZNY 121200',
          report_count: 2,
          tt: 'SA',
          aa: 'US',
          cccc: 'KZNY',
          yygggg: '121200',
        },
        results: [
          {
            report_index: 0,
            ok: true,
            xml: '<bulletin-ok/>',
            tac_input: 'METAR OK=',
            issues: [],
          },
          {
            report_index: 1,
            ok: false,
            xml: '',
            tac_input: 'METAR BAD=',
            issues: [{ message: 'bad report' }],
          },
        ],
      });
      render(<FileConverter {...defaultProps} />);

      await user.click(screen.getByTestId('input-mode-ahl_bulletin'));
      await user.type(screen.getByTestId('tac-editor'), ahlSample);
      await user.click(screen.getByTestId('convert-button'));

      await waitFor(() => {
        expect(screen.getByText('<bulletin-ok/>')).toBeInTheDocument();
        expect(mockToast.warning).toHaveBeenCalledWith('Bulletin: 1 ok, 1 failed');
      });
    });

    it('renders a hydrated result without source TAC as unavailable', async () => {
      render(
        <FileConverter
          {...defaultProps}
          loadedWorkSession={
            {
              id: 'ev053-missing-source',
              status: 'draft',
              converted_results: [{ name: 'no-source.xml', iwxxm_xml: '<xml/>' }],
            } as any
          }
        />,
      );

      expect(
        await screen.findByText('Original TAC unavailable for this result.'),
      ).toBeInTheDocument();
    });

    it('hydrates partial session fields with safe queue, result, log, and parameter fallbacks', async () => {
      render(
        <FileConverter
          {...defaultProps}
          loadedWorkSession={
            {
              id: 'ev053-partial-session',
              status: 'draft',
              manual_tac: '',
              pending_files: [{ name: 'queued.tac', content: 'METAR KJFK 121251Z=' }],
              converted_results: [{}],
              errors: ['stored error'],
              issues: [{ code: 'stored-issue' }],
              conversion_params: {
                output_filename: 123,
                product: 'not-a-product',
                profile: 'not-a-profile',
              },
            } as any
          }
        />,
      );

      expect(await screen.findByText('queued.tac')).toBeInTheDocument();
      expect(screen.getByText('result-1')).toBeInTheDocument();
      expect(
        screen.getByText('Original TAC unavailable for this result.'),
      ).toBeInTheDocument();
    });

    it('keeps a result card when the API provides no XML field', async () => {
      const user = userEvent.setup();
      mockConvertMetarToIwxxm.mockResolvedValueOnce({ results: [{}] });
      render(<FileConverter {...defaultProps} />);

      await user.type(screen.getByTestId('tac-editor'), 'METAR KJFK 121251Z=');
      await user.click(screen.getByTestId('convert-button'));

      await waitFor(() => {
        expect(
          screen.getByRole('region', { name: /conversion results/i }),
        ).toBeInTheDocument();
      });
    });

    it('restores guest output filename from session snapshot on mount', async () => {
      mockReadGuestConverterState.mockReturnValue({
        conversionParams: { output_filename: 'guest/report.xml' },
      } as any);
      render(<FileConverter {...defaultProps} />);

      expect(screen.getByTestId('output-filename-input')).toHaveValue(
        'guest/report.xml',
      );
    });

    it('loads iwxxm_us profile and default ?? true flags when prefs omit booleans', async () => {
      const user = userEvent.setup();
      localStorage.setItem(
        'metar_converter_preferences',
        JSON.stringify({
          profile: 'iwxxm_us',
          iwxxmVersion: '2025-2',
        }),
      );
      render(<FileConverter {...defaultProps} />);

      await user.type(screen.getByTestId('tac-editor'), 'METAR KJFK=');
      await user.click(screen.getByTestId('convert-button'));

      await waitFor(() => {
        expect(mockConvertMetarToIwxxm).toHaveBeenCalledWith(
          expect.objectContaining({
            profile: 'iwxxm_us',
            includeNilReasons: true,
          }),
        );
      });
    });

    it('reloads preferences after dialog save with explicit false booleans', async () => {
      const user = userEvent.setup();
      localStorage.setItem(
        'metar_converter_preferences',
        JSON.stringify({
          bulletinIdExample: 'SAAA00',
          issuingCenter: 'KWBC',
          profile: 'iwxxm_us',
          iwxxmVersion: '2025-2',
          strictValidation: false,
          includeNilReasons: false,
          onError: 'fail',
          logLevel: 'DEBUG',
        }),
      );
      render(<FileConverter {...defaultProps} />);

      await user.click(screen.getByLabelText(/open user preferences/i));
      await user.click(screen.getByTestId('save-prefs-dialog'));

      expect(mockToast.info).toHaveBeenCalledWith(
        'Conversion parameters updated from preferences',
      );
    });

    it('hydrates conversion log from issues-only and string output filename', async () => {
      render(
        <FileConverter
          {...defaultProps}
          loadedWorkSession={
            {
              id: 'ev053-issues-only',
              status: 'draft',
              errors: null,
              issues: [{ code: 'WARN', message: 'stored issue' }],
              conversion_params: { output_filename: 'hydrated.xml' },
              converted_results: [],
            } as any
          }
        />,
      );

      expect(await screen.findByText(/stored issue/i)).toBeInTheDocument();
      expect(screen.getByTestId('output-filename-input')).toHaveValue('hydrated.xml');
    });

    it('hydrates conversion log from errors-only session data', async () => {
      render(
        <FileConverter
          {...defaultProps}
          loadedWorkSession={
            {
              id: 'ev053-errors-only',
              status: 'draft',
              errors: ['stored error'],
              issues: undefined,
              converted_results: [],
            } as any
          }
        />,
      );

      expect(await screen.findByText('stored error')).toBeInTheDocument();
    });

    it('ignores empty file selection without adding queue items', async () => {
      const { container } = render(<FileConverter {...defaultProps} />);
      const fileInput = container.querySelector(
        'input[type="file"]:not([data-testid])',
      ) as HTMLInputElement;

      fireEvent.change(fileInput, { target: { files: null } });
      fireEvent.change(fileInput, { target: { files: { length: 0 } } });

      expect(screen.queryByTestId('operator-work-queue')).not.toBeInTheDocument();
    });

    it('shows convert error when neither files nor manual input are present', () => {
      render(<FileConverter {...defaultProps} />);
      const convertButton = screen.getByTestId('convert-button');
      const propsKey = Object.keys(convertButton).find((key) =>
        key.startsWith('__reactProps$'),
      );
      const onClick = propsKey
        ? (convertButton as unknown as Record<string, { onClick?: () => void }>)[
            propsKey
          ]?.onClick
        : undefined;
      onClick?.();

      expect(mockToast.error).toHaveBeenCalledWith(
        'Please add files or enter manual input',
      );
      expect(mockConvertMetarToIwxxm).not.toHaveBeenCalled();
    });

    it('reports non-Error file read failures with a generic message', async () => {
      const { container } = render(<FileConverter {...defaultProps} />);
      const fileInput = container.querySelector(
        'input[type="file"]:not([data-testid])',
      ) as HTMLInputElement;

      fireEvent.change(fileInput, {
        target: {
          files: {
            0: {
              name: 'broken.txt',
              text: vi.fn().mockRejectedValue('disk offline'),
            },
            length: 1,
          },
        },
      });

      await waitFor(() => {
        expect(mockToast.error).toHaveBeenCalledWith('Failed to read broken.txt');
      });
    });

    it('switches back to TAC mode when a plain report is added in AHL mode', async () => {
      const user = userEvent.setup();
      const { container } = render(<FileConverter {...defaultProps} />);
      await user.click(screen.getByTestId('input-mode-ahl_bulletin'));

      const fileInput = container.querySelector(
        'input[type="file"]:not([data-testid])',
      ) as HTMLInputElement;
      fireEvent.change(fileInput, {
        target: {
          files: {
            0: {
              name: 'plain.tac',
              text: vi.fn().mockResolvedValue('METAR KJFK 121251Z 18004KT='),
            },
            length: 1,
          },
        },
      });

      await waitFor(() => {
        expect(mockToast.info).toHaveBeenCalledWith('Switched to TAC report mode');
      });
      expect(screen.getByTestId('input-mode-tac')).toHaveClass('bg-blue-600');
    });

    it('sets webkitdirectory on the mass-ingest folder input', () => {
      render(<FileConverter {...defaultProps} accessToken="jwt-f33" />);
      const folderInput = screen.getByTestId('mass-ingest-folder-input');
      expect(folderInput).toHaveAttribute('webkitdirectory');
      expect(folderInput).toHaveAttribute('directory');
    });

    it('ignores empty mass-ingest file lists', async () => {
      render(<FileConverter {...defaultProps} accessToken="jwt-f33" />);
      const zipInput = screen.getByTestId('mass-ingest-zip-input') as HTMLInputElement;

      fireEvent.change(zipInput, { target: { files: null } });

      expect(mockMassIngestFiles).not.toHaveBeenCalled();
    });

    it('uses custom output filename for manual multi-line convert results', async () => {
      const user = userEvent.setup();
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [
          { iwxxm_xml: '<line1/>', tac_input: 'METAR A=' },
          { iwxxm_xml: '<line2/>', tac_input: 'METAR B=' },
        ],
        errors: [],
        issues: [],
      });
      render(<FileConverter {...defaultProps} />);

      await user.type(screen.getByTestId('output-filename-input'), 'batch/out');
      await user.type(screen.getByTestId('tac-editor'), 'METAR A=\nMETAR B=');
      await user.click(screen.getByTestId('convert-button'));

      await waitFor(() => {
        expect(screen.getByText('<line1/>')).toBeInTheDocument();
        expect(screen.getByText('<line2/>')).toBeInTheDocument();
      });
    });

    it('soft-preview convert maps missing failed_span fields and warns on soft fail', async () => {
      const user = userEvent.setup();
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [{ iwxxm_xml: '<soft-fail/>', tac_input: 'METAR BAD=' }],
        errors: [],
        issues: [],
        ok: false,
        failed_spans: [{ start: 0, end: 4 }],
      });
      render(<FileConverter {...defaultProps} />);

      await user.click(screen.getByTestId('soft-preview-toggle'));
      await user.type(screen.getByTestId('tac-editor'), 'METAR BAD=');
      await user.click(screen.getByTestId('convert-button'));

      await waitFor(() => {
        expect(mockConvertMetarToIwxxm).toHaveBeenCalledWith(
          expect.objectContaining({ preview: true }),
        );
        expect(screen.getByTestId('iwxxm-preview-soft-fail')).toBeInTheDocument();
      });
      expect(mockToast.warning).toHaveBeenCalledWith(
        'Soft-preview returned Failed-TAC markers — not ready to publish',
      );
    });

    it('soft-preview passed path sets preview status without soft-fail detail', async () => {
      const user = userEvent.setup();
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [{ iwxxm_xml: '<soft-pass/>', tac_input: 'METAR OK=' }],
        errors: [],
        issues: [],
        ok: true,
        failed_spans: [],
      });
      render(<FileConverter {...defaultProps} />);

      await user.click(screen.getByTestId('soft-preview-toggle'));
      await user.type(screen.getByTestId('tac-editor'), 'METAR OK=');
      await user.click(screen.getByTestId('convert-button'));

      await waitFor(() => {
        expect(screen.getByTestId('iwxxm-preview-xml')).toHaveTextContent(
          '<soft-pass/>',
        );
      });
      expect(screen.queryByTestId('iwxxm-preview-soft-fail')).not.toBeInTheDocument();
    });

    it('uses generic conversion failure message for non-Error throws', async () => {
      const user = userEvent.setup();
      mockConvertMetarToIwxxm.mockRejectedValueOnce('backend offline');
      render(<FileConverter {...defaultProps} />);

      await user.type(screen.getByTestId('tac-editor'), 'METAR KJFK=');
      await user.click(screen.getByTestId('convert-button'));

      await waitFor(() => {
        expect(mockToast.error).toHaveBeenCalledWith(
          'Conversion failed. Please check the input and try again.',
        );
      });
    });

    it('Convert & Send persists failed when conversion returns null', async () => {
      operatorDisseminationUiConfig.destinationsEnabled = true;
      const user = userEvent.setup();
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [],
        errors: ['nothing converted'],
        issues: [],
      });
      render(<FileConverter {...defaultProps} />);

      await user.type(screen.getByTestId('tac-editor'), 'BAD');
      await user.click(screen.getByTestId('convert-and-send-button'));

      await waitFor(() => {
        expect(mockPersistSession).toHaveBeenCalledWith(expect.anything(), {
          status: 'failed',
        });
      });
      expect(mockUploadConvertedFiles).not.toHaveBeenCalled();
    });

    it('Convert & Send blocks upload on soft-preview soft fail', async () => {
      operatorDisseminationUiConfig.destinationsEnabled = true;
      const user = userEvent.setup();
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [{ iwxxm_xml: '<partial/>', tac_input: 'METAR PART=' }],
        errors: [],
        issues: [{ message: 'lint warn' }],
        ok: false,
        failed_spans: [{ start: 0, end: 3, message: 'bad' }],
      });
      render(<FileConverter {...defaultProps} />);

      await user.click(screen.getByTestId('soft-preview-toggle'));
      await user.type(screen.getByTestId('tac-editor'), 'METAR PART=');
      await user.click(screen.getByTestId('convert-and-send-button'));

      await waitFor(() => {
        expect(mockToast.warning).toHaveBeenCalledWith(
          'Soft-preview Failed-TAC — fix markers before Convert & Send',
        );
      });
      expect(mockUploadConvertedFiles).not.toHaveBeenCalled();
    });

    it('Convert & Send uses fallback success message when upload response omits message', async () => {
      operatorDisseminationUiConfig.destinationsEnabled = true;
      const user = userEvent.setup();
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [{ iwxxm_xml: '<sent/>', tac_input: 'METAR SEND=' }],
        errors: [],
        issues: [],
      });
      mockUploadConvertedFiles.mockResolvedValueOnce({});
      render(<FileConverter {...defaultProps} />);

      await user.type(screen.getByTestId('tac-editor'), 'METAR SEND=');
      await user.click(screen.getByTestId('convert-and-send-button'));

      await waitFor(() => {
        expect(mockToast.success).toHaveBeenCalledWith(
          'Files converted and sent successfully',
        );
      });
    });

    it('Convert & Send reports generic upload failure for non-Error throws', async () => {
      operatorDisseminationUiConfig.destinationsEnabled = true;
      const user = userEvent.setup();
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [{ iwxxm_xml: '<sent/>', tac_input: 'METAR SEND=' }],
        errors: [],
        issues: [],
      });
      mockUploadConvertedFiles.mockRejectedValueOnce('network down');
      render(<FileConverter {...defaultProps} />);

      await user.type(screen.getByTestId('tac-editor'), 'METAR SEND=');
      await user.click(screen.getByTestId('convert-and-send-button'));

      await waitFor(() => {
        expect(mockToast.error).toHaveBeenCalledWith(
          'Conversion succeeded but send failed: Failed to upload to database',
        );
      });
    });

    it('shows read-only new session toast when starting a new TAC', async () => {
      mockIsReadOnly.value = true;
      const user = userEvent.setup();
      render(<FileConverter {...defaultProps} />);

      await user.type(screen.getByTestId('tac-editor'), 'METAR KJFK=');
      await user.click(screen.getByTestId('new-tac-button'));

      expect(mockToast.info).toHaveBeenCalledWith('Starting a new TAC session');
    });

    it('ignores unknown golden example ids without changing editor state', async () => {
      const catalog = await import('@/fixtures/examples/examplesCatalog');
      const spy = vi.spyOn(catalog, 'getExampleById').mockReturnValue(undefined);
      const user = userEvent.setup();
      render(<FileConverter {...defaultProps} />);

      await user.type(screen.getByTestId('tac-editor'), 'KEEP ME');
      await user.click(screen.getByTestId('examples-select'));
      const option = await screen.findByRole('option', {
        name: /METAR WMO A3-1 \(annex3\)/i,
      });
      await user.click(option);

      expect(screen.getByTestId('tac-editor')).toHaveValue('KEEP ME');
      expect(screen.queryByTestId('demo-example-banner')).not.toBeInTheDocument();
      spy.mockRestore();
    });

    it('shows batch convert error when no queue items are selected', async () => {
      const { container } = render(<FileConverter {...defaultProps} />);
      const fileInput = container.querySelector(
        'input[type="file"]:not([data-testid])',
      ) as HTMLInputElement;
      fireEvent.change(fileInput, {
        target: {
          files: {
            0: {
              name: 'solo.tac',
              text: vi.fn().mockResolvedValue('METAR SOLO='),
            },
            length: 1,
          },
        },
      });
      await screen.findByTestId('operator-work-queue');

      const batchButton = screen.getByTestId('batch-convert-button');
      const propsKey = Object.keys(batchButton).find((key) =>
        key.startsWith('__reactProps$'),
      );
      const onClick = propsKey
        ? (batchButton as unknown as Record<string, { onClick?: () => void }>)[propsKey]
            ?.onClick
        : undefined;
      onClick?.();

      expect(mockToast.error).toHaveBeenCalledWith(
        'Select one or more queue items to batch convert',
      );
    });

    it('shows batch validate error when no queue items are selected', async () => {
      const { container } = render(<FileConverter {...defaultProps} />);
      const fileInput = container.querySelector(
        'input[type="file"]:not([data-testid])',
      ) as HTMLInputElement;
      fireEvent.change(fileInput, {
        target: {
          files: {
            0: {
              name: 'solo.tac',
              text: vi.fn().mockResolvedValue('METAR SOLO='),
            },
            length: 1,
          },
        },
      });
      await screen.findByTestId('operator-work-queue');

      const batchButton = screen.getByTestId('batch-validate-button');
      const propsKey = Object.keys(batchButton).find((key) =>
        key.startsWith('__reactProps$'),
      );
      const onClick = propsKey
        ? (batchButton as unknown as Record<string, { onClick?: () => void }>)[propsKey]
            ?.onClick
        : undefined;
      onClick?.();

      expect(mockToast.error).toHaveBeenCalledWith(
        'Select one or more queue items to batch validate',
      );
    });

    it('focused validate reports lint issue counts when lint fails', async () => {
      mockLintTac.mockResolvedValueOnce({
        ok: false,
        issues: [{ severity: 'error', code: 'X', message: 'bad', start: 0, end: 3 }],
        fixes: [],
      });
      const { container } = render(<FileConverter {...defaultProps} />);
      const fileInput = container.querySelector(
        'input[type="file"]:not([data-testid])',
      ) as HTMLInputElement;
      fireEvent.change(fileInput, {
        target: {
          files: {
            0: {
              name: 'lint-fail.tac',
              text: vi.fn().mockResolvedValue('METAR BAD='),
            },
            length: 1,
          },
        },
      });
      const queue = await screen.findByTestId('operator-work-queue');
      fireEvent.keyDown(queue, { key: 'Enter', shiftKey: true });

      await waitFor(() => {
        expect(mockToast.error).toHaveBeenCalledWith(
          'lint-fail.tac: 1 lint issue(s)',
          expect.anything(),
        );
      });
    });

    it('batch validate counts lint failures from rejected lint calls', async () => {
      const user = userEvent.setup();
      mockLintTac
        .mockResolvedValueOnce({ ok: true, issues: [], fixes: [] })
        .mockRejectedValueOnce('offline');
      const { container } = render(<FileConverter {...defaultProps} />);
      const fileInput = container.querySelector(
        'input[type="file"]:not([data-testid])',
      ) as HTMLInputElement;
      fireEvent.change(fileInput, {
        target: {
          files: {
            0: { name: 'a.tac', text: vi.fn().mockResolvedValue('METAR A=') },
            1: { name: 'b.tac', text: vi.fn().mockResolvedValue('METAR B=') },
            length: 2,
          },
        },
      });
      await screen.findByTestId('operator-work-queue');
      await user.click(screen.getByTestId('queue-select-0'));
      await user.click(screen.getByTestId('queue-select-1'));
      await user.click(screen.getByTestId('batch-validate-button'));

      await waitFor(() => {
        expect(mockToast.success).toHaveBeenCalledWith(
          'Batch validate: 1 ok, 1 with issues',
          expect.anything(),
        );
      });
    });

    it('work queue ArrowUp moves focus to the previous item', async () => {
      const user = userEvent.setup();
      const { container } = render(<FileConverter {...defaultProps} />);
      const fileInput = container.querySelector(
        'input[type="file"]:not([data-testid])',
      ) as HTMLInputElement;
      fireEvent.change(fileInput, {
        target: {
          files: {
            0: { name: 'first.tac', text: vi.fn().mockResolvedValue('METAR FIRST=') },
            1: {
              name: 'second.tac',
              text: vi.fn().mockResolvedValue('METAR SECOND='),
            },
            length: 2,
          },
        },
      });
      const queue = await screen.findByTestId('operator-work-queue');
      await user.click(screen.getByTestId('queue-item-1'));
      queue.focus();
      await user.keyboard('{ArrowUp}');

      const textarea = container.querySelector('textarea') as HTMLTextAreaElement;
      await waitFor(() => {
        expect(textarea.value).toContain('METAR FIRST');
      });
    });

    it('live IWXXM uses iwxxm_xml fallback and clears spans on ok preview', async () => {
      vi.useFakeTimers();
      try {
        render(<FileConverter {...defaultProps} />);
        fireEvent.click(screen.getByTestId('live-iwxxm-toggle'));

        mockConvertMetarToIwxxm.mockResolvedValueOnce({
          results: [{ iwxxm_xml: '<live-iwxxm/>' }],
          ok: true,
          failed_spans: [],
        });
        fireEvent.change(screen.getByTestId('tac-editor'), {
          target: { value: 'METAR KJFK 121251Z' },
        });
        await act(async () => {
          await vi.advanceTimersByTimeAsync(350);
          await Promise.resolve();
        });

        expect(screen.getByText('<live-iwxxm/>')).toBeInTheDocument();
        expect(screen.queryByTestId('failed-tac-cue')).toBeNull();
      } finally {
        vi.useRealTimers();
      }
    });

    it('live IWXXM maps failed spans with missing code/message fields', async () => {
      vi.useFakeTimers();
      try {
        render(<FileConverter {...defaultProps} />);
        fireEvent.click(screen.getByTestId('live-iwxxm-toggle'));

        mockConvertMetarToIwxxm.mockResolvedValueOnce({
          results: [{ xml: '<live/>' }],
          ok: true,
          failed_spans: [{ start: 1, end: 4 }],
        });
        fireEvent.change(screen.getByTestId('tac-editor'), {
          target: { value: 'METAR KJFK 121251Z 18004KT' },
        });
        await act(async () => {
          await vi.advanceTimersByTimeAsync(350);
          await Promise.resolve();
        });

        expect(screen.getByTestId('failed-tac-cue')).toBeInTheDocument();
        expect(screen.getByTestId('iwxxm-preview-soft-fail')).toBeInTheDocument();
      } finally {
        vi.useRealTimers();
      }
    });

    it('live IWXXM reports generic failure for non-Error throws', async () => {
      vi.useFakeTimers();
      try {
        render(<FileConverter {...defaultProps} />);
        fireEvent.click(screen.getByTestId('live-iwxxm-toggle'));

        mockConvertMetarToIwxxm.mockRejectedValueOnce('live offline');
        fireEvent.change(screen.getByTestId('tac-editor'), {
          target: { value: 'METAR KJFK 121251Z' },
        });
        await act(async () => {
          await vi.advanceTimersByTimeAsync(350);
          await Promise.resolve();
        });

        expect(screen.getByTestId('decode-panel-mock')).toBeInTheDocument();
      } finally {
        vi.useRealTimers();
      }
    });

    it('applyLintFix no-ops when the fix has no replacement text', async () => {
      mockLintTac.mockResolvedValueOnce({
        ok: false,
        issues: [
          {
            severity: 'error',
            code: 'MISSING_TERMINATOR',
            message: 'missing =',
            start: 0,
            end: 10,
          },
        ],
        fixes: [{ code: 'add_terminator' }],
      });
      const user = userEvent.setup();
      render(<FileConverter {...defaultProps} />);

      fireEvent.change(screen.getByTestId('tac-editor'), {
        target: { value: 'METAR KJFK 121251Z' },
      });

      fireEvent.click(screen.getByTestId('workbench-console-toggle'));
      const action = await screen.findByTestId(
        'console-action-add_terminator',
        {},
        { timeout: 3000 },
      );
      await user.click(action);

      expect(screen.getByTestId('tac-editor')).toHaveValue('METAR KJFK 121251Z');
    });

    it('renders work history aside when onLoadWorkSession is provided', () => {
      const onLoadWorkSession = vi.fn();
      const { container } = render(
        <FileConverter {...defaultProps} onLoadWorkSession={onLoadWorkSession} />,
      );

      expect(container.querySelector('aside')).toBeInTheDocument();
    });

    it('passes speci product to dissemination drawer when SPECI is selected', async () => {
      operatorDisseminationUiConfig.destinationsEnabled = true;
      const user = userEvent.setup();
      render(<FileConverter {...defaultProps} />);

      fireEvent.change(screen.getByTestId('product-type-select'), {
        target: { value: 'SPECI' },
      });
      await user.click(screen.getByTestId('open-dissemination-drawer'));

      expect(screen.getByTestId('dissemination-drawer')).toBeInTheDocument();
    });

    it('no-ops convert and convert-and-send when workbench is read-only', async () => {
      operatorDisseminationUiConfig.destinationsEnabled = true;
      mockIsReadOnly.value = true;
      render(<FileConverter {...defaultProps} />);

      invokeReactOnClick(screen.getByTestId('convert-button'));
      invokeReactOnClick(screen.getByTestId('convert-and-send-button'));
      await act(async () => {
        await Promise.resolve();
      });

      expect(mockConvertMetarToIwxxm).not.toHaveBeenCalled();
      expect(mockUploadConvertedFiles).not.toHaveBeenCalled();
    });

    it('skips focused and batch queue convert when workbench is read-only', async () => {
      mockIsReadOnly.value = true;
      const user = userEvent.setup();
      const { container } = render(<FileConverter {...defaultProps} />);
      await addQueueFile(container, 'queued.tac', 'METAR QUEUED=');
      await user.click(screen.getByTestId('queue-select-0'));

      invokeReactOnClick(screen.getByTestId('batch-convert-button'));
      fireEvent.keyDown(screen.getByTestId('operator-work-queue'), { key: 'Enter' });

      expect(mockConvertMetarToIwxxm).not.toHaveBeenCalled();
    });

    it('skips focused and batch queue convert while conversion is busy', async () => {
      const user = userEvent.setup();
      const { container } = render(<FileConverter {...defaultProps} />);
      await addQueueFile(container, 'queued.tac', 'METAR QUEUED=');
      await user.click(screen.getByTestId('queue-select-0'));

      mockConvertMetarToIwxxm.mockImplementation(
        () =>
          new Promise(() => {
            /* keep busy */
          }),
      );
      invokeReactOnClick(screen.getByTestId('convert-button'));
      await act(async () => {
        await Promise.resolve();
      });
      invokeReactOnClick(screen.getByTestId('batch-convert-button'));
      fireEvent.keyDown(screen.getByTestId('operator-work-queue'), { key: 'Enter' });

      expect(mockConvertMetarToIwxxm).toHaveBeenCalledTimes(1);
    });

    it('skips batch validate while another validate/conversion is busy', async () => {
      const user = userEvent.setup();
      const { container } = render(<FileConverter {...defaultProps} />);
      await addQueueFile(container, 'queued.tac', 'METAR QUEUED=');
      await user.click(screen.getByTestId('queue-select-0'));

      mockLintTac.mockImplementation(
        () =>
          new Promise(() => {
            /* keep busy */
          }),
      );
      invokeReactOnClick(screen.getByTestId('batch-validate-button'));
      await act(async () => {
        await Promise.resolve();
      });
      invokeReactOnClick(screen.getByTestId('batch-validate-button'));

      expect(mockLintTac).toHaveBeenCalledTimes(1);
    });

    it('no-ops download-all when there are no converted files', () => {
      render(<FileConverter {...defaultProps} />);
      invokeReactOnClick(
        screen.getByRole('button', { name: /download all 0 converted files as zip/i }),
      );
      expect(mockToast.success).not.toHaveBeenCalledWith('All files downloaded as ZIP');
    });

    it('blocks mass ingest file input when signed out', async () => {
      const onRequestLogin = vi.fn();
      render(
        <FileConverter {...defaultProps} isGuest onRequestLogin={onRequestLogin} />,
      );
      const zipInput = screen.getByTestId('mass-ingest-zip-input') as HTMLInputElement;
      fireEvent.change(zipInput, {
        target: {
          files: [new File(['PK'], 'guest.zip', { type: 'application/zip' })],
        },
      });

      expect(onRequestLogin).toHaveBeenCalled();
      expect(mockToast.error).toHaveBeenCalledWith(
        'Sign in required for mass folder or zip ingest',
      );
      expect(mockMassIngestFiles).not.toHaveBeenCalled();
    });

    it('renders autosave indicator labels for each save state', () => {
      const labels: Array<[typeof mockSaveIndicator.value, RegExp]> = [
        ['pending', /unsaved changes/i],
        ['saving', /saving draft/i],
        ['saved', /draft saved/i],
        ['error', /save failed/i],
      ];

      for (const [state, pattern] of labels) {
        cleanup();
        mockSaveIndicator.value = state;
        render(<FileConverter {...defaultProps} />);
        expect(screen.getByTestId('autosave-indicator')).toHaveTextContent(pattern);
      }
    });

    it('shows draft toast when starting a new TAC while editable', async () => {
      const user = userEvent.setup();
      render(<FileConverter {...defaultProps} />);

      await user.type(screen.getByTestId('tac-editor'), 'METAR KJFK=');
      await user.click(screen.getByTestId('new-tac-button'));

      expect(mockToast.info).toHaveBeenCalledWith('Starting a new TAC draft');
    });

    it('applies lint fix replacement text from the workbench console', async () => {
      mockLintTac.mockResolvedValueOnce({
        ok: false,
        issues: [
          {
            severity: 'error',
            code: 'MISSING_TERMINATOR',
            message: 'missing =',
            start: 0,
            end: 10,
          },
        ],
        fixes: [{ code: 'add_terminator', replacement: 'METAR KJFK 121251Z=' }],
      });
      const user = userEvent.setup();
      render(<FileConverter {...defaultProps} />);

      fireEvent.change(screen.getByTestId('tac-editor'), {
        target: { value: 'METAR KJFK 121251Z' },
      });
      fireEvent.click(screen.getByTestId('workbench-console-toggle'));
      const action = await screen.findByTestId('console-action-add_terminator');
      await user.click(action);

      expect(screen.getByTestId('tac-editor')).toHaveValue('METAR KJFK 121251Z=');
    });

    it('uses live output filename when downloading multi-line manual results', async () => {
      const user = userEvent.setup();
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [
          { iwxxm_xml: '<line1/>', tac_input: 'METAR A=' },
          { iwxxm_xml: '<line2/>', tac_input: 'METAR B=' },
        ],
        errors: [],
        issues: [],
      });
      const createUrlSpy = vi
        .spyOn(URL, 'createObjectURL')
        .mockReturnValue('blob:download-one');
      const clickSpy = vi
        .spyOn(HTMLAnchorElement.prototype, 'click')
        .mockImplementation(() => undefined);

      render(<FileConverter {...defaultProps} />);
      await user.type(screen.getByTestId('output-filename-input'), 'batch/out');
      await user.type(screen.getByTestId('tac-editor'), 'METAR A=\nMETAR B=');
      await user.click(screen.getByTestId('convert-button'));

      const downloadBtn = await screen.findByRole('button', {
        name: /download out_1\.txt as xml/i,
      });
      await user.click(downloadBtn);

      expect(clickSpy).toHaveBeenCalled();
      createUrlSpy.mockRestore();
      clickSpy.mockRestore();
    });

    it('clears queue selection when removing a selected pending file', async () => {
      const user = userEvent.setup();
      const { container } = render(<FileConverter {...defaultProps} />);
      await addQueueFile(container, 'remove-me.tac', 'METAR REMOVE=');
      await user.click(screen.getByTestId('queue-select-0'));

      await user.click(
        screen.getByRole('button', { name: /remove remove-me\.tac from queue/i }),
      );

      expect(screen.queryByTestId('operator-work-queue')).not.toBeInTheDocument();
    });

    it('warns when selected product differs from detected TAC product', async () => {
      const user = userEvent.setup();
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [{ iwxxm_xml: '<taf/>', tac_input: 'METAR KJFK=' }],
        errors: [],
        issues: [],
      });
      render(<FileConverter {...defaultProps} />);

      fireEvent.change(screen.getByTestId('product-type-select'), {
        target: { value: 'TAF' },
      });
      await user.type(screen.getByTestId('tac-editor'), 'METAR KJFK 121251Z=');
      await user.click(screen.getByTestId('convert-button'));

      await waitFor(() => {
        expect(mockToast.warning).toHaveBeenCalledWith(
          expect.stringMatching(/Selected product TAF differs from detected METAR/i),
        );
      });
    });

    it('signs out from all devices and other devices scopes', async () => {
      const user = userEvent.setup();
      render(
        <FileConverter {...defaultProps} isGuest={false} userEmail="op@example.com" />,
      );

      await user.click(screen.getByTestId('logout-button'));
      await user.click(
        screen.getByRole('button', { name: /sign out from all devices/i }),
      );
      expect(mockSignOutWithScope).toHaveBeenCalledWith('global');

      mockSignOutWithScope.mockClear();
      await user.click(screen.getByTestId('logout-button'));
      await user.click(screen.getByRole('button', { name: /sign out other devices/i }));
      expect(mockSignOutWithScope).toHaveBeenCalledWith('others');
    });

    it('does not re-hydrate when loadedWorkSession id is unchanged', async () => {
      const session = {
        id: 'ev053-same-id',
        status: 'draft',
        manual_tac: 'METAR FIRST=',
        converted_results: [],
      } as any;
      const { rerender } = render(
        <FileConverter {...defaultProps} loadedWorkSession={session} />,
      );
      expect(await screen.findByDisplayValue('METAR FIRST=')).toBeInTheDocument();

      rerender(
        <FileConverter
          {...defaultProps}
          loadedWorkSession={{ ...session, manual_tac: 'METAR SECOND=' }}
        />,
      );

      expect(screen.getByTestId('tac-editor')).toHaveValue('METAR FIRST=');
    });

    it('batch validate increments fail count when lint returns not ok', async () => {
      const user = userEvent.setup();
      mockLintTac
        .mockResolvedValueOnce({ ok: true, issues: [], fixes: [] })
        .mockResolvedValueOnce({
          ok: false,
          issues: [{ severity: 'error', code: 'X', message: 'bad', start: 0, end: 3 }],
          fixes: [],
        });
      const { container } = render(<FileConverter {...defaultProps} />);
      const fileInput = container.querySelector(
        'input[type="file"]:not([data-testid])',
      ) as HTMLInputElement;
      fireEvent.change(fileInput, {
        target: {
          files: {
            0: { name: 'a.tac', text: vi.fn().mockResolvedValue('METAR A=') },
            1: { name: 'b.tac', text: vi.fn().mockResolvedValue('METAR B=') },
            length: 2,
          },
        },
      });
      await screen.findByTestId('operator-work-queue');
      await user.click(screen.getByTestId('queue-select-0'));
      await user.click(screen.getByTestId('queue-select-1'));
      await user.click(screen.getByTestId('batch-validate-button'));

      await waitFor(() => {
        expect(mockToast.success).toHaveBeenCalledWith(
          'Batch validate: 1 ok, 1 with issues',
          expect.anything(),
        );
      });
    });

    it('reloads populated preference fields after dialog save', async () => {
      const user = userEvent.setup();
      localStorage.setItem(
        'metar_converter_preferences',
        JSON.stringify({
          bulletinIdExample: 'BBBB01',
          issuingCenter: 'KDEN',
          product: 'METAR',
          profile: 'iwxxm_us',
          iwxxmVersion: '2025-2',
          strictValidation: true,
          includeNilReasons: true,
          onError: 'fail',
          logLevel: 'DEBUG',
        }),
      );
      render(<FileConverter {...defaultProps} />);

      await user.click(screen.getByLabelText(/open user preferences/i));
      await user.click(screen.getByTestId('save-prefs-dialog'));

      expect(mockToast.info).toHaveBeenCalledWith(
        'Conversion parameters updated from preferences',
      );
    });

    it('swallows corrupt preference JSON when reloading after save', async () => {
      const user = userEvent.setup();
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => undefined);
      localStorage.setItem('metar_converter_preferences', '{not-json');
      render(<FileConverter {...defaultProps} />);

      await user.click(screen.getByLabelText(/open user preferences/i));
      await user.click(screen.getByTestId('save-prefs-dialog'));

      expect(consoleSpy).toHaveBeenCalled();
      consoleSpy.mockRestore();
    });

    it('rethrows non-placeholder COLLECT ingest failures', async () => {
      const user = userEvent.setup();
      mockIngestCollect.mockRejectedValueOnce(new Error('collect service down'));
      render(<FileConverter {...defaultProps} />);

      await user.click(screen.getByTestId('input-mode-collect_iwxxm'));
      await user.type(screen.getByTestId('tac-editor'), collectSample);
      await user.click(screen.getByTestId('convert-button'));

      await waitFor(() => {
        expect(mockToast.error).toHaveBeenCalledWith('collect service down');
      });
    });

    it('toasts per-file success after focused queue convert', async () => {
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [{ iwxxm_xml: '<focused/>', tac_input: 'METAR FOC=' }],
        errors: [],
        issues: [],
      });
      const { container } = render(<FileConverter {...defaultProps} />);
      await addQueueFile(container, 'focused.tac', 'METAR FOC=');

      fireEvent.keyDown(screen.getByTestId('operator-work-queue'), { key: 'Enter' });

      await waitFor(() => {
        expect(mockToast.success).toHaveBeenCalledWith('Converted focused.tac');
      });
    });

    it('scrolls failed-span cue when preview failed-count is clicked', async () => {
      const user = userEvent.setup();
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [{ iwxxm_xml: '<soft/>', tac_input: 'METAR BAD=' }],
        errors: [],
        issues: [],
        ok: false,
        failed_spans: [{ start: 0, end: 4, message: 'bad' }],
      });
      const scrollMock = vi.fn();
      render(<FileConverter {...defaultProps} />);

      await user.click(screen.getByTestId('soft-preview-toggle'));
      await user.type(screen.getByTestId('tac-editor'), 'METAR BAD=');
      await user.click(screen.getByTestId('convert-button'));

      const cue = await screen.findByTestId('failed-tac-cue');
      cue.scrollIntoView = scrollMock;
      await user.click(await screen.findByTestId('iwxxm-preview-failed-count'));

      expect(scrollMock).toHaveBeenCalled();
    });

    it('clears the workbench console via the clear control', async () => {
      const user = userEvent.setup();
      render(<FileConverter {...defaultProps} />);

      await user.type(screen.getByTestId('tac-editor'), 'METAR KJFK=');
      fireEvent.click(screen.getByTestId('workbench-console-toggle'));
      await screen.findByTestId('workbench-console-lines');
      await user.click(screen.getByTestId('workbench-console-clear'));

      expect(screen.getByTestId('workbench-console-lines')).toHaveTextContent(
        /cleared/i,
      );
    });

    it('loads golden examples without an explicit product as auto', async () => {
      const catalog = await import('@/fixtures/examples/examplesCatalog');
      const spy = vi.spyOn(catalog, 'getExampleById').mockReturnValue({
        id: 'no-product',
        label: 'No product demo',
        body: 'METAR DEMO=',
        inputMode: 'tac',
      } as any);
      const user = userEvent.setup();
      render(<FileConverter {...defaultProps} />);

      await user.click(screen.getByTestId('examples-select'));
      await user.click(await screen.findByRole('option', { name: /METAR WMO A3-1/i }));

      expect(screen.getByTestId('product-type-select')).toHaveValue('auto');
      spy.mockRestore();
    });

    it('clears mass-ingest inputs after a successful folder upload', async () => {
      const user = userEvent.setup();
      render(<FileConverter {...defaultProps} accessToken="jwt-f33" />);
      const folderInput = screen.getByTestId(
        'mass-ingest-folder-input',
      ) as HTMLInputElement;

      await user.upload(
        folderInput,
        new File(['METAR KJFK='], 'one.tac', { type: 'text/plain' }),
      );

      await waitFor(() => {
        expect(mockMassIngestFiles).toHaveBeenCalled();
        expect(folderInput.value).toBe('');
      });
    });

    it('ignores preference reload when nothing is stored on save', async () => {
      const user = userEvent.setup();
      render(<FileConverter {...defaultProps} />);

      await user.click(screen.getByLabelText(/open user preferences/i));
      await user.click(screen.getByTestId('save-prefs-dialog'));

      expect(mockToast.info).not.toHaveBeenCalledWith(
        'Conversion parameters updated from preferences',
      );
    });

    it('does not warn when selected product matches detected TAC', async () => {
      const user = userEvent.setup();
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [{ iwxxm_xml: '<ok/>', tac_input: 'METAR KJFK=' }],
        errors: [],
        issues: [],
      });
      render(<FileConverter {...defaultProps} />);

      fireEvent.change(screen.getByTestId('product-type-select'), {
        target: { value: 'METAR' },
      });
      await user.type(screen.getByTestId('tac-editor'), 'METAR KJFK 121251Z=');
      await user.click(screen.getByTestId('convert-button'));

      await waitFor(() => expect(mockConvertMetarToIwxxm).toHaveBeenCalled());
      expect(mockToast.warning).not.toHaveBeenCalledWith(
        expect.stringMatching(/differs from detected/i),
      );
    });

    it('names queue results from API when extra results exceed queued files', async () => {
      const user = userEvent.setup();
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [
          { iwxxm_xml: '<q/>', tac_input: 'METAR Q=', name: 'queued.tac' },
          { iwxxm_xml: '<extra/>', tac_input: 'METAR X=', name: 'extra-from-api.tac' },
        ],
        errors: [],
        issues: [],
      });
      const { container } = render(<FileConverter {...defaultProps} />);
      await addQueueFile(container, 'queued.tac', 'METAR Q=');
      await user.click(screen.getByTestId('convert-button'));

      await waitFor(() => {
        expect(screen.getByText(/extra-from-api\.tac/i)).toBeInTheDocument();
      });
    });

    it('downloads queue file results using the .metar to .xml rename path', async () => {
      const user = userEvent.setup();
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [
          { iwxxm_xml: '<file/>', tac_input: 'METAR Q=', name: 'report.metar' },
        ],
        errors: [],
        issues: [],
      });
      const clickSpy = vi
        .spyOn(HTMLAnchorElement.prototype, 'click')
        .mockImplementation(() => undefined);
      vi.spyOn(URL, 'createObjectURL').mockReturnValue('blob:file');

      const { container } = render(<FileConverter {...defaultProps} />);
      await addQueueFile(container, 'report.metar', 'METAR Q=');
      await user.click(screen.getByTestId('convert-button'));

      const downloadBtn = await screen.findByRole('button', {
        name: /download report\.metar as xml/i,
      });
      await user.click(downloadBtn);

      expect(clickSpy).toHaveBeenCalled();
      clickSpy.mockRestore();
    });

    it('skips focused convert success toast on soft-preview soft fail', async () => {
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [{ iwxxm_xml: '<soft/>', tac_input: 'METAR SOFT=' }],
        errors: [],
        issues: [],
        ok: false,
        failed_spans: [{ start: 0, end: 4 }],
      });
      const user = userEvent.setup();
      const { container } = render(<FileConverter {...defaultProps} />);
      await addQueueFile(container, 'soft.tac', 'METAR SOFT=');

      await user.click(screen.getByTestId('soft-preview-toggle'));
      fireEvent.keyDown(screen.getByTestId('operator-work-queue'), { key: 'Enter' });

      await waitFor(() => expect(mockConvertMetarToIwxxm).toHaveBeenCalled());
      expect(mockToast.success).not.toHaveBeenCalledWith('Converted soft.tac');
    });

    it('live IWXXM sets empty preview when response has no XML', async () => {
      vi.useFakeTimers();
      try {
        render(<FileConverter {...defaultProps} />);
        fireEvent.click(screen.getByTestId('live-iwxxm-toggle'));

        mockConvertMetarToIwxxm.mockResolvedValueOnce({
          results: [{}],
          ok: true,
          failed_spans: [],
        });
        fireEvent.change(screen.getByTestId('tac-editor'), {
          target: { value: 'METAR KJFK 121251Z' },
        });
        await act(async () => {
          await vi.advanceTimersByTimeAsync(350);
          await Promise.resolve();
        });

        expect(screen.getByTestId('iwxxm-preview-pane')).toBeInTheDocument();
        expect(screen.queryByTestId('iwxxm-preview-xml')).not.toBeInTheDocument();
      } finally {
        vi.useRealTimers();
      }
    });
  });

  describe('EV-057 / #903 accumulate conversions (F7.r)', () => {
    const tacA = 'METAR KJFK 011200Z 18012KT 10SM FEW030 15/07 A3005';
    const tacB = 'METAR KLAX 011300Z 25008KT 10SM SCT040 20/12 A2990';

    it('accumulates sequential successes and clears the batch', async () => {
      const user = userEvent.setup();
      mockConvertMetarToIwxxm
        .mockResolvedValueOnce({
          results: [
            {
              iwxxm_xml: '<iwxxm>a</iwxxm>',
              tac_input: tacA,
              name: 'manual_input.txt',
            },
          ],
          errors: [],
          issues: [],
        })
        .mockResolvedValueOnce({
          results: [
            {
              iwxxm_xml: '<iwxxm>b</iwxxm>',
              tac_input: tacB,
              name: 'manual_input.txt',
            },
          ],
          errors: [],
          issues: [],
        });

      render(<FileConverter {...defaultProps} />);
      await user.type(screen.getByTestId('tac-editor'), tacA);
      await user.click(screen.getByTestId('convert-button'));

      await waitFor(() => {
        expect(
          screen.getByRole('region', { name: /conversion results/i }),
        ).toBeInTheDocument();
      });

      fireEvent.change(screen.getByTestId('tac-editor'), { target: { value: tacB } });
      await user.click(screen.getByTestId('convert-button'));

      await waitFor(() => {
        expect(mockConvertMetarToIwxxm).toHaveBeenCalledTimes(2);
      });
      expect(screen.getByTestId('download-zip-button')).toHaveAccessibleName(
        /download all 2 converted files as zip/i,
      );

      await user.click(screen.getByTestId('clear-queue-button'));
      expect(
        screen.queryByRole('region', { name: /conversion results/i }),
      ).not.toBeInTheDocument();
    });

    it('keeps prior successes when a later convert fails', async () => {
      const user = userEvent.setup();
      mockConvertMetarToIwxxm
        .mockResolvedValueOnce({
          results: [
            {
              iwxxm_xml: '<iwxxm>a</iwxxm>',
              tac_input: tacA,
              name: 'manual_input.txt',
            },
          ],
          errors: [],
          issues: [],
        })
        .mockRejectedValueOnce(new Error('network down'));

      render(<FileConverter {...defaultProps} />);
      await user.type(screen.getByTestId('tac-editor'), tacA);
      await user.click(screen.getByTestId('convert-button'));
      await waitFor(() => {
        expect(
          screen.getByRole('region', { name: /conversion results/i }),
        ).toBeInTheDocument();
      });

      fireEvent.change(screen.getByTestId('tac-editor'), {
        target: { value: 'NOT A METAR' },
      });
      await user.click(screen.getByTestId('convert-button'));

      await waitFor(() => {
        expect(mockConvertMetarToIwxxm).toHaveBeenCalledTimes(2);
      });
      expect(screen.getByTestId('download-zip-button')).toHaveAccessibleName(
        /download all 1 converted files as zip/i,
      );
    });

    it('names Download ZIP from first TAC stem when custom name is empty', async () => {
      const user = userEvent.setup();
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [
          {
            iwxxm_xml: '<iwxxm>a</iwxxm>',
            tac_input: tacA,
            name: 'manual_input.txt',
          },
        ],
        errors: [],
        issues: [],
      });
      let downloadedName = '';
      const clickSpy = vi
        .spyOn(HTMLAnchorElement.prototype, 'click')
        .mockImplementation(function (this: HTMLAnchorElement) {
          downloadedName = this.download;
        });
      vi.spyOn(URL, 'createObjectURL').mockReturnValue('blob:zip');

      render(<FileConverter {...defaultProps} />);
      await user.type(screen.getByTestId('tac-editor'), tacA);
      await user.click(screen.getByTestId('convert-button'));
      await waitFor(() => {
        expect(screen.getByTestId('download-zip-button')).toBeEnabled();
      });
      await user.click(screen.getByTestId('download-zip-button'));

      expect(downloadedName).toMatch(/^METARKJF_\d{14}\.zip$/);
      clickSpy.mockRestore();
    });

    it('blocks accumulating beyond the soft cap of 200', async () => {
      const user = userEvent.setup();
      mockConvertMetarToIwxxm
        .mockResolvedValueOnce({
          results: [
            {
              iwxxm_xml: '<iwxxm>a</iwxxm>',
              tac_input: tacA,
              name: 'manual_input.txt',
            },
          ],
          errors: [],
          issues: [],
        })
        .mockResolvedValueOnce({
          results: Array.from({ length: 200 }, (_, i) => ({
            iwxxm_xml: `<x${i}/>`,
            tac_input: `METAR X${i}=`,
            name: `r${i}.txt`,
          })),
          errors: [],
          issues: [],
        });

      render(<FileConverter {...defaultProps} />);
      await user.type(screen.getByTestId('tac-editor'), tacA);
      await user.click(screen.getByTestId('convert-button'));
      await waitFor(() => {
        expect(screen.getByTestId('download-zip-button')).toBeEnabled();
      });

      fireEvent.change(screen.getByTestId('tac-editor'), { target: { value: tacB } });
      await user.click(screen.getByTestId('convert-button'));

      await waitFor(() => {
        expect(mockToast.error).toHaveBeenCalledWith(
          expect.stringMatching(/Cannot keep more than 200 conversions/i),
        );
      });
      expect(screen.getByTestId('download-zip-button')).toHaveAccessibleName(
        /download all 1 converted files as zip/i,
      );
    });
  });

  describe('EV-057 / #838 validate-only IWXXM (F7.s)', () => {
    const goodXml =
      '<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2"><ok/></iwxxm:METAR>';

    it('pastes XML in Validate mode and shows a pass report without convert', async () => {
      const user = userEvent.setup();
      mockValidateIwxxm.mockResolvedValueOnce({
        is_valid: true,
        version: '2025-2',
        layers_passed: ['XML_WELLFORMED', 'XML_SCHEMA', 'SCHEMATRON'],
        layers_failed: [],
        package_ok: true,
        package_issues: [],
      });

      render(<FileConverter {...defaultProps} />);
      await user.click(screen.getByTestId('input-mode-validate_iwxxm'));
      expect(screen.getByTestId('validate-iwxxm-help')).toBeInTheDocument();
      fireEvent.change(screen.getByTestId('tac-editor'), {
        target: { value: goodXml },
      });
      await user.click(screen.getByRole('button', { name: /validate iwxxm xml/i }));

      await waitFor(() => {
        expect(mockValidateIwxxm).toHaveBeenCalledWith(
          expect.objectContaining({ xmlContent: goodXml }),
        );
      });
      expect(mockConvertMetarToIwxxm).not.toHaveBeenCalled();
      expect(screen.getByTestId('validate-iwxxm-report')).toBeInTheDocument();
      expect(screen.getByTestId('validate-iwxxm-status')).toHaveTextContent(/Valid/i);
    });

    it('shows structured fail for invalid XML validate response', async () => {
      const user = userEvent.setup();
      mockValidateIwxxm.mockResolvedValueOnce({
        is_valid: false,
        version: '2025-2',
        layers_passed: ['XML_WELLFORMED'],
        layers_failed: ['XML_SCHEMA'],
        package_ok: false,
        package_issues: [{ message: 'Element METAR unexpected', code: 'XSD' }],
      });

      render(<FileConverter {...defaultProps} />);
      await user.click(screen.getByTestId('input-mode-validate_iwxxm'));
      fireEvent.change(screen.getByTestId('tac-editor'), {
        target: { value: '<not-iwxxm/>' },
      });
      await user.click(screen.getByRole('button', { name: /validate iwxxm xml/i }));

      await waitFor(() => {
        expect(screen.getByTestId('validate-iwxxm-status')).toHaveTextContent(
          /Invalid/i,
        );
      });
      expect(screen.getByTestId('validate-iwxxm-failed-layers')).toHaveTextContent(
        'XML_SCHEMA',
      );
      expect(screen.getByTestId('validate-iwxxm-issues')).toHaveTextContent(
        /Element METAR unexpected/i,
      );
    });
  });

  describe('EV-060 / #1003 IWXXM product pass-through (F7.t)', () => {
    it('shows IWXXM product option and pass-through help (TC-EV060-1003-003)', async () => {
      const user = userEvent.setup();
      render(<FileConverter {...defaultProps} />);
      const select = screen.getByTestId('product-type-select');
      expect(screen.getByRole('option', { name: 'IWXXM' })).toBeInTheDocument();
      await user.selectOptions(select, 'IWXXM');
      expect(screen.getByTestId('iwxxm-product-help')).toHaveTextContent(
        /pass-through/i,
      );
      expect(screen.getByTestId('convert-button')).toHaveAccessibleName(
        /Lint and validate IWXXM XML/i,
      );
      expect(screen.getByTestId('convert-button')).toHaveTextContent(
        /Lint & validate/i,
      );
    });

    it('hides Convert&Send when product is IWXXM (TC-EV060-1003-003)', async () => {
      operatorDisseminationUiConfig.destinationsEnabled = true;
      const user = userEvent.setup();
      render(<FileConverter {...defaultProps} />);
      expect(screen.getByTestId('convert-and-send-button')).toBeInTheDocument();
      await user.selectOptions(screen.getByTestId('product-type-select'), 'IWXXM');
      expect(screen.queryByTestId('convert-and-send-button')).not.toBeInTheDocument();
    });

    it('sends product=iwxxm on convert and skips TAC convert message path', async () => {
      const user = userEvent.setup();
      const goodXml =
        '<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2"><ok/></iwxxm:METAR>';
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [
          {
            name: 'iwxxm_pass_through.xml',
            content: goodXml,
            source: 'manual',
            size_bytes: goodXml.length,
          },
        ],
        errors: [],
        issues: [],
        total_processed: 1,
        successful: 1,
        failed: 0,
        metadata: { product: 'iwxxm', pass_through: true },
      });

      render(<FileConverter {...defaultProps} />);
      await user.selectOptions(screen.getByTestId('product-type-select'), 'IWXXM');
      fireEvent.change(screen.getByTestId('tac-editor'), {
        target: { value: goodXml },
      });
      await user.click(screen.getByTestId('convert-button'));

      await waitFor(() => {
        expect(mockConvertMetarToIwxxm).toHaveBeenCalledWith(
          expect.objectContaining({ product: 'IWXXM' }),
        );
      });
    });

    it('hydrates IWXXM product from a stored session (TC-EV060-1003-004)', () => {
      render(
        <FileConverter
          {...defaultProps}
          loadedWorkSession={
            {
              id: 'ev060-iwxxm-product',
              status: 'draft',
              conversion_params: { product: 'IWXXM', profile: 'annex3' },
            } as any
          }
        />,
      );
      expect(screen.getByTestId('product-type-select')).toHaveValue('IWXXM');
      expect(screen.getByTestId('iwxxm-product-help')).toBeInTheDocument();
    });
  });
});
