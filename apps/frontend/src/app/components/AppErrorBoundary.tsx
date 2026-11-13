/**
 * Top-level error boundary for the operator app.
 *
 * Without a boundary, any render-time error unmounts the whole React tree and the
 * page goes completely blank with no operator feedback. This boundary catches those
 * errors and shows a clear, non-blank fallback with a reload action instead.
 *
 * [Corpus: product §F7] [Corpus: ui-style]
 */

import { Component, type ErrorInfo, type ReactNode } from 'react';

/**
 * Props for the app error boundary.
 * @example
 * const _ = true;
 */
export interface AppErrorBoundaryProps {
  /** Application tree to guard. */
  children: ReactNode;
}

/**
 * Internal boundary state.
 * @example
 * const _ = true;
 */
export interface AppErrorBoundaryState {
  /** True once a descendant render threw. */
  hasError: boolean;
}

/** Operator-facing fallback copy (plain language, no internal references). */
export const APP_ERROR_BOUNDARY_TITLE = 'The page could not be displayed';
export const APP_ERROR_BOUNDARY_BODY =
  'Something went wrong while loading the app. Reload the page to try again. If it keeps happening, your work drafts stay saved on this device.';
export const APP_ERROR_BOUNDARY_RELOAD = 'Reload page';

/**
 * Catch render crashes so the operator always sees a message instead of a blank page.
 *
 * @example
 * const _ = true;
 */
export class AppErrorBoundary extends Component<
  AppErrorBoundaryProps,
  AppErrorBoundaryState
> {
  state: AppErrorBoundaryState = { hasError: false };

  /**
   * Flip into the fallback state when a descendant throws during render.
   *
   * @returns Next boundary state
   */
  static getDerivedStateFromError(): AppErrorBoundaryState {
    return { hasError: true };
  }

  /**
   * Log the crash so it is recoverable from the browser console / monitoring.
   *
   * @param error - Thrown error
   * @param info - React component stack
   */
  componentDidCatch(error: Error, info: ErrorInfo): void {
    console.error('[AppErrorBoundary] render error:', error, info.componentStack);
  }

  /** Reload the current page to recover from the crash. */
  private readonly handleReload = (): void => {
    window.location.reload();
  };

  /**
   * Render the guarded children, or the non-blank fallback after a crash.
   *
   * @returns App tree or fallback
   */
  render(): ReactNode {
    if (!this.state.hasError) {
      return this.props.children;
    }

    return (
      <div
        role="alert"
        data-testid="app-error-boundary"
        className="mx-auto flex min-h-screen max-w-lg flex-col items-center justify-center gap-4 px-6 text-center"
      >
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          {APP_ERROR_BOUNDARY_TITLE}
        </h1>
        <p className="text-base text-gray-600 dark:text-gray-300">
          {APP_ERROR_BOUNDARY_BODY}
        </p>
        <button
          type="button"
          data-testid="app-error-boundary-reload"
          onClick={this.handleReload}
          className="rounded-md bg-gray-900 px-4 py-2 text-sm font-medium text-white dark:bg-gray-100 dark:text-gray-900"
        >
          {APP_ERROR_BOUNDARY_RELOAD}
        </button>
      </div>
    );
  }
}
