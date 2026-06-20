import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { Checkbox } from './checkbox'
import { RadioGroup, RadioGroupItem } from './radio-group'
import { Switch } from './switch'
import { Toggle } from './toggle'

describe('Form Basics UI Wrappers', () => {
  it('renders checkbox slot and toggles checked state', async () => {
    const user = userEvent.setup()
    render(<Checkbox aria-label="Enable reports" />)

    const checkbox = screen.getByRole('checkbox', { name: 'Enable reports' })
    expect(checkbox).toHaveAttribute('data-slot', 'checkbox')
    expect(checkbox).toHaveAttribute('data-state', 'unchecked')

    await user.click(checkbox)
    expect(checkbox).toHaveAttribute('data-state', 'checked')
  })

  it('renders radio group and updates selected item', async () => {
    const user = userEvent.setup()
    render(
      <RadioGroup defaultValue="a" aria-label="Wind direction">
        <RadioGroupItem id="radio-a" value="a" aria-label="North" />
        <RadioGroupItem id="radio-b" value="b" aria-label="South" />
      </RadioGroup>,
    )

    const north = screen.getByRole('radio', { name: 'North' })
    const south = screen.getByRole('radio', { name: 'South' })

    expect(north).toHaveAttribute('data-slot', 'radio-group-item')
    expect(north).toHaveAttribute('data-state', 'checked')

    await user.click(south)
    expect(south).toHaveAttribute('data-state', 'checked')
    expect(north).toHaveAttribute('data-state', 'unchecked')
  })

  it('renders switch slot and supports disabled state', async () => {
    const user = userEvent.setup()
    const { rerender } = render(<Switch aria-label="Auto-convert" />)

    const enabledSwitch = screen.getByRole('switch', { name: 'Auto-convert' })
    expect(enabledSwitch).toHaveAttribute('data-slot', 'switch')
    expect(enabledSwitch).toHaveAttribute('data-state', 'unchecked')

    await user.click(enabledSwitch)
    expect(enabledSwitch).toHaveAttribute('data-state', 'checked')

    rerender(<Switch aria-label="Auto-convert" disabled />)
    const disabledSwitch = screen.getByRole('switch', { name: 'Auto-convert' })
    expect(disabledSwitch).toBeDisabled()
  })

  it('renders toggle slot and toggles pressed state', async () => {
    const user = userEvent.setup()
    render(
      <Toggle aria-label="Pin parameters" variant="outline" size="sm">
        Pin
      </Toggle>,
    )

    const toggle = screen.getByRole('button', { name: 'Pin parameters' })
    expect(toggle).toHaveAttribute('data-slot', 'toggle')
    expect(toggle).toHaveAttribute('data-state', 'off')

    await user.click(toggle)
    expect(toggle).toHaveAttribute('data-state', 'on')
  })
})
