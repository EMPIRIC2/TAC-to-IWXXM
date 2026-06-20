import React from 'react'
import { describe, expect, it } from 'vitest'
import { fireEvent, render, screen } from '@testing-library/react'

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from './dialog'

describe('Dialog', () => {
  it('opens and closes content from trigger', () => {
    render(
      <Dialog>
        <DialogTrigger>Open dialog</DialogTrigger>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Dialog Title</DialogTitle>
            <DialogDescription>Dialog Description</DialogDescription>
          </DialogHeader>
          <DialogFooter>Footer text</DialogFooter>
        </DialogContent>
      </Dialog>,
    )

    expect(screen.queryByText('Dialog Title')).not.toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: 'Open dialog' }))

    expect(screen.getByText('Dialog Title')).toBeInTheDocument()
    expect(screen.getByText('Dialog Description')).toBeInTheDocument()
    expect(screen.getByText('Footer text')).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: 'Close' }))

    expect(screen.queryByText('Dialog Title')).not.toBeInTheDocument()
  })

  it('renders overlay and content slot attributes when open', () => {
    render(
      <Dialog defaultOpen>
        <DialogContent>
          <DialogTitle>Open by default</DialogTitle>
        </DialogContent>
      </Dialog>,
    )

    const overlay = document.querySelector('[data-slot="dialog-overlay"]')
    const content = document.querySelector('[data-slot="dialog-content"]')
    expect(overlay).toBeTruthy()
    expect(content).toBeTruthy()
    expect(screen.getByText('Open by default')).toBeInTheDocument()
  })
})
