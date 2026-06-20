import { describe, expect, it } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from './collapsible'
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from './accordion'
import { Popover, PopoverContent, PopoverTrigger } from './popover'
import { HoverCard, HoverCardContent, HoverCardTrigger } from './hover-card'

describe('Collapse and Disclosure UI Wrappers', () => {
  it('toggles collapsible content from trigger click', async () => {
    const user = userEvent.setup()
    render(
      <Collapsible>
        <CollapsibleTrigger>Details</CollapsibleTrigger>
        <CollapsibleContent>Hidden details</CollapsibleContent>
      </Collapsible>,
    )

    const trigger = screen.getByRole('button', { name: 'Details' })
    expect(trigger).toHaveAttribute('data-slot', 'collapsible-trigger')
    expect(screen.queryByText('Hidden details')).not.toBeInTheDocument()

    await user.click(trigger)
    expect(screen.getByText('Hidden details')).toBeInTheDocument()
  })

  it('opens accordion item when trigger is clicked', async () => {
    const user = userEvent.setup()
    render(
      <Accordion type="single" collapsible>
        <AccordionItem value="item-1">
          <AccordionTrigger>Weather Settings</AccordionTrigger>
          <AccordionContent>Settings panel content</AccordionContent>
        </AccordionItem>
      </Accordion>,
    )

    const trigger = screen.getByRole('button', { name: 'Weather Settings' })
    expect(trigger).toHaveAttribute('data-slot', 'accordion-trigger')

    await user.click(trigger)
    expect(screen.getByText('Settings panel content')).toBeInTheDocument()
  })

  it('opens popover content from trigger click', async () => {
    const user = userEvent.setup()
    render(
      <Popover>
        <PopoverTrigger>Open Popover</PopoverTrigger>
        <PopoverContent>Popover body</PopoverContent>
      </Popover>,
    )

    const trigger = screen.getByRole('button', { name: 'Open Popover' })
    await user.click(trigger)

    const content = await screen.findByText('Popover body')
    expect(content).toHaveAttribute('data-slot', 'popover-content')
  })

  it('shows hover card content on hover', async () => {
    const user = userEvent.setup()
    render(
      <HoverCard openDelay={0} closeDelay={0}>
        <HoverCardTrigger>Hover me</HoverCardTrigger>
        <HoverCardContent>Hover details</HoverCardContent>
      </HoverCard>,
    )

    const trigger = screen.getByText('Hover me')
    await user.hover(trigger)

    await waitFor(() => {
      expect(screen.getByText('Hover details')).toBeInTheDocument()
    })
  })
})
