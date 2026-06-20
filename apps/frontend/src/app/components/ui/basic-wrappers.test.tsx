import React from 'react'
import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'

import { Alert, AlertDescription, AlertTitle } from './alert'
import { Badge } from './badge'
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from './card'
import { Separator } from './separator'

describe('basic UI wrappers', () => {
  it('renders all card slots', () => {
    const { container } = render(
      <Card>
        <CardHeader>
          <CardTitle>Flight Summary</CardTitle>
          <CardDescription>Details</CardDescription>
          <CardAction>Action</CardAction>
        </CardHeader>
        <CardContent>Body</CardContent>
        <CardFooter>Footer</CardFooter>
      </Card>,
    )

    expect(container.querySelector('[data-slot="card"]')).toBeTruthy()
    expect(container.querySelector('[data-slot="card-header"]')).toBeTruthy()
    expect(container.querySelector('[data-slot="card-title"]')).toHaveTextContent('Flight Summary')
    expect(container.querySelector('[data-slot="card-description"]')).toHaveTextContent('Details')
    expect(container.querySelector('[data-slot="card-action"]')).toHaveTextContent('Action')
    expect(container.querySelector('[data-slot="card-content"]')).toHaveTextContent('Body')
    expect(container.querySelector('[data-slot="card-footer"]')).toHaveTextContent('Footer')
  })

  it('renders alert variants and alert role', () => {
    render(
      <Alert variant="destructive">
        <AlertTitle>Conversion Failed</AlertTitle>
        <AlertDescription>Please retry with a valid METAR.</AlertDescription>
      </Alert>,
    )

    const alert = screen.getByRole('alert')
    expect(alert).toHaveAttribute('data-slot', 'alert')
    expect(alert.className).toContain('text-destructive')
    expect(screen.getByText('Conversion Failed')).toHaveAttribute('data-slot', 'alert-title')
    expect(screen.getByText('Please retry with a valid METAR.')).toHaveAttribute('data-slot', 'alert-description')
  })

  it('supports badge variants and asChild slotting', () => {
    const { rerender } = render(<Badge variant="secondary">Queued</Badge>)
    const badge = screen.getByText('Queued')
    expect(badge).toHaveAttribute('data-slot', 'badge')
    expect(badge.className).toContain('bg-secondary')

    rerender(
      <Badge asChild variant="outline">
        <a href="/status">Status</a>
      </Badge>,
    )

    const link = screen.getByRole('link', { name: 'Status' })
    expect(link).toHaveAttribute('data-slot', 'badge')
    expect(link.className).toContain('text-foreground')
  })

  it('renders separator with orientation classes', () => {
    const { container, rerender } = render(<Separator orientation="horizontal" />)

    const horizontal = container.querySelector('[data-slot="separator-root"]')
    expect(horizontal).toBeTruthy()
    expect(horizontal?.className).toContain('data-[orientation=horizontal]:h-px')

    rerender(<Separator orientation="vertical" decorative={false} />)
    const vertical = container.querySelector('[data-slot="separator-root"]')
    expect(vertical).toHaveAttribute('data-orientation', 'vertical')
    expect(vertical?.className).toContain('data-[orientation=vertical]:w-px')
  })
})
