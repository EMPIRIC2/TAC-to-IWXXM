/**
 * Optional browser Sentry init (EV-052 / AC6).
 * Uses runtime ``sentryDsn`` from ``/config.json``, then ``VITE_SENTRY_DSN``.
 */

import * as Sentry from '@sentry/react';

import { getRuntimeConfig } from './runtime-config';

/**
 * Initialize browser error reporting when a DSN is configured.
 *
 * @returns True when Sentry was initialized; false when no DSN is available.
 */
export function initSentry(): boolean {
  const fromConfig = getRuntimeConfig().sentryDsn?.trim() ?? '';
  const fromVite = (import.meta.env.VITE_SENTRY_DSN || '').trim();
  const dsn = fromConfig || fromVite;
  if (!dsn) {
    return false;
  }
  Sentry.init({
    dsn,
    tracesSampleRate: 0,
    sendDefaultPii: false,
  });
  return true;
}
