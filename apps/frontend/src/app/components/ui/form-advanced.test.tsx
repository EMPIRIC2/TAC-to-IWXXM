import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { OTPInputContext } from 'input-otp'

import { InputOTP, InputOTPGroup, InputOTPSeparator, InputOTPSlot } from './input-otp'
import { Slider } from './slider'
import { ToggleGroup, ToggleGroupItem } from './toggle-group'
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectSeparator,
  SelectTrigger,
  SelectValue,
} from './select'

describe('Form Advanced UI Wrappers', () => {
  it('renders input-otp root with slot and custom classes', () => {
    const { container } = render(
      <InputOTP
        maxLength={6}
        value="123"
        onChange={() => undefined}
        aria-label="OTP"
        className="otp-class"
        containerClassName="otp-container"
      />,
    )

    const root = container.querySelector('[data-slot="input-otp"]')
    expect(root).toBeTruthy()
    expect(root).toHaveClass('otp-class')

    const otpContainer = container.querySelector('.otp-container')
    expect(otpContainer).toBeTruthy()
  })

  it('renders input-otp group and separator slots', () => {
    render(
      <>
        <InputOTPGroup data-testid="otp-group" />
        <InputOTPSeparator />
      </>,
    )

    expect(screen.getByTestId('otp-group')).toHaveAttribute('data-slot', 'input-otp-group')
    const separator = screen.getByRole('separator')
    expect(separator).toHaveAttribute('data-slot', 'input-otp-separator')
  })

  it('renders input-otp slot with active state from context', () => {
    render(
      <OTPInputContext.Provider
        value={{
          slots: [
            {
              char: '7',
              hasFakeCaret: true,
              isActive: true,
            },
          ],
          isFocused: true,
          isHovering: false,
        }}
      >
        <InputOTPSlot index={0} />
      </OTPInputContext.Provider>,
    )

    const slot = document.querySelector('[data-slot="input-otp-slot"]')
    expect(slot).toBeTruthy()
    expect(slot).toHaveAttribute('data-active', 'true')
    expect(screen.getByText('7')).toBeInTheDocument()
  })

  it('renders slider with single thumb by default value', () => {
    const { container } = render(<Slider defaultValue={[20]} min={0} max={100} />)

    const slider = container.querySelector('[data-slot="slider"]')
    const thumbs = container.querySelectorAll('[data-slot="slider-thumb"]')
    expect(slider).toBeTruthy()
    expect(thumbs).toHaveLength(1)
  })

  it('renders slider with two thumbs when value array has two items', () => {
    const { container } = render(<Slider value={[10, 80]} min={0} max={100} onValueChange={() => undefined} />)

    const thumbs = container.querySelectorAll('[data-slot="slider-thumb"]')
    expect(thumbs).toHaveLength(2)
  })

  it('renders slider with two thumbs when defaultValue is omitted', () => {
    const { container } = render(<Slider min={0} max={100} />)
    const thumbs = container.querySelectorAll('[data-slot="slider-thumb"]')
    expect(thumbs).toHaveLength(2)
  })

  it('toggles toggle-group single selection between items', async () => {
    const user = userEvent.setup()
    render(
      <ToggleGroup type="single" defaultValue="metar" aria-label="Format select">
        <ToggleGroupItem value="metar" aria-label="METAR">METAR</ToggleGroupItem>
        <ToggleGroupItem value="taf" aria-label="TAF">TAF</ToggleGroupItem>
      </ToggleGroup>,
    )

    const metar = screen.getByRole('radio', { name: 'METAR' })
    const taf = screen.getByRole('radio', { name: 'TAF' })
    expect(metar).toHaveAttribute('data-state', 'on')

    await user.click(taf)
    expect(taf).toHaveAttribute('data-state', 'on')
    expect(metar).toHaveAttribute('data-state', 'off')
  })

  it('propagates variant and size from toggle-group root to items', () => {
    render(
      <ToggleGroup type="single" variant="outline" size="sm" defaultValue="a">
        <ToggleGroupItem value="a" aria-label="A">A</ToggleGroupItem>
      </ToggleGroup>,
    )

    const group = document.querySelector('[data-slot="toggle-group"]')
    const item = document.querySelector('[data-slot="toggle-group-item"]')
    expect(group).toHaveAttribute('data-variant', 'outline')
    expect(group).toHaveAttribute('data-size', 'sm')
    expect(item).toHaveAttribute('data-variant', 'outline')
    expect(item).toHaveAttribute('data-size', 'sm')
  })

  it('opens select content and selects item', async () => {
    const user = userEvent.setup()

    render(
      <Select defaultValue="2025-2">
        <SelectTrigger aria-label="IWXXM Version">
          <SelectValue placeholder="Select version" />
        </SelectTrigger>
        <SelectContent>
          <SelectGroup>
            <SelectLabel>Versions</SelectLabel>
            <SelectItem value="2025-2">2025-2</SelectItem>
            <SelectItem value="2023-1">2023-1</SelectItem>
          </SelectGroup>
        </SelectContent>
      </Select>,
    )

    const trigger = screen.getByRole('combobox', { name: 'IWXXM Version' })
    expect(trigger).toHaveAttribute('data-slot', 'select-trigger')

    await user.click(trigger)
    const option = await screen.findByRole('option', { name: '2023-1' })
    await user.click(option)

    expect(screen.getByRole('combobox', { name: 'IWXXM Version' })).toHaveTextContent('2023-1')
  })

  it('renders select label and separator in content', async () => {
    const user = userEvent.setup()

    render(
      <Select>
        <SelectTrigger aria-label="Error behavior">
          <SelectValue placeholder="Select mode" />
        </SelectTrigger>
        <SelectContent>
          <SelectGroup>
            <SelectLabel>Modes</SelectLabel>
            <SelectItem value="warn">Warn</SelectItem>
            <SelectSeparator />
            <SelectItem value="fail">Fail</SelectItem>
          </SelectGroup>
        </SelectContent>
      </Select>,
    )

    await user.click(screen.getByRole('combobox', { name: 'Error behavior' }))
    expect(await screen.findByText('Modes')).toBeInTheDocument()
    const separator = document.querySelector('[data-slot="select-separator"]')
    expect(separator).toBeTruthy()
  })

  it('prevents selecting disabled select item', async () => {
    const user = userEvent.setup()

    render(
      <Select defaultValue="warn">
        <SelectTrigger aria-label="Disabled check">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectGroup>
            <SelectItem value="warn">Warn</SelectItem>
            <SelectItem value="blocked" disabled>Blocked</SelectItem>
          </SelectGroup>
        </SelectContent>
      </Select>,
    )

    const trigger = screen.getByRole('combobox', { name: 'Disabled check' })
    await user.click(trigger)

    const blocked = await screen.findByRole('option', { name: 'Blocked' })
    await user.click(blocked)

    expect(screen.getByRole('combobox', { name: 'Disabled check', hidden: true })).toHaveTextContent('Warn')
  })
})
