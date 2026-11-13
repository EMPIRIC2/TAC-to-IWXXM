/**
 * Regression: a render crash must never leave a blank page (HF-blank-main).
 */

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { cleanup, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import {
  AppErrorBoundary,
  APP_ERROR_BOUNDARY_BODY,
  APP_ERROR_BOUNDARY_RELOAD,
  APP_ERROR_BOUNDARY_TITLE,
} from './AppErrorBoundary';

/** Child that throws on render to exercise the boundary. */
function Boom(): JSX.Element {
  throw new Error('boom');
}

describe('AppErrorBoundary', () => {
  let consoleErrorSpy: ReturnType<typeof vi.spyOn>;

  beforeEach(() => {
    consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => undefined);
  });

  afterEach(() => {
    consoleErrorSpy.mockRestore();
    cleanup();
  });

  it('renders children unchanged when nothing throws', () => {
    render(
      <AppErrorBoundary>
        <div data-testid="healthy-child">healthy</div>
      </AppErrorBoundary>,
    );

    expect(screen.getByTestId('healthy-child')).toHaveTextContent('healthy');
    expect(screen.queryByTestId('app-error-boundary')).not.toBeInTheDocument();
  });

  it('shows a clear non-blank fallback when a child throws', () => {
    render(
      <AppErrorBoundary>
        <Boom />
      </AppErrorBoundary>,
    );

    const fallback = screen.getByTestId('app-error-boundary');
    expect(fallback).toBeInTheDocument();
    expect(fallback).toHaveAttribute('role', 'alert');
    expect(fallback).toHaveTextContent(APP_ERROR_BOUNDARY_TITLE);
    expect(fallback).toHaveTextContent(APP_ERROR_BOUNDARY_BODY);
    // Fallback is never blank: it carries visible operator text.
    expect((fallback.textContent ?? '').trim().length).toBeGreaterThan(0);
  });

  it('logs the crash so it is recoverable from the console', () => {
    render(
      <AppErrorBoundary>
        <Boom />
      </AppErrorBoundary>,
    );

    expect(consoleErrorSpy).toHaveBeenCalledWith(
      '[AppErrorBoundary] render error:',
      expect.any(Error),
      expect.anything(),
    );
  });

  it('offers a reload action that reloads the page', async () => {
    const reload = vi.fn();
    const original = window.location;
    Object.defineProperty(window, 'location', {
      configurable: true,
      value: { ...original, reload },
    });

    try {
      const user = userEvent.setup();
      render(
        <AppErrorBoundary>
          <Boom />
        </AppErrorBoundary>,
      );

      const button = screen.getByTestId('app-error-boundary-reload');
      expect(button).toHaveTextContent(APP_ERROR_BOUNDARY_RELOAD);
      await user.click(button);
      expect(reload).toHaveBeenCalledTimes(1);
    } finally {
      Object.defineProperty(window, 'location', {
        configurable: true,
        value: original,
      });
    }
  });

  it('keeps fallback copy free of internal planning references', () => {
    render(
      <AppErrorBoundary>
        <Boom />
      </AppErrorBoundary>,
    );

    const fallback = screen.getByTestId('app-error-boundary');
    expect(fallback.textContent ?? '').not.toMatch(/\[Corpus|ADR-|EV-|TC-|#\d|S0\d/);
  });
});
