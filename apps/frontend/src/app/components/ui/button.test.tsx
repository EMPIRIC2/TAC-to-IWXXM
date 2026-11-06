import React from 'react';
import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';

import { Button } from './button';

describe('Button', () => {
  it('renders with default slot attributes', () => {
    render(<Button>Run</Button>);

    const button = screen.getByRole('button', { name: 'Run' });
    expect(button).toHaveAttribute('data-slot', 'button');
    expect(button.className).toContain('inline-flex');
  });

  it('applies variant and size classes', () => {
    render(
      <Button variant="destructive" size="sm">
        Delete
      </Button>,
    );

    const button = screen.getByRole('button', { name: 'Delete' });
    expect(button.className).toContain('bg-destructive');
    expect(button.className).toContain('h-8');
  });

  it('centers default-size label with flex and no vertical padding fight', () => {
    // UX-2026-10-29-center-button-text: h-9 + py-2 crowds the line box → bottom-heavy caps.
    render(<Button>Convert</Button>);

    const button = screen.getByRole('button', { name: 'Convert' });
    expect(button.className).toContain('inline-flex');
    expect(button.className).toContain('items-center');
    expect(button.className).toContain('justify-center');
    expect(button.className).toContain('h-9');
    expect(button.className.split(/\s+/)).not.toContain('py-2');
  });

  it('supports asChild rendering', () => {
    render(
      <Button asChild>
        <a href="/home">Home</a>
      </Button>,
    );

    const link = screen.getByRole('link', { name: 'Home' });
    expect(link).toHaveAttribute('data-slot', 'button');
    expect(link).toHaveAttribute('href', '/home');
  });
});
