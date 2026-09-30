/**
 * Blocking acknowledgement before convert, catalogs, and the rest of the public shell.
 * @example
 * const _ = true;
 */

import { useState } from 'react';
import { Button } from './ui/button';
import {
  SITE_TERMS_BODY,
  SITE_TERMS_CHECKBOX,
  SITE_TERMS_CONTINUE,
  SITE_TERMS_TITLE,
} from '@/utils/siteTermsCopy';

/**
 * Type `TermsConsentGateProps`.
 * @example
 * const _ = true;
 */
export interface TermsConsentGateProps {
  onAcknowledge: () => void;
}

/**
 * Full-screen gate. Continue stays disabled until the checkbox is checked.
 * @example
 * const _ = true;
 */
export function TermsConsentGate({ onAcknowledge }: TermsConsentGateProps) {
  const [checked, setChecked] = useState(false);

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="site-terms-title"
      data-testid="site-terms-gate"
      className="flex min-h-screen items-center justify-center bg-gray-50 p-4 dark:bg-gray-950"
    >
      <div className="w-full max-w-lg rounded-lg border border-gray-200 bg-white p-6 text-left shadow-sm dark:border-gray-700 dark:bg-gray-900">
        <h1
          id="site-terms-title"
          className="text-lg font-semibold text-gray-900 dark:text-gray-100"
        >
          {SITE_TERMS_TITLE}
        </h1>
        <p className="mt-3 text-sm text-gray-700 dark:text-gray-200">
          {SITE_TERMS_BODY}
        </p>
        <label className="mt-4 flex items-start gap-2 text-sm text-gray-800 dark:text-gray-100">
          <input
            type="checkbox"
            className="mt-1 h-4 w-4"
            data-testid="site-terms-ack"
            checked={checked}
            onChange={(event) => setChecked(event.target.checked)}
          />
          <span>{SITE_TERMS_CHECKBOX}</span>
        </label>
        <Button
          type="button"
          className="mt-4"
          data-testid="site-terms-continue"
          disabled={!checked}
          onClick={onAcknowledge}
        >
          {SITE_TERMS_CONTINUE}
        </Button>
      </div>
    </div>
  );
}
