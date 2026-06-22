import React from 'react';
import { describe, expect, it } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/react';

import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from './dialog';

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
    );

    expect(screen.queryByText('Dialog Title')).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Open dialog' }));

    expect(screen.getByText('Dialog Title')).toBeInTheDocument();
    expect(screen.getByText('Dialog Description')).toBeInTheDocument();
    expect(screen.getByText('Footer text')).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Close' }));

    expect(screen.queryByText('Dialog Title')).not.toBeInTheDocument();
  });

  it('renders overlay and content slot attributes when open', () => {
    render(
      <Dialog defaultOpen>
        <DialogContent>
          <DialogTitle>Open by default</DialogTitle>
        </DialogContent>
      </Dialog>,
    );

    const overlay = document.querySelector('[data-slot="dialog-overlay"]');
    const content = document.querySelector('[data-slot="dialog-content"]');
    expect(overlay).toBeTruthy();
    expect(content).toBeTruthy();
    expect(screen.getByText('Open by default')).toBeInTheDocument();
  });

  it('closes dialog from explicit DialogClose control', () => {
    render(
      <Dialog defaultOpen>
        <DialogContent>
          <DialogTitle>Closeable dialog</DialogTitle>
          <DialogClose>Close dialog</DialogClose>
        </DialogContent>
      </Dialog>,
    );

    expect(screen.getByText('Closeable dialog')).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Close dialog' }));

    expect(screen.queryByText('Closeable dialog')).not.toBeInTheDocument();
  });

  it('renders dialog subcomponents with custom class names', () => {
    render(
      <Dialog defaultOpen>
        <DialogContent className="custom-content">
          <DialogHeader className="custom-header">
            <DialogTitle className="custom-title">Styled dialog</DialogTitle>
            <DialogDescription className="custom-description">
              Styled description
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="custom-footer">Footer actions</DialogFooter>
        </DialogContent>
      </Dialog>,
    );

    expect(document.querySelector('[data-slot="dialog-overlay"]')).toBeTruthy();
    expect(document.querySelector('.custom-content')).toBeTruthy();
    expect(document.querySelector('.custom-header')).toBeTruthy();
    expect(document.querySelector('.custom-title')).toHaveTextContent('Styled dialog');
    expect(document.querySelector('.custom-description')).toHaveTextContent(
      'Styled description',
    );
    expect(document.querySelector('.custom-footer')).toHaveTextContent(
      'Footer actions',
    );
  });
});
