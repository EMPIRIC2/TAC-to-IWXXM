import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useState } from 'react'

import { IcaoAutocomplete } from './IcaoAutocomplete'

const mockIsValid = vi.hoisted(() => vi.fn())
const mockSearchByIcao = vi.hoisted(() => vi.fn())

vi.mock('../../utils/airportsData', () => ({
  airports: {
    isValid: mockIsValid,
    searchByIcao: mockSearchByIcao,
  },
}))

describe('IcaoAutocomplete', () => {
  const renderHarness = (onChangeSpy?: (value: string) => void) => {
    function Harness() {
      const [value, setValue] = useState('')

      return (
        <IcaoAutocomplete
          label="ICAO"
          value={value}
          onChange={(next) => {
            setValue(next)
            onChangeSpy?.(next)
          }}
        />
      )
    }

    return render(<Harness />)
  }

  beforeEach(() => {
    vi.clearAllMocks()
    mockIsValid.mockReturnValue(false)
    mockSearchByIcao.mockReturnValue([])
  })

  it('normalizes input to uppercase and calls onChange', async () => {
    const user = userEvent.setup()
    const onChange = vi.fn()

    renderHarness(onChange)

    await user.type(screen.getByLabelText('ICAO'), 'kj')

    expect(onChange).toHaveBeenLastCalledWith('KJ')
  })

  it('shows valid icon for valid 4-letter ICAO code', async () => {
    const user = userEvent.setup()
    mockIsValid.mockReturnValue(true)

    renderHarness()

    await user.type(screen.getByLabelText('ICAO'), 'KJFK')

    expect(mockIsValid).toHaveBeenCalledWith('KJFK')
    expect(screen.getByLabelText(/valid icao code/i)).toBeInTheDocument()
  })

  it('shows invalid icon for invalid 4-letter ICAO code', async () => {
    const user = userEvent.setup()
    mockIsValid.mockReturnValue(false)

    renderHarness()

    await user.type(screen.getByLabelText('ICAO'), 'XXXX')

    expect(screen.getByLabelText(/invalid icao code/i)).toBeInTheDocument()
  })

  it('shows suggestions and selects one from dropdown', async () => {
    const user = userEvent.setup()
    const onChange = vi.fn()
    mockSearchByIcao.mockReturnValue([
      { icao: 'KJFK', name: 'John F Kennedy', city: 'New York', country: 'US' },
      { icao: 'KLAX', name: 'Los Angeles', city: 'Los Angeles', country: 'US' },
    ])

    renderHarness(onChange)

    await user.type(screen.getByLabelText('ICAO'), 'KJ')

    expect(await screen.findByText('KJFK')).toBeInTheDocument()
    await user.click(screen.getByText('KJFK'))

    expect(onChange).toHaveBeenCalledWith('KJFK')
    await waitFor(() => {
      expect(screen.queryByText('KLAX')).not.toBeInTheDocument()
    })
  })

  it('clears suggestions and hides dropdown on empty input', async () => {
    const user = userEvent.setup()
    mockSearchByIcao.mockReturnValue([
      { icao: 'KJFK', name: 'John F Kennedy' },
    ])

    renderHarness()

    await user.type(screen.getByLabelText('ICAO'), 'KJ')
    expect(await screen.findByText('KJFK')).toBeInTheDocument()

    await user.clear(screen.getByLabelText('ICAO'))

    await waitFor(() => {
      expect(screen.queryByText('KJFK')).not.toBeInTheDocument()
    })
  })

  it('handles search error and shows empty suggestions on exception', async () => {
    const user = userEvent.setup()
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => undefined)
    mockSearchByIcao.mockImplementation(() => {
      throw new Error('search failed')
    })

    renderHarness()

    await user.type(screen.getByLabelText('ICAO'), 'KJ')

    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalledWith('Error fetching airports:', expect.any(Error))
    })

    expect(screen.queryByRole('option')).not.toBeInTheDocument()
    consoleSpy.mockRestore()
  })

  it('hides suggestions when clicking outside', async () => {
    const user = userEvent.setup()
    mockSearchByIcao.mockReturnValue([
      { icao: 'KJFK', name: 'John F Kennedy' },
    ])

    function Wrapper() {
      const [value, setValue] = useState('')

      return (
        <div>
          <IcaoAutocomplete label="ICAO" value={value} onChange={setValue} />
          <button type="button">Outside</button>
        </div>
      )
    }

    render(
      <Wrapper />,
    )

    await user.type(screen.getByLabelText('ICAO'), 'KJ')
    expect(await screen.findByText('KJFK')).toBeInTheDocument()

    fireEvent.mouseDown(screen.getByText('Outside'))

    await waitFor(() => {
      expect(screen.queryByText('KJFK')).not.toBeInTheDocument()
    })
  })

  it('handles search errors gracefully', async () => {
    const user = userEvent.setup()
    const errorSpy = vi.spyOn(console, 'error').mockImplementation(() => undefined)
    mockSearchByIcao.mockImplementation(() => {
      throw new Error('search failed')
    })

    renderHarness()

    await user.type(screen.getByLabelText('ICAO'), 'KJ')

    expect(errorSpy).toHaveBeenCalled()
    expect(screen.queryByText('KJFK')).not.toBeInTheDocument()

    errorSpy.mockRestore()
  })

  it('handles suggestion click when icao is undefined (falls back to empty string)', async () => {
    const user = userEvent.setup()
    const onChange = vi.fn()
    mockSearchByIcao.mockReturnValue([
      { name: 'Unknown Airport' }, // no icao property
    ])

    renderHarness(onChange)

    await user.type(screen.getByLabelText('ICAO'), 'KJ')
    expect(await screen.findByText('Unknown Airport')).toBeInTheDocument()

    await user.click(screen.getByText('Unknown Airport'))

    expect(onChange).toHaveBeenCalledWith('')
    await waitFor(() => {
      expect(screen.queryByText('Unknown Airport')).not.toBeInTheDocument()
    })
  })

  it('does not search when input length is exactly 1', async () => {
    const user = userEvent.setup()
    renderHarness()

    await user.type(screen.getByLabelText('ICAO'), 'K')

    expect(mockSearchByIcao).not.toHaveBeenCalled()
    expect(screen.queryByRole('option')).not.toBeInTheDocument()
  })

  it('displays city and country in suggestion list', async () => {
    const user = userEvent.setup()
    mockSearchByIcao.mockReturnValue([
      { icao: 'KJFK', name: 'John F Kennedy', city: 'New York', country: 'US' },
    ])

    renderHarness()

    await user.type(screen.getByLabelText('ICAO'), 'KJ')

    expect(await screen.findByText('KJFK')).toBeInTheDocument()
    expect(screen.getByText('New York, US')).toBeInTheDocument()
  })
})
