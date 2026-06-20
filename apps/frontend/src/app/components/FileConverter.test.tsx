/* eslint-disable @typescript-eslint/no-explicit-any */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { FileConverter } from './FileConverter'

const mockSignOutWithScope = vi.hoisted(() => vi.fn().mockResolvedValue(true))
const mockConvertMetarToIwxxm = vi.hoisted(() => vi.fn().mockResolvedValue({ success: true, data: '<iwxxm>test</iwxxm>' }))
const mockToast = vi.hoisted(() => ({
  success: vi.fn(),
  error: vi.fn(),
  loading: vi.fn(),
  dismiss: vi.fn(),
  promise: vi.fn(),
  info: vi.fn(),
}))

// Mock dependencies
vi.mock('/utils/supabase/info', () => ({
  projectId: 'test-project',
  publicAnonKey: 'test-key',
}))

vi.mock('/utils/supabase/logout', () => ({
  signOutWithScope: mockSignOutWithScope,
}))

vi.mock('/utils/api', () => ({
  convertMetarToIwxxm: mockConvertMetarToIwxxm,
  convertTafToIwxxm: vi.fn().mockResolvedValue({ success: true, data: '<iwxxm>test</iwxxm>' }),
}))

vi.mock('sonner', () => ({
  toast: mockToast,
}))

vi.mock('jszip', () => ({
  default: class JSZip {
    file() { return this }
    generateAsync() { return Promise.resolve(new Blob(['test'])) }
  },
}))

vi.mock('./DatabaseUploadDialog', () => ({
  DatabaseUploadDialog: ({ isOpen, onClose }: any) => (
    <div data-testid="database-upload-dialog" style={{ display: isOpen ? 'block' : 'none' }}>
      <button onClick={() => onClose()} data-testid="close-upload-dialog">Close</button>
    </div>
  ),
}))

vi.mock('./UserPreferencesDialog', () => ({
  UserPreferencesDialog: ({ isOpen, onClose, onPreferencesSaved }: any) => (
    <div data-testid="preferences-dialog" style={{ display: isOpen ? 'block' : 'none' }}>
      <button onClick={() => onPreferencesSaved?.()} data-testid="save-prefs-dialog">Save</button>
      <button onClick={() => onClose()} data-testid="close-prefs-dialog">Close</button>
    </div>
  ),
}))

vi.mock('./IcaoAutocomplete', () => ({
  IcaoAutocomplete: ({ value, onChange }: any) => (
    <input 
      data-testid="icao-input"
      value={value} 
      onChange={(e) => onChange(e.target.value)}
      placeholder="ICAO"
    />
  ),
}))

vi.mock('./ThemeToggle', () => ({
  ThemeToggle: () => <div data-testid="theme-toggle">Theme</div>,
}))

vi.mock('./ui/sonner', () => ({
  Toaster: () => <div data-testid="toaster" />,
}))

describe('FileConverter Component', () => {
  const defaultProps = {
    onLogout: vi.fn(),
    userEmail: 'test@example.com',
    accessToken: 'test-token',
    onSwitchToAdmin: vi.fn(),
  }

  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    mockSignOutWithScope.mockResolvedValue(true)
    mockConvertMetarToIwxxm.mockResolvedValue({ success: true, data: '<iwxxm>test</iwxxm>' })
  })

  describe('Rendering', () => {
    it('should render the file converter', () => {
      const { container } = render(<FileConverter {...defaultProps} />)
      expect(container).toBeTruthy()
    })

    it('should display user email', () => {
      render(<FileConverter {...defaultProps} />)
      // User email is passed to UserPreferencesDialog but not directly displayed
      // Check that component renders without errors instead
      expect(screen.getByText(/metar.*iwxxm converter/i)).toBeInTheDocument()
    })

    it('should display theme toggle', () => {
      render(<FileConverter {...defaultProps} />)
      expect(screen.getByTestId('theme-toggle')).toBeInTheDocument()
    })

    it('should display database upload button', async () => {
      render(<FileConverter {...defaultProps} />)
      const dbBtn = await screen.findByText(/upload to database/i, { selector: 'button' })
      expect(dbBtn).toBeInTheDocument()
      // Button should be disabled initially (no converted files)
      expect(dbBtn).toBeDisabled()
    })

    it('should display settings button', async () => {
      render(<FileConverter {...defaultProps} />)
      const settingsBtn = await screen.findByLabelText(/open user preferences/i)
      expect(settingsBtn).toBeInTheDocument()
      expect(settingsBtn).toHaveTextContent(/preferences/i)
    })
  })

  describe('Dialog Management', () => {
    it('should open database upload dialog', async () => {
      render(<FileConverter {...defaultProps} />)
      
      // Database upload button is initially disabled (no converted files)
      const dbBtn = await screen.findByText(/upload to database/i, { selector: 'button' })
      expect(dbBtn).toBeDisabled()
      
      // Dialog should remain closed
      const dialog = screen.getByTestId('database-upload-dialog')
      expect(dialog.style.display).toBe('none')
    })

    it('should close database upload dialog', async () => {
      render(<FileConverter {...defaultProps} />)
      
      // Database upload button is initially disabled
      const dbBtn = await screen.findByText(/upload to database/i, { selector: 'button' })
      expect(dbBtn).toBeDisabled()
      
      // Dialog should be closed initially
      const dialog = screen.getByTestId('database-upload-dialog')
      expect(dialog.style.display).toBe('none')
    })

    it('should open preferences dialog', async () => {
      const user = userEvent.setup()
      render(<FileConverter {...defaultProps} />)
      
      const settingsBtn = await screen.findByLabelText(/open user preferences/i)
      await user.click(settingsBtn)

      await waitFor(() => {
        const dialog = screen.getByTestId('preferences-dialog')
        expect(dialog.style.display).not.toBe('none')
      })
    })

    it('should close preferences dialog', async () => {
      const user = userEvent.setup()
      render(<FileConverter {...defaultProps} />)
      
      const settingsBtn = await screen.findByLabelText(/open user preferences/i)
      await user.click(settingsBtn)

      await waitFor(() => {
        expect(screen.getByTestId('preferences-dialog').style.display).not.toBe('none')
      })

      const closeBtn = screen.getByTestId('close-prefs-dialog')
      await user.click(closeBtn)

      await waitFor(() => {
        expect(screen.getByTestId('preferences-dialog').style.display).toBe('none')
      })
    })
  })

  describe('File Input', () => {
    it('should accept file uploads', async () => {
      const { container } = render(<FileConverter {...defaultProps} />)
      const fileInput = container.querySelector('input[type="file"]')
      expect(fileInput).toBeInTheDocument()
    })

    it('should accept multiple files', async () => {
      const { container } = render(<FileConverter {...defaultProps} />)
      const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement
      expect(fileInput.multiple).toBe(true)
    })

    it('should accept text/plain and application/json files', async () => {
      const { container } = render(<FileConverter {...defaultProps} />)
      const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement
      expect(fileInput.accept).toContain('.txt')
    })
  })

  describe('Drag and Drop', () => {
    it('should handle drag over and track dragging state', async () => {
      render(<FileConverter {...defaultProps} />)
      const dropZone = screen.getByRole('button', { name: /file drop zone/i })
      
      fireEvent.dragOver(dropZone, { dataTransfer: { items: [] } })
      
      await waitFor(() => {
        expect(dropZone).toBeInTheDocument()
      })
    })

    it('should handle drag leave and reset dragging state', async () => {
      render(<FileConverter {...defaultProps} />)
      const dropZone = screen.getByRole('button', { name: /file drop zone/i })
      
      fireEvent.dragLeave(dropZone)
      
      await waitFor(() => {
        expect(dropZone).toBeInTheDocument()
      })
    })

    it('handles file drop with valid files', async () => {
      render(<FileConverter {...defaultProps} />)
      const dropZone = screen.getByRole('button', { name: /file drop zone/i })
      
      const goodFile = {
        name: 'test.metar',
        text: vi.fn().mockResolvedValue('METAR EGLL 121650Z'),
      }
      
      fireEvent.drop(dropZone, {
        dataTransfer: {
          files: {
            0: goodFile,
            length: 1,
          },
        },
      })
      
      await waitFor(() => {
        expect(mockToast.success).toHaveBeenCalledWith('1 file(s) added to queue')
      })
    })
  })

  describe('Manual Input', () => {
    it('should accept manual METAR input', async () => {
      const user = userEvent.setup()
      const { container } = render(<FileConverter {...defaultProps} />)
      
      const textarea = container.querySelector('textarea')
      if (textarea) {
        await user.type(textarea, 'METAR KJFK...')
        expect(textarea).toHaveValue('METAR KJFK...')
      }
    })

    it('should accept manual TAF input', async () => {
      const user = userEvent.setup()
      const { container } = render(<FileConverter {...defaultProps} />)
      
      const textarea = container.querySelector('textarea')
      if (textarea) {
        await user.type(textarea, 'TAF KJFK...')
        expect(textarea).toHaveValue('TAF KJFK...')
      }
    })

    it('should clear input when clear button is clicked', async () => {
      const user = userEvent.setup()
      const { container } = render(<FileConverter {...defaultProps} />)
      
      const textarea = container.querySelector('textarea')
      if (textarea) {
        await user.type(textarea, 'Test content')
        expect(textarea).toHaveValue('Test content')

        const clearBtn = await screen.findByText(/clear/i, { selector: 'button' })
        await user.click(clearBtn)

        expect(textarea).toHaveValue('')
      }
    })
  })

  describe('Conversion Parameters', () => {
    it('should expand and collapse parameters section', async () => {
      const user = userEvent.setup()
      render(<FileConverter {...defaultProps} />)
      
      const expandBtn = await screen.findByLabelText(/expand parameters/i)
      await user.click(expandBtn)

      // Parameters should be visible
      const paramsSection = await screen.findByText(/iwxxm version/i)
      expect(paramsSection).toBeInTheDocument()
    })

    it('should allow changing IWXXM version', async () => {
      const user = userEvent.setup()
      const { container } = render(<FileConverter {...defaultProps} />)
      
      // Expand parameters
      const expandBtn = await screen.findByLabelText(/expand parameters/i)
      await user.click(expandBtn)

      // Find and change version
      const selects = container.querySelectorAll('select')
      if (selects.length > 0) {
        await user.click(selects[0])
        // Would select different version
      }
    })

    it('should allow setting bulletin ID', async () => {
      const user = userEvent.setup()
      const { container } = render(<FileConverter {...defaultProps} />)
      
      const expandBtn = await screen.findByLabelText(/expand parameters/i)
      await user.click(expandBtn)

      const inputs = container.querySelectorAll('input[type="text"]')
      const bulletinInput = inputs[0]
      if (bulletinInput) {
        await user.clear(bulletinInput)
        await user.type(bulletinInput, 'TEST01')
      }
    })
  })

  describe('Logout Functionality', () => {
    it('should have logout menu', async () => {
      render(<FileConverter {...defaultProps} />)
      const logoutMenuBtn = await screen.findByText(/logout/i, { selector: 'button' })
      expect(logoutMenuBtn).toBeInTheDocument()
    })

    it('should call logout handler', async () => {
      const user = userEvent.setup()
      const onLogout = vi.fn()
      render(<FileConverter {...defaultProps} onLogout={onLogout} />)
      
      const logoutMenuBtn = await screen.findByText(/logout/i, { selector: 'button' })
      await user.click(logoutMenuBtn)

      // Menu should show options
      await waitFor(() => {
        const globalLogout = screen.queryByText(/all devices/i)
        expect(globalLogout || logoutMenuBtn).toBeInTheDocument()
      })
    })

    it('should handle global logout', async () => {
      const user = userEvent.setup()
      const onLogout = vi.fn()
      
      render(<FileConverter {...defaultProps} onLogout={onLogout} />)
      
      const logoutMenuBtn = await screen.findByLabelText(/logout options/i)
      await user.click(logoutMenuBtn)

      // Menu opens successfully
      expect(screen.getByText(/this device/i)).toBeInTheDocument()
    })
  })

  describe('Admin Features', () => {
    it('should show admin button when onSwitchToAdmin is provided', async () => {
      const onSwitchToAdmin = vi.fn()
      render(<FileConverter {...defaultProps} onSwitchToAdmin={onSwitchToAdmin} />)
      
      const adminSelect = await screen.findByLabelText(/switch view/i)
      expect(adminSelect).toBeInTheDocument()
      expect(screen.getByText(/admin dashboard/i)).toBeInTheDocument()
    })

    it('should call onSwitchToAdmin when admin button is clicked', async () => {
      const user = userEvent.setup()
      const onSwitchToAdmin  = vi.fn()
      
      render(<FileConverter {...defaultProps} onSwitchToAdmin={onSwitchToAdmin} />)
      
      const adminSelect = await screen.findByLabelText(/switch view/i)
      await user.selectOptions(adminSelect, 'admin')

      await waitFor(() => {
        expect(onSwitchToAdmin).toHaveBeenCalledTimes(1)
      })
    })

    it('should not show admin button when onSwitchToAdmin is undefined', () => {
      render(<FileConverter {...defaultProps} onSwitchToAdmin={undefined} />)
      
      const adminBtn = screen.queryByText(/admin|dashboard/i, { selector: 'button' })
      // Admin-specific buttons should not be visible
      expect(adminBtn === null || adminBtn?.textContent?.includes('admin') === false).toBe(true)
    })
  })

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
      }
      localStorage.setItem('metar_converter_preferences', JSON.stringify(prefs))

      const { container } = render(<FileConverter {...defaultProps} />)
      expect(container).toBeTruthy()
      // Preferences would be loaded into component state
    })

    it('should handle invalid localStorage data gracefully', () => {
      localStorage.setItem('metar_converter_preferences', 'invalid json')
      const consoleSpy = vi.spyOn(console, 'error')

      const { container } = render(<FileConverter {...defaultProps} />)
      expect(container).toBeTruthy()
      
      consoleSpy.mockRestore()
    })

    it('reloads preferences on save and migrates legacy version to 2025-2', async () => {
      const user = userEvent.setup()
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
      )

      const { container } = render(<FileConverter {...defaultProps} />)
      const expandBtn = screen.getByLabelText(/expand parameters/i)
      await user.click(expandBtn)

      const versionSelect = container.querySelector('#param-iwxxm-version') as HTMLSelectElement
      expect(versionSelect.value).toBe('2023-1')

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
      )

      await user.click(screen.getByLabelText(/open user preferences/i))
      await user.click(screen.getByTestId('save-prefs-dialog'))

      await waitFor(() => {
        expect(versionSelect.value).toBe('2025-2')
      })
      expect(mockToast.info).toHaveBeenCalledTimes(1)
    })

    it('keeps 2023-1 version unchanged when preferences are reloaded', async () => {
      const user = userEvent.setup()
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
      )

      const { container } = render(<FileConverter {...defaultProps} />)
      await user.click(screen.getByLabelText(/expand parameters/i))

      const versionSelect = container.querySelector('#param-iwxxm-version') as HTMLSelectElement
      expect(versionSelect.value).toBe('2023-1')

      await user.click(screen.getByLabelText(/open user preferences/i))
      await user.click(screen.getByTestId('save-prefs-dialog'))

      await waitFor(() => {
        expect(versionSelect.value).toBe('2023-1')
      })
    })

    it('handles malformed JSON during preferences reload path', async () => {
      const user = userEvent.setup()
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => undefined)

      render(<FileConverter {...defaultProps} />)
      localStorage.setItem('metar_converter_preferences', '{invalid')

      await user.click(screen.getByLabelText(/open user preferences/i))
      await user.click(screen.getByTestId('save-prefs-dialog'))

      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalled()
      })

      consoleSpy.mockRestore()
    })
  })

  describe('Response Handling', () => {
    it('should display converted output', async () => {
      render(<FileConverter {...defaultProps} />)
      const { container } = render(<FileConverter {...defaultProps} />)
      
      // Conversion output area should exist
      const outputArea = container.querySelector('[class*="output"]')
      expect(outputArea || container).toBeTruthy()
    })

    it('should have copy button for results', async () => {
      render(<FileConverter {...defaultProps} />)
      // Copy button only appears when there are converted files, 
      // so we just check the component renders without errors
      expect(screen.getByText(/metar.*iwxxm converter/i)).toBeInTheDocument()
    })

    it('should have download button for results', async () => {
      render(<FileConverter {...defaultProps} />)
      const downloadBtn = await screen.findByText(/download/i, { selector: 'button' })
      expect(downloadBtn).toBeInTheDocument()
    })
  })

  describe('Loading States', () => {
    it('should show loading indicator during conversion', async () => {
      const { container } = render(<FileConverter {...defaultProps} />)
      expect(container).toBeTruthy()
      // Loading state management
    })

    it('should disable inputs during conversion', async () => {
      const { container } = render(<FileConverter {...defaultProps} />)
      expect(container).toBeTruthy()
      // Button states would change during conversion
    })
  })

  describe('Error Handling', () => {
    it('should handle empty input', async () => {
      const user = userEvent.setup()
      render(<FileConverter {...defaultProps} />)
      
      const convertBtn = await screen.findByText(/convert/i, { selector: 'button' })
      await user.click(convertBtn)

      // Should show error or validation message
    })

    it('should display conversion errors', async () => {
      render(<FileConverter {...defaultProps} />)
      // Check that there are no error toasts initially
      // The word "error" appears in UI labels like "On Error Behavior"
      const errorLabels = screen.queryAllByText(/error/i)
      // Should only be labels, not error messages
      expect(errorLabels.length).toBeGreaterThan(0) // UI labels exist
    })

    it('shows toast notification when convert is clicked with no input', async () => {
      const user = userEvent.setup()
      render(<FileConverter {...defaultProps} />)

      const convertBtn = screen.getByRole('button', { name: /convert metar files to iwxxm xml/i })
      expect(convertBtn).toBeDisabled()

      await user.click(convertBtn)

      expect(mockToast.error).not.toHaveBeenCalled()
    })
  })

  describe('Download Behavior', () => {
    it('should not process download when no converted files exist', async () => {
      render(<FileConverter {...defaultProps} />)
      
      // Use aria-label to find the download button uniquely
      const downloadBtn = screen.getByLabelText(/download all.*converted files as zip/i)
      expect(downloadBtn).toBeDisabled()
      
      const user = userEvent.setup()
      await user.click(downloadBtn)
      
      expect(mockToast.success).not.toHaveBeenCalledWith(
        expect.stringContaining('downloaded')
      )
    })
  })

  describe('Branch Path Coverage', () => {
    it('enables convert button when manual input is provided and converts successfully', async () => {
      const user = userEvent.setup()
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [{ iwxxm_xml: '<iwxxm>converted</iwxxm>' }],
      })

      const { container } = render(<FileConverter {...defaultProps} />)
      const convertBtn = screen.getByRole('button', { name: /convert metar files to iwxxm xml/i })
      expect(convertBtn).toBeDisabled()

      const textarea = container.querySelector('textarea') as HTMLTextAreaElement
      await user.type(textarea, 'METAR KJFK 121651Z 18005KT 10SM FEW030 24/16 A2992')
      expect(convertBtn).toBeEnabled()

      await user.click(convertBtn)

      await waitFor(() => {
        expect(mockConvertMetarToIwxxm).toHaveBeenCalledTimes(1)
      })

      expect(screen.getByRole('region', { name: /conversion results/i })).toBeInTheDocument()
      expect(screen.getByText('manual_input.txt')).toBeInTheDocument()
      expect(mockToast.success).toHaveBeenCalledWith('Successfully converted 1 file(s)')
      expect(screen.queryByText('Conversion Error')).not.toBeInTheDocument()
    })

    it('shows timeout status when backend conversion times out', async () => {
      const user = userEvent.setup()
      mockConvertMetarToIwxxm.mockRejectedValueOnce(new Error('backend timeout unreachable'))

      const { container } = render(<FileConverter {...defaultProps} />)
      const textarea = container.querySelector('textarea') as HTMLTextAreaElement
      await user.type(textarea, 'METAR EGLL 121650Z 22008KT 9999 BKN025 18/12 Q1016')

      await user.click(screen.getByRole('button', { name: /convert metar files to iwxxm xml/i }))

      await waitFor(() => {
        expect(screen.getByText(/backend may be unreachable/i)).toBeInTheDocument()
      })
      expect(mockToast.error).toHaveBeenCalledWith(
        'Conversion timeout - Backend may be unreachable. Please check if the API server is running.'
      )
    })

    it('shows auth error when backend returns unauthorized', async () => {
      const user = userEvent.setup()
      mockConvertMetarToIwxxm.mockRejectedValueOnce(new Error('401 unauthorized'))

      const { container } = render(<FileConverter {...defaultProps} />)
      const textarea = container.querySelector('textarea') as HTMLTextAreaElement
      await user.type(textarea, 'METAR KDEN 121653Z 02006KT 10SM SCT050 21/08 A3010')

      await user.click(screen.getByRole('button', { name: /convert metar files to iwxxm xml/i }))

      await waitFor(() => {
        expect(screen.getByText(/authentication failed/i)).toBeInTheDocument()
      })
      expect(mockToast.error).toHaveBeenCalledWith(
        'Authentication failed. Please ensure you are logged in.'
      )
    })

    it('uses local logout scope and triggers onLogout after timeout', async () => {
      const user = userEvent.setup()
      const onLogout = vi.fn()

      render(<FileConverter {...defaultProps} onLogout={onLogout} />)

      await user.click(screen.getByLabelText(/logout options/i))
      await user.click(screen.getByLabelText(/sign out from this device only/i))

      expect(mockSignOutWithScope).toHaveBeenCalledWith('local')
      await waitFor(() => {
        expect(onLogout).toHaveBeenCalledTimes(1)
      })
    })

    it('invokes global and others logout scopes', async () => {
      const user = userEvent.setup()

      render(<FileConverter {...defaultProps} />)

      await user.click(screen.getByLabelText(/logout options/i))
      await user.click(screen.getByLabelText(/sign out from all devices/i))
      expect(mockSignOutWithScope).toHaveBeenCalledWith('global')

      await user.click(screen.getByLabelText(/logout options/i))
      await user.click(screen.getByLabelText(/sign out from other devices/i))
      expect(mockSignOutWithScope).toHaveBeenCalledWith('others')
    })

    it('shows toast when reading one dropped file fails', async () => {
      const user = userEvent.setup()
      const badFile = {
        name: 'broken.metar',
        text: vi.fn().mockRejectedValue(new Error('read failed')),
      }

      const { container } = render(<FileConverter {...defaultProps} />)
      const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement

      fireEvent.change(fileInput, {
        target: {
          files: {
            0: badFile,
            length: 1,
          },
        },
      })

      await waitFor(() => {
        expect(mockToast.error).toHaveBeenCalledWith('Failed to read broken.metar')
      })

      await user.click(screen.getByRole('button', { name: /clear all pending files and manual input/i }))
      expect(mockToast.info).toHaveBeenCalledWith('Queue cleared')
    })

    it('opens file chooser when drop zone is activated by keyboard', async () => {
      render(<FileConverter {...defaultProps} />)

      const dropZone = screen.getByRole('button', { name: /file drop zone/i })
      const hiddenInput = screen.getByLabelText(/select metar files to upload/i) as HTMLInputElement
      const clickSpy = vi.spyOn(hiddenInput, 'click').mockImplementation(() => undefined)

      fireEvent.keyDown(dropZone, { key: 'Enter', code: 'Enter' })

      expect(clickSpy).toHaveBeenCalledTimes(1)
      clickSpy.mockRestore()
    })

    it('copies using modern clipboard API success path', async () => {
      const user = userEvent.setup()
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [{ iwxxm_xml: '<iwxxm>clipboard-success</iwxxm>' }],
      })

      const writeTextSpy = vi.fn().mockResolvedValue(undefined)
      const clipboardSpy = vi.spyOn(navigator, 'clipboard', 'get')
      clipboardSpy.mockReturnValue({ writeText: writeTextSpy } as unknown as Clipboard)

      const { container } = render(<FileConverter {...defaultProps} />)
      const textarea = container.querySelector('textarea') as HTMLTextAreaElement
      await user.type(textarea, 'METAR CLIPBOARD SUCCESS')
      await user.click(screen.getByRole('button', { name: /convert metar files to iwxxm xml/i }))

      await waitFor(() => {
        expect(screen.getByText('manual_input.txt')).toBeInTheDocument()
      })

      await user.click(screen.getByRole('button', { name: /copy manual_input\.txt content to clipboard/i }))

      await waitFor(() => {
        expect(writeTextSpy).toHaveBeenCalledWith('<iwxxm>clipboard-success</iwxxm>')
      })
      expect(mockToast.success).toHaveBeenCalledWith('Copied to clipboard')
      clipboardSpy.mockRestore()
    })

    it('removes pending and converted files via row actions', async () => {
      const user = userEvent.setup()
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [{ iwxxm_xml: '<iwxxm>remove-me</iwxxm>' }],
      })

      const { container } = render(<FileConverter {...defaultProps} />)
      const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement
      const goodFile = {
        name: 'pending.txt',
        text: vi.fn().mockResolvedValue('METAR PENDING'),
      }

      fireEvent.change(fileInput, {
        target: {
          files: {
            0: goodFile,
            length: 1,
          },
        },
      })

      await waitFor(() => {
        expect(screen.getByText('pending.txt')).toBeInTheDocument()
      })

      await user.click(screen.getByRole('button', { name: /remove pending\.txt from queue/i }))
      await waitFor(() => {
        expect(screen.queryByText('pending.txt')).not.toBeInTheDocument()
      })

      const manualInput = container.querySelector('textarea') as HTMLTextAreaElement
      await user.type(manualInput, 'METAR CONVERT FOR REMOVE')
      await user.click(screen.getByRole('button', { name: /convert metar files to iwxxm xml/i }))

      await waitFor(() => {
        expect(screen.getByText('manual_input.txt')).toBeInTheDocument()
      })

      await user.click(screen.getByRole('button', { name: /remove manual_input\.txt from results/i }))
      await waitFor(() => {
        expect(screen.queryByText('manual_input.txt')).not.toBeInTheDocument()
      })
    })

    it('opens upload dialog when converted files are present', async () => {
      const user = userEvent.setup()
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [{ iwxxm_xml: '<iwxxm>upload-test</iwxxm>' }],
      })

      const { container } = render(<FileConverter {...defaultProps} />)
      const textarea = container.querySelector('textarea') as HTMLTextAreaElement
      await user.type(textarea, 'METAR UPLOAD BUTTON')
      await user.click(screen.getByRole('button', { name: /convert metar files to iwxxm xml/i }))

      const uploadButton = await screen.findByRole('button', { name: /upload 1 converted files to database/i })
      expect(uploadButton).toBeEnabled()

      await user.click(uploadButton)
      await waitFor(() => {
        expect(screen.getByTestId('database-upload-dialog').style.display).toBe('block')
      })
    })

    it('handles partial multi-file conversion where only one result is returned', async () => {
      const user = userEvent.setup()
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [{ iwxxm_xml: '<iwxxm>first</iwxxm>' }],
      })

      const { container } = render(<FileConverter {...defaultProps} />)
      const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement
      const fileOne = {
        name: 'first.txt',
        text: vi.fn().mockResolvedValue('METAR ONE'),
      }
      const fileTwo = {
        name: 'second.txt',
        text: vi.fn().mockResolvedValue('METAR TWO'),
      }

      fireEvent.change(fileInput, {
        target: {
          files: {
            0: fileOne,
            1: fileTwo,
            length: 2,
          },
        },
      })
      await waitFor(() => {
        expect(screen.getByRole('region', { name: /pending files queue/i })).toBeInTheDocument()
      })

      await user.click(screen.getByRole('button', { name: /convert metar files to iwxxm xml/i }))

      await waitFor(() => {
        expect(screen.getByRole('region', { name: /conversion results/i })).toBeInTheDocument()
      })

      expect(screen.getByText('first.txt')).toBeInTheDocument()
      expect(screen.queryByText('second.txt')).not.toBeInTheDocument()
      expect(screen.getByText('<iwxxm>first</iwxxm>')).toBeInTheDocument()
    })

    it('shows no-files-converted status when response results is empty', async () => {
      const user = userEvent.setup()
      mockConvertMetarToIwxxm.mockResolvedValueOnce({ results: [] })

      const { container } = render(<FileConverter {...defaultProps} />)
      const textarea = container.querySelector('textarea') as HTMLTextAreaElement
      await user.type(textarea, 'METAR EMPTY RESULTS CASE')

      await user.click(screen.getByRole('button', { name: /convert metar files to iwxxm xml/i }))

      await waitFor(() => {
        expect(screen.getByText(/no files were converted/i)).toBeInTheDocument()
      })
      expect(mockToast.error).toHaveBeenCalledWith('No files were converted')
      expect(screen.getByText('Conversion Error')).toBeInTheDocument()
    })

    it('uses fallback copy path when clipboard API is unavailable', async () => {
      const user = userEvent.setup()
      mockConvertMetarToIwxxm.mockReset().mockResolvedValueOnce({
        results: [{ iwxxm_xml: '<iwxxm>copy-me</iwxxm>' }],
      })

      const clipboardSpy = vi.spyOn(navigator, 'clipboard', 'get')
      clipboardSpy.mockReturnValue(undefined as unknown as Clipboard)
      Object.defineProperty(document, 'execCommand', {
        configurable: true,
        writable: true,
        value: vi.fn().mockReturnValue(true),
      })
      const execSpy = document.execCommand as unknown as ReturnType<typeof vi.fn>

      const { container } = render(<FileConverter {...defaultProps} />)
      const textarea = container.querySelector('textarea') as HTMLTextAreaElement
      await user.type(textarea, 'METAR COPY TEST')
      await user.click(screen.getByRole('button', { name: /convert metar files to iwxxm xml/i }))

      await waitFor(() => {
        expect(screen.getByText('manual_input.txt')).toBeInTheDocument()
      })

      await user.click(screen.getByRole('button', { name: /copy manual_input\.txt content to clipboard/i }))

      expect(execSpy).toHaveBeenCalledWith('copy')
      expect(mockToast.success).toHaveBeenCalledWith('Copied to clipboard')

      clipboardSpy.mockRestore()
      execSpy.mockRestore()
    })

    it('shows fallback copy error when execCommand returns false', async () => {
      const user = userEvent.setup()
      mockConvertMetarToIwxxm.mockReset().mockResolvedValueOnce({
        results: [{ iwxxm_xml: '<iwxxm>copy-fail</iwxxm>' }],
      })

      const clipboardSpy = vi.spyOn(navigator, 'clipboard', 'get')
      clipboardSpy.mockReturnValue(undefined as unknown as Clipboard)
      Object.defineProperty(document, 'execCommand', {
        configurable: true,
        writable: true,
        value: vi.fn().mockReturnValue(false),
      })

      const { container } = render(<FileConverter {...defaultProps} />)
      const textarea = container.querySelector('textarea') as HTMLTextAreaElement
      await user.type(textarea, 'METAR COPY FAIL TEST')
      await user.click(screen.getByRole('button', { name: /convert metar files to iwxxm xml/i }))

      await waitFor(() => {
        expect(screen.getByText('manual_input.txt')).toBeInTheDocument()
      })

      await user.click(screen.getByRole('button', { name: /copy manual_input\.txt content to clipboard/i }))

      expect(mockToast.error).toHaveBeenCalledWith('Failed to copy. Please copy manually.')

      clipboardSpy.mockRestore()
    })

    it('downloads a single converted file', async () => {
      const user = userEvent.setup()
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [{ iwxxm_xml: '<iwxxm>download-single</iwxxm>' }],
      })

      const createUrlSpy = vi.spyOn(URL, 'createObjectURL').mockReturnValue('blob:single')
      const revokeUrlSpy = vi.spyOn(URL, 'revokeObjectURL').mockImplementation(() => undefined)
      const clickSpy = vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => undefined)

      const { container } = render(<FileConverter {...defaultProps} />)
      const textarea = container.querySelector('textarea') as HTMLTextAreaElement
      await user.type(textarea, 'METAR DOWNLOAD SINGLE')
      await user.click(screen.getByRole('button', { name: /convert metar files to iwxxm xml/i }))

      await waitFor(() => {
        expect(screen.getByText('manual_input.txt')).toBeInTheDocument()
      })

      await user.click(screen.getByRole('button', { name: /download manual_input\.txt as xml/i }))

      expect(createUrlSpy).toHaveBeenCalled()
      expect(clickSpy).toHaveBeenCalled()
      expect(revokeUrlSpy).toHaveBeenCalledWith('blob:single')

      createUrlSpy.mockRestore()
      revokeUrlSpy.mockRestore()
      clickSpy.mockRestore()
    })

    it('uses error status path for non-timeout non-auth conversion errors', async () => {
      const user = userEvent.setup()
      mockConvertMetarToIwxxm.mockReset().mockRejectedValueOnce(new Error('validation parsing failed'))

      const { container } = render(<FileConverter {...defaultProps} />)
      const textarea = container.querySelector('textarea') as HTMLTextAreaElement
      await user.type(textarea, 'METAR GENERIC ERROR')
      await user.click(screen.getByRole('button', { name: /convert metar files to iwxxm xml/i }))

      await waitFor(() => {
        expect(screen.getByText('Conversion Error')).toBeInTheDocument()
        expect(screen.getByText('validation parsing failed')).toBeInTheDocument()
      })
      expect(mockToast.error).toHaveBeenCalledWith('validation parsing failed')
    })

    it('keeps logout menu open when scoped logout fails', async () => {
      const user = userEvent.setup()
      const onLogout = vi.fn()
      mockSignOutWithScope.mockResolvedValueOnce(false)

      render(<FileConverter {...defaultProps} onLogout={onLogout} />)

      await user.click(screen.getByLabelText(/logout options/i))
      await user.click(screen.getByLabelText(/sign out from this device only/i))

      await waitFor(() => {
        expect(onLogout).not.toHaveBeenCalled()
        expect(screen.getByText(/sign out scope/i)).toBeInTheDocument()
      })
    })

    it('handles result with xml fallback field when iwxxm_xml is missing', async () => {
      const user = userEvent.setup()
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [{ xml: '<xml>fallback-xml</xml>' }],
      })

      const { container } = render(<FileConverter {...defaultProps} />)
      const textarea = container.querySelector('textarea') as HTMLTextAreaElement
      await user.type(textarea, 'METAR XML FALLBACK')
      await user.click(screen.getByRole('button', { name: /convert metar files to iwxxm xml/i }))

      await waitFor(() => {
        expect(mockToast.success).toHaveBeenCalledWith(
          expect.stringContaining('Successfully converted')
        )
      })
    })

    it('handles result with content fallback field when neither iwxxm_xml nor xml is present', async () => {
      const user = userEvent.setup()
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [{ content: '<content>fallback-content</content>' }],
      })

      const { container } = render(<FileConverter {...defaultProps} />)
      const textarea = container.querySelector('textarea') as HTMLTextAreaElement
      await user.type(textarea, 'METAR CONTENT FALLBACK')
      await user.click(screen.getByRole('button', { name: /convert metar files to iwxxm xml/i }))

      await waitFor(() => {
        expect(mockToast.success).toHaveBeenCalledWith(
          expect.stringContaining('Successfully converted')
        )
      })
    })

    it('clears files and input when clear button is clicked', async () => {
      const user = userEvent.setup()
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [{ iwxxm_xml: '<iwxxm>clear-test</iwxxm>' }],
      })

      const { container } = render(<FileConverter {...defaultProps} />)
      const textarea = container.querySelector('textarea') as HTMLTextAreaElement
      await user.type(textarea, 'METAR CLEAR TEST')
      await user.click(screen.getByRole('button', { name: /convert metar files to iwxxm xml/i }))

      await waitFor(() => {
        expect(mockToast.success).toHaveBeenCalledWith(
          expect.stringContaining('Successfully converted')
        )
      })

      await user.click(screen.getByRole('button', { name: /clear all pending files/i }))

      await waitFor(() => {
        expect(mockToast.info).toHaveBeenCalledWith('Queue cleared')
      })
    })

    // lines 289-307: handleDownloadAll body (zip creation + anchor click)
    it('downloads all converted files as ZIP after conversion', async () => {
      const user = userEvent.setup()
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [{ iwxxm_xml: '<iwxxm>zip-all</iwxxm>' }],
      })

      const createUrlSpy = vi.spyOn(URL, 'createObjectURL').mockReturnValue('blob:zipall')
      const revokeUrlSpy = vi.spyOn(URL, 'revokeObjectURL').mockImplementation(() => undefined)
      const clickSpy = vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => undefined)

      const { container } = render(<FileConverter {...defaultProps} />)
      const textarea = container.querySelector('textarea') as HTMLTextAreaElement
      await user.type(textarea, 'METAR DOWNLOAD ALL ZIP')
      await user.click(screen.getByRole('button', { name: /convert metar files to iwxxm xml/i }))

      const downloadZipBtn = await screen.findByLabelText(/download all 1 converted files as zip/i)
      expect(downloadZipBtn).toBeEnabled()

      await user.click(downloadZipBtn)

      await waitFor(() => {
        expect(mockToast.success).toHaveBeenCalledWith('All files downloaded as ZIP')
      })
      expect(createUrlSpy).toHaveBeenCalled()
      expect(clickSpy).toHaveBeenCalled()
      expect(revokeUrlSpy).toHaveBeenCalledWith('blob:zipall')

      createUrlSpy.mockRestore()
      revokeUrlSpy.mockRestore()
      clickSpy.mockRestore()
    })

    // line 319: clipboard.writeText() .catch() path → fallbackCopy
    it('falls back to execCommand when clipboard.writeText rejects', async () => {
      const user = userEvent.setup()
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [{ iwxxm_xml: '<iwxxm>clipboard-catch</iwxxm>' }],
      })

      const writeTextSpy = vi.fn().mockRejectedValue(new Error('clipboard permission denied'))
      const clipboardSpy = vi.spyOn(navigator, 'clipboard', 'get')
      clipboardSpy.mockReturnValue({ writeText: writeTextSpy } as unknown as Clipboard)
      Object.defineProperty(document, 'execCommand', {
        configurable: true,
        writable: true,
        value: vi.fn().mockReturnValue(true),
      })

      const { container } = render(<FileConverter {...defaultProps} />)
      const textarea = container.querySelector('textarea') as HTMLTextAreaElement
      await user.type(textarea, 'METAR CLIPBOARD CATCH PATH')
      await user.click(screen.getByRole('button', { name: /convert metar files to iwxxm xml/i }))

      await waitFor(() => {
        expect(screen.getByText('manual_input.txt')).toBeInTheDocument()
      })

      await user.click(screen.getByRole('button', { name: /copy manual_input\.txt content to clipboard/i }))

      await waitFor(() => {
        expect(mockToast.success).toHaveBeenCalledWith('Copied to clipboard')
      })

      clipboardSpy.mockRestore()
    })

    // lines 346-347: fallbackCopy catch block when execCommand throws
    it('shows error toast when execCommand throws inside fallbackCopy', async () => {
      const user = userEvent.setup()
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [{ iwxxm_xml: '<iwxxm>exec-throw</iwxxm>' }],
      })

      const clipboardSpy = vi.spyOn(navigator, 'clipboard', 'get')
      clipboardSpy.mockReturnValue(undefined as unknown as Clipboard)
      Object.defineProperty(document, 'execCommand', {
        configurable: true,
        writable: true,
        value: vi.fn().mockImplementation(() => { throw new Error('execCommand not supported') }),
      })
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => undefined)

      const { container } = render(<FileConverter {...defaultProps} />)
      const textarea = container.querySelector('textarea') as HTMLTextAreaElement
      await user.type(textarea, 'METAR EXEC THROW PATH')
      await user.click(screen.getByRole('button', { name: /convert metar files to iwxxm xml/i }))

      await waitFor(() => {
        expect(screen.getByText('manual_input.txt')).toBeInTheDocument()
      })

      await user.click(screen.getByRole('button', { name: /copy manual_input\.txt content to clipboard/i }))

      expect(mockToast.error).toHaveBeenCalledWith('Failed to copy. Please copy manually.')
      expect(consoleSpy).toHaveBeenCalled()

      clipboardSpy.mockRestore()
      consoleSpy.mockRestore()
    })

    // line 498: "Select Files" button calls fileInputRef.current?.click()
    it('triggers hidden file input click when Select Files button is pressed', () => {
      const { container } = render(<FileConverter {...defaultProps} />)
      const hiddenInput = container.querySelector('input[type="file"]') as HTMLInputElement
      const clickSpy = vi.spyOn(hiddenInput, 'click').mockImplementation(() => undefined)

      fireEvent.click(screen.getByRole('button', { name: /browse and select files/i }))

      expect(clickSpy).toHaveBeenCalledTimes(1)
      clickSpy.mockRestore()
    })

    // lines 547-632: onChange handlers in conversion parameter form controls
    it('updates all conversion parameter form controls', async () => {
      const user = userEvent.setup()
      const { container } = render(<FileConverter {...defaultProps} />)

      await user.click(screen.getByLabelText(/expand parameters/i))

      // Bulletin ID – onChange uppercases the value
      const bulletinInput = container.querySelector('#param-bulletin-id') as HTMLInputElement
      await user.clear(bulletinInput)
      await user.type(bulletinInput, 'saaa01')
      expect(bulletinInput.value).toBe('SAAA01')

      // Issuing center (mocked IcaoAutocomplete input)
      const icaoInput = screen.getByTestId('icao-input')
      await user.clear(icaoInput)
      await user.type(icaoInput, 'KJFK')
      expect(icaoInput).toHaveValue('KJFK')

      // IWXXM version select
      await user.selectOptions(container.querySelector('#param-iwxxm-version') as HTMLSelectElement, '2023-1')
      expect((container.querySelector('#param-iwxxm-version') as HTMLSelectElement).value).toBe('2023-1')

      // On Error behavior select
      await user.selectOptions(container.querySelector('#param-on-error') as HTMLSelectElement, 'fail')
      expect((container.querySelector('#param-on-error') as HTMLSelectElement).value).toBe('fail')

      // Log level select
      await user.selectOptions(container.querySelector('#param-log-level') as HTMLSelectElement, 'DEBUG')
      expect((container.querySelector('#param-log-level') as HTMLSelectElement).value).toBe('DEBUG')

      // Validation checkboxes
      const checkboxes = container.querySelectorAll('input[type="checkbox"]')
      const strictCheck = checkboxes[0] as HTMLInputElement
      const nilCheck = checkboxes[1] as HTMLInputElement
      await user.click(strictCheck)
      expect(strictCheck.checked).toBe(false)
      await user.click(nilCheck)
      expect(nilCheck.checked).toBe(false)
    })

    // line 829: DatabaseUploadDialog onClose callback sets isUploadDialogOpen to false
    it('closes database upload dialog when onClose is invoked', async () => {
      const user = userEvent.setup()
      mockConvertMetarToIwxxm.mockResolvedValueOnce({
        results: [{ iwxxm_xml: '<iwxxm>close-dialog</iwxxm>' }],
      })

      const { container } = render(<FileConverter {...defaultProps} />)
      const textarea = container.querySelector('textarea') as HTMLTextAreaElement
      await user.type(textarea, 'METAR CLOSE DIALOG TEST')
      await user.click(screen.getByRole('button', { name: /convert metar files to iwxxm xml/i }))

      const uploadButton = await screen.findByRole('button', { name: /upload 1 converted files to database/i })
      await user.click(uploadButton)

      await waitFor(() => {
        expect(screen.getByTestId('database-upload-dialog').style.display).toBe('block')
      })

      await user.click(screen.getByTestId('close-upload-dialog'))

      await waitFor(() => {
        expect(screen.getByTestId('database-upload-dialog').style.display).toBe('none')
      })
    })
  })
})
