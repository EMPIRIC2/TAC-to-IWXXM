import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { SystemSettingsPanel } from './SystemSettingsPanel'

const mockToast = vi.hoisted(() => ({
  error: vi.fn(),
  success: vi.fn(),
  info: vi.fn(),
}))

vi.mock('/utils/supabase/info', () => ({
  projectId: 'test-project',
}))

vi.mock('../IcaoAutocomplete', () => ({
  IcaoAutocomplete: ({ value, onChange }: { value: string; onChange: (v: string) => void }) => (
    <input
      aria-label="Default issuing center"
      value={value}
      onChange={(e) => onChange(e.target.value)}
    />
  ),
}))

vi.mock('sonner', () => ({
  toast: mockToast,
}))

describe('SystemSettingsPanel', () => {
  const accessToken = 'access-token-123'

  beforeEach(() => {
    vi.clearAllMocks()
    vi.stubGlobal('fetch', vi.fn())
  })

  it('loads settings and renders editable controls', async () => {
    const fetchMock = vi.mocked(fetch)
    fetchMock.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        settings: {
          defaultBulletinId: 'SAAA00',
          defaultIssuingCenter: 'KWBC',
          defaultIwxxmVersion: '2025-2',
          defaultStrictValidation: true,
          defaultIncludeNilReasons: true,
          defaultOnError: 'warn',
          defaultLogLevel: 'INFO',
          allowedIcaoCodes: ['KJFK'],
        },
      }),
    } as Response)

    render(<SystemSettingsPanel accessToken={accessToken} />)

    expect(await screen.findByRole('heading', { name: /system settings/i })).toBeInTheDocument()
    expect(screen.getByDisplayValue('SAAA00')).toBeInTheDocument()
    expect(screen.getByText('KJFK')).toBeInTheDocument()
  })

  it('shows error toast when load settings fails', async () => {
    const fetchMock = vi.mocked(fetch)
    fetchMock.mockResolvedValueOnce({ ok: false, json: async () => ({}) } as Response)

    render(<SystemSettingsPanel accessToken={accessToken} />)

    await waitFor(() => {
      expect(mockToast.error).toHaveBeenCalledWith('Failed to load system settings')
    })
  })

  it('saves changed settings and shows success toast', async () => {
    const user = userEvent.setup()
    const fetchMock = vi.mocked(fetch)
    fetchMock
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          settings: {
            defaultBulletinId: 'SAAA00',
            defaultIssuingCenter: 'KWBC',
            defaultIwxxmVersion: '2025-2',
            defaultStrictValidation: true,
            defaultIncludeNilReasons: true,
            defaultOnError: 'warn',
            defaultLogLevel: 'INFO',
            allowedIcaoCodes: [],
          },
        }),
      } as Response)
      .mockResolvedValueOnce({ ok: true, json: async () => ({}) } as Response)

    render(<SystemSettingsPanel accessToken={accessToken} />)

    const bulletinInput = await screen.findByLabelText(/default bulletin id/i)
    await user.clear(bulletinInput)
    await user.type(bulletinInput, 'ABCD12')

    await user.click(screen.getByRole('button', { name: /save settings/i }))

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining('/admin/settings'),
        expect.objectContaining({ method: 'POST' }),
      )
      expect(mockToast.success).toHaveBeenCalledWith('System settings saved successfully')
    })
  })

  it('shows error toast when save settings fails', async () => {
    const user = userEvent.setup()
    const fetchMock = vi.mocked(fetch)
    fetchMock
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          settings: {
            defaultBulletinId: 'SAAA00',
            defaultIssuingCenter: 'KWBC',
            defaultIwxxmVersion: '2025-2',
            defaultStrictValidation: true,
            defaultIncludeNilReasons: true,
            defaultOnError: 'warn',
            defaultLogLevel: 'INFO',
            allowedIcaoCodes: [],
          },
        }),
      } as Response)
      .mockResolvedValueOnce({ ok: false, json: async () => ({}) } as Response)

    render(<SystemSettingsPanel accessToken={accessToken} />)

    const bulletinInput = await screen.findByLabelText(/default bulletin id/i)
    await user.clear(bulletinInput)
    await user.type(bulletinInput, 'ABCD12')

    await user.click(screen.getByRole('button', { name: /save settings/i }))

    await waitFor(() => {
      expect(mockToast.error).toHaveBeenCalledWith('Failed to save system settings')
    })
  })

  it('updates issuing center, select fields and nil-reasons checkbox', async () => {
    const user = userEvent.setup()
    const fetchMock = vi.mocked(fetch)
    fetchMock.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        settings: {
          defaultBulletinId: 'SAAA00',
          defaultIssuingCenter: 'KWBC',
          defaultIwxxmVersion: '2025-2',
          defaultStrictValidation: true,
          defaultIncludeNilReasons: true,
          defaultOnError: 'warn',
          defaultLogLevel: 'INFO',
          allowedIcaoCodes: [],
        },
      }),
    } as Response)

    render(<SystemSettingsPanel accessToken={accessToken} />)

    const issuingCenter = await screen.findByLabelText(/default issuing center/i)
    await user.clear(issuingCenter)
    await user.type(issuingCenter, 'KDEN')

    await user.selectOptions(screen.getByLabelText(/default iwxxm version/i), '2023-1')
    await user.selectOptions(screen.getByLabelText(/default on error behavior/i), 'fail')
    await user.selectOptions(screen.getByLabelText(/default log level/i), 'ERROR')

    const includeNilReasons = screen.getByLabelText(/include nil reasons/i) as HTMLInputElement
    expect(includeNilReasons.checked).toBe(true)
    await user.click(includeNilReasons)

    expect((issuingCenter as HTMLInputElement).value).toBe('KDEN')
    expect((screen.getByLabelText(/default iwxxm version/i) as HTMLSelectElement).value).toBe('2023-1')
    expect((screen.getByLabelText(/default on error behavior/i) as HTMLSelectElement).value).toBe('fail')
    expect((screen.getByLabelText(/default log level/i) as HTMLSelectElement).value).toBe('ERROR')
    expect(includeNilReasons.checked).toBe(false)
  })

  it('adds and removes ICAO codes with validation', async () => {
    const user = userEvent.setup()
    const fetchMock = vi.mocked(fetch)
    fetchMock.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        settings: {
          defaultBulletinId: 'SAAA00',
          defaultIssuingCenter: 'KWBC',
          defaultIwxxmVersion: '2025-2',
          defaultStrictValidation: true,
          defaultIncludeNilReasons: true,
          defaultOnError: 'warn',
          defaultLogLevel: 'INFO',
          allowedIcaoCodes: ['KJFK'],
        },
      }),
    } as Response)

    render(<SystemSettingsPanel accessToken={accessToken} />)

    const addInput = await screen.findByPlaceholderText(/enter icao code/i)

    await user.type(addInput, 'KLAX')
    await user.click(screen.getByRole('button', { name: /add code/i }))
    expect(mockToast.success).toHaveBeenCalledWith('ICAO code KLAX added')

    await user.clear(addInput)
    await user.type(addInput, 'KJFK')
    await user.click(screen.getByRole('button', { name: /add code/i }))
    expect(mockToast.error).toHaveBeenCalledWith('ICAO code already exists')

    await user.clear(addInput)
    await user.type(addInput, 'ABC')
    await user.click(screen.getByRole('button', { name: /add code/i }))
    expect(mockToast.error).toHaveBeenCalledWith('Invalid ICAO code (must be 4 letters)')

    await user.click(screen.getAllByRole('button', { name: '×' })[0])
    expect(mockToast.info).toHaveBeenCalledWith('ICAO code KJFK removed')
  })

  it('adds ICAO code using Enter key in input field', async () => {
    const fetchMock = vi.mocked(fetch)
    fetchMock.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        settings: {
          defaultBulletinId: 'SAAA00',
          defaultIssuingCenter: 'KWBC',
          defaultIwxxmVersion: '2025-2',
          defaultStrictValidation: true,
          defaultIncludeNilReasons: true,
          defaultOnError: 'warn',
          defaultLogLevel: 'INFO',
          allowedIcaoCodes: [],
        },
      }),
    } as Response)

    render(<SystemSettingsPanel accessToken={accessToken} />)

    const addInput = await screen.findByPlaceholderText(/enter icao code/i)
    fireEvent.change(addInput, { target: { value: 'KSEA' } })
    fireEvent.keyDown(addInput, { key: 'Enter', code: 'Enter', charCode: 13 })

    expect(mockToast.success).toHaveBeenCalledWith('ICAO code KSEA added')
    expect(screen.getByText('KSEA')).toBeInTheDocument()
  })

  it('resets unsaved settings back to original values', async () => {
    const user = userEvent.setup()
    const fetchMock = vi.mocked(fetch)
    fetchMock.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        settings: {
          defaultBulletinId: 'SAAA00',
          defaultIssuingCenter: 'KWBC',
          defaultIwxxmVersion: '2025-2',
          defaultStrictValidation: true,
          defaultIncludeNilReasons: true,
          defaultOnError: 'warn',
          defaultLogLevel: 'INFO',
          allowedIcaoCodes: [],
        },
      }),
    } as Response)

    render(<SystemSettingsPanel accessToken={accessToken} />)

    const strictCheckbox = (await screen.findByLabelText(/strict validation/i)) as HTMLInputElement
    expect(strictCheckbox.checked).toBe(true)

    fireEvent.click(strictCheckbox)
    expect(strictCheckbox.checked).toBe(false)

    await user.click(screen.getByRole('button', { name: /reset/i }))

    await waitFor(() => {
      expect(strictCheckbox.checked).toBe(true)
      expect(mockToast.info).toHaveBeenCalledWith('Settings reset to last saved values')
    })
  })
})
