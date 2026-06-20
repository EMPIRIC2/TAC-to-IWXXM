import React from 'react'
import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'

import { Button } from './button'

describe('Button', () => {
  it('renders with default slot attributes', () => {
    render(<Button>Run</Button>)

    const button = screen.getByRole('button', { name: 'Run' })
    expect(button).toHaveAttribute('data-slot', 'button')
    expect(button.className).toContain('inline-flex')
  })

  it('applies variant and size classes', () => {
    render(
      <Button variant="destructive" size="sm">
        Delete
      </Button>,
    )

    const button = screen.getByRole('button', { name: 'Delete' })
    expect(button.className).toContain('bg-destructive')
    expect(button.className).toContain('h-8')
  })

  it('supports asChild rendering', () => {
    render(
      <Button asChild>
        <a href="/home">Home</a>
      </Button>,
    )

    const link = screen.getByRole('link', { name: 'Home' })
    expect(link).toHaveAttribute('data-slot', 'button')
    expect(link).toHaveAttribute('href', '/home')
  })
})
