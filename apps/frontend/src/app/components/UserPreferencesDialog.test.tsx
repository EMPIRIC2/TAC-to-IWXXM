/* eslint-disable @typescript-eslint/no-explicit-any */
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { UserPreferencesDialog } from './UserPreferencesDialog'

const mockToast = vi.hoisted(() => ({
  success: vi.fn(),
  error: vi.fn(),
}))

vi.mock('sonner', () => ({
  toast: mockToast,
}))

vi.mock('./IcaoAutocomplete', () => ({
  IcaoAutocomplete: ({ value, onChange, id, label }: any) => (
    <label htmlFor={id}>
      {label}
      <input
        id={id}
        data-testid="icao-autocomplete"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
    </label>
  ),
}))

const defaultProps = {
  isOpen: true,
  onClose: vi.fn(),
  userEmail: 'prefs@example.com',
  onPreferencesSaved: vi.fn(),
}

describe('UserPreferencesDialog', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    vi.spyOn(console, 'error').mockImplementation(() => undefined)
  })

  it('renders nothing when closed', () => {
    const { container } = render(<UserPreferencesDialog {...defaultProps} isOpen={false} />)
    expect(container).toBeEmptyDOMElement()
  })

  it('loads defaults for first-time users', async () => {
    render(<UserPreferencesDialog {...defaultProps} />)

    expect(await screen.findByDisplayValue('prefs')).toBeInTheDocument()
    expect(screen.getByDisplayValue('prefs@example.com')).toBeInTheDocument()
    expect(screen.getByLabelText(/iwxxm schema version/i)).toHaveValue('2025-2')
  })

  it('merges stored preferences from localStorage', async () => {
    localStorage.setItem(
      'metar_converter_preferences',
      JSON.stringify({
        bulletinIdExample: 'ABCD12',
        issuingCenter: 'KLAX',
        iwxxmVersion: '2023-1',
        onError: 'skip',
        logLevel: 'DEBUG',
      }),
    )

    render(<UserPreferencesDialog {...defaultProps} />)

    await waitFor(() => {
      expect(screen.getByDisplayValue('ABCD12')).toBeInTheDocument()
      expect(screen.getByTestId('icao-autocomplete')).toHaveValue('KLAX')
      expect(screen.getByLabelText(/iwxxm schema version/i)).toHaveValue('2023-1')
      expect(screen.getByLabelText(/on error behavior/i)).toHaveValue('skip')
      expect(screen.getByLabelText(/log level/i)).toHaveValue('DEBUG')
    })
  })

  it('saves updated preferences and notifies parent', async () => {
    const onPreferencesSaved = vi.fn()
    const user = userEvent.setup()
    render(<UserPreferencesDialog {...defaultProps} onPreferencesSaved={onPreferencesSaved} />)

    const displayName = await screen.findByLabelText(/display name/i)
    await user.clear(displayName)
    await user.type(displayName, 'Workflow User')

    await user.click(screen.getByRole('button', { name: /save preferences/i }))

    const stored = JSON.parse(localStorage.getItem('metar_converter_preferences') || '{}')
    expect(stored.displayName).toBe('Workflow User')
    expect(mockToast.success).toHaveBeenCalledWith('Preferences saved successfully')
    expect(onPreferencesSaved).toHaveBeenCalledTimes(1)
    expect(screen.getByText(/preferences saved successfully/i)).toBeInTheDocument()
  })

  it('updates preference fields across sections', async () => {
    const user = userEvent.setup()
    render(<UserPreferencesDialog {...defaultProps} />)

    await screen.findByLabelText(/display name/i)

    fireEvent.change(screen.getByLabelText(/bulletin id/i), { target: { value: 'wxyz99' } })
    await user.selectOptions(screen.getByLabelText(/input file encoding/i), 'ASCII')
    await user.selectOptions(screen.getByLabelText(/max input file size/i), '25MB')
    await user.selectOptions(screen.getByLabelText(/output file extension/i), '.iwxxm')
    await user.selectOptions(screen.getByLabelText(/output file encoding/i), 'UTF-16')
    await user.click(screen.getByLabelText(/strict validation/i))
    await user.click(screen.getByLabelText(/include nil reasons/i))
    fireEvent.change(screen.getByLabelText(/max metar length/i), { target: { value: '1500' } })
    fireEvent.change(screen.getByLabelText(/metar encoding/i), { target: { value: 'UTF-8' } })

    expect(screen.getByLabelText(/bulletin id/i)).toHaveValue('WXYZ99')
    expect(screen.getByLabelText(/input file encoding/i)).toHaveValue('ASCII')
    expect(screen.getByLabelText(/max input file size/i)).toHaveValue('25MB')
    expect(screen.getByLabelText(/output file extension/i)).toHaveValue('.iwxxm')
    expect(screen.getByLabelText(/output file encoding/i)).toHaveValue('UTF-16')
    expect(screen.getByLabelText(/strict validation/i)).not.toBeChecked()
    expect(screen.getByLabelText(/include nil reasons/i)).not.toBeChecked()
    expect(screen.getByLabelText(/max metar length/i)).toHaveValue(1500)
    expect(screen.getByLabelText(/metar encoding/i)).toHaveValue('UTF-8')
  })

  it('resets preferences after confirmation', async () => {
    localStorage.setItem(
      'metar_converter_preferences',
      JSON.stringify({ bulletinIdExample: 'ZZZZ99', issuingCenter: 'KJFK' }),
    )
    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(true)
    const onPreferencesSaved = vi.fn()
    const user = userEvent.setup()

    render(<UserPreferencesDialog {...defaultProps} onPreferencesSaved={onPreferencesSaved} />)

    await screen.findByDisplayValue('ZZZZ99')
    await user.click(screen.getByRole('button', { name: /reset preferences to defaults/i }))

    expect(confirmSpy).toHaveBeenCalled()
    expect(screen.getByDisplayValue('SAAA00')).toBeInTheDocument()
    expect(mockToast.success).toHaveBeenCalledWith('Preferences reset to defaults')
    expect(onPreferencesSaved).toHaveBeenCalledTimes(1)
  })

  it('does not reset when confirmation is cancelled', async () => {
    localStorage.setItem(
      'metar_converter_preferences',
      JSON.stringify({ bulletinIdExample: 'KEEP01' }),
    )
    vi.spyOn(window, 'confirm').mockReturnValue(false)
    const user = userEvent.setup()

    render(<UserPreferencesDialog {...defaultProps} />)

    await screen.findByDisplayValue('KEEP01')
    await user.click(screen.getByRole('button', { name: /reset preferences to defaults/i }))

    expect(screen.getByDisplayValue('KEEP01')).toBeInTheDocument()
    expect(mockToast.success).not.toHaveBeenCalled()
  })

  it('handles invalid stored preferences gracefully', async () => {
    localStorage.setItem('metar_converter_preferences', '{not-json')
    render(<UserPreferencesDialog {...defaultProps} />)

    await waitFor(() => {
      expect(mockToast.error).toHaveBeenCalledWith('Failed to load preferences')
      expect(screen.getByDisplayValue('prefs@example.com')).toBeInTheDocument()
    })
  })

  it('closes when cancel is clicked', async () => {
    const onClose = vi.fn()
    const user = userEvent.setup()
    render(<UserPreferencesDialog {...defaultProps} onClose={onClose} />)

    await screen.findByRole('button', { name: /^cancel$/i })
    await user.click(screen.getByRole('button', { name: /^cancel$/i }))

    expect(onClose).toHaveBeenCalledTimes(1)
  })
})
